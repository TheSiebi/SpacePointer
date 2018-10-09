# ----------------------------------------------------------------------------------
# This script detects the position of the user and can output
# the topocentric coordinates of a desired celestial object. 
#
# Author:   Michael Siebenmann
# Date :    30.07.2018
#
# History:
# Version   Date        Who     Changes
# 1.0       30.07.2018  M7ma    created
# 1.1       14.08.2018  M7ma    complete overhaul, better usability
# 1.2       29.08.201# ----------------------------------------------------------------------------------
# This script detects the position of the user and can output
# the topocentric coordinates of a desired celestial object. 
#
# Author:   Michael Siebenmann
# Date :    30.07.2018
#
# History:
# Version   Date        Who     Changes
# 1.0       30.07.2018  M7ma    created
# 1.1       14.08.2018  M7ma    complete overhaul, better usability
# 1.2       29.08.2018  M7ma    added Display Interface
# 1.3       08.09.2018  M7ma    added serial communication
# 1.4       19.09.2018  M7ma    added GPS
# 1.5       20.09.2018  M7ma    added orbit visualization, menu redesign
#
# Copyright © Michae$l Siebenmann, Matzingen, Switzerland. All rights reserved
# ----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os
import time
import Adafruit_CharLCD as LCD
import datetime, math
import serial
import gpsd
from pytz import timezone
from time import sleep

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------

os.system("sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock")

date_format = "%d.%m.%Y"
time_format = "%H:%M"
dayepoch    = datetime.datetime.strptime('01.01.2000', date_format)
timeepoch   = datetime.datetime.strptime('00:00', time_format)
timeepoch   = timeepoch.replace(tzinfo = timezone('UTC'))

ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(3)

# Coordinates of Frauenfeld, in case the GPS receives no signal:
local_lon = 8.89888888
local_lat = math.radians(47.5577777)

