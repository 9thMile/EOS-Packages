# -*- coding: utf-8 -*-
import httplib, urllib, socket
import fcntl
import struct
from array import *
from string import Template
import sys
import subprocess
import os
import ftplib
import re
import string
import MySQLdb as mdb
import eosutils as eosu
from datetime import date, datetime, time, timedelta, tzinfo

GET_IP_CMD = "hostname --all-ip-addresses"
SET_TIME = "hwclock --set "
timeout = 2
ftptimeout = 10


class SiteFTP:
    host = ""
    username = ""
    password = ""

    


def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True).decode('utf-8')


def settime(t):
    return run_cmd(SET_TIME + t) [:-1]
             
def get_my_ip():
    return run_cmd(GET_IP_CMD)[:-1]

def wait_for_ip():
    ip = ""
    while len(ip) <= 0:
        sleep(1)
        ip = get_my_ip()

def camupload(uname, pwd, filename):
    try:
        if is_connected() == True:
            
            if uname <> "":
                rp = "Login Attempt"
                ftp = ftplib.FTP("webcam.wunderground.com", uname, pwd,"", ftptimeout)
                ftp.set_pasv(True)
                rp = ftp.sendcmd("TYPE I")
                rp = ftp.sendcmd("PASV")
                fd = open(filename,"r")
                rp = ftp.storbinary("STOR image.jpg", fd)
                ftp.quit()
                
                return True, rp
            else:
                return False, "No file"
        else:
            return False, "No Connection"
    except:
        return False, rp

def burstupload( Station, sfile, filename):
    try:
        if is_connected() == True:
            sendfile = Station.Remote_ID + sfile
            if len(filename) >0:
                rp = "Login Attempt"
                
                ftp = ftplib.FTP(Station.Remote_Conn, Station.Burst_USN, Station.Burst_PWD,"", ftptimeout)
                ftp.set_pasv(True)
                rp = ftp.sendcmd("TYPE I")
                rp = ftp.sendcmd("PASV")
                fd = open(filename,"r")
                rp = ftp.storbinary("STOR " + sendfile, fd)
                ftp.quit()
                
                return True, rp
            else:
                return False, "No file"
        else:
            return False, "No connection"
    except:
        return False, rp    

def sendawekas(AOS, awekasDir):
    try:

        os.chdir(awekasDir)
        awekas = open("awekas_wl.htm",'w')

        awekas.write('AWEKAS_Template_start\n')
        awekas.write(str(AOS.t_avg) + '\n')
        awekas.write(str(AOS.h_avg) + '\n')
        awekas.write(str(AOS.p_avg) + '\n')
        awekas.write(str(AOS.r_dsum) + '\n')
        awekas.write(str(AOS.w_avg) + '\n')
        awekas.write(str(AOS.c_avg) + '\n')
        awekas.write(str(AOS.aw_time) + '\n')
        awekas.write(str(AOS.aw_date) + '\n') 
        awekas.write(AOS.p_trend + '\n')
        awekas.write('-\n')
        awekas.write('-\n')
        awekas.write('-\n')
        awekas.write('-\n')
        awekas.write('-\n')
        awekas.write('-\n')
        awekas.write('-\n')
        awekas.write(str(AOS.w_max) + '\n')
        awekas.write(str(AOS.sr_avg) + '\n')
        awekas.write(str(AOS.su_max) + '\n')
        awekas.write(str(AOS.r_max) + '\n')
        awekas.write('---\n')
        awekas.write('°C\n')
        awekas.write('%\n')
        awekas.write('km/hr\n')
        awekas.write('mb\n')
        awekas.write('mm\n')
        awekas.write('W/m²\n')
        awekas.write('mm/hr\n')
        awekas.write('index\n')
        awekas.write('Template_V1.5\n')
        awekas.close()
        return True

    except:
        return False

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0X8915,
        struct.pack('256s',ifname[:15])
        )[20:24])


    
def is_connected():
    try:
        host = socket.gethostbyname('www.google.com')
        s = socket.create_connection((host,80),2)
        s.close()
        return True
    except:
        return False
    
