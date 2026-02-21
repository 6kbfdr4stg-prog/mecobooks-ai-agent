import re

with open("templates/verification.html", "r", encoding="utf-8") as f:
    html = f.read()

# Make background more premium
html = html.replace('bg-gray-50 min-h-screen font-sans', 'bg-slate-50 min-h-screen font-sans bg-gradient-to-br from-indigo-50 via-white to-purple-50')
# Update sidebar
html = html.replace('class="w-64 bg-gray-900 text-white hidden md:flex flex-col"', 'id="sidebar" class="w-64 bg-slate-900 text-white flex-col absolute inset-y-0 left-0 transform -translate-x-full md:relative md:translate-x-0 transition duration-300 ease-in-out z-50 md:flex shadow-2xl md:shadow-none"')
# Add Hamburger button to header
header_btn = '''<button id="mobile-menu-btn" class="md:hidden text-gray-500 hover:text-gray-700 focus:outline-none focus:text-gray-700 flex items-center">
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                    </svg>
                </button>
                <h2 class="text-xl font-bold text-gray-800 ml-4 md:ml-0">Dashboard Overview</h2>'''
html = html.replace('<h2 class="text-xl font-bold text-gray-800">Dashboard Overview</h2>', header_btn)

# Add script for mobile menu
script_add = '''
        // Mobile menu toggle
        const btn = document.querySelector('#mobile-menu-btn');
        const sidebar = document.querySelector('#sidebar');
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('-translate-x-full');
        });
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && !sidebar.classList.contains('-translate-x-full') && window.innerWidth < 768) {
                sidebar.classList.add('-translate-x-full');
            }
        });
'''
html = html.replace('// --- 1. Stats & Charts Logic ---', script_add + '\n        // --- 1. Stats & Charts Logic ---')

# Upgrade agent cards
card_replacements = {
    'card bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:border-purple-300 transition-all group': 
    'card bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl shadow-indigo-100/20 border border-white/60 p-5 hover:border-purple-400 hover:shadow-purple-200/40 transition-all duration-300 group hover:-translate-y-1',
    'card bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:border-blue-300 transition-all group': 
    'card bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl shadow-indigo-100/20 border border-white/60 p-5 hover:border-blue-400 hover:shadow-blue-200/40 transition-all duration-300 group hover:-translate-y-1',
    'card bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:border-yellow-300 transition-all group': 
    'card bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl shadow-indigo-100/20 border border-white/60 p-5 hover:border-yellow-400 hover:shadow-yellow-200/40 transition-all duration-300 group hover:-translate-y-1',
    'card bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:border-red-300 transition-all group': 
    'card bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl shadow-indigo-100/20 border border-white/60 p-5 hover:border-red-400 hover:shadow-red-200/40 transition-all duration-300 group hover:-translate-y-1',
    'card bg-white rounded-xl shadow-sm border border-emerald-200 p-5 hover:border-emerald-400 transition-all group ring-2 ring-emerald-50 ring-offset-2':
    'card bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl shadow-emerald-100/20 border border-emerald-200 p-5 hover:border-emerald-400 hover:shadow-emerald-200/40 transition-all duration-300 group hover:-translate-y-1 ring-2 ring-emerald-50 ring-offset-2',
    'card bg-white rounded-xl shadow-sm border border-blue-200 p-5 hover:border-blue-400 transition-all group ring-2 ring-blue-50 ring-offset-2':
    'card bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl shadow-blue-100/20 border border-blue-200 p-5 hover:border-blue-400 hover:shadow-blue-200/40 transition-all duration-300 group hover:-translate-y-1 ring-2 ring-blue-50 ring-offset-2'
}

for old, new in card_replacements.items():
    html = html.replace(old, new)

# Change basic generic cards to glassmorphism
html = html.replace('bg-white p-6 rounded-xl shadow-sm border border-gray-200', 'bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-xl shadow-indigo-100/40 border border-white text-gray-800')
html = html.replace('bg-white rounded-xl shadow-sm border border-gray-200 p-6', 'bg-white/70 backdrop-blur-xl rounded-3xl shadow-xl shadow-indigo-100/40 border border-white p-6 text-gray-800')

# Upgrade buttons
btn_replacements = {
    'bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 transition flex items-center gap-2': 
    'bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:from-blue-700 hover:to-indigo-700 shadow-md shadow-blue-500/30 flex items-center gap-2 transform hover:scale-105 transition-all duration-300',
    'bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 font-semibold transition-all shadow-sm flex items-center justify-center gap-2': 
    'bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-3 rounded-xl hover:from-indigo-700 hover:to-purple-700 font-bold transition-all duration-300 transform hover:scale-105 shadow-xl shadow-indigo-500/30 flex items-center justify-center gap-2',
    'class="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 font-semibold transition-all shadow-sm flex items-center justify-center gap-2"': 
    'class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-xl hover:from-blue-700 hover:to-indigo-700 font-bold transition-all duration-300 transform hover:scale-105 shadow-xl shadow-blue-500/30 flex items-center justify-center gap-2"'
}

for old, new in btn_replacements.items():
    html = html.replace(old, new)

# Make grid layouts responsive for mobile
html = html.replace('<div class="grid grid-cols-1 md:grid-cols-4 gap-6">', '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">')

with open("templates/verification.html", "w", encoding="utf-8") as f:
    f.write(html)
print("UI UPGRADE SUCCESSFUL")
