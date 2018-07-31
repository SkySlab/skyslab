#!/bin/bash

while true; do
        sleep 5
        raspistill -ss 10000000 -ISO 1600 -q 10 -o /var/www/stillhd1.jpg >> /home/pi/stills.log 2>&1
        mogrify -brightness-contrast 55x45 /var/www/stillhd1.jpg
        expect /home/pi/sendfile1.sh
#       expect /home/pi/chmodhd1.sh
#       uncomment this if you want streaming video
#       /usr/local/bin/mjpg_streamer -i "/usr/local/lib/input_file.so -f /tmp/stream -n pic.jpg" -o "/usr/local/lib/output_http.so -w /usr/local/www -p 9090" &
        raspistill -n -ex night -q 20 -o /var/www/stillhd2.jpg >> /home/pi/stills.log 2>&1
        expect /home/pi/sendfile2.sh
#       expect /home/pi/chmodhd2.sh
        sleep 3600
done
