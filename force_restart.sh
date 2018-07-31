#! /bin/bash

KILL_FILE=/home/pi/killcounter.txt
RESTART_COUNTER=$(/bin/cat $KILL_FILE)

echo "Operation completed, auto-reboot initiated" >> /home/pi/pikill.txt
echo $(date) >> /home/pi/pikill.txt
((RESTART_COUNTER++))
echo $RESTART_COUNTER > $KILL_FILE
sudo reboot -f
