#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import re
from datetime import datetime


fontsize=15
titlesize=20

# Use the log file name passed as command line argument, or default to "main.log"
if len(sys.argv) > 1:
    main_log_file = sys.argv[1]
else:
    main_log_file = "main.log"

# Extract date and time from the log file name
log_date_time_str = re.search(r'\d{8}_\d{6}', main_log_file)
if log_date_time_str:
    log_date_time_str = log_date_time_str.group()
else:
    log_date_time_str = datetime.now().strftime('%Y%m%d_%H%M%S')

# Initialize lists for timestamps and throughput values (all data, including zeros)
timestamps = []
throughputs = []

# Updated regex:
#   \[\s*\d+\]                 : Matches the id part (e.g., "[  5]")
#   \s+\d+\.\d+-(\d+\.\d+)\s+sec : Captures the ending time (group 1) from "0.00-1.00 sec"
#   \s+\S+\s+\S+\s+             : Skips over the transfer amount (e.g., "1.62 MBytes")
#   ([\d\.]+)\s+((?:[GM])?bits/sec) : Captures the bitrate value (group 2) and its unit (group 3)
pattern = re.compile(
    r"\[\s*\d+\]\s+\d+\.\d+-(\d+\.\d+)\s+sec\s+\S+\s+\S+\s+([\d\.]+)\s+((?:[GM])?bits/sec)"
)

with open(main_log_file, "r") as file:
    for line in file:
        match = pattern.search(line)
        if match:
            end_time = float(match.group(1))
            bitrate = float(match.group(2))
            unit = match.group(3)
            # Convert to Mbits/sec:
            if unit.startswith("G"):
                bitrate *= 1000
            elif unit.startswith("bits"):
                bitrate /= 1e6
            timestamps.append(end_time)
            throughputs.append(bitrate)
        else:
            # Uncomment the next line for debugging unmatched lines
            # print("No match for line:", line.strip())
            pass

print("Timestamps:", timestamps)
print("Throughputs:", throughputs)

# Prepare filtered data for the instantaneous throughput plot (excluding zero values)
nonzero_timestamps = [t for t, th in zip(timestamps, throughputs) if th > 0]
nonzero_throughputs = [th for t, th in zip(timestamps, throughputs) if th > 0]

# Compute accumulated throughput from the complete dataset (including zeros)
accumulated = [0]  # starting at 0 Mbits
for i in range(1, len(timestamps)):
    dt = timestamps[i] - timestamps[i - 1]
    # Trapezoidal integration: average throughput over the interval
    area = 0.5 * (throughputs[i] + throughputs[i - 1]) * dt
    accumulated.append(accumulated[-1] + area)

# Create subplots: top for instantaneous (nonzero) throughput, bottom for accumulated throughput
fig, axs = plt.subplots(2, 1, figsize=(10, 10))

# Top subplot: Instantaneous throughput (nonzero values only)
axs[0].plot(nonzero_timestamps, nonzero_throughputs, label="Main Flow Throughput")
# Mark background flow start times
bg_start_times = [150, 300, 450]
colors = ['red', 'green', 'purple']
for t, col in zip(bg_start_times, colors):
    axs[0].axvline(x=t, color=col, linestyle="--", label=f"BG flow started at {t}s", linewidth=2)
axs[0].set_xlabel("Time (s)", fontsize=fontsize)
axs[0].set_ylabel("Throughput (Mbits/sec)", fontsize=fontsize)
axs[0].set_title("Main Flow Instantaneous Throughput (Non-Zero)", fontsize=titlesize)
axs[0].legend(fontsize=fontsize)
axs[0].grid(True)

# Bottom subplot: Accumulated throughput (all data)
axs[1].plot(timestamps, accumulated, label="Accumulated Throughput")
for t, col in zip(bg_start_times, colors):
    axs[1].axvline(x=t, color=col, linestyle="--", label=f"BG flow started at {t}s", linewidth=2)
axs[1].set_xlabel("Time (s)", fontsize=fontsize)
axs[1].set_ylabel("Accumulated Throughput (Mbit)", fontsize=fontsize)
axs[1].set_title("Accumulated Throughput Over Time", fontsize=titlesize)
axs[1].legend(fontsize=fontsize)
axs[1].grid(True)

plt.tight_layout()

# Save the plot with the extracted date/time stamp
plot_filename = f"throughput_plot_{log_date_time_str}.png"
plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
print("Plot saved to", plot_filename)
plt.show()
