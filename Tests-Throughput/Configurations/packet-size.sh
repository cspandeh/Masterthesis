#!/bin/bash
# This script performs a 2-minute iperf3 test and then determines
# the average packet size (tcp) of the iperf data on port 5201.
#
# Usage: ./iperf_avg_packet_size.sh <iperf-server-ip>
#
# Note: Root privileges may be required for tcpdump.

if [ -z "$1" ]; then
  echo "Usage: $0 <iperf-server-ip>"
  exit 1
fi

SERVER_IP="$1"
CAPTURE_FILE="iperf_capture.pcap"
INTERFACE="enp2s0"

echo "Starting tcpdump on interface $INTERFACE, saving to $CAPTURE_FILE..."
# Start tcpdump in the background, filter packets on port 5201 (iperf3 default)
sudo tcpdump -i "$INTERFACE" -w "$CAPTURE_FILE" port 5201 &
TCPDUMP_PID=$!

# Give tcpdump some time to really start
sleep 2

echo "Starting iperf3 test to $SERVER_IP for 2 minutes (120 seconds)..."
iperf3 -c "$SERVER_IP" -t 120 --congestion cubic

echo "Test finished. Stopping tcpdump (PID $TCPDUMP_PID)..."
sudo kill -SIGINT "$TCPDUMP_PID"
# Wait until tcpdump has cleanly terminated
wait "$TCPDUMP_PID" 2>/dev/null

echo "Processing the recording..."

# Calculate the average packet size of the iperf3 data.
# TCP payload 'tcp.len' and optionally add the filter "&& tcp.len>0".

# Number of captured packets (only from 10.42.0.2 to 10.42.0.1)
PACKET_COUNT=$(tshark -r "$CAPTURE_FILE" -Y "ip.src==10.42.0.2 and ip.dst==10.42.0.1 and tcp.port==5201" -T fields -e tcp.len | wc -l)

# Sum of frame sizes (only from 10.42.0.2 to 10.42.0.1)
TOTAL_BYTES=$(tshark -r "$CAPTURE_FILE" -Y "ip.src==10.42.0.2 and ip.dst==10.42.0.1 and tcp.port==5201" -T fields -e tcp.len | paste -sd+ - | bc)

if [ "$PACKET_COUNT" -gt 0 ]; then
  AVG_SIZE=$(echo "scale=2; $TOTAL_BYTES / $PACKET_COUNT" | bc)
  echo "Average packet size: $AVG_SIZE bytes (over $PACKET_COUNT packets)."
else
  echo "No packets found."
fi
