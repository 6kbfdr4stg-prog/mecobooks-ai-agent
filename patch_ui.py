import re

with open("templates/verification.html", "r", encoding="utf-8") as f:
    html = f.read()

# Define agents and their visual colors to keep it looking nice
agents = {
    "content_creator": "purple", 
    "market_research": "blue", 
    "inventory_analyst": "yellow", 
    "integrity_manager": "red", 
    "auto_debug": "indigo",
    "bi_analyst": "emerald" # Actually it's just BI
}

# The block to replace looks like:
# <span class="badge bg-green-50 text-green-700 border border-green-100">Ready</span>
# Or for NEW:
# <span class="badge bg-emerald-50 text-emerald-700 border border-emerald-100">NEW</span>

# Because we have multiple agents and they all just say "Ready" or "NEW", 
# we need to be careful to only replace the badge for the specific agent's card.
# The card structure:
# <!-- Agent Name -->
# <div class="card ...">
#   <div class="flex justify-between items-start mb-3">
#       <div class="w-10 h-10 ..."> ICON </div>
#       <span class="badge ...">Ready</span>

def patch_agent_card(agent_id, html_content):
    # Find the button id="btn-{agent_id}" to locate the card
    # Then work backwards to find the badge
    btn_marker = f'id="btn-{agent_id}"'
    idx = html_content.find(btn_marker)
    if idx == -1: return html_content
    
    # search backwards from the button for the first badge
    badge_end = html_content.rfind('</span>', 0, idx)
    badge_start = html_content.rfind('<span class="badge', 0, badge_end)
    
    if badge_start != -1 and badge_end != -1:
        # replace just that span
        replacement = f'''
                                <div class="text-right flex flex-col items-end">
                                    <span id="badge-{agent_id}" class="badge bg-gray-50 text-gray-500 border border-gray-200 shadow-sm text-[10px] px-1.5 py-0.5" style="border-radius: 6px;">Tiếp nhận...</span>
                                    <span id="time-{agent_id}" class="text-[9px] text-gray-400 mt-1 font-medium tracking-wide">--</span>
                                </div>
        '''
        html_content = html_content[:badge_start] + replacement.strip() + html_content[badge_end+7:]
        
    return html_content

for agent in agents.keys():
    html = patch_agent_card(agent, html)

with open("templates/verification.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Patched UI!")
