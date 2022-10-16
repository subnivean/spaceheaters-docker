from heatpump import HeatPumpData
from ambientweather import WeatherData

hhpdata = HeatPumpData('house', '192.168.1.9')
hhpwatts = hhpdata.watts

awx1 = WeatherData(stationnum=1)
outtemp = awx1.tempf
intemp = awx1.tempinf

print(f"{hhpwatts=}, {outtemp=}, {intemp=}")