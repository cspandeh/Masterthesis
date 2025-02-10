#!/usr/bin/env python3

import sys
import re

# Check if the user provided at least one argument (the input file)
if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <input_file> [<output_file>]")
    sys.exit(1)

# The first argument is our input file
INPUT_FILE = sys.argv[1]

# If the user provided a second argument, use that as output file,
# otherwise default to "sorted_rtt.txt"
if len(sys.argv) > 2:
    OUTPUT_FILE = sys.argv[2]
else:
    OUTPUT_FILE = "sorted_rtt.txt"

# Compile a regex to find RTT lines like "rtt=194.6 ms"
pattern = re.compile(r'rtt=([\d\.]+)\s*ms')

# We'll collect tuples of (float_rtt, original_line)
lines_with_rtt = []

# Read from the input file
with open(INPUT_FILE, 'r') as f:
    for line in f:
        match = pattern.search(line)
        if match:
            try:
                rtt_value = float(match.group(1))
                # Store (rtt_value, line) so we can sort by rtt_value
                lines_with_rtt.append((rtt_value, line.rstrip('\n')))
            except ValueError:
                # In case float parsing fails, just skip
                pass

# Sort by the RTT value (ascending)
lines_with_rtt.sort(key=lambda x: x[0], reverse=True)

# Write only the original lines to the output, in sorted order
with open(OUTPUT_FILE, 'w') as out:
    for rtt, original_line in lines_with_rtt:
        out.write(original_line + "\n")

print(f"Sorted {len(lines_with_rtt)} lines by RTT. Output in '{OUTPUT_FILE}'.")
