import sys, select, os, urllib, urllib2, json, plotly, datetime, time, httplib, subprocess, sqlite3
import numpy as np
import matplotlib
# Force matplotlib to not use any Xwindows backend
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.plotly as py
from plotly.graph_objs import *
#import Adafruit_BMP.BMP085 as BMP085

# Define Colours

class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Define Data Series
datestamps = []
cpu_temps = []
pressures = []
internal_temps = []
external_temps = []
cpu_loads = []

# Paths to database and save location
database = "/var/www/stats.db"
plot_1_location = "/var/www/plot1.png"
plot_2_location = "/var/www/plot2.png"

# Define Variables

COUNTER=1
wait_time=1800
years = mdates.YearLocator()
months = mdates.MonthLocator()
yearsFmt = mdates.DateFormatter('%Y')
altitude = 600

# Read the number of times this pi has restarted
f = open("/home/pi/killcounter.txt", "r")
RESTART = f.read()
f.close()

# Import plotly, weather_underground and Thingspeak keys
with open('/home/pi/config.json') as config_file:
    user_config = json.load(config_file)

plotly_username = user_config['plotly_username']
plotly_api = user_config['plotly_api_key']
plotly_stream_token = user_config['plotly_streaming_token']
wu_api = user_config['weather_underground_api']
ts_api = user_config['thingspeak_api']

print 'User Config Imported ' + bcolours.OKBLUE + 'OK' + bcolours.ENDC

# Connect to SQLITE database
conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

# Initialise the BMP085 and use STANDARD mode (default value)
# sensor = BMP085.BMP085()

# Procedures
def get_BMP_internal_temp():
        internal_temp = 10
        return internal_temp

def get_BMP_pressure():
        # Read pressure at sea level
        sealevel = 1010
        # Read the current barometric pressure level
#       pressure = sensor.read_pressure()
        pressure = 1010
        return pressure

def get_BMP_altitude():
        # To calculate altitude based on an estimated mean sea level pressure
        # (1013.25 hPa) call the function as follows, but this won't be very accurate
        altitude = 600
        return altitude

        # To specify a more accurate altitude, enter the correct mean sea level
        # pressure level.  For example, if the current pressure level is 1023.50 hPa
        # enter 102350 since we include two decimal places in the integer value
        # altitude = bmp.readAltitude(1023)

# Return CPU temperature as a character string
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return RAM information (unit=kb) in a list
# Index 0: total RAM
# Index 1: used RAM
# Index 2: free RAM
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

# Return % of CPU used by user as a character string
def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

# Return information about disk space as a list (unit included)
# Index 0: total disk space
# Index 1: used disk space
# Index 2: remaining disk space
# Index 3: percentage of disk used
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])

# Get the ambient temperature from Weather Underground
def getAmbient():
        f = urllib2.urlopen('http://api.wunderground.com/api/' + wu_api + '/geolookup/conditions/q/-34.966209,149.019295.json')
        json_string = f.read()
        parsed_json = json.loads(json_string)
        location = parsed_json['location']['city']
        temp_c = parsed_json['current_observation']['temp_c']
        return(temp_c)
        f.close()

# Send stuff to ThingSpeak
def post_ts():
        params = urllib.urlencode({'field1': CPU_temp, 'field2': CPU_usage, 'field3': Ambient, 'field4': internal_temp, 'field5': internal_pressure, 'key':ts_api})
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("api.thingspeak.com:80")
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print response.status, response.reason
        data = response.read()
        conn.close()

# Check the Internet is alive
def check_ping():
    hostname = "www.02144.com"
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        pingstatus = "True"
    else:
        pingstatus = "False"
    return pingstatus

# Reboot if things turn to pot
def restart():
        subprocess.call("/home/pi/kill.sh", shell=True)

# Every 48 posts this will reboot itself
def force_restart():
        subprocess.call("/home/pi/force_restart.sh", shell=True)

# Main procedure
print 'Checking 1st ping test'
check = check_ping()

if check=='True':
        print "The Internet is " + bcolours.OKBLUE + "ALIIIVE! Mwuaahahaa." + bcolours.ENDC
else:
        print bcolours.FAIL + "The Internet is not alive, logging stats without the internet, I'll try the internet again in "  + bcolours.OKBLUE,wait_time,bcolours.ENDC + "seconds."+ bcolours.ENDC

now = datetime.datetime.now()
today = datetime.datetime.now().date()
print today
print bcolours.WARNING,now,bcolours.ENDC
print "Checked :" + bcolours.WARNING,COUNTER,bcolours.ENDC + ". Restarted :" +bcolours.FAIL,RESTART,bcolours.ENDC

# CPU informatiom
CPU_temp = getCPUtemperature()
CPU_usage = getCPUuse()

# RAM information
# Output is in kb, here I convert it in Mb for readability
RAM_stats = getRAMinfo()
RAM_used = round(int(RAM_stats[1]) / 1000,1)
RAM_free = round(int(RAM_stats[2]) / 1000,1)

# Disk information
DISK_stats = getDiskSpace()
DISK_free = DISK_stats[1]

# Ambient Weather
Ambient = getAmbient()

# BMP Sensor Info
internal_temp = get_BMP_internal_temp()
internal_pressure = get_BMP_pressure()
altitude = get_BMP_altitude()

# Print Stuff Out
print 'CPU Temperature: ',CPU_temp
print 'CPU Load:                ',CPU_usage
print 'RAM Used:                ',RAM_used
print 'Free Ram:                ',RAM_free
print 'Disk free:               ',DISK_free
print 'Ambient Temperature:     ',Ambient
print 'Internal Temperature:    ',internal_temp
print 'Pressure:                ',internal_pressure
print 'Altitude:                ',altitude,bcolours.ENDC

# Send stuff to Thingspeak
if check=='True':
        print bcolours.OKBLUE + 'Posting to ThingSpeak' + bcolours.ENDC
        post_ts()