modes = ("Echtzeit", "Custom", "Bahnsimulation")
planets = ("Sonne", "Mond", "Merkur", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptun")

lcd = LCD.Adafruit_CharLCDPlate() # Initialize the LCD using the pins
lcd.clear()

# Create 2 custom characters
up_arrow = [
  0x04,
  0x0E,
  0x1F,
  0x04,
  0x04,
  0x04,
  0x04,
  0x00
  ]

down_arrow = [
  0x04,
  0x04,
  0x04,
  0x04,
  0x1F,
  0x0E,
  0x04,
  0x00
  ]

lcd.create_char(0, up_arrow)
lcd.create_char(1, down_arrow)

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

def shutdown():
    lcd.clear()
    lcd.set_backlight(0)
    os.system("sudo poweroff") # Shutdown the RPi if SELECT and RIGHT are pressed at the same time

# Get user's desired mode

def get_mode():
    i = 0
    lcd.clear()
    lcd.set_cursor(0,0) # Column 0 Row 0
    lcd.message('Modus:')
    lcd.set_cursor(0,1)
    lcd.message(modes[i])
    
    while True:
        # Loop through buttons and check if pressed
        if lcd.is_pressed(LCD.LEFT):
            i -= 1
            i %= 3
            lcd.clear()
            lcd.message('Modus:')
            lcd.set_cursor(0,1)
            lcd.message(modes[i])
            time.sleep(0.3)
        elif lcd.is_pressed(LCD.RIGHT):
            i += 1
            i %= 3
            lcd.clear()
            lcd.message('Modus:')
            lcd.set_cursor(0,1)
            lcd.message(modes[i])
            time.sleep(0.3)
        elif lcd.is_pressed(LCD.SELECT):
            sleep(1)
            lcd.clear()
            break
    mode = modes[i]
    return(mode)

# Get user's desired object

def get_object():
    i = 0 # Variable for switching between planets
    lcd.clear()
    lcd.set_cursor(0,0) # Column 0 Row 0
    lcd.message('Himmelsobjekt:')
    lcd.set_cursor(0,1)
    lcd.message(planets[i])
    print('Press Ctrl-C to quit.')
    while True:
        # Loop through buttons and check if pressed
        if lcd.is_pressed(LCD.LEFT):
            i -= 1
            i %= 9
            lcd.clear()
            lcd.message('Himmelsobjekt:')
            lcd.set_cursor(0,1)
            lcd.message(planets[i])
            time.sleep(0.3)
        elif lcd.is_pressed(LCD.RIGHT):
            i += 1
            i %= 9
            lcd.clear()
            lcd.message('Himmelsobjekt:')
            lcd.set_cursor(0,1)
            lcd.message(planets[i])
            time.sleep(0.3)
        elif lcd.is_pressed(LCD.SELECT):
            sleep(1)
            lcd.clear()
            break
        if lcd.is_pressed(LCD.SELECT) and lcd.is_pressed(LCD.RIGHT):
            shutdown()
    planet = planets[i]
    return(planet)

# Calculate altitude and azimuth of the chosen object

def get_alt_az(p, y):
    if y == 1:
        date = datetime.datetime.now()
        time_str = datetime.datetime.now(timezone('UTC'))
        print(time_str)
    elif y == 0:
        time.sleep(0.3)
        isValid = False
        while not isValid:
            m = 0
            lcd.message("Datum:")
            lcd.set_cursor(0,1)
            user_date = [1,1,2000]
            date = repr(user_date[0]).zfill(2) + "." + repr(user_date[1]).zfill(2) + "." + repr(user_date[2]).zfill(4)
            lcd.message(date)
            while True:
                if lcd.is_pressed(LCD.RIGHT):
                    m += 1
                    m %= 3
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.LEFT):
                    m -= 1
                    m %= 3
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.UP):
                    user_date[m] += 1
                    if (m == 0):
                        user_date[m] %= 32
                        if (user_date[m] == 0):
                            user_date[m] = 1
                    elif (m == 1):
                        user_date[m] %= 13
                        if (user_date[m] == 0):
                            user_date[m] = 1
                    lcd.clear()
                    lcd.message("Datum:")
                    lcd.set_cursor(0,1)
                    date = repr(user_date[0]).zfill(2) + "." + repr(user_date[1]).zfill(2) + "." + repr(user_date[2]).zfill(2)
                    lcd.message(date)
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.DOWN):
                    user_date[m] -= 1
                    if (m == 0):
                        if (user_date[m] <= 0):
                            user_date[m] = 31
                    elif (m == 1):
                        if (user_date[m] <= 0):
                            user_date[m] = 12
                    lcd.clear()
                    lcd.message("Datum:")
                    lcd.set_cursor(0,1)
                    date = repr(user_date[0]).zfill(2) + "." + repr(user_date[1]).zfill(2) + "." + repr(user_date[2]).zfill(2)
                    lcd.message(date)
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.SELECT):
                    time.sleep(0.3)
                    break
                if lcd.is_pressed(LCD.SELECT) and lcd.is_pressed(LCD.RIGHT):
                    shutdown()
            try:
                datetime.datetime.strptime(date, date_format)
                isValid = True
                lcd.clear()
            except:
                lcd.clear()
                lcd.message("Kein korrektes")
                lcd.set_cursor(0,1)
                lcd.message("Datum!")
                time.sleep(2)
                lcd.clear()
        date = datetime.datetime.strptime(date, date_format)
                
        isRight = False
        m = int(isRight)
        lcd.message("Uhrzeit:")
        lcd.set_cursor(0,1)
        user_time = [0,0]
        time_str = repr(user_time[0]).zfill(2) + ":" + repr(user_time[1]).zfill(2)
        lcd.message(time_str)
        
        while True:
            if lcd.is_pressed(LCD.LEFT) or lcd.is_pressed(LCD.RIGHT):
                isRight = not isRight # Switch between hours and minutes
                m = int(isRight)
                time.sleep(0.2)
                
            if lcd.is_pressed(LCD.UP):
                user_time[m]+= 1
                if isRight:
                    user_time[m] %= 60
                else:
                    user_time[m] %= 24
                lcd.clear()
                lcd.message("Uhrzeit:")
                lcd.set_cursor(0,1)
                time_str = repr(user_time[0]).zfill(2) + ":" + repr(user_time[1]).zfill(2)
                lcd.message(time_str)
                time.sleep(0.2)

            if lcd.is_pressed(LCD.DOWN):
                user_time[m]-= 1
                if isRight:
                    user_time[m] %= 60
                    if (user_time[m] < 0):
                        user_time[m] = 59
                else:
                    user_time[m] %= 24
                    if (user_time[m] < 0):
                        user_time[m] = 23
                lcd.clear()
                lcd.message("Uhrzeit:")
                lcd.set_cursor(0,1)
                time_str = repr(user_time[0]).zfill(2) + ":" + repr(user_time[1]).zfill(2)
                lcd.message(time_str)
                time.sleep(0.2)
                
            if lcd.is_pressed(LCD.SELECT):
                    time.sleep(0.3)
                    lcd.clear()
                    break
            
            if lcd.is_pressed(LCD.SELECT) and lcd.is_pressed(LCD.RIGHT):
                shutdown()
            
        time_str  = datetime.datetime.strptime(time_str, time_format)
        time_str  = time_str.replace(tzinfo = timezone('UTC'))
    else:
        global speed_date
        global speed_time
        speed_date += datetime.timedelta(minutes = 5)
        speed_time += datetime.timedelta(minutes = 5)
        date = speed_date
        time_str = speed_time
        
    datediff = date - dayepoch
    d = datediff.days + 1
    timediff = time_str - timeepoch
    diff_ind = (datetime.timedelta.total_seconds(timediff)%86400) / (3600*24)
    print(repr(diff_ind))
    d += diff_ind
    UT = diff_ind * 24


    # Orbital elements

    ref = {
        "Sonne":   (0.0,
                    0.0,
                    282.9404 + 4.70935E-5 * d,
                    1.000000,
                    0.016709 - 1.151E-9 * d,
                    356.0470 + 0.9856002585 * d),
           
        "Mond":    (125.1228 - 0.0529538083 * d,
                    5.1454,
                    318.0634 + 0.1643573223 * d,
                    60.2666,
                    0.054900,
                    115.3654 + 13.0649929509 * d),

        "Merkur":  (48.3313 + 3.24587E-5 * d,
                    7.0047 + 5.00E-8 * d,
                    29.1241 + 1.01444E-5 * d,
                    0.387098,
                    0.205635 + 5.59E-10 * d,
                    168.6562 + 4.0923344368 * d),

        "Venus":   (76.6799 + 2.46590E-5 * d,
                    3.3946 + 2.75E-8 * d,
                    54.8910 + 1.38374E-5 * d,
                    0.723330,
                    0.006773 - 1.302E-9 * d,
                    48.0052 + 1.6021302244 * d),

        "Mars":    (49.5574 + 2.11081E-5 * d,
                    1.8497 - 1.78E-8 * d,
                    286.5016 + 2.92961E-5 * d,
                    1.523688,
                    0.093405 + 2.516E-9 * d,
                    18.6021 + 0.5240207766 * d),

        "Jupiter": (100.4542 + 2.76854E-5 * d,
                    1.3030 - 1.557E-7 * d,
                    273.8777 + 1.64505E-5 * d,
                    5.20256,
                    0.048498 + 4.469E-9 * d,
                    19.8950 + 0.0830853001 * d),

        "Saturn":  (113.6634 + 2.38980E-5 * d,
                    2.4886 - 1.081E-7 * d,
                    339.3939 + 2.97661E-5 * d,
                    9.55475,
                    0.055546 - 9.499E-9 * d,
                    316.9670 + 0.0334442282 * d),

        "Uranus":  (74.0005 + 1.3978E-5 * d,
                    0.7733 + 1.9E-8 * d,
                    96.6612 + 3.0565E-5 * d,
                    19.18171 - 1.55E-8 * d,
                    0.047318 + 7.45E-9 * d,
                    142.5905 + 0.011725806 * d),

        "Neptun":  (131.7806 + 3.0173E-5 * d,
                    1.7700 - 2.55E-7 * d,
                    272.8461 - 6.027E-6 * d,
                    30.05826 + 3.313E-8 * d,
                    0.008606 + 2.15E-9 * d,
                    260.2471 + 0.005995147 * d)
    }

    # Planet's orbital elements

    N = math.radians(ref[p][0]%360)
    i = math.radians(ref[p][1]%360)
    w = math.radians(ref[p][2]%360)
    a = ref[p][3]
    e = ref[p][4]
    M = math.radians(ref[p][5]%360)

    # Sonne's orbital elements

    ws = math.radians(ref["Sonne"][2]%360)
    es = ref["Sonne"][4]
    Ms = math.radians(ref["Sonne"][5]%360)

    # Eccentric anomaly E

    E0 = M + e * math.sin(M) * (1 + e * math.cos(M))
    while True:
        E1 = E0 - (E0 - e * math.sin(E0) - M) / (1 - e * math.cos(E0))
        if abs(E1-E0) < 0.0001:
            break
        else:
            E0 = E1

    # True anomaly v and radius r

    xv = a * (math.cos(E0) - e )
    yv = a * (math.sqrt(1.0 - e*e) * math.sin(E0))
    v  = math.atan2(yv, xv)
    r  = math.sqrt(xv*xv + yv*yv)

    # Heliocentric coordinates (geocentric for moon)

    xh = r * (math.cos(N) * math.cos(v+w) - math.sin(N) * math.sin(v+w) * math.cos(i))
    yh = r * (math.sin(N) * math.cos(v+w) + math.cos(N) * math.sin(v+w) * math.cos(i))
    zh = r * (math.sin(v+w) * math.sin(i))

    lon = math.atan2(yh, xh)
    lat = math.atan2(zh, math.sqrt(xh*xh+yh*yh))

    # Sun's position

    Es = Ms + es * math.sin(Ms) * (1.0 + es * math.cos(Ms))

    xvs = math.cos(Es) - es
    yvs = math.sqrt(1.0 - es*es) * math.sin(Es)

    vs = math.atan2(yvs, xvs)
    rs = math.sqrt(xvs*xvs + yvs*yvs)

    lonsun = (vs + ws)%(2*math.pi) # 26.8388

    xs = rs * math.cos(lonsun)
    ys = rs * math.sin(lonsun)


    # Geocentric ecliptical coordinaates

    xg = xh + xs
    yg = yh + ys
    zg = zh

    # Equatorial coordinates

    ecl = math.radians(23.4393 - 3.563E-7 * d)

    xe = xg
    ye = yg * math.cos(ecl) - zg * math.sin(ecl)
    ze = yg * math.sin(ecl) + zg * math.cos(ecl)

    RA  = math.atan2(ye, xe)

    while (RA < 0):
        RA += 2 * math.pi

    Dec = math.atan2(ze, math.sqrt(xe*xe + ye*ye))
    rg  = math.sqrt(xe*xe + ye*ye + ze*ze)

    print("RA  = " + repr(math.degrees(RA)) + "°")
    print("Dec = " + repr(math.degrees(Dec)) + "°")
    print("r   = " + repr(rg) + " (AU)")

    # Local Sidereal Time LST
    
    LST = (math.degrees(lonsun)/15 + 12 + UT + local_lon/15)%24

    print("LST = " + repr(LST) + "h")

    # Azimuthal coordinates

    HA = (LST - math.degrees(RA)/15)%24 # Hour Angle

    print("HA  = " + repr(HA) + "h")

    HA *= 15

    x = math.cos(math.radians(HA)) * math.cos(Dec)
    y = math.sin(math.radians(HA)) * math.cos(Dec)
    z = math.sin(Dec)

    xa = x * math.sin(local_lat) - z * math.cos(local_lat)
    ya = y
    za = x * math.cos(local_lat) + z * math.sin(local_lat)

    az  = math.degrees(math.atan2(ya, xa) + math.pi)
    alt = math.degrees(math.atan2(za, math.sqrt(xa*xa + ya*ya)))

    print("Az  = " + repr(az) + "°")
    print("Alt = " + repr(alt) + "°")
    return alt, az