def sendpushover(App, User, Message, Level):
    ##Level 0=normal, 1=priority, 2=needs responce -1=quite -2=No notification        
    conn = httplib.HTTPSConnection("api.pushover.net:443",timeout=timeout + 4)
    conn.request("POST","/1/messages.json",
                 urllib.urlencode({
                     "token":App,
                     "user":User,
                     "priority":Level,
                     "message":Message
                }),{"Content-type":"application/x-www-form-urlencoded"})
    conn.getresponse()

def sendrelay(site, cmd, script, trigger):
    
    if len(site) > 0:

        try:

            conn = httplib.HTTPConnection(site,80,timeout=timeout)
            params = urllib.urlencode({
                             cmd:trigger
                        })

            conn.request("POST",script, params
                         ,{"Content-type":"application/x-www-form-urlencoded"})
            r1 = conn.getresponse()

            return True, r1.status, r1.reason

        except:
            return False, "", ""
    else:
        return False, "", ""

def resendremote(param, Site, Script):
    try:
        conn = httplib.HTTPConnection(Site,80,timeout=timeout + 2)
        conn.request("POST",Script,param,{"Content-type":"application/x-www-form-urlencoded"})
        r1 =conn.getresponse()
        return True, r1.status, r1.reason, param
    except Exception,e:
        return False,999, str(e), param        

def resendwunderground(parama):
    try:
        if parama.find("---") < 0:
            conn = httplib.HTTPConnection("weatherstation.wunderground.com",80,timeout=timeout + 2)
            conn.request("POST","/weatherstation/updateweatherstation.php?", parama
                         ,{"Content-type":"application/x-www-form-urlencoded"})
            r1 = conn.getresponse()

            return True, r1.status, r1.reason, parama
        else:
            return False, 900,"Data has invalid value ---", parama

    except Exception,e:
        return False, 999, str(e), ""    

def get_tide(tyear, tmonth, tday):
    conn = httplib.HTTPConnection("tbone.biol.sc.edu",80,timeout=timeout + 2)
    parama = urllib.urlencode({
                 "tplotdir":"vert",
                 "caltype":"ndp",
                 "type":"mrare",
                 "interval":"00:10",
                 "year":str(tyear),
                 "month":str(tmonth),
                 "day":str(tday),
                 "hour":"00",
                 "min":"00",
                 "glen":"1",
                 "units":"default",
                 "killsun":"1",
                 "cleanout":"1",
                 "tzone":"utc",
                 "ampm24":"24",
                 "site":"Westport, St. Mary Bay, Nova Scotia"
            })
    conn.request("POST","/tide/tideshow.cgi?", parama
                 ,{"Content-type":"application/x-www-form-urlencoded"})
    r1 = conn.getresponse()
    msg = r1.read()
    b = msg.find("<pre>") + 5
    c = msg.find("</pre>")
    msg = msg[b:c]
    ##print msg
    return msg

def sendwunderground(AOS, ID, PWD):
    
    if len(ID) > 0:

        try:

            conn = httplib.HTTPConnection("weatherstation.wunderground.com",80,timeout=timeout + 2)
            parama = urllib.urlencode({
                             "ID":ID,
                             "PASSWORD":PWD,
                             "dateutc":str(AOS.we_datetime),
                             "action":"updateraw"
                        })
            paramwind = ""
            paramtemp = ""
            paramrain = ""
            paramsun = ""
            paramok = False
            
            if AOS.w_avg <> "---":                
                paramwind = urllib.urlencode({
                                 "winddir":str(AOS.c_avg),
                                 "windspeedmph":str(eosu.convert.windspeed(eosu.Units.MPH,AOS.w_avg)),
                                 "windgustdir":str(AOS.c_avg),
                                 "windgustmph":str(eosu.convert.windspeed(eosu.Units.MPH,AOS.w_max))
                            })
            if AOS.t_avg <> "---":
                paramtemp = urllib.urlencode({
                                 "humidity":str(AOS.h_avg),
                                 "dewptf":str(eosu.convert.temp(eosu.Units.Fahrenheit, AOS.d_avg)),
                                 "baromin":str(eosu.convert.pressure(eosu.Units.Inches, AOS.p_avg)),
                                 "tempf":str(eosu.convert.temp(eosu.Units.Fahrenheit, AOS.t_avg))
                            })
            if AOS.r_hrsum <> "---":
                paramrain = urllib.urlencode({
                                 "rainin":str(eosu.convert.rain(eosu.Units.Inches, AOS.r_hrsum)),
                                 "dailyrainin":str(eosu.convert.rain(eosu.Units.Inches, AOS.r_dsum))
                            })
            if AOS.sr_avg <> "---":  
                paramsun = urllib.urlencode({
                                 "solarradiation":str(AOS.sr_avg),
                                 "UV":str(AOS.su_max)
                            })
            if len(paramwind) > 0:
                parama = parama + "&" + paramwind
            if len(paramtemp) > 0:
                parama = parama + "&" + paramtemp
            if len(paramrain) > 0:
                parama = parama + "&" + paramrain
            if len(paramsun) > 0:
                parama = parama + "&" + paramsun
            paramok = True
            #print parama
            if parama.find("---") < 0:
                conn.request("POST","/weatherstation/updateweatherstation.php?", parama
                             ,{"Content-type":"application/x-www-form-urlencoded"})
                r1 = conn.getresponse()
                msg = r1.read()
                #print msg
                if msg.find("sucess"):
                    return True, r1.status, r1.reason, parama                    
                else:
                    return False, 900, msg, parama
                    
            else:
                return False, 999,"Data has invalid value ---", parama

        except Exception,e:
            if paramok == True:
                return True, 500, str(e), parama
            else:
                return False, 999, str(e), ""
    else:
        return False, 999, "Nothing to send", ""

