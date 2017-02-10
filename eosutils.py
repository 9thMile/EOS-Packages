#
#    Copyright (c) 2016 Gary Fisher <gary@eosweather.ca>
#
#    See the file LICENSE.txt for your full rights.
#

# Python Imports
import array
from math import *
from decimal import *
import calendar
from datetime import date, datetime, timedelta
from array import *
import os
import logging
import time as ttime
import ctypes
import ctypes.util
import re
import MySQLdb as mdb


#===============================================================================
#                    Class for UoM
#===============================================================================
class Units:
    Metric = 0
    Imperial = 1
    Celcius = 0
    Fahrenheit = 1
    KPH = 1
    MPS = 2
    MPH = 3
    Knots = 4
    CMeter = 0
    Inches = 1
    mbars = 0
    Feet = 3
    Mile = 4
    NMile = 5
    
    
#===============================================================================
#                    Class Logging
#===============================================================================

class log:

    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}
 
 ## clear all logs on start up   
    @staticmethod
    def clear(logname):
        try:
            os.remove(logname)        
            os.remove(logname + ".1")
            os.remove(logname + ".2")
            os.remove(logname + ".3")
            os.remove(logname + ".4")
            os.remove(logname + ".5")
            os.remove(logname + ".6")
            os.remove(logname + ".7")
            os.remove(logname + ".8")
            os.remove(logname + ".9")
            os.remove(logname + ".10")
        except:
            pass

#===============================================================================
#                    Class for Pressure
#===============================================================================
class pressure:
    @staticmethod
    def trend(level):
        if level == [1,6]:
            return 'Steady'
        if level == 7:
            return 'Rising-Slow'
        if level == 8:
            return 'Rising'
        if level >= 9:
            return 'Rising-Rapidly'
        if level == 2:
            return 'Falling-Slow'
        if level == 3:
            return 'Falling'
        if level == 4:
            return 'Falling-Rapidly'
        if level == 5:
            return 'Falling Very Fast'
        if level <= 0:
            return '---'
    @staticmethod
    def StationPressure(AP,Elv):
        #Comes in with mbars and meters
        AIn = convert.pressure(Units.Inches,AP)
        #Station Pressure = Ps = Altimeter in Inches * ((288 - 0.0065 * Elevation in MEters)/288)^5.2561
        Ps = AIn * pow((288 - .0065 * Elv)/288,5.2561)
        #Exit in mbars
        return convert.pressure(Units.mbars,Ps)

    @staticmethod
    def Altimeter(Sp,Elv):
        As = (Sp -.3) * pow((1 + ((pow(1013.25,0.190284) * .0065)/288) * (Elv/pow((Sp -.3),.190284))),(1/.190287))
        #print As
        return As

