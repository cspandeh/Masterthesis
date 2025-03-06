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

### `Tests-Throughput/`
Contains test results and configurations for PScheduler- and IPerf3-based measurements.
- **Measurement Results:**  
  Various JSON and TXT files documenting throughput and performance under different conditions (realistic, optimistic, zero-loss, etc.).
- **Plots:**  
  PDF and other image files automatically generated to visualize measurement results.
- **Scripts:**  
  A suite of shell and Python scripts for running tests, processing logs, and plotting results (e.g., `run-real-baseline-test.sh`, `plot-measurement.py`, `throughput-per-interval.py`).
- **Subdirectories:**
  - `Realistic-Tests/`: Test results simulating realistic network conditions.
    - **Baseline/**: Baseline measurements for realistic scenarios.
    - **Bg-Flows/**: Measurements with background traffic under realistic conditions.
    - **Buffer/**: Tests investigating the impact of 1 GB buffer sizes.
    - **FQ-Codel/**: Experiments evaluating FQ-CoDel queue management.
  - `Optimistic-Tests/`: Test results under optimistic network conditions (no loss).
    - **Baseline/**: Baseline measurements for optimistic scenarios.
    - **Bg-Flows/**: Optimistic tests with background traffic.
    - **Buffer/**: Tests investigating the impact of 1 GB buffer sizes.
    - **FQ-Codel/**: Optimistic tests focusing on FQ-CoDel performance.
  - `Configurations/`: Configuration files and miscellaneous scripts for setting up PScheduler and network parameters.
  - `More-and-more/`: Additional experiments focusing on adding more and more Background Traffic.
    - **test_results/**: Measurements and test results in a zero-loss network environment, including various test result folders and processing scripts.
  - `Initial-Tests/`: Test results simulating realistic network conditions.
    - **distribution-model-tests/**: Measurements for different tc netem delay distribution models.
    - **Varying-loss-bg-traffic/**: Measurements for initial tests, involving 0, 2 and 4 Background Streams, as well as 0%, 0.01% and 0.1% packet loss.

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

