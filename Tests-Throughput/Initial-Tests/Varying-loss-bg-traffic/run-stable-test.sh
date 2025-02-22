#!/bin/bash
# HINT: Please adapt this Script depending on Number of Background Streams, and Loss Rate.
# Input: ./run-test.sh (Duration in s:) 120 (CCA:) bbr

CONGESTION_TEST=${2:-"cubic"}    # Congestion control for measurement test
DURATION_SECONDS=${1:-"120"}     # Duration in sec
DURATION_PSCHED="PT${DURATION_SECONDS}S" # Duration of the throughput-test

# User-defined variables
INTERFACE="enp2s0"              # Network interface
DESTINATION="10.42.0.1"         # Destination IP for throughput test
PARALLEL_STREAMS=1            # Number of parallel streams for background traffic
CONGESTION_BG="cubic"           # Congestion control for background traffic
SLEEP_DURATION=5                # Duration to wait before starting measurement task (in seconds)

# Generate dynamic log filenames based on options
TIMESTAMP=$(date +"%Y%m%d_%H%M") 		 # Current timestamp for file naming
LOG_MEASUREMENT="stable-test_${CONGESTION_TEST}_${TIMESTAMP}.txt"
JSON_MEASUREMENT="stable-test_${CONGESTION_TEST}_${TIMESTAMP}.json"

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
sudo tc qdisc add dev "$INTERFACE" root netem delay 196ms loss 0.1%
#sudo tc qdisc add dev enp2s0 root handle 1: tbf rate 10gbit burst 2500kb latency 50ms
#sudo tc qdisc add dev enp2s0 parent 1:1 handle 10: netem delay 196ms loss 0%

# Run throughput measurement
{
    echo "Measurement Test"
    echo "Timestamp: $(date)"
    echo "Interface: $INTERFACE"
    echo "Destination: $DESTINATION"
    echo "Duration: $DURATION_SECONDS"
    echo "Congestion Control: $CONGESTION_TEST"
    echo "--------------------------------"
} #> "$LOG_MEASUREMENT"

# Start background streams (load traffic)
iperf3 --congestion "$CONGESTION_BG" -t $(($DURATION_SECONDS + 15)) -c "$DESTINATION" -P "$PARALLEL_STREAMS" -p 5002 >> "$LOG_MEASUREMENT" 2>&1 &
BACKGROUND_PID=$!
#iperf3 --congestion htcp -t $(($DURATION_SECONDS + 15)) -c "$DESTINATION" -P "$PARALLEL_STREAMS" -p 5001
# Short wait for background streams to stabilize
sleep "$SLEEP_DURATION"

# Start main throughput test with pscheduler
sudo pscheduler task --format json throughput --congestion="$CONGESTION_TEST" -t "$DURATION_PSCHED" --dest "$DESTINATION" > "$JSON_MEASUREMENT" 2>&1

# Wait for all tasks to finish
wait "$BACKGROUND_PID"

# Remove network emulation
sudo tc qdisc del dev "$INTERFACE" root 


# Print log locations
echo "JSON saved:"
echo " - $JSON_MEASUREMENT"

wait

# Plot the throughput and the window sizes
python plot-measurement.py "$JSON_MEASUREMENT"
