import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Load condition labels (in order: low, moderate, substantial, high)
load_labels = ["Low (1-1-1)", "Moderate (3-2-2)", "Substantial (4-5-6)", "High (5-10-15)"]
x = np.arange(len(load_labels))  # positions for the 4 load conditions

# Time interval labels (for the stacked segments)
time_intervals = ["0-150 sec", "150-300 sec", "300-450 sec", "450-600 sec"]
# Muted colors for the segments
segment_colors = ["#b3cde3", "#ccebc5", "#decbe4", "#fed9a6"]

# --- Data for Throughput (MB) ---
# Each row is a load condition; each column is a time interval segment.
# (Values are averages over Test 1, Test 2, and Test 3.)

# CUBIC data
cubic_low = [38040.3, 25973, 14488.6, 9365.7]
cubic_mod = [37979.60, 14856.97, 1975.67, 286.00]
cubic_sub = [40686.23, 6459.60, 278.67, 142.00]
cubic_high = [40528.43, 4445.67, 89.33, 141.00]
cubic_data = np.array([cubic_low, cubic_mod, cubic_sub, cubic_high])

# H-TCP data
httcp_low = [31351.59, 17259.70, 11107.10, 4109.03]
httcp_mod = [30765.28, 8219.91, 642.33, 267.17]
httcp_sub = [23843.84, 2984.00, 210.33, 169.67]
httcp_high = [23077.46, 2754.67, 165.00, 89.33]
httcp_data = np.array([httcp_low, httcp_mod, httcp_sub, httcp_high])

# BBRv1 data
bbrv1_low = [45862.38, 46222.33, 46051.79, 45684.47]
bbrv1_mod = [45948.48, 46061.67, 45683.33, 45431.00]
bbrv1_sub = [45881.39, 45799.93, 45143.18, 44213.00]
bbrv1_high = [45896.36, 45673.93, 44421.67, 43054.33]
bbrv1_data = np.array([bbrv1_low, bbrv1_mod, bbrv1_sub, bbrv1_high])


title_fontsize = 48        
label_fontsize = 40        
tick_fontsize = 40        
legend_fontsize = 30      
annotation_fontsize = 30  

fig, axs = plt.subplots(3, 1, figsize=(30, 48))

def plot_stacked_bars(ax, data, protocol_title):
    # data is a 4x4 array:
    #   rows: load conditions (Low, Moderate, Substantial, High)
    #   columns: time segments (0-150, 150-300, 300-450, 450-600)
    bar_width = 0.4  # width for each bar
    bottoms = np.zeros(len(x))  # starting bottom for stacking
    totals = np.sum(data, axis=1)  # total height per bar
    # For each bar, track the highest y coordinate used for an annotation so far.
    annot_y = np.copy(bottoms)
    
    # Fractional thresholds (adjustable)
    threshold_fraction = 0.03  # segments with height <3% of total are "small"
    margin_fraction = 0.08     # ensure at least 8% of total gap between annotations
    
    # Loop over each time segment to stack the bars
    for seg in range(data.shape[1]):
        segment_values = data[:, seg]
        old_bottom = bottoms.copy()
        bars = ax.bar(x, segment_values, bar_width, bottom=old_bottom,
                      color=segment_colors[seg], edgecolor='white')
        # Annotate each segment
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if height < threshold_fraction * totals[i]:
                intended_y = old_bottom[i] + height + margin_fraction * totals[i]
                if intended_y < annot_y[i] + margin_fraction * totals[i]:
                    intended_y = annot_y[i] + margin_fraction * totals[i]
                y_pos = intended_y
                bbox_props = dict(facecolor=segment_colors[seg], edgecolor='none', alpha=0.7, pad=1.0)
                ax.text(bar.get_x() + bar.get_width()/2, y_pos,
                        f"{segment_values[i]:.0f}",
                        ha='center', va='center',
                        fontsize=annotation_fontsize, color='black',
                        bbox=bbox_props)
            else:
                y_pos = old_bottom[i] + height/2
                ax.text(bar.get_x() + bar.get_width()/2, y_pos,
                        f"{segment_values[i]:.0f}",
                        ha='center', va='center',
                        fontsize=annotation_fontsize, color='black')
            annot_y[i] = max(annot_y[i], y_pos)
        bottoms += segment_values
    
    ax.set_xticks(x)
    ax.set_xticklabels(load_labels, fontsize=tick_fontsize)
    ax.xaxis.labelpad = 20
    ax.yaxis.labelpad = 20
    ax.set_xlabel("", fontsize=label_fontsize)
    ax.set_ylabel("Throughput (MB)", fontsize=label_fontsize)
    ax.set_title(protocol_title, fontsize=title_fontsize)
    ax.tick_params(axis='x', labelsize=tick_fontsize, pad=20)
    ax.tick_params(axis='y', labelsize=tick_fontsize, pad=20)
    # Force plain formatting on the y-axis so numbers appear fully.
    ax.ticklabel_format(style='plain', axis='y')
    ax.set_axisbelow(True)
    ax.grid(True, axis='y', color='lightgrey', linestyle='-', linewidth=0.7)
    
    patches = [mpatches.Patch(color=segment_colors[seg], label=time_intervals[seg])
               for seg in range(len(time_intervals))]
    ax.legend(handles=patches, fontsize=legend_fontsize)

plot_stacked_bars(axs[0], cubic_data, "CUBIC")
plot_stacked_bars(axs[1], httcp_data, "H-TCP")
plot_stacked_bars(axs[2], bbrv1_data, "BBRv1")

plt.subplots_adjust(hspace=0.5)
plt.tight_layout(pad=3.0)
plt.savefig("stacked_throughput_annotated.pdf")
plt.show()
