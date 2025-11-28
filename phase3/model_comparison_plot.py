#!/usr/bin/env python3
"""
Model Comparison Forest Plot for Paper
Visualizes H0 and Δχ² across all models
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Set up nice fonts
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.2

# Load chain data
def load_chain(name):
    fname = f"chains/{name}.1.txt"
    with open(fname, "r") as f:
        header = f.readline().strip()
    if header.startswith("#"):
        header = header[1:]
    cols = header.split()
    col_map = {c: i for i, c in enumerate(cols)}
    data = np.loadtxt(fname)
    
    H0 = data[:, col_map["H0"]]
    if "S8" in col_map:
        S8 = data[:, col_map["S8"]]
    else:
        S8 = data[:, col_map["sigma8"]] * np.sqrt(data[:, col_map["Omega_m"]]/0.3)
    
    # Best-fit chi2
    best_idx = np.argmin(data[:, 1])
    chi2_best = data[best_idx, 1] * 2
    
    return {
        "H0_mean": np.mean(H0),
        "H0_std": np.std(H0),
        "H0_16": np.percentile(H0, 16),
        "H0_84": np.percentile(H0, 84),
        "S8_mean": np.mean(S8),
        "S8_std": np.std(S8),
        "chi2": chi2_best
    }

# Define models to plot (SHOES world focus)
models = [
    # (name, display_name, color, style)
    ("tier9_lcdm_shoes", "ΛCDM (Reference)", "#666666", "ref"),
    ("tier9_phenom_shoes", "CPL (k=8)", "#888888", "cpl"),
    ("tier9_v3_shoes_minimal", "EDE Minimal (k=8)", "#CC0000", "gold"),
    ("tier9_v3_shoes_wide_ocdm", "EDE Wide ωcdm (k=9)", "#FF6666", "ede"),
    ("tier9_v3_shoes_fresh", "EDE Fresh (k=9)", "#FF9999", "ede"),
    ("tier9_v3_shoes_optimal", "EDE Optimal (k=9)", "#FFAAAA", "ede"),
]

# Load all data
data = {}
for name, display, color, style in models:
    try:
        data[name] = load_chain(name)
        data[name]["display"] = display
        data[name]["color"] = color
        data[name]["style"] = style
    except Exception as e:
        print(f"Error loading {name}: {e}")

# Reference chi2
ref_chi2 = data["tier9_lcdm_shoes"]["chi2"]

# Create figure with two panels
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
fig.subplots_adjust(wspace=0.05)

# Y positions
y_positions = np.arange(len(models))[::-1]

# Plot H0 panel (left)
ax1.set_title("Hubble Constant H₀ [km/s/Mpc]", fontsize=14, fontweight='bold')
ax1.axvline(73.04, color='#2E86AB', linestyle='--', linewidth=2, alpha=0.7, label='SH0ES (73.04±1.04)')
ax1.axvspan(73.04-1.04, 73.04+1.04, alpha=0.15, color='#2E86AB')
ax1.axvline(67.4, color='#A23B72', linestyle=':', linewidth=2, alpha=0.7, label='Planck ΛCDM (67.4±0.5)')
ax1.axvspan(67.4-0.5, 67.4+0.5, alpha=0.15, color='#A23B72')

for i, (name, display, color, style) in enumerate(models):
    if name not in data:
        continue
    d = data[name]
    y = y_positions[i]
    
    # Error bar style based on model type
    if style == "gold":
        lw = 3
        ms = 12
        marker = 's'
        zorder = 10
    elif style == "ref":
        lw = 2
        ms = 10
        marker = 'o'
        zorder = 5
    elif style == "cpl":
        lw = 2
        ms = 10
        marker = 'd'
        zorder = 5
    else:
        lw = 1.5
        ms = 8
        marker = 'o'
        zorder = 3
    
    # Plot error bar (16-84 percentile)
    ax1.errorbar(d["H0_mean"], y, 
                 xerr=[[d["H0_mean"]-d["H0_16"]], [d["H0_84"]-d["H0_mean"]]],
                 fmt=marker, color=color, markersize=ms, linewidth=lw,
                 capsize=4, capthick=lw, zorder=zorder)

ax1.set_xlabel("H₀ [km/s/Mpc]", fontsize=12)
ax1.set_xlim(66, 75)
ax1.set_yticks(y_positions)
ax1.set_yticklabels([m[1] for m in models])
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(True, alpha=0.3, axis='x')

# Plot Δχ² panel (right)
ax2.set_title("Δχ² relative to ΛCDM", fontsize=14, fontweight='bold')
ax2.axvline(0, color='black', linestyle='-', linewidth=1.5)
ax2.axvspan(-5, 5, alpha=0.1, color='green', label='|Δχ²| < 5 (acceptable)')

for i, (name, display, color, style) in enumerate(models):
    if name not in data:
        continue
    d = data[name]
    y = y_positions[i]
    dchi2 = d["chi2"] - ref_chi2
    
    if style == "gold":
        lw = 3
        ms = 12
        marker = 's'
        zorder = 10
    elif style == "ref":
        lw = 2
        ms = 10
        marker = 'o'
        zorder = 5
    elif style == "cpl":
        lw = 2
        ms = 10
        marker = 'd'
        zorder = 5
    else:
        lw = 1.5
        ms = 8
        marker = 'o'
        zorder = 3
    
    # Plot point
    ax2.plot(dchi2, y, marker, color=color, markersize=ms, zorder=zorder)
    
    # Add value label
    ax2.annotate(f'{dchi2:+.1f}', (dchi2, y), 
                 xytext=(5, 0), textcoords='offset points',
                 fontsize=9, va='center')

ax2.set_xlabel("Δχ²", fontsize=12)
ax2.set_xlim(-20, 10)
ax2.grid(True, alpha=0.3, axis='x')

plt.suptitle('Ridder Field EDE Model Comparison (SHOES World)', 
             fontsize=16, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('model_comparison_forest.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('model_comparison_forest.pdf', bbox_inches='tight')
print("Saved: model_comparison_forest.png and .pdf")

# Also create a simpler version focusing on k=8 comparison
fig2, ax = plt.subplots(figsize=(10, 5))

# Just the key models
key_models = [
    ("tier9_lcdm_shoes", "ΛCDM (k=6)", "#666666", "o", 10),
    ("tier9_phenom_shoes", "CPL (k=8)", "#888888", "d", 10),
    ("tier9_v3_shoes_minimal", "EDE Minimal (k=8)", "#CC0000", "s", 14),
]

for i, (name, display, color, marker, ms) in enumerate(key_models):
    d = data[name]
    dchi2 = d["chi2"] - ref_chi2
    
    ax.scatter(d["H0_mean"], dchi2, c=color, s=ms**2, marker=marker, 
               label=f'{display}: H₀={d["H0_mean"]:.1f}, S₈={d["S8_mean"]:.3f}',
               edgecolors='black', linewidths=1.5, zorder=10)
    
    # Error ellipse (simplified as error bars)
    ax.errorbar(d["H0_mean"], dchi2, 
                xerr=d["H0_std"], 
                fmt='none', color=color, alpha=0.5, capsize=3)

# Add reference lines
ax.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
ax.axvline(73.04, color='#2E86AB', linestyle='--', linewidth=2, alpha=0.7)
ax.axvspan(73.04-1.04, 73.04+1.04, alpha=0.1, color='#2E86AB')
ax.axvline(67.4, color='#A23B72', linestyle=':', linewidth=2, alpha=0.7)

# Labels
ax.set_xlabel('H₀ [km/s/Mpc]', fontsize=12)
ax.set_ylabel('Δχ² (relative to ΛCDM)', fontsize=12)
ax.set_title('Model Comparison: H₀ vs Δχ² Trade-off (SHOES World)', fontsize=14, fontweight='bold')
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim(66, 75)
ax.set_ylim(-18, 5)

# Annotations
ax.annotate('SH0ES\nH₀=73', (73.04, -16), ha='center', fontsize=9, color='#2E86AB')
ax.annotate('Planck\nH₀=67.4', (67.4, -16), ha='center', fontsize=9, color='#A23B72')
ax.annotate('Better fit →', (66.5, -15), fontsize=9, color='green')
ax.annotate('← Worse fit', (66.5, 3), fontsize=9, color='red')

plt.tight_layout()
plt.savefig('model_comparison_h0_chi2.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('model_comparison_h0_chi2.pdf', bbox_inches='tight')
print("Saved: model_comparison_h0_chi2.png and .pdf")

