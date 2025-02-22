#!/bin/bash

# List of settings
SETTINGS=("300 bbr" "300 cubic" "300 htcp")

# Loop through each setting and run the process_data.sh script with that setting
for SETTING in "${SETTINGS[@]}"; do
   DURATION=$(echo $SETTING | cut -d' ' -f1)
    CCA=$(echo $SETTING | cut -d' ' -f2)
./run-stable-test.sh "$DURATION" "$CCA"
done

