import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Sample data
categories = ['Baseline', 'Buffer 1 GB', 'FQ - CoDel', 'Mixed Backgound Traffic']
optimistic_values1 = [2010.33, 1948, 2017.33, 6365.67]
realistic_values1  = [797.79, 1315.83, 1130.67, 1058.49]
optimistic_values2 = [2514.33, 2821.33, 2798.33, 7097.67]
realistic_values2  = [888.73, 1023.85, 812.65, 895.13]
optimistic_values3 = [190.7, 190.77, 190.5, 190.97]
realistic_values3  = [154.55, 153.76, 154.06, 153.78]

# Number of test conditions
n_conditions = len(categories)

# Muted color palette for the four test conditions
colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3']

# Define two groups on the x-axis: 0 for 'Realistic' and 1 for 'Optimistic'
groups = np.array([0, 1])

# Define bar width and a small gap between bars
bar_width = 0.12
gap = 0.03
# Total width occupied by the group of bars (bars + gaps)
total_group_width = n_conditions * bar_width + (n_conditions - 1) * gap

# Compute x offsets for each bar within a group so they're centered around the group center
offsets = [ -total_group_width/2 + i*(bar_width + gap) + bar_width/2 for i in range(n_conditions)]
offsets = np.array(offsets)

# Font sizes
title_fontsize = 30
label_fontsize = 26
tick_fontsize = 24
legend_fontsize = 24

# Create figure with 3 subplots
fig, axs = plt.subplots(3, 1, figsize=(20, 15))

def plot_subplot(ax, realistic_vals, optimistic_vals, title, ylabel):
    # Plot each test condition as a bar in the respective group (Realistic and Optimistic)
    for i in range(n_conditions):
        # Group 'Realistic' at x = groups[0] with offset for test condition i
        ax.bar(groups[0] + offsets[i], realistic_vals[i], bar_width, color=colors[i])
        # Group 'Optimistic' at x = groups[1] with offset for test condition i
        ax.bar(groups[1] + offsets[i], optimistic_vals[i], bar_width, color=colors[i])
    
    # Set x-axis ticks for the two groups
    ax.set_xticks(groups)
    ax.set_xticklabels(['Realistic', 'Optimistic'], fontsize=tick_fontsize)
    ax.set_xlabel('', fontsize=label_fontsize)
    ax.set_ylabel(ylabel, fontsize=label_fontsize)
    ax.set_title(title, fontsize=title_fontsize)
    ax.tick_params(axis='y', labelsize=tick_fontsize)
    
    # Add light grey horizontal grid lines only for y-axis ticks
    ax.set_axisbelow(True)
    ax.grid(True, axis='y', color='lightgrey', linestyle='-', linewidth=0.7)
    
    # Create a custom legend for the four test conditions using the muted colors
    patches = [mpatches.Patch(color=colors[i], label=categories[i]) for i in range(n_conditions)]
    ax.legend(handles=patches, fontsize=legend_fontsize)

# Plot each subplot with its respective data
plot_subplot(axs[0], realistic_values1, optimistic_values1, 'CUBIC', 'MB')
plot_subplot(axs[1], realistic_values2, optimistic_values2, 'H-TCP', 'MB')
plot_subplot(axs[2], realistic_values3, optimistic_values3, 'BBRv1', 'GB')

plt.tight_layout()
plt.savefig('plot.pdf')
plt.show()
