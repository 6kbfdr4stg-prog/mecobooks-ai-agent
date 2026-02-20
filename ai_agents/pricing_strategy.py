import logging
import sys
import os
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

    def suggest_prices(self, book_title: str) -> dict:
        """
        Given a book title, return a full pricing suggestion for Tier 1 and Tier 2.
        """
        logger.info(f"Calculating pricing strategy for: {book_title}")
        market_price = self._get_market_price(book_title)

        if market_price <= 0:
            return {
                "book_title": book_title,
                "market_price": None,
                "error": "Không tìm thấy giá thị trường. Vui lòng kiểm tra tên sách.",
                "tier1": None,
                "tier2": None,
            }

        tier1_price = round(market_price * self.TIER1_RATIO / 1000) * 1000
        tier2_price = round(market_price * self.TIER2_RATIO / 1000) * 1000

        return {
            "book_title": book_title,
            "market_price": int(market_price),
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
            "estimated_days_tier1": 30,
            "recommendation": f"Đặt giá {int(tier1_price):,}đ trong {self.TIER1_DAYS} ngày đầu. Nếu chưa bán được, hạ xuống {int(tier2_price):,}đ để thoát hàng."
        }

    def find_stale_inventory(self, days: int = None) -> list:
        """
        Find products listed on Haravan but with no orders in the past `days` days.
        Returns list of products that should move to Tier 2 pricing.
        """
        days = days or self.TIER1_DAYS
        logger.info(f"Scanning for stale inventory (no orders in {days} days)...")

        try:
            # Get all products
            products = self.hrv.get_products_all()

            # Get recent orders to find sold SKUs
            cutoff_date = (get_now_hanoi() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
            recent_orders = self.hrv.get_orders(created_at_min=cutoff_date, status="any", limit=250)

            # Build set of recently sold product IDs
            sold_ids = set()
            for order in recent_orders:
                for item in order.get('line_items', []):
                    sold_ids.add(str(item.get('product_id', '')))

            # Identify stale products (in stock but not recently sold)
            stale = []
            for product in products:
                pid = str(product.get('id', ''))
                # Check if any variant has stock
                has_stock = any(
                    v.get('inventory_quantity', 0) > 0
                    for v in product.get('variants', [])
                )
                if has_stock and pid not in sold_ids:
                    # Get current price from first variant
                    variants = product.get('variants', [])
                    current_price = float(variants[0].get('price', 0)) if variants else 0
                    stale.append({
                        'id': pid,
                        'title': product.get('title', ''),
                        'current_price': int(current_price),
                        'variants': variants,
                    })

            logger.info(f"Found {len(stale)} stale products (unsold > {days} days).")
            return stale

        except Exception as e:
            logger.error(f"Error scanning stale inventory: {e}")
            return []

    def apply_markdown(self, dry_run: bool = False) -> dict:
        """
        Find stale Tier-1 products and reduce their price to Tier-2 level.
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

            # Multiply back to get implied market price (based on tier1 ratio), then apply tier2
            # Simplified: we just apply TIER2/TIER1 ratio to current price
            new_price = round((current_price * self.TIER2_RATIO / self.TIER1_RATIO) / 1000) * 1000
            new_price = max(new_price, 5000)  # Safety floor: min 5,000 VND

            if dry_run:
                applied.append({
                    'title': product['title'],
                    'old_price': current_price,
                    'new_price': int(new_price),
                    'status': 'dry_run'
                })
            else:
                try:
                    # Update each variant's price via Haravan API
                    for variant in product.get('variants', []):
                        if variant.get('inventory_quantity', 0) > 0:
                            self.hrv.update_variant_price(
                                variant_id=variant['id'],
                                new_price=str(int(new_price))
                            )
                    applied.append({
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
