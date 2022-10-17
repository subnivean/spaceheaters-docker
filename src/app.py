from datetime import datetime, timedelta
import json
import sys

from heatpump import HeatPumpData
#from ambientweather.ambientweather import WeatherData
from ambientweatherdata import WeatherData

# Looks at the outside temperature combined with the heat pump wattage,
# and adds BTUs to the system by turning on space heaters (through
# smart plugs) when temp is 'low' and the heat pump is starting a
# defrost cycle.

# Smart switch IP addresses
HPNAME = "house"
HPIP = "192.168.1.9"
WXSTATIONNUM = 1
STOPTIMEFILENAME = "stoptime.json"

SSIPS = [int(plugnum) for plugnum in sys.argv[1:]]

# Equation: y = -5.0(x) - 5.0; gives 10 minutes at -3F, 60 minutes at -13F
M = -5.0
B = -5.0

# Wattage below this value can indicate the start of a defrost
LOWWATTS = 250
# Don't do anything until we are at or lower than this temp
#STARTTEMP = -3
STARTTEMP = 60
# Max 'on' time for the space heaters; don't exceed the heat pump cycle (~120 minutes)
MAXMINUTES = 90

now = datetime.now()

try:
    with open(STOPTIMEFILENAME) as fh:
        stopdata = json.load(fh)
except FileNotFoundError:
    # File won't be there the first time this is run
    stopdata = {'stoptime': "1970-01-01T00:00:00"}

stoptime = datetime.fromisoformat(stopdata['stoptime'])
if now < stoptime:
    minutesleft = int((stoptime - now).seconds / 60)
    print(f"Waiting until {stoptime.isoformat()=}, {minutesleft=}")
    sys.exit()

hhpdata = HeatPumpData(HPNAME, HPIP)
hhpwatts = hhpdata.watts

awx1 = WeatherData(stationnum=WXSTATIONNUM)
outtemp = awx1.tempf
intemp = awx1.tempinf

print(f"{hhpwatts=}, {outtemp=}, {intemp=}")

if (hhpwatts < LOWWATTS and outtemp < STARTTEMP):
    # onminutes = min(M * outtemp + B, MAXMINUTES)
    # DEV TESTING
    onminutes = 2
    stoptime = (now + timedelta(minutes=onminutes)).isoformat()
    print(f"Turn on the space heaters for {onminutes=}, until {stoptime=}")

    for ssip in SSIPS:
        print(f"Turning on space heater {ssip=}")
        pass

    stopdata = {'starttime': now.isoformat(),
                'stoptime': stoptime, 'onminutes': onminutes}
    stopdata['plugs'] = SSIPS

    with open(STOPTIMEFILENAME, 'w') as fh:
        json.dump(stopdata, fh, sort_keys=True, indent=4)


else:
    print("As you were.")