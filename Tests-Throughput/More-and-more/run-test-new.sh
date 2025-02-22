#!/bin/bash

# Get current date and time for filenames (format: YYYYMMDD_HHMMSS)
NOW=$(date +"%Y%m%d_%H%M%S")
SERVER="10.42.0.1"  # Your iperf server IP
sudo tc qdisc add dev enp2s0 root netem delay 195ms 1.6ms distribution paretonormal loss 0.1%

# Define log file names with date/time stamp
MAIN_LOG="main_${NOW}.log"
BG1_LOG="bg1_${NOW}.log"
BG2_LOG="bg2_${NOW}.log"
BG3_LOG="bg3_${NOW}.log"

echo "Starting main flow on port 5201..."
iperf3 -c $SERVER -p 5201 -t 600 --congestion cubic | tee $MAIN_LOG &
MAIN_PID=$!

# Launch background flows at equal intervals:
sleep 150
echo "Adding background flow 1 on port 5101..."
iperf3 -c $SERVER -p 5101 -t 450 --congestion cubic -P 2 > $BG1_LOG &

sleep 150
echo "Adding background flow 2 on port 5001..."
iperf3 -c $SERVER -p 5001 -t 300 --congestion cubic -P 3 > $BG2_LOG &

sleep 150
echo "Adding background flow 3 on port 5002..."
iperf3 -c $SERVER -p 5002 -t 140 --congestion cubic -P 4 > $BG3_LOG &

# Wait for the main flow to complete
wait $MAIN_PID
echo "Test completed."

sudo tc qdisc del dev enp2s0 root netem

# Automatically run the Python plotting script with the main log file as parameter.
python plot-graph.py $MAIN_LOG
