#!/bin/bash

# Define the base directory
BASE_DIR="/home/cspandeh/Masterthesis/PScheduler/More-and-more/noloss/test_results"

# Find all main_***.log files in the base directory and its subfolders
find "$BASE_DIR" -type f -name "main_*.log" | while read -r log_file; do
    echo "Processing $log_file"
    # Get the directory of the log file
    log_dir=$(dirname "$log_file")
    # Temporary file to store the new content
    temp_file=$(mktemp)
    # Run the Python script and store the output in the temporary file
    python3 /home/cspandeh/Masterthesis/PScheduler/More-and-more/noloss/throughput-per-interval.py "$log_file" > "$temp_file"
    # Append the rest of the parameters.txt content to the temporary file
    grep -v "Interval" "$log_dir/parameters.txt" >> "$temp_file"
    # Overwrite the original parameters.txt with the temporary file
    mv "$temp_file" "$log_dir/parameters.txt"
done