def sendpws(AOS, ID, PWD):

    if len(ID) > 0:

        try:

            conn = httplib.HTTPConnection("www.pwsweather.com",80,timeout=timeout)
            parama = urllib.urlencode({
                             "ID":ID,
                             "PASSWORD":PWD,
                             "dateutc":str(AOS.we_datetime)
                        })
            paramwind = ""
            paramtemp = ""
            paramrain = ""
            paramsun = ""
            paramok = False
            
            if AOS.w_avg <> "---":                
                paramwind = urllib.urlencode({
                                 "winddir":str(AOS.c_avg),
                                 "windspeedmph":str(eosu.convert.windspeed(eosu.Units.MPH,AOS.w_avg)),
                                 "windgustdir":str(AOS.c_avg),
                                 "windgustmph":str(eosu.convert.windspeed(eosu.Units.MPH,AOS.w_max))
                            })
            if AOS.t_avg <> "---":
                paramtemp = urllib.urlencode({
                                 "humidity":str(AOS.h_avg),
                                 "dewptf":str(eosu.convert.temp(eosu.Units.Fahrenheit, AOS.d_avg)),
                                 "baromin":str(eosu.convert.pressure(eosu.Units.Inches, AOS.p_avg)),
                                 "tempf":str(eosu.convert.temp(eosu.Units.Fahrenheit, AOS.t_avg))
                            })
            if AOS.r_hrsum <> "---":
                paramrain = urllib.urlencode({
                                 "rainin":str(eosu.convert.rain(eosu.Units.Inches, AOS.r_hrsum)),
                                 "dailyrainin":str(eosu.convert.rain(eosu.Units.Inches, AOS.r_dsum))
                            })
            if AOS.sr_avg <> "---":  
                paramsun = urllib.urlencode({
                                 "solarradiation":str(AOS.sr_avg),
                                 "UV":str(AOS.su_max)
                            })
            if len(paramwind) > 0:
                parama = parama + "&" + paramwind
            if len(paramtemp) > 0:
                parama = parama + "&" + paramtemp
            if len(paramrain) > 0:
                parama = parama + "&" + paramrain
            if len(paramsun) > 0:
                parama = parama + "&" + paramsun
            paramok = True
            #print parama
            if parama.find("---") < 0:
                conn.request("POST","/pwsupdate/pwsupdate.php?", parama
                             ,{"Content-type":"application/x-www-form-urlencoded"})
                r1 = conn.getresponse()
                msg = r1.read()
                #print msg
                if msg.find("sucess"):
                    return True, r1.status, r1.reason, parama                    
                else:
                    return False, 900, msg, parama
                    
            else:
                return False, 999,"Data has invalid value ---", parama

        except Exception,e:
            if paramok == True:
                return True, 500, str(e), parama
            else:
                return False, 999, str(e), ""
    else:
        return False, 999, "Nothing to send", ""

    
