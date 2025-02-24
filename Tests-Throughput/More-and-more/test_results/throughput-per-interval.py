#!/usr/bin/env python3
import re
import sys

def convert_to_bytes(value, unit):
    """
    Convert a transfer value to bytes using 1024-based conversion.
    Acceptable units: Bytes, KBytes, MBytes, GBytes.
    """
    value = float(value)
    unit = unit.upper()
    if "GBYTES" in unit:
        return value * 1024**3
    elif "MBYTES" in unit:
        return value * 1024**2
    elif "KBYTES" in unit:
        return value * 1024
    else:
        return value

def process_iperf3_log(file_path, block_duration=150, num_intervals=4):
    """
    This script always prints exactly four fixed intervals: 
      0-150, 150-300, 300-450, and 450-600 seconds.
    """
    pattern = re.compile(
        r"^\[\s*\d+\]\s+(\d+\.\d+)-(\d+\.\d+)\s+sec\s+([\d\.]+)\s+(\w+Bytes)",
        re.IGNORECASE
    )
    
    # Initialize dictionary for fixed intervals.
    intervals = {i: 0.0 for i in range(num_intervals)}
    
    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.match(line)
            if not match:
                continue
            start_str, end_str, transfer_str, transfer_unit = match.groups()
            try:
                start_time = float(start_str)
                end_time = float(end_str)
            except ValueError:
                continue
            # Only consider records that represent ~1-second intervals.
            duration = end_time - start_time
            if abs(duration - 1.0) > 0.1:
                continue
            # Only include records that fall within the first (num_intervals*block_duration) seconds.
            if start_time >= num_intervals * block_duration:
                continue
            transfer_bytes = convert_to_bytes(transfer_str, transfer_unit)
            interval_index = int(start_time // block_duration)
            intervals[interval_index] += transfer_bytes

    # For each fixed interval, compute TP-Sum in MBytes and throughput in Mbit/s.
    for i in range(num_intervals):
        sum_bytes = intervals.get(i, 0.0)
        tp_sum_mbytes = sum_bytes / (1024**2)
        throughput_mbit = (sum_bytes * 8) / (block_duration * 1e6)
        start_sec = i * block_duration
        end_sec = (i + 1) * block_duration
        print(f"Interval {start_sec:.0f} - {end_sec:.0f} sec: TP-Sum = {tp_sum_mbytes:.2f} MBytes; {throughput_mbit:.2f} Mbit/s")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python throughput_fixed_intervals.py <iperf3_log_file> [block_duration_seconds]")
        sys.exit(1)
    log_file = sys.argv[1]
    block_duration = 150  # default block duration in seconds
    if len(sys.argv) >= 3:
        try:
            block_duration = float(sys.argv[2])
        except ValueError:
            print("Invalid block duration provided. Using default 150 seconds.")
    process_iperf3_log(log_file, block_duration)