#===============================================================================
#                    Class for NMEA
#===============================================================================
class nmea:
    @staticmethod
    def GGA(conn, Station, EOS):
        cur = conn.cursor(mdb.cursors.DictCursor)
        try:
            cur.execute("Select * from NMEA where SENTENCE LIKE '%GGA' order by WE_Date_Time desc limit 0,1")
            row = cur.fetchone()
            if row is not None:
                lat = float(row['B2'])
                if row['B3'] == 'S':
                    lat = lat * -1
                lon = float(row['B4'])
                if row['B5'] == 'W':
                    lon = lon * -1
                Station.Latitude = geo.get_degree(lat)                            
                Station.Longitude = geo.get_degree(lon)
                EOS.LAT = geo.get_degree(lat)
                EOS.LONG = geo.get_degree(lon)
                cur.close()
                return True
            else:
                cur.close()
                return False 
        except:
            cur.close()
            return False
    @staticmethod    
    def RMC(conn, Station, EOS):
        cur = conn.cursor(mdb.cursors.DictCursor)
        try:
            cur.execute("Select * from NMEA where SENTENCE LIKE '%RMC' order by WE_Date_Time desc limit 0,1")
            row = cur.fetchone()
            if row is not None:
                lat = float(row['B3'])
                if row['B4'] == 'S':
                    lat = lat * -1
                lon = float(row['B5'])
                if row['B6'] == 'W':
                    lon = lon * -1
                Station.Latitude = geo.get_degree(lat)
                Station.Longitude = geo.get_degree(lon)
                EOS.LAT = geo.get_degree(lat)
                EOS.LONG = geo.get_degree(lon)
                ##we need to keep speed in KPH, comes in with knots
                EOS.SOG = convert.boatspeed(Units.KPH,float(row['B7']))
                if EOS.SOG > .5:
                    EOS.COG = float(row['B8'])
                else:
                    EOS.SOG = 0
                    EOS.COG = Station.Compass
                cur.close()
                return True
            else:
                cur.close()
                return False
            cur.close()
        except:
            cur.close()
            return False
    @staticmethod    
    def HDT(conn, Station):

        cur = conn.cursor(mdb.cursors.DictCursor)
        try:
            cur.execute("Select * from NMEA where SENTENCE LIKE '%HDT' order by WE_Date_Time desc limit 0,1")
            row = cur.fetchone()
            if row is not None:
                Station.Compass = float(row['B1'])
                cur.close()
                return True
            else:
                cur.close()
                return False
            cur.close()
        except:
            cur.close()
            return False
    @staticmethod    
    def HDM(conn, Station):
        cur = conn.cursor(mdb.cursors.DictCursor)
        try:
            cur.execute("Select * from NMEA where SENTENCE LIKE '%HDM' order by WE_Date_Time desc limit 0,1")
            row = cur.fetchone()
            if row is not None:
                Station.Magnetic = float(row['B1'])
                cur.close()
                return True
            else:
                cur.close()
                return False
            cur.close()
        except:
            cur.close()
            return False
        
    @staticmethod
    def split_sentence(ADR, Sentence):
        ADR.Count = Sentence.count(",")
        if ADR.Count <21:
            if ADR.Count == 20:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12, ADR.B13, ADR.B14, ADR.B15, ADR.B16, ADR.B17, ADR.B18, ADR.B19, ADR.B20 = Sentence.strip().split(',')[1:]
                return True        
            if ADR.Count == 19:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12, ADR.B13, ADR.B14, ADR.B15, ADR.B16, ADR.B17, ADR.B18, ADR.B19 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 18:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12, ADR.B13, ADR.B14, ADR.B15, ADR.B16, ADR.B17, ADR.B18 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 17:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12, ADR.B13, ADR.B14, ADR.B15, ADR.B16, ADR.B17 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 16:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12, ADR.B13, ADR.B14, ADR.B15, ADR.B16 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 15:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12, ADR.B13, ADR.B14, ADR.B15 = Sentence.strip().split(',')[1:]
                return True 
            if ADR.Count == 14:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12, ADR.B13, ADR.B14  = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 13:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12, ADR.B13  = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 12:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11, ADR.B12  = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 11:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10, ADR.B11 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 10:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9, ADR.B10 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 9:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8, ADR.B9 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 8:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7, ADR.B8 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 7:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6,ADR.B7 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 6:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5,ADR.B6 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 5:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4, ADR.B5 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 4:
                ADR.B1, ADR.B2, ADR.B3, ADR.B4 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 3:
                ADR.B1, ADR.B2, ADR.B3 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 2:
                ADR.B1, ADR.B2 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 1:
                ADR.B1 = Sentence.strip().split(',')[1:]
                return True
            if ADR.Count == 0:
                return False
        else:
            return False

    @staticmethod
    def get_sentence(ADR, line, CheckSum):
        a = "INSERT INTO NMEA (WE_Date_Time, SENTENCE, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, CSUM) VALUES('" 
        u = datetime.utcnow()
        a = a +  u.strftime("%Y-%m-%d %H:%M:%S") + "','" + line[:6]
        a = a + "','" + ADR.B1 +  \
            "','" + ADR.B2 +  \
            "','" + ADR.B3 +  \
            "','" + ADR.B4 +  \
            "','" + ADR.B5 +  \
            "','" + ADR.B6 +  \
            "','" + ADR.B7 +  \
            "','" + ADR.B8 +  \
            "','" + ADR.B9 +  \
            "','" + ADR.B10 +  \
            "','" + ADR.B11 +  \
            "','" + ADR.B12 +  \
            "','" + ADR.B13 +  \
            "','" + ADR.B14 +  \
            "','" + ADR.B15 +  \
            "','" + ADR.B16 +  \
            "','" + ADR.B17 +  \
            "','" + ADR.B18 +  \
            "','" + ADR.B19 +  \
            "','" + ADR.B20 +  \
            "','" + CheckSum + "')"
        return a

    @staticmethod
    def put_sentence(row, e, c):
        a = row['SENTENCE'] + "," + row['B1']
        if c > 1:
            a = a + "," + row['B2']
        if c > 2:
            a = a + "," + row['B3']
        if c > 3:
            a = a + "," + row['B4']
        if c > 4:
            a = a + "," + row['B5']
        if c > 5:
            a = a + "," + row['B6']
        if c > 6:
            a = a + "," + row['B7']
        if c > 7:
            a = a + "," + row['B8']
        if c > 8:
            a = a + "," + row['B9']
        if c > 9:
            a = a + "," + row['B10']
        if c > 10:
            a = a + "," + row['B11']
        if c > 11:
            a = a + "," + row['B12']
        if c > 12:
            a = a + "," + row['B13']
        if c > 13:
            a = a + "," + row['B14']
        if c > 14:
            a = a + "," + row['B15']
        if c > 15:
            a = a + "," + row['B16']
        if c > 16:
            a = a + "," + row['B17']
        if c > 17:
            a = a + "," + row['B18']
        if c > 18:
            a = a + "," + row['B19']
        if c > 19:
            a = a + "," + row['B20']
        a  = a + ',' + e

        return a
    
    @staticmethod
    def checksumnmea(ADR, sentence):
        cksum = sentence[sentence.find("*") + 1:sentence.find("*") + 3]

        chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$") +1:sentence.find("*")])
        csum = 0
        for c in chksumdata:
            csum ^= ord(c)

        t = str(hex(csum))
        t = t.upper()[2:4]

        if t == cksum:
            ADR.B1 = ''
            ADR.B2 = ''
            ADR.B3 = ''
            ADR.B4 = ''
            ADR.B5 = ''
            ADR.B6 = ''
            ADR.B7 = ''
            ADR.B8 = ''
            ADR.B9 = ''
            ADR.B10 = ''
            ADR.B11 = ''
            ADR.B12 = ''
            ADR.B13 = ''
            ADR.B14 = ''
            ADR.B15 = ''
            ADR.B16 = ''
            ADR.B17 = ''
            ADR.B18 = ''
            ADR.B19 = ''
            ADR.B20 = ''
            return True
        return False


