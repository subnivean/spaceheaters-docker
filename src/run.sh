#!/bin/bash

# Looks at the outside temperature combined with the heat pump wattage,
# and adds BTUs to the system by turning on space heaters (through 
# smart plugs) when temp is 'low' and the heat pump is starting a
# defrost cycle.

# Smart switch IP addresses
SSIPS="20 21"

# Equation: y = -5.0(x) - 5.0; gives 10 minutes at -3F, 60 minutes at -13F
M=-5.0
B=-5.0

# Wattage below this value can indicate the start of a defrost
LOWWATTS=250
# Don't do anything until we are at or lower than this temp
STARTTEMP=-3
# Max 'on' time for the space heaters; don't exceed the heat pump cycle (~120 minutes)
MAXMINUTES=90

while true
do
  # Read the heat pump wattage and outside temp from log files
  hhpwatts=$(ssh hhpmonpi tail -n1 house_heat_pump_ct_readings.log |cut -d',' -f5)
  outtemp=$(tail -n1 ../ambientweather/data/temps.log |cut -d'|' -f2)

  echo "$hhpwatts $outtemp"

  if (( $(echo "$hhpwatts < $LOWWATTS" | bc -l) )) && (( $(echo "$outtemp < $STARTTEMP" | bc -l) ))
  then

    echo -n "Cold defrost on $(date) - "

    # Calculate the 'on' time based on the outside temperature
    onminutes=$(echo "$M * $outtemp + $B" | bc -l)
    # Don't allow the space heaters to run longer than
    # the time between heat pump defrosts (typ. 2 hours)
    if (( $(echo "$onminutes > $MAXMINUTES" | bc -l) ))
    then
      onminutes=$MAXMINUTES
    fi
    onseconds=$(echo "60 * $onminutes" | bc -l)

    printf "turning on space heaters for %.1f minutes\n" $onminutes

    # Turn on the space heaters
    for ssip in $SSIPS
    do
      curl http://192.168.1.$ssip/cm?cmnd=Power%20On
    done

    # Leave them on for the calculated time
    sleep $onseconds

    # Turn them off
    for ssip in $SSIPS
    do
      curl http://192.168.1.$ssip/cm?cmnd=Power%20Off
    done

  fi

  # Wait a little before we check again
  sleep 11

done
