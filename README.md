# README

## Master Thesis Project

This repository contains scripts, results, and analysis related to network performance measurements conducted for the Master's thesis. The project focuses on evaluating different congestion control algorithms and their impact on data transmission over long-distance, high-latency networks.

---

## Directory Structure

### `hping/`
Contains hping measurement results and scripts for parsing and analyzing RTT (Round Trip Time) data.
- **Results:** `hping_24h_result*.txt`, `sorted_output_*.txt`
- **Scripts:** `parse-rtt.py`, `sort_rtt.py`

### `MTR/`
Includes MTR (My Traceroute) results, analysis scripts, and shell scripts for automated testing.
- **Results:** `mtr_results*.csv`, `mtr_results.json`, `mtr_routenanalyse.txt`
- **Scripts:** `mtr_script.sh`, `mtr_to_csv.sh`

### `PScheduler/`
Contains test results and configurations for PScheduler-based measurements.
- **Measurement Results:** JSON and TXT files from different congestion control algorithms (BBR, CUBIC, HTCP)
- **Plots:** PDF files visualizing measurement results
- **Scripts:** `run-test.sh`, `plot-measurement.py`
- **Subdirectories:**
  - `Messungen-Testen/`: Initial tests and plotting scripts
  - `NeueTest/`: New test configurations and results
  - `Baseline/`: Baseline measurements for comparison
  - `Bg-Flows/`: Measurements with background traffic
  - `BUFFER/`: Tests related to buffer size impact
  - `FQ_CODEL/`: Tests evaluating FQ-CoDel queue management
  - `realistic-tests/`: Tests simulating real-world traffic distributions
  - `stable-tests/`: Stability tests for different congestion control mechanisms
  - `ZeroLoss/`: Measurements in a zero-loss network environment

### `Wireshark/`
Contains Wireshark measurement results and scripts for parsing and analyzing Wireshark CSV data.
- **Results:** `Setting_wireshark`
- **Scripts:** `wireshark-1GB`, `analyze_wireshark.py`

---

## How to Run Tests
1. Navigate to the relevant test directory.
2. Execute the provided shell scripts (`run-test.sh`, `mtr_script.sh`, etc.).
3. Parse results using corresponding Python scripts (`parse-rtt.py`, `plot-measurement.py`).
4. View the results in generated CSV, JSON, and PDF files.

---

## Dependencies
- `hping3`
- `mtr`
- `pscheduler`
- `Python3` (with `matplotlib`, `pandas`, etc.)
- `Wireshark` (optional for deeper analysis)

---

## Contact
For questions or collaboration, please reach out to the author of this research.

