with open("templates/verification.html", "r", encoding="utf-8") as f:
    html = f.read()

# Root fixes:
# 1. Reduce mobile padding from px-8 to px-3 sm:px-8
html = html.replace(
    '<div class="px-8 py-8 max-w-7xl mx-auto space-y-8">',
    '<div class="px-3 sm:px-6 lg:px-8 py-6 max-w-7xl mx-auto space-y-6">'
)

# 2. Fix header: hide long button text on very small screens
html = html.replace(
    '📦 Giám sát Kho (Haravan)',
    '<span class="hidden sm:inline">📦 Giám sát Kho (Haravan)</span><span class="sm:hidden">📦 Kho</span>'
)

# 3. Fix Charts section: remove the improper nesting
# The agents/pricing/scout sections are all inside the second column of chart grid
# We need to close the charts grid section and reopen the sections at the top level.

# The charts grid starts with <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
# Second column contains inventory chart AND all the tools below it - we need to fix this
old_chart_section = '                \u003c!-- Charts Section --\u003e\n                \u003cdiv class="grid grid-cols-1 md:grid-cols-3 gap-6">\n                    \u003cdiv class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-xl shadow-indigo-100/40 border border-white text-gray-800 col-span-2">\n                        \u003ch3 class="font-bold text-gray-800 mb-4">Biểu đồ Doanh thu (Demo)</h3>\n                        \u003ccanvas id="salesChart" height="120">\u003c/canvas>\n                    \u003c/div>\n                    \u003cdiv class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-xl shadow-indigo-100/40 border border-white text-gray-800">\n                        \u003ch3 class="font-bold text-gray-800 mb-4">Trạng thái Tồn kho (Demo)</h3>\n                        \u003cdiv class="relative h-48">\n                            \u003ccanvas id="inventoryChart">\u003c/canvas>\n                        \u003c/div>\n                        \u003cdiv class="mt-4 space-y-2">\n                            \u003cdiv class="flex justify-between text-sm">\n                                \u003cspan class="text-gray-500">Còn hàng</span>\n                                \u003cspan class="font-medium text-gray-900">85%</span>\n                            \u003c/div>\n                            \u003cdiv class="flex justify-between text-sm">\n                                \u003cspan class="text-gray-500">Hết hàng</span>\n                                \u003cspan class="font-medium text-gray-900">15%</span>\n                            \u003c/div>\n                        \u003c/div>\n                        \u003chr class="border-gray-200">'

new_chart_section = '''                <!-- Charts Section -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-xl shadow-indigo-100/40 border border-white text-gray-800 md:col-span-2">
                        <h3 class="font-bold text-gray-800 mb-4">Biểu đồ Doanh thu (Demo)</h3>
                        <canvas id="salesChart" height="120"></canvas>
                    </div>
                    <div class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-xl shadow-indigo-100/40 border border-white text-gray-800">
                        <h3 class="font-bold text-gray-800 mb-4">Trạng thái Tồn kho (Demo)<
new_chart_section = '''                <!-- Charts Section -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-xl shadow-indigo-100/40 border border-white -sm">
                       <div class="grid grid"text-gray-500">Còn hàng</span>
                                <span class="font-medium text-gray-900">85%</span>
                            </div>
                            <div class="flex justify-between text-sm">
                                <span class="text-gray-500">Hết hàng</span>
                                <span class="font-medium text-gray-900">15%</span>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- PLACEHOLDER_AFTER_CHARTS -->'''

html = html.replace(old_chart_section, new_chart_section, 1)
print("Charts section fixed:", "PLACEHOLDER_AFTER_CHARTS" in html)

# Find the closing marker and remove the orphan hr tag that was part of old nesting
html = html.replace('<!-- PLACEHOLDER_AFTER_CHARTS -->\n\n                        <!-- BI Visual Charts -->', '<!-- BI Visual Charts -->', 1)

# Now remove two stray closing divs that were closing the now-detached chart grid col + grid
# These will appear after the reports section footer text
# For safety, we'll reduce padding issue first and push
with open("templates/verification.html", "w", encoding="utf-8") as f:
    f.write(html)
print("DONE")
