#!/usr/bin/env python3
"""
Create the Triangular Tension Figure for the paper.
Shows:
1. Left panel: Schematic of the three-way pull
2. Right panel: Chi2 component bar chart (Pre-DESI vs +DESI)
"""

import matplotlib.pyplot as plt
import numpy as np

# Set up the figure with two panels
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ============================================================================
# LEFT PANEL: Triangular Tension Schematic
# ============================================================================

ax1.set_xlim(-1.5, 1.5)
ax1.set_ylim(-1.2, 1.4)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('The Triangular Tension', fontsize=14, fontweight='bold', pad=20)

# Triangle vertices
top = (0, 1.0)
left = (-1.0, -0.5)
right = (1.0, -0.5)
center = (0, 0)

# Draw the triangle
triangle = plt.Polygon([top, left, right], fill=False, edgecolor='gray', 
                        linewidth=2, linestyle='--')
ax1.add_patch(triangle)

# Add nodes (circles with labels)
# Top: Planck high-ell (red, penalty)
circle_top = plt.Circle(top, 0.25, color='#ff6b6b', ec='darkred', linewidth=2)
ax1.add_patch(circle_top)
ax1.text(top[0], top[1], r'$+19$', ha='center', va='center', fontsize=14, fontweight='bold')
ax1.text(top[0], top[1]+0.4, 'Planck high-$\\ell$\nTTTEEE', ha='center', va='bottom', fontsize=11)

# Bottom-left: Planck low-ell EE (green, benefit)
circle_left = plt.Circle(left, 0.25, color='#69db7c', ec='darkgreen', linewidth=2)
ax1.add_patch(circle_left)
ax1.text(left[0], left[1], r'$-15$', ha='center', va='center', fontsize=14, fontweight='bold')
ax1.text(left[0]-0.1, left[1]-0.4, 'Planck low-$\\ell$ EE\n(+SH0ES coupling)', ha='center', va='top', fontsize=11)

# Bottom-right: SH0ES (blue)
circle_right = plt.Circle(right, 0.2, color='#74c0fc', ec='darkblue', linewidth=2)
ax1.add_patch(circle_right)
ax1.text(right[0], right[1], r'$-3.5$', ha='center', va='center', fontsize=13, fontweight='bold')
ax1.text(right[0]+0.1, right[1]-0.4, 'SH0ES\n$H_0$ prior', ha='center', va='top', fontsize=11)

# Center: EDE (gold star)
circle_center = plt.Circle(center, 0.3, color='#ffd43b', ec='darkorange', linewidth=3)
ax1.add_patch(circle_center)
ax1.text(center[0], center[1], 'EDE', ha='center', va='center', fontsize=12, fontweight='bold')

# Arrows showing pull directions
arrow_kwargs = dict(head_width=0.08, head_length=0.05, fc='gray', ec='gray', alpha=0.7)
# Top arrow (pulling away from center)
ax1.annotate('', xy=(0, 0.55), xytext=(0, 0.3),
            arrowprops=dict(arrowstyle='->', color='#ff6b6b', lw=2))
# Left arrow (pulling toward center)
ax1.annotate('', xy=(-0.45, -0.22), xytext=(-0.7, -0.35),
            arrowprops=dict(arrowstyle='->', color='#69db7c', lw=2))
# Right arrow (pulling toward center)  
ax1.annotate('', xy=(0.45, -0.22), xytext=(0.7, -0.35),
            arrowprops=dict(arrowstyle='->', color='#74c0fc', lw=2))

# Net result annotation
ax1.text(0, -1.0, 'Net: $\\Delta\\chi^2 = -4.5$ (Pre-DESI)', 
         ha='center', fontsize=12, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='#e9ecef', edgecolor='gray'))

# DESI note
ax1.text(0, -1.25, 'DESI shifts parameters → low-$\\ell$ benefit lost → Net: $+10.8$',
         ha='center', fontsize=10, style='italic', color='gray')

# ============================================================================
# RIGHT PANEL: Chi2 Component Bar Chart
# ============================================================================

components = ['Planck\nhigh-$\\ell$', 'Planck\nlow-$\\ell$ EE', 'Planck\nlow-$\\ell$ TT', 
              'SH0ES', 'BAO/DESI', 'TOTAL']

pre_desi = [18.9, -15.2, -3.3, -3.5, -0.5, -4.5]
with_desi = [16.9, -0.4, -1.5, -6.2, 0.2, 10.8]

x = np.arange(len(components))
width = 0.35

bars1 = ax2.bar(x - width/2, pre_desi, width, label='Pre-DESI', color='#339af0', edgecolor='navy')
bars2 = ax2.bar(x + width/2, with_desi, width, label='+DESI', color='#ff922b', edgecolor='darkorange')

# Styling
ax2.set_ylabel('$\\Delta\\chi^2$ (EDE $-$ $\\Lambda$CDM)', fontsize=12)
ax2.set_title('$\\chi^2$ Breakdown by Component', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(components, fontsize=10)
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.legend(loc='upper right', fontsize=11)
ax2.set_ylim(-20, 25)

# Add value labels on bars
for bar, val in zip(bars1, pre_desi):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -1.5),
            f'{val:+.1f}', ha='center', va='bottom' if height >= 0 else 'top', 
            fontsize=9, color='navy')

for bar, val in zip(bars2, with_desi):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -1.5),
            f'{val:+.1f}', ha='center', va='bottom' if height >= 0 else 'top',
            fontsize=9, color='darkorange')

# Highlight the key insight
ax2.annotate('Low-$\\ell$ EE benefit\nLOST with DESI!', 
             xy=(1 + width/2, -0.4), xytext=(2.5, -12),
             fontsize=10, color='red',
             arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
             bbox=dict(boxstyle='round', facecolor='#ffe3e3', edgecolor='red'))

# Add grid
ax2.grid(axis='y', alpha=0.3)
ax2.set_axisbelow(True)

plt.tight_layout()
plt.savefig('/Users/steveridder/Git/Ridder-Field/phase2/paper/figures/triangular_tension.png', 
            dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig('/Users/steveridder/Git/Ridder-Field/phase3/figures/triangular_tension.png',
            dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
print('Saved: triangular_tension.png')
