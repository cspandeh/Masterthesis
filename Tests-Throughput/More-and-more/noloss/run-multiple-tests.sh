#!/bin/bash

# Number of tests to run for each set of parameters
NUM_TESTS=3

# Define the sets of parameters for each test
TEST_PARAMS=(
    "cubic 3 2 2"
    "htcp 3 2 2"
    "bbr 3 2 2"
)

TEST_COUNT=20

for params in "${TEST_PARAMS[@]}"; do
    for i in $(seq 1 $NUM_TESTS); do
        echo "Starting test $TEST_COUNT with parameters: $params..."
        ./run-test-new.sh $params $TEST_COUNT
        wait # Wait for the current test to complete
        echo "Test $TEST_COUNT with parameters: $params completed."
        TEST_COUNT=$((TEST_COUNT + 1))
        # Ensure all iperf processes are terminated before starting the next test
        pkill -f iperf3
        sleep 10
    done
done

echo "All tests completed."