def sendwow(AOS, ID, PWD):

    if len(ID) > 0:

        try:

            conn = httplib.HTTPConnection("wow.metoffice.gov.uk",80,timeout=timeout)
            parama = urllib.urlencode({
                             "siteid":ID,
                             "siteAuthenticationKey":PWD,
                             "dateutc":str(AOS.we_datetime),
                             "softwaretype":"EOS Software 1.0"
                        })
            paramwind = ""
            paramtemp = ""
            paramrain = ""
            paramok = False
            
            if AOS.w_avg <> "---":                
                paramwind = urllib.urlencode({
                                 "winddir":str(AOS.c_avg),
                                 "windspeedmph":str(eosu.convert.windspeed(eosu.Units.MPH,AOS.w_avg)),
                                 "windgustdir":str(AOS.c_avg),
                                 "windgustmph":str(eosu.convert.windspeed(eosu.Units.MPH,AOS.w_max))
                            })
            if AOS.t_avg <> "---":
                paramtemp = urllib.urlencode({
                                 "humidity":str(AOS.h_avg),
                                 "dewptf":str(eosu.convert.temp(eosu.Units.Fahrenheit, AOS.d_avg)),
                                 "baromin":str(eosu.convert.pressure(eosu.Units.Inches, AOS.p_avg)),
                                 "tempf":str(eosu.convert.temp(eosu.Units.Fahrenheit, AOS.t_avg))
                            })
            if AOS.r_hrsum <> "---":
                paramrain = urllib.urlencode({
                                 "rainin":str(eosu.convert.rain(eosu.Units.Inches, AOS.r_hrsum)),
                                 "dailyrainin":str(eosu.convert.rain(eosu.Units.Inches, AOS.r_dsum))
                            })
            if len(paramwind) > 0:
                parama = parama + "&" + paramwind
            if len(paramtemp) > 0:
                parama = parama + "&" + paramtemp
            if len(paramrain) > 0:
                parama = parama + "&" + paramrain
            paramok = True
            #print parama
            if parama.find("---") < 0:
                conn.request("POST","/automaticreading?", parama
                             ,{"Content-type":"application/x-www-form-urlencoded"})
                r1 = conn.getresponse()
                msg = r1.read()
                #print msg
                if msg.find("sucess"):
                    return True, r1.status, r1.reason, parama                    
                else:
                    return False, 900, msg, parama
                    
            else:
                return False, 999,"Data has invalid value ---", parama

        except Exception,e:
            if paramok == True:
                return True, 500, str(e), parama
            else:
                return False, 999, str(e), ""
    else:
        return False, 999, "Nothing to send", ""    


def sendremote(AOS, ID, Site, Script):
    if len(ID) > 0:
        try: 
            conn = httplib.HTTPConnection(Site, timeout=timeout*10)
            param = urllib.urlencode({
                                "ID":ID,
                                "WE_DATE":str(AOS.we_date),
                                "WE_TIME":str(AOS.we_time),
                                "TEMP_OUT":str(AOS.t_avg),
                                "TEMP_HI":str(AOS.t_max),
                                "TEMP_LOW":str(AOS.t_min),
                                "HUM_OUT":str(AOS.h_avg),
                                "DEW_OUT":str(AOS.d_avg),
                                "WIND_SPEED":str(AOS.w_avg),
                                "WIND_DIR":str(AOS.w_rose),
                                "WIND_RUN":str(AOS.windrun),
                                "WIND_HI":str(AOS.g_max),
                                "WIND_CHILL":str(AOS.windchill),
                                "HEAT_OUT":str(AOS.heatout),
                                "THW":str(AOS.thw),
                                "THWS":str(AOS.thws),
                                "BAR":str(AOS.p_avg),
                                "RAIN":str(AOS.ts_sum),
                                "RAIN_RATE":str(AOS.r_avg),
                                "SOLAR_RAD":str(AOS.sr_avg),
                                "SOLAR_ENERGY":str(AOS.se_sum),
                                "SOLAR_RAD_HI":str(AOS.sh_max),
                                "SOLAR_UV":str(AOS.su_max),
                                "SOLAR_MAX":str(AOS.solarmax),
                                "CLOUDY":str(AOS.cloudy),
                                "HEAT_DD":str(AOS.heat_dd),
                                "COOL_DD":str(AOS.cool_dd),
                                "ARC_INT":str(AOS.we_Interval),
                                "LATITUDE":str(AOS.p_lat),
                                "LONGITUDE":str(AOS.p_long),
                                "COG":str(AOS.p_cog),
                                "SOG":str(AOS.p_sog),
                                "SOIL_TEMP":str(AOS.stemp),
                                "SOIL_MOISTURE":str(AOS.smoisture),
                                "TREND":str(AOS.trend),
                                "RISE":str(AOS.rise),
                                "TIDE":str(AOS.tide),
                                "DATUM":str(AOS.datum),
                                "B_TEMP":str(AOS.b_avg),
                                "VOLTS_B":str(AOS.v_battery),
                                "VOLTS_S":str(AOS.v_source),
                                "WE_DATE_TIME":AOS.we_datetime

                        })
            
            conn.request("POST",Script,param,{"Content-type":"application/x-www-form-urlencoded"})
            r1 =conn.getresponse()
            msg = r1.read()
