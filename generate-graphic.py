import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')

# Title
ax.text(7, 9.5, 'MCP Orchestration', fontsize=28, fontweight='bold', ha='center', color='#f0f6fc')
ax.text(7, 9.0, 'Beyond Individual Servers — Coordinated AI Workflows', fontsize=14, ha='center', color='#8b949e')

# Central agent box
agent_box = FancyBboxPatch((5.5, 5.5), 3, 2, boxstyle="round,pad=0.1", facecolor='#1f6feb', edgecolor='#58a6ff', linewidth=2)
ax.add_patch(agent_box)
ax.text(7, 6.8, 'AI Agent', fontsize=14, fontweight='bold', ha='center', color='white')
ax.text(7, 6.4, 'The Orchestrator', fontsize=10, ha='center', color='#c9d1d9')
ax.text(7, 6.0, 'Reasons • Adapts • Learns', fontsize=8, ha='center', color='#8b949e')

# Server boxes around the agent
servers = [
    ('Arxiv MCP', 1.5, 8.5, '#238636'),
    ('Wikipedia MCP', 4.0, 8.5, '#8957e5'),
    ('GitHub MCP', 6.5, 8.5, '#f778ba'),
    ('Crypto MCP', 9.0, 8.5, '#d2991d'),
    ('SEO MCP', 10.5, 6.0, '#0969da'),
    ('HTTP Fetch', 10.5, 3.5, '#6e7681'),
    ('Text Diff MCP', 8.0, 1.5, '#bf8700'),
    ('Unit MCP', 5.5, 1.5, '#2ea043'),
    ('UUID MCP', 3.0, 1.5, '#1f6feb'),
    ('Regex MCP', 1.5, 3.5, '#6356e5'),
]

for name, x, y, color in servers:
    box = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, boxstyle="round,pad=0.05", facecolor=color, edgecolor='white', linewidth=1)
    ax.add_patch(box)
    ax.text(x, y, name, fontsize=8, ha='center', va='center', color='white', fontweight='bold')

# Arrows from servers to agent
arrows = [
    ((2.2, 8.1), (6.0, 7.3)),
    ((4.7, 8.1), (6.5, 7.3)),
    ((7.2, 8.1), (7.0, 7.5)),
    ((9.7, 8.1), (8.0, 7.3)),
    ((11.2, 5.6), (8.5, 6.8)),
    ((11.2, 3.9), (8.5, 6.2)),
    ((8.7, 1.9), (7.5, 5.9)),
    ((6.2, 1.9), (6.5, 5.5)),
    ((3.7, 1.9), (6.0, 5.9)),
    ((2.2, 3.9), (6.0, 6.5)),
]

for (x1, y1), (x2, y2) in arrows:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color='#58a6ff', lw=1.5, alpha=0.6))

# Bottom section: key concepts
concepts = [
    ('Specialization', 'Each server does\none thing exceptionally well'),
    ('Composition', 'Outputs become inputs\nin natural pipelines'),
    ('Error Recovery', 'Fallbacks, retries,\npartial success reporting'),
    ('Standardization', 'Same protocol, easy\nswapping and scaling'),
]

for i, (title, desc) in enumerate(concepts):
    x = 1.5 + i * 3.0
    box = FancyBboxPatch((x-1.3, 0.5), 2.6, 1.8, boxstyle="round,pad=0.1", facecolor='#21262d', edgecolor='#30363d', linewidth=1)
    ax.add_patch(box)
    ax.text(x, 1.9, title, fontsize=11, fontweight='bold', ha='center', color='#58a6ff')
    ax.text(x, 1.3, desc, fontsize=8, ha='center', color='#c9d1d9')

# Footer
ax.text(7, 0.2, '#ModelContextProtocol #AIAgents #MCP #AIOrchestration', fontsize=9, ha='center', color='#8b949e')

plt.axis('off')
plt.tight_layout()
plt.savefig('C:\\Users\\marek\\mcp-orchestration-graphic.png', dpi=150, bbox_inches='tight', facecolor='#0d1117')
print('Graphic saved.')