#===============================================================================
#                    Class for Location (geo)
#===============================================================================
class geo:
    @staticmethod
    def get_degree(L):
        d = int(L/100)
        m = int(((L/100) - d) * 100)
        s = float(modf(L)[1] / 100)
        lat = float(d) + (float(m)/60)
        lat = lat + (s/3600)
        return lat
    
    @staticmethod
    def get_longitude(L):
        d = int(L/100)
        m = int(((L/100) - d) * 100)
        s = float(modf(L)[1] / 100)
        lon = float(d) + (float(m)/60)
        lon = lon + (s/3600)
        NS = " "
        if lon < 0:
            NS = "W"
        else:
            NS = "E"
        L = abs(lon)   
        Deg = int(lon)
        Min = (L - int(lon))*60
        Sec = (Min - int(Min))*60
        Min = int(Min)
        Sec = int(Sec)

        return str(Deg) + " " + str(Min) + " " + str(Sec) + " " + NS
    
    @staticmethod
    def get_latitude(L):
        d = int(L/100)
        m = int(((L/100) - d) * 100)
        s = float(modf(L)[1] / 100)
        lat = float(d) + (float(m)/60)
        lat = lat + (s/3600)
        NS = " "
        if lat > 0:
            NS = "N"
        else:
            NS = "S"
        L = abs(lat)
        Deg = int(lat)
        Min = (L - int(lat))*60
        Sec = (Min - int(Min))*60
        Min = int(Min)
        Sec = int(Sec)

        return str(Deg) + " " + str(Min) + " " + str(Sec) + " " + NS

#===============================================================================
#                    Class for WIND
#===============================================================================  
class wind:
    @staticmethod
    def windrose(Dir):
        if Dir in range(0,11):
            return "N"
        elif Dir in range(350, 360):
            return "N"
        elif Dir in range(12, 34):
            return "NNE"
        elif Dir in range(34, 57):
            return "NE"
        elif Dir in range(57, 80):
            return "ENE"
        elif Dir in range(80, 102):
            return "E"
        elif Dir in range(102, 125):
            return "ESE"
        elif Dir in range(125, 148):
            return "SE"
        elif Dir in range(148, 170):
            return "SSE"
        elif Dir in range(170,192):
            return "S"
        elif Dir in range(192, 215):
            return "SSW"
        elif Dir in range(215, 238):
            return "SW"
        elif Dir in range(238, 260):
            return "WSW"
        elif Dir in range(260, 283):
            return "W"
        elif Dir in range(283, 306):
            return "WNW"
        elif Dir in range(306, 328):
            return "NW"
        elif Dir in range(328, 350):
            return "NNW"
        else:
            return "---"

    @staticmethod
    def winddir(Rose):
        if Rose == "N":
            return 0
        elif Rose == "NNE":
            return 20
        elif Rose == "NE":
            return 45
        elif Rose == "ENE":
            return 70
        elif Rose == "E":
            return 90
        elif Rose == "ESE":
            return 110
        elif Rose == "SE":
            return 135
        elif Rose == "SSE":
            return 160
        elif Rose == "S":
            return 180
        elif Rose == "SSW":
            return 205
        elif Rose == "SW":
            return 225
        elif Rose == "WSW":
            return 250
        elif Rose == "W":
            return 270
        elif Rose == "WNW":
            return 295
        elif Rose == "NW":
            return 315
        elif Rose == "NNW":
            return 340
        else:
            return 0

    @staticmethod
    def truewind(AW_Speed, Degree, Compass, SOG):
        HD = float(Compass)
        ##HD = 345
        if HD == 0:
            C = Degree
        else:
            if Degree > 180:
                C = 360 - Degree
                Y = 90 - C
                a = AW_Speed * (cos(Y))
                bb = AW_Speed * (sin(Y))
                b = bb - SOG
                D = round(atan(b/a),0)
                C = HD - (C + D)

            else:
                C = Degree
                Y = 90 - C
                a = AW_Speed * (cos(Y))
                bb = AW_Speed * (sin(Y))
                b = bb - SOG
                D = round(atan(b/a),0)
                C = HD + (C + D)
                
        if C > 360:
            C = 360 - C
        elif C < 0:
            C = C + 360
            if C < 0:
                C = C + 360
        return C
        
    @staticmethod
    def truewindspeed(AW_Speed, Degree, SOG):
        if SOG < 1:
            return AW_Speed
        else:
            if Degree > 180:
                C = 360 - Degree
                Y = 90 - C
                a = AW_Speed * (cos(Y))
                bb = AW_Speed * (sin(Y))
                b = bb - SOG
                FC = round(pow(((a*a) + (b*b)),.5),1)

                return FC
            
            else:
                C = Degree
                Y = 90 - C
                a = AW_Speed * (cos(Y))
                bb = AW_Speed * (sin(Y))
                b = bb - SOG
                FC = round(pow(((a*a) + (b*b)),.5),1)

                return FC

    @staticmethod
    def add_dir(Dir, Var):
        mag = Dir + Var
        if mag > 360:
            mag = mag - 360
        elif mag < 0:
            mag = mag + 360

        return mag



