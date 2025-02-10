#!/usr/bin/env python3

import re
import sys
import math

def simple_percentile(sorted_list, p):
    """
    Returns the p-th percentile (0 <= p <= 100) of a *sorted* list
    using a simple 'nearest-rank' approach (no linear interpolation).
    """
    if not sorted_list:
        return None
    # Convert percentile p (e.g. 95) to an index in the range 0..len-1
    idx = int(round((p / 100.0) * (len(sorted_list) - 1)))
    return sorted_list[idx]

rtt_values = []

# Read all lines from stdin
for line in sys.stdin:
    match = re.search(r'rtt=([\d\.]+)\s+ms', line)
    if match:
        val = float(match.group(1))
        rtt_values.append(val)

if not rtt_values:
    print("No RTT found!")
    sys.exit(0)

# Calculate mean and std. dev.
mean = sum(rtt_values)/len(rtt_values)
if len(rtt_values) > 1:
    var = sum((x - mean)**2 for x in rtt_values) / (len(rtt_values)-1)
    sd = math.sqrt(var)
else:
    sd = 0.0

# Sort the values for percentile calculation
sorted_rtt = sorted(rtt_values)

# Example percentiles to compute
percentiles = [50, 90, 95, 99]

# Print the basic stats
print(f"Count: {len(rtt_values)}")
print(f"Mean RTT: {mean:.2f} ms")
print(f"StdDev: {sd:.2f} ms")

# Print the percentiles
print("Percentiles:")
for p in percentiles:
    val = simple_percentile(sorted_rtt, p)
    print(f"  {p}th: {val:.2f} ms")