##            print param
##            print msg
            if msg.find("sucess"):
                return True, r1.status, r1.reason, param                    
            else:
                return False, 900, msg, parama
        except Exception,e:
            return False,999, str(e), param
    else:
        return False, 999, "Nothing to send", ""

def sendBurst(bb, ID, Site, Script):
    wind = ''
    solar = ''
    rain = ''
    temp = ''
    board = ''
    pressure = ''
    tide = ''

    if len(ID) > 0:
        
        try:
            for item in bb:
                Type, Sentence = item.split(':')
                if Type == "WIND":
                    wind = Sentence
                if Type == "SOLAR":
                    solar = Sentence
                if Type == "RAIN":
                    rain = Sentence
                if Type == "TEMP":
                    temp = Sentence
                if Type == "BOARD":
                    board = Sentence
                if Type == "PRESSURE":
                    pressure = Sentence
                if Type == "TIDE":
                    tide = Sentence

            param = urllib.urlencode({
                                "ID":ID,
                                "TIDE":tide,
                                "SOLAR":solar,
                                "RAIN":rain,
                                "TEMP":temp,
                                "BOARD":board,
                                "WIND":wind,
                                "PRESSURE":pressure
                        })
                    
            conn = httplib.HTTPConnection(Site,80,timeout=timeout)
            conn.request("POST",Script,param,{"Content-type":"application/x-www-form-urlencoded"})
            r1 =conn.getresponse()
            msg = r1.read()
            #print param
            #print msg
            if msg.find("sucess"):
                return True, r1.status, r1.reason, param                    
            else:
                return False, 900, msg, parama
        except Exception,e:
            return False,999, str(e), param
    else:
        return False, 999, "Nothing to send", ""


