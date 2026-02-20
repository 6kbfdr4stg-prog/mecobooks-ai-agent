import logging
import sys
import os
import sqlite3
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

    def __init__(self):
        from haravan_client import HaravanClient
        self.hrv = HaravanClient()
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pricing_history.db")
        self._init_history_db()

    def _init_history_db(self):
        """Create the pricing_history table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pricing_history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id  TEXT    NOT NULL,
                    title       TEXT    NOT NULL,
                    from_tier   INTEGER,
                    to_tier     INTEGER NOT NULL,
                    old_price   INTEGER,
                    new_price   INTEGER,
                    transitioned_at TEXT NOT NULL
                )
            """)
            conn.commit()

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
            current_price = product['current_price']
            if current_price <= 0:
                continue

            new_price = round((current_price * self.TIER2_RATIO / self.TIER1_RATIO) / 1000) * 1000
            new_price = max(new_price, 5000)  # Safety floor: min 5,000 VND

            if dry_run:
                applied.append({
                    'id': product['id'],
                    'title': product['title'],
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
                    self.hrv.tag_product_tier(int(product['id']), tier=2)

                    # Log the transition to pricing_history
                    self._log_tier_transition(
                        product_id=product['id'],
                        title=product['title'],
                        from_tier=product.get('current_tier', 1),
                        to_tier=2,
                        old_price=current_price,
                        new_price=int(new_price)
                    )

                    applied.append({
                        'id': product['id'],
                        'title': product['title'],
                        'old_price': current_price,
                        'new_price': int(new_price),
                        'status': 'updated'
                    })
                    logger.info(f"  ✅ Markdown: {product['title']} | {current_price:,}đ → {int(new_price):,}đ")
                except Exception as e:
                    errors.append({'title': product['title'], 'error': str(e)})
                    logger.error(f"  ❌ Failed to update {product['title']}: {e}")

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
                    f"• {item['title'][:40]}\n"
                    f"  {item['old_price']:,}đ → {item['new_price']:,}đ"
                )
            send_telegram_message("\n".join(lines))
        except Exception as e:
            logger.error(f"Failed to send markdown report: {e}")


if __name__ == "__main__":
    agent = PricingStrategyAgent()
    result = agent.suggest_prices("Nhà giả kim")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
