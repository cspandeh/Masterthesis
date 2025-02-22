#!/bin/bash
# HINT: This script it the same as run-real-baseline-test.sh, please refer to the FQ--Configuration file for further information
# Input: ./run-real-fq-codel-test.sh (duration in s:) 120 (CCA:) bbr

CONGESTION_TEST=${2:-"cubic"}    # Congestion control for measurement test
DURATION_SECONDS=${1:-"120"}     # Duration in sec
DURATION_PSCHED="PT${DURATION_SECONDS}S" # Duration of the throughput-test

# Configuration
INTERFACE="enp2s0"              # Network interface
DESTINATION="10.42.0.1"         # Destination IP for throughput test
PARALLEL_STREAMS=5              # Number of parallel streams for background traffic
CONGESTION_BG="cubic"           # Congestion control for background traffic
SLEEP_DURATION=5                # Duration to wait before starting measurement task (in seconds)

# Generate dynamic log filenames based on options
TIMESTAMP=$(date +"%Y%m%d_%H%M") 		 # Current timestamp for file naming
LOG_MEASUREMENT="${CONGESTION_TEST}_test_${TIMESTAMP}.txt"
JSON_MEASUREMENT="${CONGESTION_TEST}_test_${TIMESTAMP}.json"


# Display configuration
echo "Starting Network Throughput Test"
echo "--------------------------------"
echo "Interface:         $INTERFACE"
echo "Destination:       $DESTINATION"
echo "Test Duration:     $DURATION_SECONDS seconds"
echo "Background Streams:$PARALLEL_STREAMS"
echo "Background CC:     $CONGESTION_BG"
echo "Measurement CC:    $CONGESTION_TEST"
echo "TXT:               $LOG_MEASUREMENT"
echo "JSON:              $JSON_MEASUREMENT"
echo "--------------------------------"

# Add latency and loss simulation with netem
sudo tc qdisc add dev "$INTERFACE" root netem delay 195ms 1.6ms distribution paretonormal loss 0.1%

# Run throughput measurement
{
    echo "Measurement Test"
    echo "Timestamp: $(date)"
    echo "Interface: $INTERFACE"
    echo "Destination: $DESTINATION"
    echo "Duration: $DURATION_SECONDS"
    echo "Congestion Control: $CONGESTION_TEST"
    echo "--------------------------------"
} > "$LOG_MEASUREMENT"

#Background Streams
iperf3  --congestion cubic -t $(($DURATION_SECONDS + 20)) -c 10.42.0.1 -P "$PARALLEL_STREAMS" -p 5002 >> "$LOG_MEASUREMENT" 2>&1 &
BACKGROUND_PID=$! 

# Short wait for background streams to stabilize
sleep "$SLEEP_DURATION"

#Start Main Stream and throughput measurement
sudo pscheduler task --format json throughput --congestion="$CONGESTION_TEST" -t "$DURATION_PSCHED" --dest "$DESTINATION" > "$JSON_MEASUREMENT" 2>&1

# Wait for all tasks to finish
wait "$BACKGROUND_PID"

# Print log locations
echo "JSON saved:"
echo " - $JSON_MEASUREMENT"

# Remove network emulation
sudo tc qdisc del dev "$INTERFACE" root netem
wait

# Plot the throughput and the window sizes
python plot-measurement.py "$JSON_MEASUREMENT"