def sendalarm(conn, ID, dend, Dur, Level, A_Key, U_Key):
    alarm = False
    ##Do Alarms
    ##  ID
    ##      1 = high wind for 4 hrs
    ##      2 = heat index for 4 hrs
    ##      3 = thw index for 4 hrs
    ##      4 = thws index for 4 hrs
    ##      5 = Solar UV for 1 hr (at solar count level)
    ##      6 = Rain Rate for 15 min (at rain count level)
    ##      7 = Presure Drop for 4 hrs 
    ##      8 = Freezing temps for 4 hrs
    ##      9 = Battery Volts for 4 hrs
    ##     10 = Depth for 4 hrs
    if Level <> "---":
        ta = float(Level)
        IDr = 0

        if ID == 1:
            #do high Wind
            triggers = eosu.getsetting(conn, "WIND_COUNT", 0)
            low = 40.0
            mid = 60.0
            hi = 90.0
            
            if isinstance(triggers,str):
                if triggers.find(','):
                    trigger = triggers.split(',')
                    low = float(trigger[0].split('=')[1])
                    mid = float(trigger[1].split('=')[1])
                    hi = float(trigger[2].split('=')[1])
                    Dur = float(trigger[3].split('=')[1])
                
            if ta >= low:
                e = "Hi Gusts : "
                IDr = ID
                if ta > mid:
                    e = "Strong Gusts : "
                    IDr = ID + 100
                    if ta > hi:
                        e = "Damaging Gusts :"
                        IDr = ID + 200
                e = e + str(ta) + " k/h"
                alarm = True
        elif ID == 2:
            #do Heat index
            
            if ta >= 28:
                e = "Heat Index HI : "
                IDr = ID
                if ta > 32:
                    e = "CAUTION HI Heat Index : "
                    IDr = ID + 100
                    if ta > 42:
                        e = "DANGEROUS Heat Index :"
                        IDr = ID + 200
                        if ta > 54:
                            e = "EXTREME DANGEROUS Heat Index : "
                            IDr = ID + 300

                e = e + str(ta) + " C"
                alarm = True
        elif ID == 3:
            #do thw index
            if ta >= 28:
                e = "THW Index Hi : "
                IDr = ID
                if ta > 32:
                    e = "CAUTION HI THW Index : "
                    IDr = ID + 100
                    if ta > 42:
                        e = "DANGEROUS THW Index :"
                        IDr = ID + 200
                        if ta > 54:
                            e = "EXTREME DANGEROUS THW Index : "
                            IDr = ID + 300

                e = e + str(ta) + " C"
                alarm = True
        elif ID == 4:
            #do thw index
            if ta >= 22:
                e = "THWS Index Hi : "
                IDr = ID
                if ta > 24:
                    e = "CAUTION HI THWS Index : "
                    IDr = ID + 100
                    if ta > 26:
                        e = "EXTREME DANGEROUS THWS Index :"
                        IDr = ID + 200
                e = e + str(ta) + " C"
                alarm = True
        elif ID == 5:
            #do Solar UV

            if ta >= 7:
                e = "UV index HI : "
                IDr = ID
                if ta >= 10:
                    e = "EXTREME UV Index : "
                    IDr = ID + 100
                e = e + str(ta)
                alarm = True
        elif ID == 6:
            #do Rain Rate
            triggers = eosu.getsetting(conn, "RAIN_COUNT", 0)
            low = 10.0
            mid = 20.0
            hi = 30.0
            
            if isinstance(triggers,str):
                if triggers.find(','):
                    trigger = triggers.split(',')
                    low = float(trigger[0].split('=')[1])
                    mid = float(trigger[1].split('=')[1])
                    hi = float(trigger[2].split('=')[1])
                    
                    Dur = float(trigger[3].split('=')[1])
  
            if ta >= low:
                e = "It is raining"
                Idr = ID
                if ta >= mid:
                    e = "Heavy Rain Fall Occuring"
                    IDr = ID + 100
                    if ta >= hi:
                        e = "Raining Cats and Dogs"
                        IDr = ID + 200
                alarm = True
        elif ID == 7:
            #do Presuure Drop
            e = "Pressure Trend Falling Fast"
            IDr = ID
            alarm = True
        elif ID == 8:
            #do temp alarms
            triggers = eosu.getsetting(conn, "TEMP_COUNT", 0)
            low = 0.0
            mid = 30.0
            hi = 35.0
            
            if isinstance(triggers,str):
                if triggers.find(','):
                    trigger = triggers.split(',')
                    low = float(trigger[0].split('=')[1])
                    mid = float(trigger[1].split('=')[1])
                    hi = float(trigger[2].split('=')[1])
                    Dur = float(trigger[3].split('=')[1])
            if ta <=low:
                e = "Freezing Temperatures: " + str(ta) + " C"
                IDr = ID
                if ta >= mid:
                    e = "High Temperatures" + str(ta) + " C"
                    IDr = ID + 100
                    if ta >= hi:
                        e = "Extreme Temperatures" + str(ta) + " C"
                        IDr = ID + 200
                alarm = True
        elif ID == 9:
            e = "Low Battery: " + str(ta) + " Volts"
            IDr = ID
            alarm = True
        elif ID == 10:
            #do depth alarms
            triggers = eosu.getsetting(conn, "DEPTH_COUNT", 0)
            low = 0.0
            hi = 35.0
            
            if isinstance(triggers,str):
                if triggers.find(','):
                    trigger = triggers.split(',')
                    low = float(trigger[0].split('=')[1])
                    hi = float(trigger[1].split('=')[1])
                    Dur = float(trigger[2].split('=')[1])
            if ta <=low:
                e = "Depth below: " + str(ta) + " cm"
                IDr = ID
            if ta >= hi:
                e = "Depth aboves" + str(ta) + " cm"
                IDr = ID + 200
            alarm = True

    if alarm == True and IDr != 0:
        with conn:
            try:
                
                cur = conn.cursor()
                cur.execute("Select * from ALARM where AM_TYPE = " + str(IDr) + " and AM_END > '" + dend.isoformat() + "'")
                row = cur.fetchone()
                if row is None:
                    aend = dend + timedelta(hours= Dur)
                    psent = 0
                    if len(U_Key) > 0:
                        sendpushover(A_Key, U_Key, "ALARM:" + str(e), 0)
                        psent = 1
                    a = "INSERT INTO ALARM (AM_START, AM_END, AM_TYPE, MESSAGE, SENT) values('" + dend.isoformat() + "','" + aend.isoformat() + "'," + str(IDr) + ",'" + e + "'," + str(psent) +")"
                    cur.execute(a)
                    Rem_Id = eosu.getsetting(conn,"REM_ID",0)
                    if len(Rem_Id) > 1:                   
                       responce, status, reason, message = remotealert(conn, Rem_Id, dend.isoformat(), aend.isoformat(), str(ID), e, str(psent))  
                    return True
                else:
                    return False
            except:
                return False
    else:
        return False
    
