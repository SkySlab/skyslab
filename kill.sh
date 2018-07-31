#! /bin/bash

KILL_FILE=/home/pi/killcounter.txt
RESTART_COUNTER=$(/bin/cat $KILL_FILE)

echo "OOPS, internet is dead? Rebooting the operation"
sleep 20s

if [ -z "$(ping -c 1 www.02144.com)" ]; then
        echo "Network Reboot failed, killing pi" >> /home/pi/pikill.txt
        echo $(date) >> /home/pi/pikill.txt
        ((RESTART_COUNTER++))
        echo $RESTART_COUNTER > $KILL_FILE
        sudo reboot -f
fi
