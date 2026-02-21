import logging
import time
import sys
import os
import sqlite3
import base64
import io
import requests
from PIL import Image
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from config import get_now_hanoi, HANOI_TZ

logger = logging.getLogger("pricing_strategy")
logging.basicConfig(level=logging.INFO)


class PricingStrategyAgent:
    """
    Implements a 2-tier dynamic markdown pricing strategy for used books.

    Tier 1: ~65% of new book market price. Target window: 30 days.
    Tier 2: ~40% of new book market price. Goal: rapid liquidation / capital recovery.
    """

    TIER1_RATIO = 0.65  # 65% of new-book market price
    TIER2_RATIO = 0.40  # 40% of new-book market price
    TIER1_DAYS = 30     # After 30 days unsold, move to Tier 2
    COGS_RATIO = 0.35   # 35% of List Price (compare_at_price)


    def __init__(self):
        from haravan_client import HaravanClient
        self.hrv = HaravanClient()
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pricing_history.db")
        self._init_history_db()

    def _init_history_db(self):
        """Initializes the pricing history and bundle mappings database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # History table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS pricing_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id TEXT,
                        title TEXT,
                        from_tier INTEGER,
                        to_tier INTEGER,
                        old_price REAL,
                        new_price REAL,
                        transitioned_at TEXT
                    )
                ''')
                # Bundle Mappings table (Phase 7.5)
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS bundle_mappings (
                        bundle_id TEXT PRIMARY KEY,
                        bundle_title TEXT,
                        component_ids TEXT, -- Commma separated IDs
                        component_skus TEXT, -- Comma separated SKUs
                        created_at TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def _log_tier_transition(self, product_id, title, from_tier, to_tier, old_price, new_price):
        """Record a tier change in the local pricing_history SQLite database."""
        try:
            now = get_now_hanoi().strftime("%Y-%m-%d %H:%M:%S")
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO pricing_history (product_id, title, from_tier, to_tier, old_price, new_price, transitioned_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (str(product_id), title, from_tier, to_tier, old_price, new_price, now)
                )
                conn.commit()
            logger.info(f"  📝 History logged: {title} Tier{from_tier}→Tier{to_tier}")
        except Exception as e:
            logger.error(f"Failed to log tier transition for {title}: {e}")

    def _get_market_price(self, book_title: str) -> float:
        """Fetch the median market price (new books) from Price Scout."""
        try:
            from ai_agents.price_scout import PriceScoutAgent
            scout = PriceScoutAgent()
            # Only search Tiki for speed & reliability (has API)
            tiki_results = scout.scout_tiki(book_title)
            prices = [r['price'] for r in tiki_results if r.get('price', 0) > 0]
            if prices:
                # Use the median price to avoid outliers
                prices_sorted = sorted(prices)
                mid = len(prices_sorted) // 2
                return float(prices_sorted[mid])
        except Exception as e:
            logger.warning(f"Could not fetch market price for '{book_title}': {e}")
        return 0.0

    # Category floor prices (VND) for rare books when no market data exists
    CATEGORY_FLOOR_PRICES = {
        "van-hoc":     60_000,
        "lich-su":     80_000,
        "kinh-te":    120_000,
        "chuyen-nganh": 200_000,
        "khoa-hoc":   150_000,
        "thieu-nhi":   40_000,
        "self-help":   70_000,
        "default":     60_000,
    }

    def _get_tiki_median_price(self, book_title: str) -> float:
        """Fetch the median new-book market price from Tiki."""
        try:
            from ai_agents.price_scout import PriceScoutAgent
            scout = PriceScoutAgent()
            tiki_results = scout.scout_tiki(book_title)
            prices = [r['price'] for r in tiki_results if r.get('price', 0) > 0]
            if prices:
                prices_sorted = sorted(prices)
                return float(prices_sorted[len(prices_sorted) // 2])
        except Exception as e:
            logger.warning(f"Tiki price fetch failed: {e}")
        return 0.0

    def _get_oreka_median_price(self, book_title: str) -> float:
        """Fetch the median used-book price from Oreka."""
        try:
            from ai_agents.price_scout import PriceScoutAgent
            scout = PriceScoutAgent()
            oreka_results = scout.scout_oreka(book_title)
            prices = [r['price'] for r in oreka_results if r.get('price', 0) > 0]
            if prices:
                prices_sorted = sorted(prices)
                return float(prices_sorted[len(prices_sorted) // 2])
        except Exception as e:
            logger.warning(f"Oreka price fetch failed: {e}")
        return 0.0

    def suggest_prices(self, book_title: str, category: str = "default") -> dict:
        """
        Full 3-case pricing suggestion:
          Case 1 - Common book:    found on Tiki → Tier1=65%, Tier2=40%
          Case 2 - Scarce book:   not on Tiki/Fahasa, found on Oreka → Oreka×90% / Oreka×110%
          Case 3 - Ultra-rare:    not anywhere → category floor × premium
        """
        logger.info(f"Calculating pricing strategy for: '{book_title}' (category: {category})")

        # --- Step 1: Try mainstream market (Tiki) ---
        tiki_price = self._get_tiki_median_price(book_title)

        if tiki_price > 0:
            # CASE 1: Common book
            tier1_price = round(tiki_price * self.TIER1_RATIO / 1000) * 1000
            tier2_price = round(tiki_price * self.TIER2_RATIO / 1000) * 1000
            return {
                "book_title": book_title,
                "pricing_mode": "standard",
                "pricing_mode_label": "📗 Sách phổ thông",
                "market_price": int(tiki_price),
                "market_source": "Tiki",
                "tier1": {
                    "price": int(tier1_price),
                    "ratio_pct": int(self.TIER1_RATIO * 100),
                    "strategy": f"Giá bán trong {self.TIER1_DAYS} ngày đầu",
                    "label": "Giá Cạnh Tranh",
                },
                "tier2": {
                    "price": int(tier2_price),
                    "ratio_pct": int(self.TIER2_RATIO * 100),
                    "strategy": "Giá thoát kho sau 30 ngày",
                    "label": "Giá Thanh Lý",
                },
                "recommendation": (
                    f"Đặt giá {int(tier1_price):,}đ trong {self.TIER1_DAYS} ngày đầu. "
                    f"Nếu chưa bán được, hạ xuống {int(tier2_price):,}đ để thoát hàng."
                )
            }

        # --- Step 2: Book not on Tiki — check Oreka (used market only) ---
        logger.info(f"  → Not found on Tiki. Checking Oreka for scarcity pricing...")
        oreka_price = self._get_oreka_median_price(book_title)

        if oreka_price > 0:
            # CASE 2: Scarce book — price relative to Oreka used-book market
            # Good condition: price slightly above competitors; liquidation: match or slightly below
            tier1_price = round(oreka_price * 1.05 / 1000) * 1000   # Match/slight premium over Oreka
            tier2_price = round(oreka_price * 0.85 / 1000) * 1000   # Undercut slightly to move it

            return {
                "book_title": book_title,
                "pricing_mode": "scarcity",
                "pricing_mode_label": "📙 Sách hiếm - Không còn trên Tiki/Fahasa",
                "market_price": int(oreka_price),
                "market_source": "Oreka (Sách cũ)",
                "tier1": {
                    "price": int(tier1_price),
                    "ratio_pct": 105,
                    "strategy": f"Định giá nhẹ trên Oreka vì sách hiếm",
                    "label": "Giá Sách Hiếm",
                },
                "tier2": {
                    "price": int(tier2_price),
                    "ratio_pct": 85,
                    "strategy": "Hạ giá thấp hơn Oreka để thoát nhanh",
                    "label": "Giá Thoát Kho Hiếm",
                },
                "recommendation": (
                    f"⚠️ Sách không còn trên Tiki/Fahasa — đây là sách HIẾM! "
                    f"Trên Oreka đang bán ~{int(oreka_price):,}đ. "
                    f"Định giá {int(tier1_price):,}đ (cao hơn 5%). "
                    f"Nếu 30 ngày chưa bán, hạ xuống {int(tier2_price):,}đ."
                ),
                "scarcity_badge": True,
            }

        # --- Step 3: Not found anywhere — ultra-rare, use category floor ---
        logger.info(f"  → Not found anywhere. Using category floor pricing.")
        floor = self.CATEGORY_FLOOR_PRICES.get(category, self.CATEGORY_FLOOR_PRICES["default"])
        tier1_price = round(floor * 1.5 / 1000) * 1000   # Premium for ultra-rare
        tier2_price = round(floor * 1.0 / 1000) * 1000   # Base floor as liquidation price

        return {
            "book_title": book_title,
            "pricing_mode": "ultra_rare",
            "pricing_mode_label": "📕 Sách cực hiếm - Không có đối thủ cạnh tranh",
            "market_price": None,
            "market_source": "Category Floor (không có dữ liệu thị trường)",
            "tier1": {
                "price": int(tier1_price),
                "ratio_pct": None,
                "strategy": "Giá sách cực hiếm - tự định giá theo thể loại",
                "label": "Giá Sách Độc Bản",
            },
            "tier2": {
                "price": int(tier2_price),
                "ratio_pct": None,
                "strategy": "Giá sàn theo thể loại nếu cần thoát hàng",
                "label": "Giá Sàn Thể Loại",
            },
            "recommendation": (
                f"🔥 Sách cực hiếm — không tìm thấy trên bất kỳ sàn nào! "
                f"Đề xuất định giá {int(tier1_price):,}đ dựa trên thể loại '{category}'. "
                f"Thêm nhãn 'Sách Hiếm' vào mô tả để tăng giá trị cảm nhận."
            ),
            "scarcity_badge": True,
        }

    def find_stale_inventory(self, days: int = None) -> list:
        """
        Find products listed on Haravan but with no orders in the past `days` days.
        Skips products already tagged mecobooks-tier-2 (already marked down).
        """
        days = days or self.TIER1_DAYS
        logger.info(f"Scanning for stale inventory (no orders in {days} days)...")

        try:
            products = self.hrv.get_products_all()

            cutoff_date = (get_now_hanoi() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
            recent_orders = self.hrv.get_orders(created_at_min=cutoff_date, status="any", limit=250)

            sold_ids = set()
            for order in recent_orders:
                for item in order.get('line_items', []):
                    sold_ids.add(str(item.get('product_id', '')))

            stale = []
            for product in products:
                pid = str(product.get('id', ''))
                # Skip products already at Tier 2
                tags = [t.strip() for t in product.get('tags', '').split(',')]
                if 'mecobooks-tier-2' in tags:
                    logger.debug(f"Skipping already-Tier2: {product.get('title', pid)}")
                    continue

                has_stock = any(
                    v.get('inventory_quantity', 0) > 0
                    for v in product.get('variants', [])
                )
                if has_stock and pid not in sold_ids:
                    variants = product.get('variants', [])
                    current_price = float(variants[0].get('price', 0)) if variants else 0
                    current_tier = 2 if 'mecobooks-tier-2' in tags else (1 if 'mecobooks-tier-1' in tags else None)
                    stale.append({
                        'id': pid,
                        'title': product.get('title', ''),
                        'current_price': int(current_price),
                        'current_tier': current_tier,
                        'variants': variants,
                    })

            logger.info(f"Found {len(stale)} stale Tier-1 products (unsold > {days} days).")
            return stale

        except Exception as e:
            logger.error(f"Error scanning stale inventory: {e}")
            return []

    def apply_markdown(self, dry_run: bool = False) -> dict:
        """
        Find stale Tier-1 products and reduce their price to Tier-2 level.
        Also tags the product on Haravan and logs the transition to SQLite.
        If dry_run=True, only reports what WOULD be changed (no actual API calls).
        """
        logger.info(f"Applying Tier-2 markdowns (dry_run={dry_run})...")
        stale_products = self.find_stale_inventory()

        applied = []
        errors = []

        for product in stale_products:
            current_price = product.get('current_price')
            if current_price <= 0:
                continue

            new_price = round((current_price * self.TIER2_RATIO / self.TIER1_RATIO) / 1000) * 1000
            new_price = max(new_price, 5000)  # Safety floor: min 5,000 VND

            if dry_run:
                applied.append({
                    'id': product.get('id'),
                    'title': product.get('title'),
                    'old_price': current_price,
                    'new_price': int(new_price),
                    'status': 'dry_run'
                })
            else:
                try:
                    # Update each variant's price
                    for variant in product.get('variants', []):
                        if variant.get('inventory_quantity', 0) > 0:
                            self.hrv.update_variant_price(
                                variant_id=variant['id'],
                                new_price=str(int(new_price))
                            )

                    # Tag product as Tier 2 on Haravan
                    self.hrv.tag_product_tier(int(product.get('id')), tier=2)

                    # Log the transition to pricing_history
                    self._log_tier_transition(
                        product_id=product.get('id'),
                        title=product.get('title'),
                        from_tier=product.get('current_tier', 1),
                        to_tier=2,
                        old_price=current_price,
                        new_price=int(new_price)
                    )

                    applied.append({
                        'id': product.get('id'),
                        'title': product.get('title'),
                        'old_price': current_price,
                        'new_price': int(new_price),
                        'status': 'updated'
                    })
                    logger.info(f"  ✅ Markdown: {product.get('title')} | {current_price:,}đ → {int(new_price):,}đ")
                except Exception as e:
                    errors.append({'title': product.get('title'), 'error': str(e)})
                    logger.error(f"  ❌ Failed to update {product.get('title')}: {e}")

        result = {
            'total_stale': len(stale_products),
            'total_marked_down': len(applied),
            'total_errors': len(errors),
            'markdowns': applied,
            'errors': errors,
            'dry_run': dry_run,
            'ran_at': get_now_hanoi().strftime("%Y-%m-%d %H:%M")
        }

        if not dry_run and applied:
            self._send_markdown_report(result)

        return result

    def _send_markdown_report(self, result: dict):
        """Send Telegram notification about applied markdowns."""
        try:
            from ai_agents.telegram_client import send_telegram_message
            lines = [f"📉 *Báo cáo Giảm Giá Tầng 2*\n`{result['ran_at']}`\n"]
            lines.append(f"Tổng tồn kho cũ: *{result['total_stale']}* sản phẩm")
            lines.append(f"Đã giảm giá: *{result['total_marked_down']}* sản phẩm\n")
            for item in result['markdowns'][:10]:  # Max 10 items in telegram msg
                lines.append(
                    f"• {item.get('title')[:40]}\n"
                    f"  {item.get('old_price'):,}đ → {item.get('new_price'):,}đ"
                )
            send_telegram_message("\n".join(lines))
        except Exception as e:
            logger.error(f"Failed to send markdown report: {e}")

    def find_bundle_opportunities(self) -> list:
        """
        Groups Tier 2 products by category or vendor to find bundling opportunities.
        Returns a list of suggested combos.
        """
        logger.info("Scanning for bundling opportunities (Tier 2 items)...")
        try:
            products = self.hrv.get_products_all()
            tier2_items = []
            
            for p in products:
                tags = [t.strip() for t in p.get('tags', '').split(',')]
                if 'mecobooks-tier-2' in tags:
                    # Check inventory (Phase 7.6)
                    variant = p.get('variants', [{}])[0]
                    inventory = variant.get('inventory_quantity', 0)
                    if inventory <= 0:
                        continue

                    price = float(variant.get('price', 0))
                    # List price (compare_at_price) as basis for COGS (Phase 8)
                    list_price = float(variant.get('compare_at_price') or variant.get('price') or 0)
                    
                    tier2_items.append({
                        'id': p.get('id'),
                        'title': p.get('title'),
                        'price': price,
                        'list_price': list_price,
                        'category': p.get('product_type', 'Khác'),
                        'vendor': p.get('vendor', 'Unknown'),
                        'image': p.get('images', [{}])[0].get('src', '') if p.get('images') else ''
                    })


            # Group by Vendor (Author)
            by_vendor = {}
            for item in tier2_items:
                v = item.get('vendor')
                if v not in by_vendor: by_vendor[v] = []
                by_vendor[v].append(item)

            # Group by Category (Topic)
            by_cat = {}
            for item in tier2_items:
                cat = item.get('category')
                if cat not in by_cat: by_cat[cat] = []
                by_cat[cat].append(item)

            suggestions = []
            seen_ids = set()

            # 1. Prioritize Vendor Bundles (Author Sets) - Size 2 to 4
            for vendor, items in by_vendor.items():
                if vendor == "Unknown": continue
                # Filter out items already in a suggestion
                available = [i for i in items if i['id'] not in seen_ids]
                
                while len(available) >= 2:
                    # Limit size to 20 items (Phase 7.8)
                    size = min(len(available), 20)
                    group = available[:size]
                    total_price = sum(it['price'] for it in group)
                    total_list_price = sum(it['list_price'] for it in group)
                    
                    # N items = N% discount (Phase 7.8)
                    discount = size 
                    bundle_price = round((total_price * (1 - discount/100)) / 1000) * 1000
                    
                    suggestions.append({
                        'type': 'author',
                        'label': f"Bộ sưu tập {vendor} (Giảm {discount}%)",
                        'items_count': size,
                        'items': group,
                        'original_price': int(total_price),
                        'total_list_price': int(total_list_price),
                        'suggested_price': int(bundle_price),
                        'discount_pct': discount
                    })

                    for it in group: seen_ids.add(it['id'])
                    available = available[size:]

            # 2. Topic Bundles (Category) for remaining items - Size 2 to 20
            for cat, items in by_cat.items():
                available = [i for i in items if i['id'] not in seen_ids]
                
                while len(available) >= 2:
                    size = min(len(available), 20)
                    group = available[:size]
                    total_price = sum(it['price'] for it in group)
                    total_list_price = sum(it['list_price'] for it in group)
                    
                    # N items = N% discount (Phase 7.8)
                    discount = size
                    bundle_price = round((total_price * (1 - discount/100)) / 1000) * 1000
                    
                    suggestions.append({
                        'type': 'category',
                        'label': f"Combo {cat} Tuyển Chọn (Giảm {discount}%)",
                        'items_count': size,
                        'items': group,
                        'original_price': int(total_price),
                        'total_list_price': int(total_list_price),
                        'suggested_price': int(bundle_price),
                        'discount_pct': discount
                    })

                    for it in group: seen_ids.add(it['id'])
                    available = available[size:]
            
            return suggestions
        except Exception as e:
            logger.error(f"Error finding bundle opportunities: {e}")
            return []

    def auto_liquidate_bundles(self, limit=3):
        """
        AUTONOMOUS AGENT (Phase 8): 
        Automatically creates and publishes top-performing bundles that meet profitability guardrails.
        COGS is assumed at 35% of Total List Price.
        """
        logger.info("🤖 [AutoAgent] Starting autonomous bundling liquidation...")
        suggestions = self.find_bundle_opportunities()
        if not suggestions:
            return {"status": "no_opportunities"}
        
        created = []
        for s in suggestions:
            if len(created) >= limit: break
            
            # Profitability Guardrail: 
            # Bundle Price > (Total List Price * 0.35) + 15,000 Buffer (Shipping/Fees)
            cogs_threshold = (s['total_list_price'] * self.COGS_RATIO) + 15000
            
            if s['suggested_price'] > cogs_threshold:
                logger.info(f"  ✅ Opportunity passed profit check: {s['label']} ({s['suggested_price']} > {cogs_threshold})")
                item_ids = [str(it['id']) for it in s['items']]
                res = self.create_bundle(item_ids, s['label'], s['suggested_price'])
                if 'id' in res:
                    created.append({
                        'id': res['id'],
                        'title': s['label'],
                        'price': s['suggested_price'],
                        'profit_est': s['suggested_price'] - (s['total_list_price'] * self.COGS_RATIO)
                    })
            else:
                logger.warning(f"  ❌ Opportunity rejected (low profit): {s['label']} ({s['suggested_price']} <= {cogs_threshold})")
        
        # Notify via Telegram if possible
        if created:
            try:
                from ai_agents.telegram_client import send_telegram_message
                msg = f"🤖 <b>[AutoAgent] Autonomous Bundling Report</b>\n\n"
                msg += f"Created {len(created)} liquidation bundles:\n"
                for c in created:
                    msg += f"- {c['title']}: {c['price']:,}đ (Est. Profit: {c['profit_est']:,}đ)\n"
                send_telegram_message(msg)
            except: pass
            
        return {"status": "success", "created_count": len(created), "bundles": created}

    def create_bundle(self, item_ids: list, bundle_title: str, bundle_price: int) -> dict:
        """
        Creates a bundle product on Haravan from a list of product IDs.
        """
        logger.info(f"Creating bundle '{bundle_title}' with {len(item_ids)} items...")
        try:
            # Fetch item details for description
            products = self.hrv.get_products_all()
            selected = [p for p in products if str(p.get('id')) in [str(i) for i in item_ids]]
            
            if not selected:
                return {"error": "No valid items found for bundle."}

            # Construct Description
            body_html = "<h3>Combo dọn kho giá sốc!</h3><p>Gói sản phẩm bao gồm:</p><ul>"
            images = []
            skus = []
            for p in selected:
                body_html += f"<li>{p.get('title')}</li>"
                if p.get('images'):
                    images.append(p['images'][0].get('src'))
                sku = p.get('variants', [{}])[0].get('sku') or 'NOSKU'
                skus.append(str(sku))
            body_html += "</ul><p><i>Sách hiếm, dọn kho thanh lý nhanh. Số lượng cực hạn!</i></p>"

            bundle_sku = f"BNDL-{'-'.join(skus[:2])}-{int(time.time()) % 10000}"[:50]
            
            # Merge images into a collage (Phase 7.5)
            merged_img_b64 = self._merge_bundle_images(images[:3])
            bundle_images = images[:3]
            if merged_img_b64:
                bundle_images.insert(0, {"attachment": merged_img_b64})

            # Create product on Haravan
            new_prod = self.hrv.create_product(
                title=bundle_title,
                body_html=body_html,
                price=str(bundle_price),
                sku=bundle_sku,
                images=bundle_images,
                tags="mecobooks-bundle, mecobooks-tier-2"
            )
            
            if "error" in new_prod:
                return new_prod
            
            bundle_id = str(new_prod.get('id'))
            
            # Store Mapping (Phase 7.5)
            self._store_bundle_mapping(bundle_id, bundle_title, item_ids, skus)
                
            logger.info(f"  ✅ Bundle created and mapped: {bundle_title} (ID: {bundle_id})")
            return new_prod
            
        except Exception as e:
            logger.error(f"Failed to create bundle: {e}")
            return {"error": str(e)}

    def _merge_bundle_images(self, image_urls: list) -> str:
        """Downloads images, merges them horizontally, and returns base64."""
        if not image_urls: return None
        logger.info(f"Generating bundle collage from {len(image_urls)} images...")
        try:
            imgs = []
            for url in image_urls:
                if not url: continue
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                resp = requests.get(url, timeout=10, headers=headers)
                if resp.status_code == 200:
                    img = Image.open(io.BytesIO(resp.content))
                    imgs.append(img)
            
            if not imgs: return None

            # Standardize height to 800px
            std_h = 800
            resized_imgs = []
            total_w = 0
            for img in imgs:
                aspect = img.width / img.height
                new_w = int(std_h * aspect)
                resized_imgs.append(img.resize((new_w, std_h), Image.Resampling.LANCZOS))
                total_w += new_w

            # Create canvas with 20px gutter between images
            gutter = 20
            canvas_w = total_w + (gutter * (len(resized_imgs) - 1))
            collage = Image.new('RGB', (canvas_w, std_h), (255, 255, 255))
            cur_x = 0
            for img in resized_imgs:
                collage.paste(img, (cur_x, 0))
                cur_x += img.width + gutter
            
            # Save to buffer
            buf = io.BytesIO()
            collage.save(buf, format='JPEG', quality=85)
            return base64.b64encode(buf.getvalue()).decode('utf-8')

        except Exception as e:
            logger.error(f"Image merging failed: {e}")
            return None

    def _store_bundle_mapping(self, bundle_id: str, title: str, item_ids: list, skus: list):
        """Saves bundle component relationship to SQLite."""
        try:
            from datetime import datetime
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO bundle_mappings (bundle_id, bundle_title, component_ids, component_skus, created_at) VALUES (?, ?, ?, ?, ?)",
                    (bundle_id, title, ",".join([str(i) for i in item_ids]), ",".join(skus), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing bundle mapping: {e}")

    def sync_bundle_inventory(self):
        """
        Polls Haravan for component stocks and updates Bundles accordingly.
        If any component is 0, the bundle is set to 0.
        """
        logger.info("Syncing bundle inventory with component stocks...")
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                bundles = conn.execute("SELECT * FROM bundle_mappings").fetchall()
            
            if not bundles:
                return {"message": "No bundles to sync."}

            # Fetch all products once for efficiency
            all_products = self.hrv.get_products_all()
            stock_map = {} # SKU -> Quantity
            for p in all_products:
                for v in p.get('variants', []):
                    stock_map[v.get('sku')] = v.get('inventory_quantity', 0)

            stats = {"updated": 0, "total": len(bundles)}
            for b in bundles:
                skus = b['component_skus'].split(',')
                # Check if all components have at least 1 in stock
                is_available = all(stock_map.get(s, 0) > 0 for s in skus)
                
                # Get current bundle status (using brute force find for now)
                bundle_prod = next((p for p in all_products if str(p.get('id')) == b['bundle_id']), None)
                if not bundle_prod: continue

                current_qty = bundle_prod.get('variants', [{}])[0].get('inventory_quantity', 0)
                target_qty = 1 if is_available else 0

                if current_qty != target_qty:
                    variant_id = bundle_prod.get('variants', [{}])[0].get('id')
                    logger.info(f"Syncing Bundle {b['bundle_title']}: {current_qty} -> {target_qty}")
                    self.hrv.update_variant_price(variant_id, None, inventory_quantity=target_qty)
                    stats["updated"] += 1
            
            return stats
        except Exception as e:
            logger.error(f"Inventory sync error: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    agent = PricingStrategyAgent()
    result = agent.suggest_prices("Nhà giả kim")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