#===============================================================================
#                    Class for Convertions
#===============================================================================          
class convert:
    @staticmethod
    def pressure(UoM, S):
        ##Comes in with mBars or inches
        if S != "---":

            if UoM == Units.Inches:
                ##requests mbars -> inches
                return round(float(S) * .0295337, 4)
            else:
                ##requests inches -> mbars
                return round(float(S) * 33.86, 1)
        else:
            return 0

    @staticmethod
    def rain(UoM, S):
        ## Comes in with millimeters or inches
        if S != "---":
            if UoM == Units.Inches:
                ##requests mm -> inches
                return round(float(S) * .1 * .393701, 4)
            else:
                ##request inches -> mm
                return round(float(S) * 10 * 2.54, 1)
        else:
            return 0

    @staticmethod
    def temp(UoM,S):
        if S != "---":
            if UoM == 0: # We want Celcius
                return S
            else: #we want Fahrenheit
                return round(((float(S) * 9/5)+ 32), 1)
        else:
            return 0

    @staticmethod
    def windspeed(UoM,S):
        ## 1 = KPH 2 = M/S(MPS)  3 = MPH  4 = Knots
        ## Incoming is either m/s or mph depending on station UoM
        if S != "---":
            if UoM == Units.KPH: # We want Kilometers per hour
                return S      
            elif UoM == Units.MPS: # we want meters per second
                return round((float(S) * .27777), 1)      
            elif UoM == Units.MPH: # we want miles per hour
                return round((float(S) * .621371), 2)     
            elif UoM == Units.Knots: #we want Knots

                return round((float(S) * .539957), 2)
            else: #We don't know --- return S
                S
        else:
            return 0

    @staticmethod
    def boatspeed(UoM,S):
        ##From GPS we expect Knotes and need to convert to Kph
        if S != "---":
            if UoM == Units.KPH:
                return round((float(S)* 1.852),2)
            else:
                return S
        else:
                    return 0
    
    @staticmethod    
    def distance(UoM,S):
        if S != "---":
            if UoM == Units.CMeter: # Centimeteres / inches input
                return S
            elif UoM == Units.Inches: # Centimeters / Inches input
                return round((float(S) * .393701),3)
            elif UoM == Units.Feet:  #Meters / Inches input
                return round((float(S) * 2.54 / 12), 2)
            elif UoM == Units.Mile:    # Kilometers/Miles input
                return round((float(S) * 0.621371), 2)
            elif UoM == Units.NMile:   # Kilometers/ Miles input
                return round((float(S) * 0.539957), 2)
            else:
                return S                      
        else:
            return 0

#===============================================================================
#                    Class for Station Reads
#===============================================================================  
class station:

    @staticmethod
    def EOS0(row, EOS):
##Read Time Details (No longer USED)
        Sent = False
        if row is not None:
            EOS.Hours = float(row["B1"])
            EOS.Minutes = float(row["B2"])
            EOS.Seconds = float(row["B3"])
            EOS.Day = float(row["B4"])
            EOS.Month = float(row["B5"])
            EOS.Year = float(row["B6"])
            Sent = True
        return Sent

    @staticmethod
    def EOS1(row, EOS):
##Read Wind Details
        Sent = False
        if row is not None:
            w = round(float(row["B1"]) + (float(row["B2"]) /10),1)
            if w > 50:
                if w > EOS.WindSpeed * 2:
                    EOS.WindSpeed = EOS.WindSpeed * 1.1
                else:
                    EOS.WindSpeed = w
            else:
                EOS.WindSpeed = w
            w = round(float(row["B3"]) + (float(row["B4"]) /10),1)
            if w > 50:
                if w > EOS.High_Gust * 2:
                    EOS.High_Gust = EOS.High_Gust * 1.1
                else:
                    EOS.High_Gust = w
            else:
                EOS.High_Gust = w 
            EOS.WindSpeed_Avg = round(float(row["B5"]) + (float(row["B6"]) /10),1)
            EOS.Wind_UoM = float(row["B7"])
            EOS.WindDirection = float(row["B8"] + row["B9"])
            if EOS.WindSpeed > 0:
                EOS.WindRose = wind.windrose(EOS.WindDirection)
            else:
                EOS.WindRose = "---"
            Sent = True

        return Sent

    @staticmethod    
    def EOS2(row, EOS):
##Read Pressure        
        Sent = False
        if row is not None:
            EOS.Pressure_Abs = float(int(row["B2"]) + (256 * int(row["B1"])))/10
            EOS.Altitude = float(int(row["B3"]) + (256 * int(row["B4"])))
            EOS.Pressure_Rel = float(int(row["B6"]) + (256 * int(row["B5"])))/10
            EOS.Pressure_Trend = float(int(row["B7"]))
            ##Deterime if preassure is rising then add 5
            if float(int(row["B8"]))== 1 and float(int(row["B7"])) > 0:
                EOS.Pressure_Trend = float(int(row["B7"]))+ 5

            Sent = True
        
        return Sent

    @staticmethod
    def EOS3(row, EOS):
##Read Temp
        Sent = False
        if row is not None:
            EOS.Temp_Outside = round(float(row["B1"]) + (float(row["B2"])/ 10),1)
            EOS.Temp_DewPoint = round(float(row["B3"]) + (float(row["B4"])/ 10),1)
            EOS.Humidity_Rel = float(row["B5"])
            if float(row["B6"]) == 1:
                EOS.Temp_Outside = EOS.Temp_Outside * -1
            if float(row["B7"]) == 1:
                EOS.Temp_DewPoint = EOS.Temp_DewPoint * -1
            EOS.Fan = float(row["B8"])
            EOS.Temp_Trend = float(row["B9"])
            EOS.Temp_UoM = float(row["B10"])
            Sent = True

        return Sent

 
    @staticmethod
    def EOS4(row, EOS):
##Read Rain
        Sent = False
        if row is not None:
            EOS.Rain_Rate = round(float(row["B1"]) + (float(row["B2"])/10),1)
            EOS.Rain_FallToday = round(float(row["B3"]) + (float(row["B4"])/10),1)
            EOS.Rain_FallYesterday = round(float(row["B5"]) + (float(row["B6"])/10),1)
            EOS.Rain_Tips = round(float(row["B7"]) + (float(row["B8"])* 100),0)
            Sent = True
  
        return Sent

    @staticmethod
    def EOS5(row, EOS, factor):
