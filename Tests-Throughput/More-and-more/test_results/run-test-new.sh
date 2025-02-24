#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <congestion_control> <bg1_parallel> <bg2_parallel> <bg3_parallel> <test_number>"
    exit 1
fi

# Get command line arguments
CONGESTION_CONTROL=$1
BG1_PARALLEL=$2
BG2_PARALLEL=$3
BG3_PARALLEL=$4
TEST_NUMBER=$5

# Define durations for each flow
MAIN_DURATION=700
BG1_DURATION=550
BG2_DURATION=400
BG3_DURATION=250

# Get current date and time for filenames (format: YYYYMMDD_HHMMSS)
NOW=$(date +"%Y%m%d_%H%M%S")
SERVER="10.42.0.1"  # Your iperf server IP

# Create a dedicated folder for this test run
TEST_DIR="/home/cspandeh/Masterthesis/PScheduler/More-and-more/noloss/test_results/Test_${NOW}_test${TEST_NUMBER}"
mkdir -p "$TEST_DIR"

# Write a parameters file documenting the test settings
PARAM_FILE="${TEST_DIR}/parameters.txt"
cat <<EOF > "$PARAM_FILE"
Test Number:             ${TEST_NUMBER}
Date & Time:             ${NOW}
Server IP:               ${SERVER}
Main Flow Port:          5201
Main Flow Duration:      ${MAIN_DURATION} seconds
Main Flow Congestion:    ${CONGESTION_CONTROL}

Background Flow 1:
  Port:                5002
  Duration:            ${BG1_DURATION} seconds (or ${BG1_DURATION}-15 if restarted)
  Parallel Streams:    ${BG1_PARALLEL}
  Congestion Control:  cubic

Background Flow 2:
  Port:                5001
  Duration:            ${BG2_DURATION} seconds (or ${BG2_DURATION}-15 if restarted)
  Parallel Streams:    ${BG2_PARALLEL}
  Congestion Control:  cubic

Background Flow 3:
  Port:                5101
  Duration:            ${BG3_DURATION} seconds (or ${BG3_DURATION}-15 if restarted)
  Parallel Streams:    ${BG3_PARALLEL}
  Congestion Control:  cubic

TC Netem Settings:
  sudo tc qdisc add dev enp2s0 root netem delay 195ms 1.6ms distribution paretonormal

EOF

# Setup logging of terminal output into a file.
TERMINAL_LOG="${TEST_DIR}/terminal_output.log"
# Redirect stdout and stderr to tee so that output goes to both the terminal and the log file.
exec > >(tee -a "$TERMINAL_LOG") 2>&1

# Set up the network delay (requires sudo)
sudo tc qdisc add dev enp2s0 root netem delay 195ms 1.6ms distribution paretonormal

# Define log file names (stored in the test folder)
MAIN_LOG="${TEST_DIR}/main_${NOW}_test${TEST_NUMBER}.log"
BG1_LOG="${TEST_DIR}/bg1_${NOW}_test${TEST_NUMBER}.log"
BG2_LOG="${TEST_DIR}/bg2_${NOW}_test${TEST_NUMBER}.log"
BG3_LOG="${TEST_DIR}/bg3_${NOW}_test${TEST_NUMBER}.log"

echo "Starting main flow on port 5201 with congestion control ${CONGESTION_CONTROL}..."
iperf3 -c "$SERVER" -p 5201 -t $MAIN_DURATION --congestion "$CONGESTION_CONTROL" > "$MAIN_LOG" 2>&1 &
MAIN_PID=$!

# Sleep 150 seconds after the main stream starts before starting BG flows.
sleep 150

# Function to handle errors and cleanup (if needed)
cleanup() {
    echo "An error occurred. Terminating all iperf processes..."
    pkill -P $$
    sudo tc qdisc del dev enp2s0 root netem
    exit 1
}

# Trap any error and call cleanup
trap 'cleanup' ERR

###############################################################################
# Function: check_iperf_running
# Checks if an iperf3 process for a given port is running.
# Usage: check_iperf_running <port>
###############################################################################
check_iperf_running() {
    local port=$1
    # Search for an iperf3 command that connects to the specified SERVER and port.
    if pgrep -f "iperf3 -c $SERVER -p $port" > /dev/null; then
        return 0
    else
        return 1
    fi
}

