with open("templates/verification.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Fix the Agent Cards grid: was 1 col mobile (way too narrow at 4 cols on lg)
# Switch to 2 cols on mobile, 3 on md, 4 on lg
html = html.replace(
    '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">',
    '<div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3 sm:gap-4">'
)

# 2. Fix agent card text overflow - remove fixed height that truncates text
# Replace 'h-8 overflow-hidden' text clips on agent cards with auto height
html = html.replace(
    '<p class="text-xs text-gray-500 mb-4 h-8 overflow-hidden">Viết caption, tạo script\n                                        video từ\n                                        sản phẩm</p>',
    '<p class="text-xs text-gray-500 mb-3 leading-relaxed">Viết caption, tạo script video từ sản phẩm</p>'
)
html = html.replace(
    '<p class="text-xs text-gray-500 mb-4 h-8 overflow-hidden">Nghiên cứu trend sách,\n                                        xuất Google\n                                        Sheets</p>',
    '<p class="text-xs text-gray-500 mb-3 leading-relaxed">Nghiên cứu trend sách, đăng Blog tự động</p>'
)
html = html.replace(
    '<p class="text-xs text-gray-500 mb-4 h-8 overflow-hidden">Phân loại hàng hóa và lập\n                                        kế hoạch\n                                        nhập hàng định kỳ</p>',
    '<p class="text-xs text-gray-500 mb-3 leading-relaxed">Phân loại hàng hóa ABC & kế hoạch nhập hàng</p>'
)
html = html.replace(
    '<p class="text-xs text-gray-500 mb-4 h-8 overflow-hidden">Kiểm tra Disk, Memory,\n                                        Server\n                                        health</p>',
    '<p class="text-xs text-gray-500 mb-3 leading-relaxed">Kiểm tra Disk, Memory & Server health</p>'
)
html = html.replace(
    '<p class="text-xs text-gray-500 mb-4 h-8 overflow-hidden">Tổng hợp doanh thu &amp; Gửi\n                                        báo cáo Telegram 8:00 mỗi ngày</p>',
    '<p class="text-xs text-gray-500 mb-3 leading-relaxed">Tổng hợp doanh thu & gửi báo cáo Telegram</p>'
)
html = html.replace(
    '<p class="text-xs text-gray-500 mb-4 h-8 overflow-hidden">Theo dõi tồn kho, phân\n                                        tích hàng\n                                        bán chạy và cảnh báo từ Haravan</p>',
    '<p class="text-xs text-gray-500 mb-3 leading-relaxed">Theo dõi tồn kho & cảnh báo từ Haravan</p>'
)

# 3. Fix button text truncation: shorten button labels on small screens
html = html.replace(
    'class="w-full btn bg-gray-900 text-white px-4 py-2.5 rounded-lg hover:bg-black text-sm font-medium flex justify-center gap-2">\n                                        <span>▶</span> Run Agent',
    'class="w-full btn bg-gray-900 text-white px-2 py-2 rounded-xl hover:bg-black text-xs sm:text-sm font-semibold flex justify-center gap-1.5 transition-all">\n                                        <span>▶</span><span class="hidden sm:inline">Run</span> Agent'
)

# 4. Add responsive CSS overrides in the <style> block
extra_css = """
        /* Mobile agent card fixes */
        @media (max-width: 640px) {
            .card {
                padding: 0.75rem !important;
            }
            .card h3 {
                font-size: 0.8rem !important;
                line-height: 1.2 !important;
            }
            .card .badge {
                font-size: 0.55rem !important;
                padding: 1px 5px !important;
            }
            .card .w-10 {
                width: 2rem !important;
                height: 2rem !important;
                font-size: 1rem !important;
            }
        }
"""
html = html.replace('        .badge {\n            font-size: 0.65rem;\n            padding: 2px 8px;\n            border-radius: 9999px;\n            font-weight: 500;\n        }\n    </style>',
    '        .badge {\n            font-size: 0.65rem;\n            padding: 2px 8px;\n            border-radius: 9999px;\n            font-weight: 500;\n        }\n' + extra_css + '    </style>')

with open("templates/verification.html", "w", encoding="utf-8") as f:
    f.write(html)
print("MOBILE CARD FIX APPLIED SUCCESSFULLY")