##Read Sun Data
        Sent = False
        if row is not None:
            EOS.Solar_Lum = float(int(row["B2"]) + (256 * int(row["B1"])))
            EOS.Solar_UV = float(row["B3"])
            EOS.Solar_Rad = float(int(row["B5"]) + (256 * int(row["B4"])))
            if EOS.Solar_Rad == 0:
                EOS.Solar_Rad = round(EOS.Solar_Lum * .0079,3)
            else:
                EOS.Solar_Lum = round(EOS.Solar_Rad * 126.58,0)
            EOS.Solar_RadHi = 0
            EOS.Solar_Energy = round(EOS.Solar_Rad / 50,3)
            EOS.Solar_Rad = round(EOS.Solar_Rad * factor,0)
            EOS.Solar_Lum = round(EOS.Solar_Lum * factor,0)
            EOS.Solar_Energy = round(EOS.Solar_Rad /50,3)
            Sent = True

        return Sent
    @staticmethod
    def EOS6(row, EOS):
##Station Details
        Sent = False
        if row is not None:
            EOS.B_Volts = round(float(row["B1"]) + (float(row["B2"])/ 10),1)
            EOS.S_Volts = round(float(row["B3"]) + (float(row["B4"])/ 10),1)
            EOS.C_Temp = float(row["B5"])

            if float(row["B6"]) == 1:
                if EOS.C_Temp > 0:
                    EOS.C_Temp = (256 - EOS.C_Temp) * -1
                
            EOS.Error = row["B7"]
            EOS.Error2 = row["B8"]
            EOS.Version = float(row["B10"])/100 + (float(row["B9"]))

            Sent = True
        return Sent

    @staticmethod
    def EOS7(row, EOS):
##Read SOIL data
        Sent = False
        if row is not None:
            EOS.Soil_ID = round(float(row["B1"]))
            EOS.Soil_Moisture = round(float(row["B2"]))
            EOS.Soil_Temp = float(row["B3"])

            if float(row["B4"]) == 1:
                EOS.Soil_Temp = EOS.Soil_Temp * -1

            Sent = True
        return Sent

    @staticmethod
    def EOS8(row, EOS):