###############################################################################
# Background Flow 1 with retry and 150-second interval
###############################################################################
bg_start_time=$(date +%s)
attempt=1
while [ $attempt -le 2 ]; do
    if [ $attempt -eq 1 ]; then
        runtime=$BG1_DURATION
    else
        runtime=$((BG1_DURATION - 15))
    fi
    echo "Starting background flow 1 on port 5002 (attempt $attempt) with ${BG1_PARALLEL} parallel streams for $runtime seconds..."
    iperf3 -c "$SERVER" -p 5002 -t "$runtime" --congestion cubic -P "$BG1_PARALLEL" > "$BG1_LOG" 2>&1 &
    sleep 15
    if check_iperf_running 5002; then
        echo "Background flow 1 is running."
        break
    else
        echo "Background flow 1 failed to start on attempt $attempt."
        if [ $attempt -eq 2 ]; then
            echo "Background flow 1 failed after retrying."
            cleanup
        fi
        attempt=$((attempt + 1))
    fi
done
elapsed=$(($(date +%s) - bg_start_time))
remaining=$((150 - elapsed))
[ $remaining -gt 0 ] && sleep $remaining

###############################################################################
# Background Flow 2 with retry and 150-second interval
###############################################################################
bg_start_time=$(date +%s)
attempt=1
while [ $attempt -le 2 ]; do
    if [ $attempt -eq 1 ]; then
        runtime=$BG2_DURATION
    else
        runtime=$((BG2_DURATION - 15))
    fi
    echo "Starting background flow 2 on port 5001 (attempt $attempt) with ${BG2_PARALLEL} parallel streams for $runtime seconds..."
    iperf3 -c "$SERVER" -p 5001 -t "$runtime" --congestion cubic -P "$BG2_PARALLEL" > "$BG2_LOG" 2>&1 &
    sleep 15
    if check_iperf_running 5001; then
        echo "Background flow 2 is running."
        break
    else
        echo "Background flow 2 failed to start on attempt $attempt."
        if [ $attempt -eq 2 ]; then
            echo "Background flow 2 failed after retrying."
            cleanup
        fi
        attempt=$((attempt + 1))
    fi
done
elapsed=$(($(date +%s) - bg_start_time))
remaining=$((150 - elapsed))
[ $remaining -gt 0 ] && sleep $remaining

###############################################################################
# Background Flow 3 with retry and 150-second interval
###############################################################################
bg_start_time=$(date +%s)
attempt=1
while [ $attempt -le 2 ]; do
    if [ $attempt -eq 1 ]; then
        runtime=$BG3_DURATION
    else
        runtime=$((BG3_DURATION - 15))
    fi
    echo "Starting background flow 3 on port 5101 (attempt $attempt) with ${BG3_PARALLEL} parallel streams for $runtime seconds..."
    iperf3 -c "$SERVER" -p 5101 -t "$runtime" --congestion cubic -P "$BG3_PARALLEL" > "$BG3_LOG" 2>&1 &
    sleep 15
    if check_iperf_running 5101; then
        echo "Background flow 3 is running."
        break
    else
        echo "Background flow 3 failed to start on attempt $attempt."
        if [ $attempt -eq 2 ]; then
            echo "Background flow 3 failed after retrying."
            cleanup
        fi
        attempt=$((attempt + 1))
    fi
done
elapsed=$(($(date +%s) - bg_start_time))
remaining=$((150 - elapsed))
[ $remaining -gt 0 ] && sleep $remaining

###############################################################################
# Wait for all iperf3 processes to complete.
###############################################################################
while check_iperf_running 5201 || check_iperf_running 5002 || \
      check_iperf_running 5001 || check_iperf_running 5101; do
    sleep 10
done

echo "Test completed."
sudo tc qdisc del dev enp2s0 root netem

# Run the Python plotting script with sudo.
sudo python plot-graph.py "$MAIN_LOG"

# Append the terminal output into the parameters file.
echo -e "\nTerminal comments:" >> "$PARAM_FILE"
cat "$TERMINAL_LOG" >> "$PARAM_FILE"