def sendalert(conn, ID, dend, Dur, Level, Message, A_Key, U_Key):
        with conn:
            cur = conn.cursor()
            cur.execute("Select * from ALARM where AM_TYPE = " + str(ID) + " and AM_END > '" + dend.isoformat() + "'")
            row = cur.fetchone()
            if row is None:
                aend = dend + timedelta(hours= Dur)
                psent = 0
                if len(U_Key) > 0:
                    sendpushover(A_Key, U_Key, "ALERT:" + str(Message), Level)
                    psent = 1
                a = "INSERT INTO ALARM (AM_START, AM_END, AM_TYPE, MESSAGE, SENT) values('" + dend.isoformat() + "','" + aend.isoformat() + "'," + str(ID) + ",'" + Message + "'," + str(psent) +")"
                cur.execute(a)
                Rem_Id = eosu.getsetting(conn,"REM_ID",0)
                if len(Rem_Id) > 1:                   
                   responce, status, reason, message = remotealert(conn, Rem_Id, dend.isoformat(), aend.isoformat(), str(ID), Message, str(psent))

def remotealert(db, REMID, dend, aend, ID, msg, psent):
    if len(ID) > 0:
        if is_connected() == True:
            
            try: 
                conn = httplib.HTTPConnection(eosu.getsetting(db, "REM_CONN", 0),80,timeout=timeout + 4)
                param = urllib.urlencode({
                                    "ST":REMID,
                                    "AM_START":dend,
                                    "AM_END":aend,
                                    "AM_TYPE":ID,
                                    "MESSAGE":msg,
                                    "SENT":psent

                            })
                
                conn.request("POST","/remotemsg.php?",param,{"Content-type":"application/x-www-form-urlencoded"})
                r1 =conn.getresponse()
                msg = r1.read()
                #print param
                #print msg
                if msg.find("sucess"):
                    return True, r1.status, r1.reason, param                    
                else:
                    return False, 900, msg, parama
            except Exception,e:
                return False,999, str(e), param
        else:
            return False,999,"No Connection", ""
    else:
        return False, 999, "Nothing to send", ""    
                    
def remotealmanac(db, ID, we_date, almanac):
    if len(ID) > 0:
        if  is_connected() == True:
            try: 
                conn = httplib.HTTPConnection(eosu.getsetting(db, "REM_CONN", 0),80,timeout=timeout + 4)
                param = urllib.urlencode({
                                    "ST":ID,
                                    "we_date":we_date,
                                    "sunrise":almanac.sunrise,
                                    "sunset":almanac.sunset,
                                    "solarmax":str(almanac.solar_max),
                                    "solaralt":str(almanac.solar_alt),
                                    "daylength":str(almanac.daylength),
                                    "moonindex":str(almanac.moon_index),
                                    "moonphase":str(almanac.moon_phase), 
                                    "moonfullness":str(almanac.moon_fullness)

                            })
                
                conn.request("POST","/remotealmanac.php?",param,{"Content-type":"application/x-www-form-urlencoded"})
                r1 =conn.getresponse()
                msg = r1.read()
                #print param
                #print msg
            except:
                pass