##Read Depth data
        Sent = False
        if row is not None:
            EOS.Depth_ID = round(float(row["B1"]))
            EOS.Depth = round(float(int(row["B3"]) + (256 * int(row["B2"]))),1)
            EOS.Depth_Trend = round(float(row["B4"]))
            ##print EOS.Depth

            Sent = True
  
        return Sent

   
    
    @staticmethod    
    def update(Station, db):

        Station.doUpdate = False
        try: #0 = String, 1 = Int, 2 = Float, 3 = Datetime
            if Station.GPS_Active == False:
                Station.Latitude  = getsetting(db, "LATITUDE", 0)
                Station.Longitude  = getsetting(db, "LONGITUDE", 0)
            Station.Name  = getsetting(db, "NAME", 0)
            Station.Broker_Address = getsetting(db, "BROKER_ADDRESS", 0)
            Station.Broker_Client = getsetting(db, "BROKER_CLIENT", 0)
            Station.Broker_Port = getsetting(db, "BROKER_PORT", 0)
            Station.Broker_USN = getsetting(db, "BROKER_USN", 0)
            Station.Broker_PWD = getsetting(db, "BROKER_PWD", 0)
            Station.App_Token  = getsetting(db, "APP_TOKEN", 0)
            Station.User_Key  = getsetting(db, "USER_KEY", 0)
            Station.version = getsetting(db,"EOS_VERSION",0)
            
            
            c_test = Station.Wind_Count
            Station.Wind_Count  = getsetting(db, "WIND_COUNT", 1)
            if c_test <> Station.Wind_Count:
                Station.doUpdate = True

            c_test = Station.Rain_Count
            Station.Rain_Count  = getsetting(db, "RAIN_COUNT", 1)
            if c_test <> Station.Rain_Count:
                Station.doUpdate = True

            c_test = Station.Pressure_Count
            Station.Pressure_Count  = getsetting(db, "PRESSURE_COUNT", 1)
            if c_test <> Station.Pressure_Count:
                Station.doUpdate = True

            c_test = Station.Temp_Count
            Station.Temp_Count  = getsetting(db, "TEMP_COUNT", 1)
            if c_test <> Station.Temp_Count:
                Station.doUpdate = True

            c_test = Station.Solar_Count
            Station.Solar_Count  = getsetting(db, "SOLAR_COUNT", 1)
            if c_test <> Station.Solar_Count:
                Station.doUpdate = True
            if Station.Solar_Count > 0 and getsetting(db,"HAS_FAN",1) == 1:
                Station.Has_Fan = True
            else:
                Station.Has_Fan = False

            Station.Sun_Trigger  = getsetting(db, "SUN_TRIGGER", 1)
            Station.Solar_Factor  = getsetting(db, "SOLAR_FACTOR", 2)

            Station.Location_Count  = getsetting(db, "LOCATION_COUNT", 1)
            
            c_test = Station.Board_Count
            Station.Board_Count  = getsetting(db, "BOARD_COUNT", 1)
            if c_test <> Station.Board_Count:
                Station.doUpdate = True

            c_test = Station.Soil_Count
            Station.Soil_Count  = getsetting(db, "SOIL_COUNT", 1)
            if c_test <> Station.Soil_Count:
                Station.doUpdate = True

            c_test = Station.Depth_Count
            Station.Depth_Count  = getsetting(db, "DEPTH_COUNT", 1)
            if c_test <> Station.Depth_Count:
                Station.doUpdate = True
            Station.Datum = getsetting(db,"DEPTH_COUNT",2)
            Station.Depth_Adjust = getsetting(db,"ALARM_DEPTH",2)
            HHWL = getsetting(db,"DEPTH_HHWL", 1)
            
            Station.Alarm_Volts  = getsetting(db, "ALARM_VOLTS", 1)

            if getsetting(db,"ALARM_TEMP",1) == 1:
                Station.Alarm_Temp = True
            else:
                Station.Alarm_Temp = False
            if getsetting(db,"ALARM_WIND",1) == 1:
                Station.Alarm_Wind = True
            else:
                Station.Alarm_Wind = False
            if getsetting(db,"ALARM_PRESSURE",1) == 1:
                Station.Alarm_Pressure = True
            else:
                Station.Alarm_Pressure = False
            if getsetting(db,"ALARM_SOLAR",1) == 1:
                Station.Alarm_Solar = True
            else:
                Station.Alarm_Solar = False
            if getsetting(db,"ALARM_RAIN",1) == 1:
                Station.Alarm_Rain = True
            else:
                Station.Alarm_Rain = False
            if getsetting(db,"ALARM_SOIL",1) == 1:
                Station.Alarm_Soil = True
            else:
                Station.Alarm_Soil = False
            if getsetting(db,"ALARM_BOARD",1) == 1:
                Station.Alarm_Board = True
            else:
                Station.Alarm_Board = False
            if getsetting(db,"ALARM_DEPTH",1) == 1:
                Station.Alarm_Depth = True
            else:
                Station.Alarm_Depth = False
            Station.Error_Level  = getsetting(db, "ERROR_LEVEL", 1)
            Station.Altitude  = getsetting(db, "ALTITUDE", 1)
            Station.Compass  = getsetting(db, "COMPASS", 1)
            Station.Variation  = getsetting(db, "VARIATION", 2)
            Station.WUndergroundID  = getsetting(db, "W_UNDER_ID", 0)
            Station.WUndergroundPWD  = getsetting(db, "W_UNDER_PWD", 0)
            Station.WUndergroundCAMID  = getsetting(db, "W_UNDER_CAMID", 0)
            Station.WUndergroundCAMFILE  = getsetting(db, "W_UNDER_CAMFILE", 0)
            Station.PWS_ID  = getsetting(db, "PWS_ID", 0)
            Station.PWS_PWD   = getsetting(db, "PWS_PWD", 0)
            Station.WOW_ID   = getsetting(db, "WOW_ID", 0)
            Station.WOW_KEY   = getsetting(db, "WOW_KEY", 0)
            Station.Remote_Conn  = getsetting(db, "REM_CONN", 0)
            Station.Burst_USN  = getsetting(db, "BURST_USN", 0)
            Station.Burst_PWD  = getsetting(db, "BURST_PWD", 0)
            Station.Remote_PHP  = getsetting(db, "REM_PHP", 0)
            Station.Remote_Burst  = getsetting(db, "REM_BURST", 0)
            if getsetting(db,"REM_BURST",1) == 1:
                Station.Burst_On = True
            else:
                Station.Burst_On = False
            Station.Remote_ID  = getsetting(db, "REM_ID", 0)
            Station.UoM  = getsetting(db, "UOM", 1)
            Station.WaitTime  = getsetting(db, "WAIT_ON", 1)
            Station.HeatBase  = getsetting(db, "HEAT_BASE", 2)
            Station.CoolBase  = getsetting(db, "COOL_BASE", 2)
            Station.ReportBase  = getsetting(db, "REPORT_BASE", 0)
            Station.BG_Color  = getsetting(db, "BG_COLOR", 0)
            a  = getsetting(db, "UPDATE_ON", 1)
            offset = int(getsetting(db, "UPDATE_ON", 2))
            if offset > a:
                offset = 0
            if a > 0 and a < 61:
                ## Map out intervals
                
                if offset > 0:
                    Station.UpdateOn = array("i",[offset])
                    b = a
                    a = offset
                else:
                    Station.UpdateOn = array("i",[0])
                    Station.UpdateOn.append(a)
                    b = a
                while a < 59:
                    a = a + b
                    Station.UpdateOn.append(a)
            else:
                Station.UpdateOn = array("i",[0])
            ##print Station.UpdateOn
            return True

        except:
            return False


    @staticmethod
    def NMEAupdate(NMEA, db):
        try:
            nmea  = getsetting(db, "NMEA_ON", 1)
            if nmea == 1:
                NMEA.ON = True
            nmea  = getsetting(db, "NMEA_GGA", 1)
            if nmea > 0:
                NMEA.GGA = True
            nmea  = getsetting(db, "NMEA_RMC", 1)
            if nmea > 0:
                NMEA.RMC = True
            nmea  = getsetting(db, "NMEA_HDT", 1)
            if nmea > 0:
                NMEA.HDT = True
            nmea  = getsetting(db, "NMEA_HDM", 1)
            if nmea > 0:
                NMEA.HDM = True
            nmea  = getsetting(db, "NMEA_MDA", 1)
            if nmea > 0:
                NMEA.MDA = True
            nmea  = getsetting(db, "NMEA_MWD", 1)
            if nmea > 0:
                NMEA.MWD = True
            nmea  = getsetting(db, "NMEA_MWV", 1)
            if nmea > 0:
                NMEA.MWV = True
            nmea  = getsetting(db, "NMEA_VWR", 1)
            if nmea > 0:
                NMEA.VWR = True
            return True
        except:
            return False

    @staticmethod
    def clearAOS(AOS):
        a = "---"
        AOS.w_max = a
        AOS.w_min = a
        AOS.w_avg = a
        AOS.g_max = a
        AOS.g_min = a
        AOS.g_avg = a
        AOS.c_avg = a
        AOS.windrun = a
        AOS.w_rose = a
        AOS.t_max = a
        AOS.t_min = a
        AOS.t_avg = a
        AOS.d_max = a
        AOS.d_min = a
        AOS.d_avg = a
        AOS.h_max = a
        AOS.h_min = a
        AOS.h_avg = a
        AOS.windchill = a
        AOS.heatout = a
        AOS.thw = a                             
        AOS.heat_dd = a
        AOS.cool_dd = a
        AOS.r_max = a
        AOS.r_min = a
        AOS.r_avg = a           
        AOS.ts_sum = a
        AOS.r_tips = a
        AOS.p_trend = a
        AOS.a_max = a
        AOS.a_min = a
        AOS.a_avg = a
        AOS.p_max = a
        AOS.p_min = a
        AOS.p_avg = a
        AOS.sl_sum = a
        AOS.sl_avg = a
        AOS.su_max = a
        AOS.sr_avg = a              
        AOS.sh_max = a 
        AOS.sh_min = a
        AOS.sh_avg = a
        AOS.se_sum = a
        AOS.thws = a
        AOS.dp_avg = a
        AOS.dp_min = a
        AOS.dp_max = a
        AOS.dp_trend = a
        AOS.v_source = a 
        AOS.v_battery = a
        AOS.b_avg = a


