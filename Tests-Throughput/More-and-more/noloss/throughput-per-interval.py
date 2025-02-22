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

def convert_bitrate_to_mbit(value, unit):
    """
    Convert a bitrate value to Mbit/s.
    Acceptable units: bits/sec, Mbits/sec, Gbits/sec.
    """
    value = float(value)
    unit = unit.lower()
    if unit.startswith("g"):
        return value * 1000
    elif unit.startswith("bits"):
        return value / 1e6
    else:
        return value

def process_iperf3_log(file_path, block_duration=150):
    # Regex to capture iperf3 log line fields:
    #   group(1): start time, group(2): end time,
    #   group(3): transfer value, group(4): transfer unit,
    #   group(5): instantaneous bitrate value, group(6): bitrate unit.
    pattern = re.compile(
        r"^\[\s*\d+\]\s+(\d+\.\d+)-(\d+\.\d+)\s+sec\s+([\d\.]+)\s+(\w+Bytes)\s+([\d\.]+)\s+((?:[GM])?bits/sec)",
        re.IGNORECASE
    )
    
    # Dictionaries to group transfer and bitrate values by block.
    blocks_transfer = {}  # block index -> total transfer (in bytes)
    blocks_bitrate  = {}  # block index -> list of instantaneous bitrate values (in Mbit/s)
    last_time = 0.0  # maximum end time found

    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.match(line)
            if match:
                start_str, end_str, transfer_str, t_unit, bitrate_str, b_unit = match.groups()
                try:
                    start_time = float(start_str)
                    end_time   = float(end_str)
                    transfer_bytes = convert_to_bytes(transfer_str, t_unit)
                    bitrate_mbit   = convert_bitrate_to_mbit(bitrate_str, b_unit)
                except ValueError:
                    continue

                # Update the last time reported in the log.
                if end_time > last_time:
                    last_time = end_time

                # Group by block using the start time.
                block_index = int(start_time // block_duration)
                if block_index not in blocks_transfer:
                    blocks_transfer[block_index] = 0.0
                    blocks_bitrate[block_index] = []
                blocks_transfer[block_index] += transfer_bytes
                blocks_bitrate[block_index].append(bitrate_mbit)

    # Only print complete intervals.
    # A block is considered complete if its end time is <= last_time.
    max_block = int(last_time // block_duration)
    for block_index in range(max_block):
        block_start = block_index * block_duration
        block_end   = (block_index + 1) * block_duration
        total_bytes = blocks_transfer.get(block_index, 0.0)
        tp_sum_mbytes = total_bytes / (1024**2)
        bitrate_list = blocks_bitrate.get(block_index, [])
        # Arithmetic mean including any 0 values.
        avg_bitrate = sum(bitrate_list) / block_duration if bitrate_list else 0.0
        print(f"Interval {block_start:.0f} - {block_end:.0f} sec: TP-Sum = {tp_sum_mbytes:.2f} MBytes; {avg_bitrate:.2f} Mbit/s")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python throughput_per_interval.py <iperf3_log_file> [block_duration_seconds]")
        sys.exit(1)
    log_file = sys.argv[1]
    block_duration = 150  # default block duration in seconds
    if len(sys.argv) >= 3:
        try:
            block_duration = float(sys.argv[2])
        except ValueError:
            print("Invalid block duration provided. Using default 150 seconds.")
    process_iperf3_log(log_file, block_duration)
