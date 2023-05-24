#!/bin/bash

echo "Starting system report for $HOSTNAME"

#display uptime
echo "System has been up for $(uptime -p)"

#display current disk usage
echo "Disk usage:"
df -h /

#display current memory usage
echo "Memory usage:"
free -h

echo "End of system report for $HOSTNAME"

