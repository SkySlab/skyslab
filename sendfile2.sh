#! /bin/bash

spawn scp /var/www/stillhd2.jpg admin@192.168.0.124:/share/Web/skyslab/stills/
expect "password:"
send qx6&68#XER#e\n;
interact
