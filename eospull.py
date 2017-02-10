import httplib, urllib, socket
import xml.etree.ElementTree as ET
from xml.dom import minidom




def getstations():
    stations = []
    Id = []
    param = ""
    conn = httplib.HTTPConnection("www.eosweather.ca",80,timeout=5)
    conn.request("GET","/burst/activestations.php",param,{"Content-type":"application/x-www-form-urlencoded"})
    r1 =conn.getresponse()
    msg = r1.read()
    root = ET.fromstring(msg)

    for station in root.findall('Active'):
        stations.append( station.find('StationName').text)
        Id.append(station.find("Link_ID").text)

    return stations, Id

def getburst(ST):
    param = urllib.urlencode({
                     "ST":ST
                })
    Wind = ""
    Rain = ""
    Pressure = ""
    Solar = ""
    Temp = ""
    Board = ""
    Tide = ""
    We_Date = ""
    try:
        
        conn = httplib.HTTPConnection("www.eosweather.ca",80,timeout=5)
        conn.request("POST","/burst/burstpost.php?",param,{"Content-type":"application/x-www-form-urlencoded"})
        r1 =conn.getresponse()
        msg = r1.read()
        root = ET.fromstring(msg)
##        print param
##        print msg
        for station in root.findall('Weather'):
            Wind = station.find('WIND').text
            Rain = station.find('RAIN').text
            Pressure = station.find('PRESSURE').text
            Solar = station.find('SOLAR').text
            Temp = station.find('TEMP').text
            Board = station.find('BOARD').text
            Tide = station.find('TIDE').text
            We_Date = station.find('WE_DATE_TIME').text

        return Wind, Rain, Pressure, Solar, Temp, Board, Tide, We_Date
    except:
        return "","","","","","","",""

def getdaily(ST):
    param = urllib.urlencode({
                     "ST":ST
                })
    MeanTemp = ""
    MaxTemp = ""
    LowTemp = ""
    try:
         
        conn = httplib.HTTPConnection("www.eosweather.ca",80,timeout=5)
        conn.request("POST","/burst/dailypost.php?",param,{"Content-type":"application/x-www-form-urlencoded"})
        r1 =conn.getresponse()
        msg = r1.read()
        root = ET.fromstring(msg)

        for station in root.findall('Daily'):
            MeanTemp = station.find('MEANTEMP').text
            MaxTemp = station.find('MAXTEMP').text
            LowTemp = station.find('LOWTEMP').text
            WindPeak = station.find('HIGHWIND').text


        return MeanTemp, MaxTemp, LowTemp, WindPeak
    except:
        return "","","",""

def getarchive(ST):
    param = urllib.urlencode({
                     "ST":ST
                })
    MeanTemp = ""
    MaxTemp = ""
    LowTemp = ""
    try:
         
        conn = httplib.HTTPConnection("www.eosweather.ca",80,timeout=5)
        conn.request("POST","/burst/burstarchive.php?",param,{"Content-type":"application/x-www-form-urlencoded"})
        r1 =conn.getresponse()
        msg = r1.read()
        root = ET.fromstring(msg)

        for station in root.findall('Archive'):
            We_Date = station.find("WE_Date").text
            We_Time = station.find("WE_Time").text            
            TempOut = station.find('TEMP_OUT').text
            TempHi = station.find('TEMP_HI').text
            TempLow = station.find('TEMP_LOW').text
            Wind10Avg = station.find('WIND_SPEED').text
            WindHi = station.find('WIND_HI').text
            Rain = station.find("RAIN").text
            Rain_Rate = station.find("RAIN_RATE").text            
            SolarRadHi = station.find("SOLAR_RAD_HI").text
            SolarEnergy = station.find("SOLAR_ENERGY").text
            Cloud = station.find("CLOUDY").text


        return We_Date, We_Time, TempOut, TempHi, TempLow, Wind10Avg, WindHi, Rain, Rain_Rate, SolarRadHi, SolarEnergy, Cloud
    except:
        return "","","","","","","","","","",""

def getitemdate(ST, Field, Value, Interval):
    param = urllib.urlencode({
                 "ST":ST,
                 "FIELD":Field,
                 "VALUE":Value,
                 "INTERVAL":Interval
            })
    try:
         
        conn = httplib.HTTPConnection("www.eosweather.ca",80,timeout=5)
        conn.request("POST","/burst/burstdate.php?",param,{"Content-type":"application/x-www-form-urlencoded"})
        r1 =conn.getresponse()
        msg = r1.read()
        root = ET.fromstring(msg)

        for station in root.findall('Archive'):
            We_Date = station.find('WE_DATE').text
        return We_Date
    except:
        return ""     
    
def getsummary(ST, Interval):
    param = urllib.urlencode({
                 "ST":ST,
                 "INTERVAL":Interval
            })
    try:
         
        conn = httplib.HTTPConnection("www.eosweather.ca",80,timeout=5)
        conn.request("POST","/burst/burstsummary.php?",param,{"Content-type":"application/x-www-form-urlencoded"})
        r1 =conn.getresponse()
        msg = r1.read()
        root = ET.fromstring(msg)

        for station in root.findall('Interval'):
            WindSpeed = station.find('WINDSPEED').text
            WindHi = station.find('HIGHWIND').text
            BarMax = station.find('MAXBAR').text
            BarMin = station.find('MINBAR').text
            TempMin = station.find('LOWTEMP').text
            TempMax = station.find('MAXTEMP').text
            WindRun = station.find('WINDRUN').text
            Rain = station.find("RAIN").text

        return WindSpeed, WindHi, BarMax, BarMin, TempMin, TempMax, WindRun, Rain
    except:
        return ""  

def getalarms(ST, Interval):
    param = urllib.urlencode({
                 "ST":ST,
                 "INTERVAL":Interval
            })
    Alarms = []
    try:
         
        conn = httplib.HTTPConnection("www.eosweather.ca",80,timeout=5)
        conn.request("POST","/burst/burstalarms.php?",param,{"Content-type":"application/x-www-form-urlencoded"})
        r1 =conn.getresponse()
        msg = r1.read()
        root = ET.fromstring(msg)

        for station in root.findall('Alarm'):
            Alarms.append(station.find("MESSAGE").text + " @ " + station.find("AM_START").text)


        return Alarms
    except:
        return ""      