#===============================================================================
#                    Routines
#===============================================================================  
def getsetting(conn, par, t):
    # t = 0 String
    # t = 1 Integer
    # t = 2 Float
    # t = 3 Descript
    # t = 4 Date

    cur = conn.cursor()
    try:
        cur.execute("SELECT STR_VALUE, INT_VALUE, FLOAT_VALUE, DESCRIPT, DATE_VALUE FROM STATION WHERE LABEL = '" + par + "' limit 0,1")
        row = cur.fetchone()
        if row is not None:
            a = row[t]
            if a != None:
                cur.close()
                return a
            else:
                cur.close()
                if t == 0 or t == 3:
                    return ""
                else:
                    return 0     
        else:

            if par == "BROKER_ADDRESS":
                cur.execute("INSERT INTO STATION VALUES(NULL,'BROKER_ADDRESS','Broker IP Address','',NULL,0,NULL)")
            if par == "BROKER_CLIENT":
                cur.execute("INSERT INTO STATION VALUES(NULL,'BROKER_CLIENT','Broker Client','EOS_Station',NULL,0,NULL)")
            if par == "BROKER_PORT":
                cur.execute("INSERT INTO STATION VALUES(NULL,'BROKER_PORT','Broker Port','1883',NULL,0,NULL)")
            if par == "BROKER_USN":
                cur.execute("INSERT INTO STATION VALUES(NULL,'BROKER_USN','Broker Username','',NULL,0,NULL)")
            if par == "BROKER_PWD":
                cur.execute("INSERT INTO STATION VALUES(NULL,'BROKER_PWD','Broker Password','',NULL,0,NULL)")

            if par == "BURST_USN":
                cur.execute("INSERT INTO STATION VALUES(NULL,'BURST_USN','Burst FTP Username','burst',NULL,0,NULL)")
            if par == "BURST_PWD":
                cur.execute("INSERT INTO STATION VALUES(NULL,'BURST_PWD','Burst FTP Password','eosweather1!',NULL,0,NULL)")
            if par == "REM_BURST":
                cur.execute("INSERT INTO STATION VALUES(NULL,'REM_BURST','Send Burst Mode','',NULL,0,NULL)")
            if par == "ALARM_TEMP":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_TEMP','Check for temp alarms','',NULL,0,NULL)")
            if par == "ALARM_DEPTH":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_DEPTH','Check for depth alarms','',NULL,0,NULL)")
            if par == "ALARM_VOLTS":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_VOLTS','Trigger for volts alarm','',NULL,0,NULL)")
            if par == "ALARM_WIND":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_WIND','Check for wind alarms','',NULL,0,NULL)")
            if par == "ALARM_PRESSURE":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_PRESSURE','Check for pressure alarms','',NULL,0,NULL)")
            if par == "ALARM_SOLAR":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_SOLAR','Check for solar alarms','',NULL,0,NULL)")
            if par == "ALARM_RAIN":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_RAIN','Check for rain alarms','',NULL,0,NULL)")
            if par == "ALARM_BOARD":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_BOARD','Check for board alarms','',NULL,0,NULL)")
            if par == "ALARM_SOIL":
                cur.execute("INSERT INTO STATION VALUES(NULL,'ALARM_SOIL','Check for soil alarms','',NULL,0,NULL)")
            if par == "HAS_FAN":
                cur.execute("INSERT INTO STATION VALUES(NULL,'HAS_FAN','Has a fan installed','',NULL,0,NULL)")
            if par == "LED_STATE":
                cur.execute("INSERT INTO STATION VALUES(NULL,'LED_STATE','Current State of Satation LEDs','00000000',NULL,0,NULL)")
            if par == "SOIL_COUNT":
                cur.execute("INSERT INTO STATION VALUES(NULL, 'SOIL_COUNT','Maximum soil sentence records (0= Disable)','',NULL,0,NULL)")
            if par == "DEPTH_COUNT":
                cur.execute("INSERT INTO STATION VALUES(NULL, 'DEPTH_COUNT','Maximum depth sentence records (0= Disable)','',NULL,0,NULL)")
            if par == "DEPTH_HHWL":
                cur.execute("INSERT INTO STATION VALUES(NULL, 'DEPTH_HHWL','High High Water Level (cm)','',NULL,0,NULL)")
            if par == "EOS_VERSION":
                cur.execute("INSERT INTO STATION VALUES(NULL, 'EOS_VERSION','The current eos software version','1.0-0',NULL,0,NULL)")
            if par == "EOR_VERSION":
                cur.execute("INSERT INTO STATION VALUES(NULL, 'EOR_VERSION','The current eor software version','1.0-0',NULL,0,NULL)")
            if par == "STAT_ID":
                cur.execute("INSERT INTO STATION VALUES(NULL, 'STAT_ID','The station hardware id','',NULL,0,NULL)")
            if par == "BG_COLOR":
                cur.execute("INSERT INTO STATION VALUES(NULL,'BG_COLOR','Color background for web site','white',NULL,0,NULL)")
            if par == "PWS_ID":
                cur.execute("INSERT INTO STATION VALUES(NULL,'PWS_ID','PWS station ID','',NULL,0,NULL)")
            if par == "PWS_PWD":
                cur.execute("INSERT INTO STATION VALUES(NULL,'PWS_PWD','PWS station password','',NULL,0,NULL)")
            if par == "WOW_ID":
                cur.execute("INSERT INTO STATION VALUES(NULL,'WOW_ID','WOW station ID','',NULL,0,NULL)")
            if par == "WOW_KEY":
                cur.execute("INSERT INTO STATION VALUES(NULL,'WOW_KEY','WOW Authentication Key','',NULL,0,NULL)")
            if par == "TIDE_STATION":
                cur.execute("INSERT INTO STATION VALUES(NULL,'TIDE_STATION','The tide station code from xtide','',NULL,0,NULL)")
                
            cur.execute("SELECT STR_VALUE, INT_VALUE, FLOAT_VALUE, DESCRIPT, DATE_VALUE FROM STATION WHERE LABEL = '" + par + "' limit 0,1")
            row = cur.fetchone()
            if row is not None:
                a = row[t]
                if a != None:
                    cur.close()
                    return a
                else:
                    cur.close()
                    if t == 0 or t == 3:
                        return ""
                    else:
                        return 0
            else:
                cur.close()
                if t == 0 or t == 3:
                    return ""
                else:
                    return 0               
    except:
        cur.close()
        if t == 0 or t == 3:
            return ""
        else:
            return 0        