# -----------------------------------------------------------------------------
# GPS
# -----------------------------------------------------------------------------

gpsd.connect() # Connect to the local GPS Module

lcd.clear()
lcd.message("Warte auf")
lcd.set_cursor(0,1)
lcd.message("GPS Signal...")

while (not lcd.is_pressed(LCD.SELECT)):
    packet = gpsd.get_current()
    if lcd.is_pressed(LCD.SELECT) and lcd.is_pressed(LCD.RIGHT):
        shutdown()
    if packet.mode >= 2: 
        local_lat = math.radians(packet.lat)
        local_lon = packet.lon
        lcd.clear()
        lcd.message("GPS gefunden!")
        sleep(1)
        break;
sleep(1)
lcd.clear()

# -----------------------------------------------------------------------------
# Main Program
# -----------------------------------------------------------------------------

while True:
    planet = get_object()
    mode = get_mode()
    if (mode == "Echtzeit"):
        while not lcd.is_pressed(LCD.SELECT):
            alt, az = get_alt_az(planet, 1)
            lcd.message("Objekt: " + planet)
            lcd.set_cursor(0,1)
            lcd.message(repr(round(az, 2)) + "\xDF " + repr(round(alt, 2)) + "\xDF") #\xDF = ° for HD44780U char table
            data = "<" + planet + ", " + repr(alt) +", " + repr(az) + ">"
            ser.write(data.encode()) # send data to Arduino
            timer = 0
            while (timer < 30):
                time.sleep(1)
                timer += 1
                if lcd.is_pressed(LCD.SELECT) and lcd.is_pressed(LCD.RIGHT):
                    shutdown()
                if lcd.is_pressed(LCD.SELECT):
                    break
            lcd.clear()
    elif (mode == "Custom"):
        alt, az = get_alt_az(planet, 0)
        lcd.message("Objekt: " + planet)
        lcd.set_cursor(0,1)
        lcd.message(repr(round(az, 2)) + "\xDF " + repr(round(alt, 2)) + "\xDF") #\xDF = ° for HD44780U char table
        data = "<" + planet + ", " + repr(alt) +", " + repr(az) + ">"
        ser.write(data.encode()) # send data to Arduino
        while True:
            if lcd.is_pressed(LCD.SELECT) and lcd.is_pressed(LCD.RIGHT):
                shutdown()
            if lcd.is_presed(LCD.SELECT):
                break
    else:
        speed_date  = datetime.datetime.now()
        speed_time  = datetime.datetime.now(timezone('UTC'))
        alt, az = get_alt_az(planet, 1)
        lcd.message("Objekt: " + planet)
        lcd.set_cursor(0,1)
        lcd.message(repr(round(az, 2)) + "\xDF " + repr(round(alt, 2)) + "\xDF") #\xDF = ° for HD44780U char table
        data = "<" + planet + ", " + repr(alt) +", " + repr(az) + ">"
        ser.write(data.encode()) # send data to Arduino
        while True:
            if lcd.is_pressed(LCD.SELECT):
                if lcd.is_pressed(LCD.SELECT) and lcd.is_pressed(LCD.RIGHT):
                    shutdown()
                time.sleep(2)
                break
        while not lcd.is_pressed(LCD.SELECT):
            alt, az = get_alt_az(planet, 2)
            lcd.message("Objekt: " + planet)
            lcd.set_cursor(0,1)
            lcd.message(repr(round(az, 2)) + "\xDF " + repr(round(alt, 2)) + "\xDF") #\xDF = ° for HD44780U char table
            data = "<" + planet + ", " + repr(alt) +", " + repr(az) + ">"
            ser.write(data.encode()) # send data to Arduino
            time.sleep(1)
            lcd.clear()
            if lcd.is_pressed(LCD.SELECT) and lcd.is_pressed(LCD.RIGHT):
                shutdown()
    lcd.clear()
    time.sleep(2)