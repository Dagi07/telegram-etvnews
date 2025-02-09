

#!/bin/bash

# Generate a random number between 120 and 300
sleep_time=$((RANDOM % 181 + 120))

# Log the sleep time for verification
echo "Sleeping for $sleep_time seconds..." >> ./logfile.log

# Sleep for the random duration
sleep $sleep_time

# Proceed with the rest of your script
# Your main script commands go here