def getTime(Station, EOS):
        Station.date_time = datetime.now()
        EOS.Hours = float(Station.date_time.hour)
        EOS.Minutes = float(Station.date_time.minute)
        EOS.Seconds = float(Station.date_time.second)
        EOS.Day = float(Station.date_time.day)
        EOS.Month = float(Station.date_time.month)
        EOS.Year = float(Station.date_time.year - 2000)
        return re.sub("T"," ",Station.date_time.isoformat())

def test_alarm(ID,Level):
    alarm = False
    ##Do Alarms for this Archive period
    ##  ID
    ##      1 = high wind for 4 hrs
    ##      2 = heat index for 4 hrs
    ##      3 = thw index for 4 hrs
    ##      4 = thws index for 4 hrs
    ##      5 = Solar UV for 1 hr (at solar count level)
    ##      6 = Rain Rate for 15 min (at rain count level)
    ##      7 = Presure Drop for 4 hrs (at temp count level)
    ##      8 = Freezing temps for 4 hrs
    ta = float(Level)
    IDr = 0
    if ID == 1:
        #do high Wind
        if ta >= 40:
            e = "Hi Gusts : "
            IDr = ID
            if ta > 60:
                e = "Strong Gusts : "
                IDr = ID + 100
                if ta > 90:
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
        if ta >= 20:
            e = "Heavy Rain Fall Occurring"
            Idr = ID
            if ta >= 30:
                e = "Raining Cats and Dogs"
                IDr = ID + 100
            alarm = True
    elif ID == 7:
        #do Presuure Drop
        e = "Pressure Trend Falling Fast"
        IDr = ID
        alarm = True
    elif ID == 8:
        #do temp alarms
        if ta <= 0:
            e = "Freezing Temperatures: " + str(ta) + " C"
            IDr = ID
            alarm = True
    if IDr == 0:
        alarm = False

    return alarm


def calcchecksum(s):
        """
        Calculates checksum for sending commands to the ELKM1.
        Sums the ASCII character values mod256 and takes
        the lower byte of the two's complement of that value.
        """
        #return '%2X' % (-(sum(ord(c) for c in s) % 256) & 0xFF)
        return (sum(ord(c) for c in s))& 0xFF
    


def getchecksum(sentence):
    chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$") +1:sentence.find("*")])
    csum = 0
    for c in chksumdata:
        csum ^= ord(c)

    t = str(hex(csum))
    t = t.upper()[2:4]
    return t
##
##def _cleanstr(s):
##    return ''.join([c for c in s if c.isalnum() or c in {' '}])
##
##def _getdevstringinfo(device):
##    try:
##        str_info = _cleanstr(usb.util.get_string(device,256,2))
##        str_info += ' ' + _cleanstr(usb.util.get_string(device, 256, 3))
##        return str_info
##    except USBError:
##        return str_info
##
##def getusbdevices():
##    return [(device.idVendor, device.idProduct, _getdevstringinfo(device))
##            for device in usb.find(find_all=True)
##                if device.idProduct > 2]


def utc_to_local_tt(y, m, d, hrs_utc):
    daystart_utc_tt = (y, m, d, 0,0,0,0,0,-1)
    time_ts = int(calendar.timegm(daystart_utc_tt) + hrs_utc * 3600 + .05)
    #print ttime.localtime(time_ts)
    time_local_tt = ttime.localtime(time_ts)
    return time_local_tt

def set_time(time_truple):
    CLOCK_REALTIME = 0
    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec",ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]
    librt = ctypes.CDLL(ctypes.util.find_library("rt"))
    ts= timespec()
    ts.tv_sec = int(ttime.mktime( datetime( *time_truple[:6]).timetruple()))
    ts.tv_nsec = time_truple[6] * 1000000

    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))
    
