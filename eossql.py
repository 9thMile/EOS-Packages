
from math import *
from decimal import *
import calendar
from datetime import date, datetime, timedelta
import time as ttime
from array import *
import ctypes
import ctypes.util
import re
import MySQLdb as mdb


import eosutils as eosu
import eosformulas as eosf

class SQL:
    server = "localhost"
    port = 3306
    user = "weather"
    password = "eosweather"
    database = "weather"

#This will be for new tables and views after 1.0-6

def MSGLOG(conn, a):
    ## to remove old data done on return (in case new tables added)
    a.append("Delete from WIND")
    a.append("Delete from TEMP")
    a.append("Delete from PRESSURE")
    a.append("Delete from RAIN")
    a.append("Delete from LOCATION")
    ##a.append("Delete from SOLAR")
    a.append("Delete from BOARD")
    a.append("Delete from SOIL")
    ##a.append("Delete from DEPTH")
    cur = conn.cursor()
    try:


        cur.execute("SELECT COUNT(*) from information_schema.views where table_schema = 'weather' and table_name = 'DEPTH_RISE'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE VIEW DEPTH_RISE AS select DEPTH.DEPTH_ID AS DEPTH_ID,DEPTH.DEPTH AS DEPTH,DEPTH.TREND AS TREND,DEPTH.W_TIME AS W_TIME,(select STATION.FLOAT_VALUE from STATION where (STATION.LABEL = 'DEPTH_COUNT')) AS DATUM,((select STATION.FLOAT_VALUE from STATION where (STATION.LABEL = 'DEPTH_COUNT')) - DEPTH.DEPTH) AS RISE from DEPTH;")
                conn.commit()
                
        cur.execute("SELECT COUNT(*) from information_schema.tables where table_schema = 'weather' and table_name = 'TIDE'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE TABLE TIDE (W_TIME datetime NOT NULL,`LEVEL` float NOT NULL DEFAULT '0',PRIMARY KEY (W_TIME)) ENGINE=InnoDB  DEFAULT CHARSET=latin1;")
                conn.commit()
                
        cur.execute("SELECT COUNT(*) from information_schema.views where table_schema = 'weather' and table_name = 'DEPTH_RISE_DATA'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE VIEW DEPTH_RISE_DATA as select DEPTH_DATA.WE_DATE_TIME AS WE_DATE_TIME,DEPTH_DATA.WE_Date AS WE_DATE,DEPTH_DATA.WE_Time AS WE_TIME,DEPTH_DATA.DEPTH_ID AS DEPTH_ID,DEPTH_DATA.DEPTH AS DEPTH,DEPTH_DATA.TREND AS TREND,(select STATION.FLOAT_VALUE from STATION where (STATION.LABEL = 'DEPTH_COUNT')) AS DATUM,round(((select STATION.FLOAT_VALUE from STATION where (STATION.LABEL = 'DEPTH_COUNT')) - DEPTH_DATA.DEPTH),1) AS RISE, IFNULL(round(LEVEL,1),0) as TIDE from DEPTH_DATA LEFT JOIN TIDE on TIDE.W_TIME = DEPTH_DATA.WE_DATE_TIME ")
                conn.commit()

        cur.execute("SELECT COUNT(*) from information_schema.views where table_schema = 'weather' and table_name = 'DEPTH_TREND'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE VIEW DEPTH_TREND AS select x.WE_DATE_TIME AS WE_DATE_TIME,x.WE_Date AS WE_Date,x.WE_Time AS WE_TIME,x.DEPTH_ID AS ID,x.DEPTH AS DEPTH,round(((select STATION.FLOAT_VALUE from STATION where (STATION.LABEL = 'DEPTH_COUNT')) - x.DEPTH),1) AS Datum,round((((select STATION.FLOAT_VALUE from STATION where (STATION.LABEL = 'DEPTH_COUNT')) - x.DEPTH) / 30.48),1) AS Tide,round((x.DEPTH - y.DEPTH),1) AS diff,count(0) AS cnt,round(((x.DEPTH - y.DEPTH) / count(0)),1) AS trend from (DEPTH_DATA x join DEPTH_DATA y on((y.WE_DATE_TIME < x.WE_DATE_TIME))) group by x.WE_DATE_TIME;")
                conn.commit()



        cur.execute("SELECT COUNT(*) from information_schema.tables where table_schema = 'weather' and table_name = 'CORE_IMG'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE TABLE CORE_IMG (RECID int(11) NOT NULL AUTO_INCREMENT, We_Date date NOT NULL, FILENAME varchar(255) CHARACTER SET utf8 NOT NULL, IMG longblob, PRIMARY KEY (RECID), KEY PK_Date (We_Date,FILENAME)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 ;")
                conn.commit()

        cur.execute("SELECT COUNT(*) from information_schema.tables where table_schema = 'weather' and table_name = 'DEPTH'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE TABLE IF NOT EXISTS DEPTH (DEPTH_ID int(11) NOT NULL DEFAULT '0', DEPTH float NOT NULL DEFAULT '0', TREND int(11) NOT NULL DEFAULT '0', W_TIME datetime DEFAULT NULL, PRIMARY KEY (W_TIME)) ENGINE=InnoDB DEFAULT CHARSET=utf8;")
                conn.commit()

        cur.execute("SELECT COUNT(*) from information_schema.tables where table_schema = 'weather' and table_name = 'DEPTH_DATA'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE TABLE IF NOT EXISTS DEPTH_DATA (WE_DATE_TIME datetime NOT NULL, WE_Date date NOT NULL, WE_Time time NOT NULL, DEPTH_ID int(11) NOT NULL, DEPTH varchar(5) NOT NULL DEFAULT '---', TREND varchar(5) NOT NULL DEFAULT '---', PRIMARY KEY (WE_DATE_TIME, DEPTH_ID)) ENGINE=InnoDB DEFAULT CHARSET=utf8;")
                conn.commit()

        cur.execute("SELECT COUNT(*) from information_schema.tables where table_schema = 'weather' and table_name = 'MSGLOG'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE TABLE IF NOT EXISTS MSGLOG (WE_DATE_TIME datetime NOT NULL, MSGTYPE int(11) NOT NULL DEFAULT '0', DONE tinyint(1) NOT NULL DEFAULT '1', MSG text NOT NULL, REPLY text, SENT datetime DEFAULT NULL, PRIMARY KEY (WE_DATE_TIME,MSGTYPE)) ENGINE=InnoDB DEFAULT CHARSET=utf8;")
                conn.commit()
        cur.execute("SELECT COUNT(*) from information_schema.tables where table_schema = 'weather' and table_name = 'CORE_TIME'")
        row = cur.fetchone()
        if row is not None:
            a = row[0]
            if a == 0:
                cur.execute("CREATE TABLE IF NOT EXISTS CORE_TIME (WE_Date date NOT NULL,  MAX_TEMP time DEFAULT NULL,  MIN_TEMP time DEFAULT NULL,  MAX_BAR time DEFAULT NULL,  MIN_BAR time DEFAULT NULL,  MAX_WIND time DEFAULT NULL,  PRIMARY KEY (WE_Date)) ENGINE=InnoDB DEFAULT CHARSET=utf8;")
                conn.commit()
                cur.execute("INSERT INTO CORE_TIME (WE_Date) SELECT WE_Date FROM CORE_DATE")
                conn.commit()
                cur.execute("Select WE_Date from CORE_TIME")
                for row in cur.fetchall():

                    dstart = row[0].isoformat()
                    
                    cur.execute("Select WE_TIME as MAX_TIME from CORE_DATA where WE_DATE = '" + row[0].isoformat() + "' order by cast(TEMP_OUT as DECIMAL(10,2)) desc limit 0,1")
                    rrow = cur.fetchone()
                    cur.execute("Update CORE_TIME set MAX_TEMP = '" + str(rrow[0]) + "' where WE_DATE = '" + row[0].isoformat() + "'")
                    conn.commit()
                    cur.execute("Select WE_TIME as MIN_TIME from CORE_DATA where WE_DATE = '" + row[0].isoformat()  + "' order by cast(TEMP_OUT as DECIMAL(10,2)) limit 0,1")
                    rrow = cur.fetchone()
                    cur.execute("Update CORE_TIME set MIN_TEMP = '" + str(rrow[0]) + "' where WE_DATE = '" + row[0].isoformat()  + "'")
                    conn.commit()
                    cur.execute("Select WE_TIME as MAX_TIME from CORE_DATA where WE_DATE = '" + row[0].isoformat()  + "' order by cast(BAR as DECIMAL(10,2)) desc limit 0,1")
                    rrow = cur.fetchone()
                    cur.execute("Update CORE_TIME set MAX_BAR = '" + str(rrow[0]) + "' where WE_DATE = '" + row[0].isoformat()  + "'")
                    conn.commit()
                    cur.execute("Select WE_TIME as MIN_TIME from CORE_DATA where WE_DATE = '" + row[0].isoformat()  + "' order by cast(BAR as DECIMAL(10,2)) limit 0,1")
                    rrow = cur.fetchone()
                    cur.execute("Update CORE_TIME set MIN_BAR = '" + str(rrow[0]) + "' where WE_DATE = '" + row[0].isoformat()  + "'")
                    conn.commit()
                    cur.execute("Select WE_TIME as MAX_TIME from CORE_DATA where WE_DATE = '" + row[0].isoformat()  + "' order by cast(WIND_HI as DECIMAL(10,2)) desc limit 0,1")
                    rrow = cur.fetchone()
                    cur.execute("Update CORE_TIME set MAX_WIND = '" + str(rrow[0]) + "' where WE_DATE = '" + row[0].isoformat()  + "'")
                    conn.commit()
                
                    
                
        cur.close()
        return True
    except:
        cur.close()
        return False

def sqlUpdate(conn, a):
    cur = conn.cursor()
    try:
        cur.execute(a)
        rc = cur.rowcount
        conn.commit()
        if rc ==0:
            rc = 1
        r = "affected rows:%s" %(rc)
        cur.close()
        return True, r, rc
    except Exception,e:
        cur.close()
        rc = 0
        return False, str(e), rc
        
def sqlupdate(conn, a):
    cur = conn.cursor()
    try:
        cur.execute(a)
        conn.commit()
        cur.close()
        return True
    except:
        return False

def sqlmupdate(conn, a):
    cur = conn.cursor()
    e = True
    try:
        for s in a:
            try:
                cur.execute(s)
                conn.commit()
            except:
                e = False
                
        cur.close()
        if e == False:
            return False
        else:
            return True
    except:
        return False

class stmt:
    def version(self, v):
        return "Update STATION SET STR_VALUE ='%s' where LABEL = 'EOS_VERSION'" %v

    def feedtrim(self, conn, dstart):
        cur = conn.cursor()
        before = 0
        after = 0
        try:
            cur.execute("Select count(IS_DONE) C from FEED")
            row = cur.fetchone()
            if row is not None:
                before = row[0]
                s = "DELETE from FEED where W_TIME <= '" + dstart.isoformat() + "'"
                
                cur.execute(s)
                cur.execute("Select count(IS_DONE) C from FEED")
                row = cur.fetchone()
                if row is not None:
                    after = row[0]
            return before, after
                


        except:
            return before, after
    def records(self, conn, table, c, date_time):
            cur = conn.cursor()
            try:           
                cur.execute("UPDATE FEED SET IS_DONE = 1 where TYPE = %s and IS_DONE = 0" % c)
                cur.execute("SELECT count(W_TIME) as S_COUNT from %s where W_TIME = '" %table + date_time + "'")
                row = cur.fetchone()
                cur.close()
                if row is not None:
                    return row[0]
                else:
                    return 0
            except:
                cur.close()
                return 0
                
    def trimrecords(self, conn, Table, c):
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(W_TIME) S_COUNT from " + Table)
            row = cur.fetchone()

            if row is not None:
                r = row[0]
                if row[0] > c:
                    ##Get the oldest record (first in list)
                    dr = row[0] - c
                    while dr > 0:
                        a = "SELECT W_TIME from " + Table + " limit 0,1"
                        cur.execute(a)
                        rowA = cur.fetchone()
                        
                        if rowA is not None:
                            T = str(rowA[0])
                            ##Remove it
                            a = "DELETE FROM " + Table + " WHERE W_TIME = '" + T + "'"
                            cur.execute(a)
                        dr = dr - 1
    def delete(self,c):
        return "DELETE from FEED where TYPE = %s" %c
    def solarfeed(self):
        return "SELECT * FROM FEED WHERE TYPE = 5 and IS_DONE = 0 order by W_TIME desc limit 0,1"
    def tempfeed(self):
        return "SELECT * FROM FEED WHERE TYPE = 3 and IS_DONE = 0 order by W_TIME desc limit 0,1"
    def pressurefeed(self):
        return "SELECT * FROM FEED WHERE TYPE = 2 and IS_DONE = 0 order by W_TIME desc limit 0,1"
    def rainfeed(self):
        return "SELECT * FROM FEED WHERE TYPE = 4 and IS_DONE = 0 order by W_TIME desc limit 0,1"
    def windfeed(self):
        return "SELECT * FROM FEED WHERE TYPE = 1 and IS_DONE = 0 order by W_TIME desc limit 0,1"
    def soilfeed(self):
        return "SELECT * FROM FEED WHERE TYPE = 7 and IS_DONE = 0 order by W_TIME desc limit 0,1"
    def boardfeed(self):
        return "SELECT * FROM FEED WHERE TYPE = 6 and IS_DONE = 0 order by W_TIME desc limit 0,1"
    def depthfeed(self):
        return "SELECT * FROM FEED WHERE TYPE = 8 and IS_DONE = 0 order by W_TIME desc limit 0,1"
   
    def solararch(self, AOS, dstart, dend, sunrise, dInt, conn):
        cur = conn.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT SUM(LUM) SL_SUM, AVG(LUM) SL_AVG, MAX(UV) SU_MAX, AVG(RAD) SR_AVG, AVG(RAD) SH_AVG, MAX(RAD) SH_MAX, MIN(RAD) SH_MIN, SUM(ENERGY) SE_SUM FROM SOLAR where W_TIME >= '" + dstart.isoformat() + "'")
        for row in cur.fetchall():
            if row is not None:
                AOS.sl_sum = "{0:.1f}".format(row["SL_SUM"])
                AOS.sl_avg = "{0:.1f}".format(row["SL_AVG"])
                AOS.su_max = "{0:.1f}".format(row["SU_MAX"])
                AOS.sr_avg = "{0:.1f}".format(row["SR_AVG"])
                AOS.sh_max = "{0:.1f}".format(row["SH_MAX"])
                AOS.sh_min = "{0:.1f}".format(row["SH_MIN"])
                AOS.sh_avg = "{0:.1f}".format(round(row["SH_AVG"],1))
                AOS.se_sum = "{0:.2f}".format(round(row["SR_AVG"]/ 11.622 * dInt / 60,3))
                AOS.thws = "---"
               

                if AOS.t_avg <> "---" and AOS.w_avg <> "---" and AOS.h_avg <> "---":                                       
                    if float(AOS.t_avg) >= 20 and float(AOS.w_avg) > 1 and float(AOS.h_avg) > 0 and float(AOS.sh_avg) > 0:
                        if float(AOS.w_avg) > 64:
                            Wf = 64
                        else:
                            Wf = float(AOS.w_avg)

                        rh = float(AOS.h_avg)
                        Ta = float(AOS.t_avg)
                        Q = float(AOS.sh_avg)
                        AOS.thws = "{0:.1f}".format(round(eosf.thwsC(Ta, rh, eosu.convert.windspeed(2,Wf), Q),1))
                        ## Normal 20 - 24
                        ##  Alert 24 - 26
                        ## Danger 26 - 29
                        ## Emergency > 29
            else:
                AOS.sl_sum = "0"
                AOS.sl_avg = "0"
                AOS.su_max = "0"
                AOS.sr_avg = "0"              
                AOS.sh_max = "0" 
                AOS.sh_min = "0"
                AOS.sh_avg = "0"
                AOS.se_sum = "0"
                AOS.thws = "0"
                AOS.cloudy = "0"
                AOS.solarmax = "0"                
            if float(AOS.sr_avg) > 15:  #get it above sunrise.

                
                cur.execute("Select * from ALMANAC order by WE_DATE desc limit 0,1")
                for rows in cur.fetchall():
                    if rows["SOLARMAX"]<> None:
                        stime = rows["SUNRISE"]
                        sunrise = sunrise + stime
                        solarmax = float(rows["SOLARMAX"]) / 10
                        daylength = float(rows["DAY_LENGTH"]) * 60 / 40
                        sdelta = (dend - sunrise).total_seconds() / 60
                        if sdelta > 0:
                            Q = float(AOS.sh_avg)
                            soffset = int(sdelta / daylength) + 1
                            if soffset <40:
                                trigger = array('f',[.2,.5,1.1,1.6,2.2,2.8,3.5,4.2,4.8,5.4,6,6.6,7.2,7.8,8.4,9.1,9.4,9.8,9.9,10,10.1,10,9.9,9.8,9.4,9.1,8.4,7.8,7.2,6.6,6,5.4,4.8,4.2,3.5,2.8,2.2,1.6,1.1,.5,.2,0,0])
                                #trigger = array('f',[.5,.75,1.1,3,4.6,6.1,7.6,9.2,9.8,10,10,9.8,9.2,7.6,6.1,4.6,3,1.1,.75,.5,0])
                                solarcurrent = int(trigger[soffset] * solarmax)
                                solarnext = int(trigger[soffset + 1] * solarmax)
                                solardiff = solarnext - solarcurrent
                                if AOS.solar_segment == soffset:
                                    solarcurrent = int(solarcurrent + (solardiff/2))
                                if Q < solarcurrent:
                                    cloudy = 100 - int(Q/solarcurrent * 100)
                                else:
                                    cloudy = 0
                                AOS.cloudy = "{0:.1f}".format(cloudy)
                                AOS.solarmax = "{0:.1f}".format(solarcurrent)
                                AOS.solar_segment = soffset
                            else:
                                AOS.cloudy = "0"
                                AOS.solarmax = "0"
                                AOS.solar_segment = 0
                        else:
                            AOS.cloudy = "0"
                            AOS.solarmax = "0"
                            AOS.solar_segment = 0
                    else:
                        AOS.cloudy = "0"
                        AOS.solarmax = "0"
                        AOS.solar_segment = 0                            
            else:
                AOS.solar_segment = 0
                AOS.cloudy = "0"
                AOS.solarmax = "0"  
        cur.close()

    def solar(self, EOS, date_time):
        return "INSERT INTO SOLAR VALUES(" \
                            + str(EOS.Solar_Rad) + "," \
                            + str(EOS.Solar_RadHi) + "," \
                            + str(EOS.Solar_Energy) + "," \
                            + str(EOS.Solar_Lum) + "," \
                            + str(EOS.Solar_UV) + ",'" \
                            + date_time + "');"

    def location(self, EOS, date_time):
        return "INSERT INTO LOCATION VALUES(" \
                            + str(EOS.LAT) + "," \
                            + str(EOS.LONG) + "," \
                            + str(EOS.SOG) + "," \
                            + str(EOS.COG) +  ",'" \
                            + date_time + "');"
    
    def windarch(self, AOS, dstart, dInt, conn):
        cur = conn.cursor(mdb.cursors.DictCursor)

        cur.execute("Select count(ROSE), ROSE from WIND where W_TIME >= '" + dstart.isoformat() + "' group by ROSE order by count(ROSE) desc limit 0,1")
        row = cur.fetchone()
        if row is not None:
            AOS.w_rose = row["ROSE"]
            AOS.c_avg = eosu.wind.winddir(AOS.w_rose)
        
        cur.execute("SELECT AVG(SPEED) W_AVG, MAX(SPEED) W_MAX, MIN(SPEED) W_MIN, AVG(HI_GUST) G_AVG, MAX(HI_GUST) G_MAX, MIN(HI_GUST) G_MIN FROM WIND where W_TIME >= '" + dstart.isoformat() + "'")
        for row in cur.fetchall():
            AOS.w_max = "0"
            AOS.w_min = "0"
            AOS.w_avg = "0"
            AOS.g_max = "0"
            AOS.g_min = "0"
            AOS.g_avg = "0"
            AOS.windrun = "0"            
            if row is not None:
                if type(row["W_MAX"]) == float:
                    AOS.w_max = "{0:.1f}".format(row["W_MAX"])
                if type(row["W_MIN"]) == float:
                    AOS.w_min = "{0:.1f}".format(row["W_MIN"])
                if type(row["W_AVG"]) == float:
                    AOS.w_avg = round(row["W_AVG"],1)
                    AOS.windrun = "{0:.2f}".format(eosf.windrun(AOS.w_avg,dInt))   
                if type(row["G_MAX"]) == float:
                    AOS.g_max = "{0:.1f}".format(row["G_MAX"])
                if type(row["G_MIN"]) == float:
                    AOS.g_min = "{0:.1f}".format(row["G_MIN"])
                if type(row["G_AVG"]) == float:
                    AOS.g_avg = "{0:.1f}".format(round(row["G_AVG"],1))
                
                

        cur.close()
    
    def wind(self, EOS, Station, date_time):
        EOS.APWindDirection = EOS.WindDirection
        EOS.APWindSpeed = EOS.WindSpeed
        if EOS.APWindDirection >= 180:
            EOS.WindAngle = 360 - EOS.APWindDirection
            EOS.WindBow = "L"
        else:
            EOS.WindAngle = EOS.APWindDirection
            EOS.WindBow = "R"
        EOS.WindSpeed = eosu.wind.truewindspeed(EOS.APWindSpeed, EOS.APWindDirection, EOS.SOG)
        #EOS.wg = eosu.wind.truewindspeed(EOS.High_Gust, EOS.APWindDirection, EOS.SOG)
        #Taken out to ry and fix gust reading, will just use windspeed instead
        EOS.wg = eosu.wind.truewindspeed(EOS.WindSpeed, EOS.APWindDirection, EOS.SOG)
        EOS.wv = eosu.wind.truewindspeed(EOS.WindSpeed_Avg, EOS.APWindDirection, EOS.SOG)
        EOS.WindDirection = eosu.wind.truewind(EOS.WindSpeed, EOS.APWindDirection, EOS.COG, EOS.SOG)
        EOS.WindMagnetic = eosu.wind.add_dir(EOS.WindDirection, Station.Variation)
        EOS.WindRose = eosu.wind.windrose(EOS.WindDirection)
                            
        return "INSERT INTO WIND VALUES(" \
                            + str(EOS.WindSpeed) + "," \
                            + str(EOS.APWindSpeed) + "," \
                            + str(EOS.wg) + "," + str(EOS.wv) + "," \
                            + str(EOS.Wind_UoM) + "," \
                            + str(EOS.APWindDirection) + "," \
                            + str(EOS.WindDirection) + ",'" \
                            + EOS.WindRose + "','" \
                            + date_time + "');"

    def pressurearch(self, AOS, dstart, conn):
        cur = conn.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT AVG(ABS_PRESS) A_AVG, MAX(ABS_PRESS) A_MAX, MIN(ABS_PRESS) A_MIN, AVG(REL_PRESS) P_AVG, MAX(REL_PRESS) P_MAX, MIN(REL_PRESS) P_MIN, AVG(REL_PRESS) P_AVG FROM PRESSURE where W_TIME >= '" + dstart.isoformat() + "'")
        for row in cur.fetchall():
           if row is not  None:
               AOS.a_max = row["A_MAX"]
               AOS.a_min = row["A_MIN"]
               AOS.a_avg = ("%.1f" %round(row["A_AVG"],2))
               AOS.p_max = row["P_MAX"]
               AOS.p_min = row["P_MIN"]
               AOS.p_avg = ("%.1f" %round(row["P_AVG"],2))
           else:
               AOS.a_max = "0"
               AOS.a_min = "0"
               AOS.a_avg = "0"
               AOS.p_max = "0"
               AOS.p_min = "0"
               AOS.p_avg = "0"
        
        cur.execute("SELECT TREND from PRESSURE order by W_TIME desc limit 0,1")
        for row in cur.fetchall():
            if row["TREND"] <> None:
                AOS.p_trend = eosu.pressure.trend(row["TREND"])
            else:
                AOS.p_trend = "---"
        cur.close()
        
    def pressure(self, EOS, date_time):
        return "INSERT INTO PRESSURE VALUES(" \
                            + str(EOS.Pressure_Abs) + "," \
                            + str(EOS.Altitude) + "," \
                            + str(EOS.Pressure_Rel) + "," \
                            + str(EOS.Pressure_Trend) + ",'" \
                            + date_time + "');"

    def temparch(self, AOS, dstart, dInt, Station, conn):
        cur = conn.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT AVG(OUTSIDE) T_AVG, MAX(OUTSIDE) T_MAX, MIN(OUTSIDE) T_MIN, AVG(DEWPOINT) D_AVG, MAX(DEWPOINT) D_MAX, MIN(DEWPOINT) D_MIN, AVG(REL_HUM) H_AVG, MAX(REL_HUM) H_MAX, MIN(REL_HUM) H_MIN FROM TEMP where W_TIME >= '" + dstart.isoformat() + "'")
        for row in cur.fetchall():
            if row is not None:
               AOS.t_max = round(row["T_MAX"],1)
               AOS.t_min = round(row["T_MIN"],1)
               AOS.t_avg = round(row["T_AVG"],1)
               AOS.d_max = round(row["D_MAX"],1)
               AOS.d_min = round(row["D_MIN"],1)
               AOS.d_avg = round(row["D_AVG"],1)
               AOS.h_max = int(row["H_MAX"])
               AOS.h_min = int(row["H_MIN"])
               AOS.h_avg = int(row["H_AVG"])
               if isinstance(AOS.w_avg,float):
                    try:
                       
                       if AOS.w_avg > 6:
                           AOS.windchill = "{0:.1f}".format(eosf.windchillC(AOS.t_avg, AOS.w_avg))
                       else:
                           AOS.windchill = "{0:.1f}".format(AOS.t_avg)


                       if AOS.t_avg >= 20 and AOS.w_avg > 1 and AOS.h_avg > 0:
                            if AOS.w_avg > 64:
                                Wf = 64
                            else:
                                Wf = AOS.w_avg
                            AOS.thw = "{0:.1f}".format(round(eosf.thwC(AOS.t_avg, AOS.h_avg, eosu.convert.windspeed(2,Wf)),1))
                       else:
                            AOS.thw = "---"
                            ## Normal 20 - 24
                            ##  Alert 24 - 26
                            ## Danger 26 - 29
                            ## Emergency > 29
                       AOS.w_avg = "{0:.1f}".format(AOS.w_avg)

                    except:

                       AOS.thw = "---"
                       AOS.thws = "---"                     

               else:
                   AOS.heatout = "---"
                   AOS.thw = "---"
                   AOS.thws = "---"
                   AOS.heat_dd = "---"
                   AOS.cool_dd = "---"
                   AOS.windchill = "{0:.1f}".format(AOS.t_avg)  #

               if eosu.convert.temp(1,AOS.t_avg) >=80 and AOS.h_avg >= 40:
                   ## 85 F and 80 % = 96 F  / 36 C
                   ## 80-90 caution
                   ## 90 -105 extreme caution
                   ## 105 - 130 danger
                   ## > 130 extreme danger

                   AOS.heatout = "{0:.1f}".format(eosf.heatindexC(AOS.t_avg, AOS.h_avg))
               else:
                   AOS.heatout = "---"
               if AOS.t_avg < float(Station.HeatBase):
                   AOS.heat_dd = "{0:.3f}".format(eosf.heating_degrees(AOS.t_avg, Station.HeatBase, dInt))
               else:
                   AOS.heat_dd = "{0:.3f}".format(0)  
               if AOS.t_avg > float(Station.CoolBase):
                   AOS.cool_dd = "{0:.3f}".format(eosf.cooling_degrees(AOS.t_avg, Station.CoolBase, dInt))
               else:
                   AOS.cool_dd = "{0:.3f}".format(0)
               AOS.t_max = "{0:.1f}".format(AOS.t_max)
               AOS.t_min = "{0:.1f}".format(AOS.t_min)
               AOS.t_avg = "{0:.1f}".format(AOS.t_avg)
               AOS.d_max = "{0:.1f}".format(AOS.d_max)
               AOS.d_min = "{0:.1f}".format(AOS.d_min)
               AOS.d_avg = "{0:.1f}".format(AOS.d_avg)
               
                   
            else:
               AOS.t_max = "---"
               AOS.t_min = "---"
               AOS.t_avg = "---"
               AOS.d_max = "---"
               AOS.d_min = "---"
               AOS.d_avg = "---"
               AOS.h_max = "---"
               AOS.h_min = "---"
               AOS.h_avg = "---"
               AOS.windchill = "---"
               AOS.heatout = "---"
               AOS.thw = "---"                             
               AOS.heat_dd = "---"
               AOS.cool_dd = "---"
               if isinstance(AOS.w_avg,float):
                   AOS.w_avg = "{0:.1f}".format(AOS.w_avg)
               else:
                    AOS.w_avg = "---"
               
        cur.close()
        
    def temp(self, EOS, date_time):
        return "INSERT INTO TEMP VALUES(" \
                            + str(EOS.Temp_Outside) + "," \
                            + str(EOS.Temp_DewPoint) + "," \
                            + str(EOS.Humidity_Rel) + "," \
                            + str(EOS.Temp_Trend) + "," \
                            + str(EOS.Temp_UoM) + ",'" \
                            + date_time + "');"


    def rainarch(self, AOS, dstart, conn):
        cur = conn.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT AVG(RATE) R_AVG, MAX(RATE) R_MAX, MIN(RATE) R_MIN, SUM(RAIN_AMOUNT) T_SUM, MAX(TIPS) R_TIPS FROM RAIN where W_TIME >= '" + dstart.isoformat() + "'")
        for row in cur.fetchall():
           if row["R_MAX"] <> None:
               AOS.r_max = "{0:.1f}".format(row["R_MAX"])
               AOS.r_min = "{0:.1f}".format(row["R_MIN"])
               AOS.r_avg = "{0:.1f}".format(round(row["R_AVG"],1))               
               AOS.ts_sum = "{0:.1f}".format(row["T_SUM"])
               AOS.r_tips = row["R_TIPS"]
           else:
               AOS.r_max = "0"
               AOS.r_min = "0"
               AOS.r_avg = "0"           
               AOS.ts_sum = "0"
               AOS.r_tips = "0"
        cur.close()
        
    def rain(self, EOS, date_time):
        return "INSERT INTO RAIN VALUES(" \
                            + str(EOS.Rain_Rate) + "," \
                            + str(EOS.Rain_Amount) + "," \
                            + str(EOS.Rain_FallToday) + "," \
                            + str(EOS.Rain_FallYesterday) + "," \
                            + str(EOS.Rain_Rate_UoM) + "," \
                            + str(EOS.Rain_Tips) + ",'" \
                            + date_time + "');"

    def boardarch(self, AOS, dstart, conn):
        cur = conn.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT AVG(B_VOLTAGE) B_AVG, AVG(S_VOLTAGE) S_AVG, AVG(C_TEMP) T_AVG FROM BOARD where W_TIME >= '" + dstart.isoformat() + "'")
        for row in cur.fetchall():
           if row["B_AVG"]<> None:
               AOS.v_source = "{0:.1f}".format(row["S_AVG"])
               AOS.v_battery = "{0:.1f}".format(row["B_AVG"])
               AOS.b_avg = "{0:.1f}".format(row["T_AVG"])
           else:
               AOS.v_source = "0" 
               AOS.v_battery = "0"
               AOS.b_avg = "0"
        cur.close()
        
    def board(self, EOS, Station, date_time):
        return "INSERT INTO BOARD VALUES(" \
                            + str(Station.ID) + "," \
                            + str(Station.Type) + "," \
                            + str(EOS.B_Volts) + "," \
                            + str(EOS.S_Volts) + "," \
                            + str(EOS.C_Temp) + "," \
                            + str(EOS.Error) + "," \
                            + str(EOS.Error2) + ",'" \
                            + date_time + "','" \
                            + str(EOS.Version) + "');"

    def soilarch(self, AOS, dstart, conn):
        cur = conn.cursor(mdb.cursors.DictCursor)
        cur.execute("Select SOIL_ID, ROUND(AVG(MOISTURE),1) as AVGM, ROUND(AVG(TEMP),1) AVGT from SOIL where W_TIME >= '" + dstart.isoformat() + "' group by SOIL_ID")
        a = ""
        for row in cur.fetchall():
            if a == "":
               a = "('"
            else:
                a = a + ",('"
            a = a + AOS.we_datetime + "','" \
                + AOS.we_date + "','" \
                + AOS.we_time + "','" \
                + str(row["SOIL_ID"]) + "','" \
                + str("{0:.1f}".format(round(row["AVGT"],1))) + "','" \
                + str("{0:.1f}".format(round(row["AVGM"],1))) + "')"
        cur.close()
        return a
    
    def soil(self, EOS, date_time):
        return "INSERT INTO SOIL VALUES(" \
                            + str(EOS.Soil_ID) + "," \
                            + str(EOS.Soil_Moisture) + "," \
                            + str(EOS.Soil_Temp) + ",'" \
                            + date_time + "');"

    def depth(self, EOS, date_time):
        return "INSERT INTO DEPTH VALUES(" \
                            + str(EOS.Depth_ID) + "," \
                            + str(EOS.Depth) + "," \
                            + str(EOS.Depth_Trend) + ",'" \
                            + date_time + "');"

    def deptharch(self, Datum, AOS, dstart, conn):
        cur = conn.cursor(mdb.cursors.DictCursor)
        a = "Select DEPTH_ID, ROUND(AVG(DEPTH),1) AVGD, round(AVG(TREND),0) as TREND from DEPTH where W_TIME >= '" + dstart.isoformat() + "' group by DEPTH_ID"
        ##print a
        cur.execute(a)
        a = ""
        for row in cur.fetchall():
            if a == "":
               a = "('"
            else:
                a = a + ",('"
            a = a + AOS.we_datetime + "','" \
                + AOS.we_date + "','" \
                + AOS.we_time + "','" \
                + str(row["DEPTH_ID"]) + "','" \
                + str("{0:.1f}".format(round(row["AVGD"],1))) + "','" \
                + str(row["TREND"]) + "')"
            ##print a
        cur.close()
        
        return a
        
    def mda(self, EOS, u):
        return "INSERT INTO NMEA (WE_Date_Time, SENTENCE, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, CSUM)" + \
                            "VALUES('" + u.strftime("%Y-%m-%d %H:%M:%S") + "','$WIMDA','" + str(round(EOS.Pressure_Abs/1000*29.92,2)) + "','I','" + \
                            str(round(EOS.Pressure_Abs/1000,3)) + "','B','" + \
                            str(round(EOS.Temp_Outside,1)) + "','C','" + \
                            "','C','" + \
                            str(round(EOS.Humidity_Rel,1)) + "','','" + \
                            str(round(EOS.Temp_DewPoint,1)) + "','C','" + \
                            str(EOS.WindDirection) + "','T','" + \
                            str(EOS.WindDirection) + "','M','" + \
                            str(eosu.convert.windspeed(4,EOS.WindSpeed)) + "','N','" + \
                            str(eosu.convert.windspeed(2,EOS.WindSpeed)) + "','M','CSUM')"

    def mvw(self, EOS, u):
        return "INSERT INTO NMEA (WE_Date_Time, SENTENCE, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, CSUM)" + \
                            "VALUES('" + u.strftime("%Y-%m-%d %H:%M:%S") + "','$WIMWV','" + str(round(EOS.APWindDirection,1)) + "','R','" + \
                            str(round(eosu.convert.windspeed(4,EOS.APWindSpeed),2)) + "','N','" + \
                            str(round(eosu.convert.windspeed(2,EOS.APWindSpeed),2)) + "','M','" + \
                            str(round(eosu.convert.windspeed(1,EOS.APWindSpeed),2)) + "','K','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','CSUM')"

    def mwd(self, EOS, u):
        return "INSERT INTO NMEA (WE_Date_Time, SENTENCE, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, CSUM)" + \
                            "VALUES('" + u.strftime("%Y-%m-%d %H:%M:%S") + "','$WIMWD','" + str(round(EOS.APWindDirection,1)) + "','T','" + \
                            str(round(EOS.WindMagnetic),1) + "','M','" + \
                            str(round(eosu.convert.windspeed(4,EOS.APWindSpeed),2)) + "','N','" + \
                            str(round(eosu.convert.windspeed(2,EOS.APWindSpeed),2)) + "','M','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','CSUM')"

    def vwr(self, EOS, u):
        return "INSERT INTO NMEA (WE_Date_Time, SENTENCE, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, CSUM)" + \
                            "VALUES('" + u.strftime("%Y-%m-%d %H:%M:%S") + "','$WIVWR','" + str(round(EOS.WindAngle,1)) + "','" +EOS.WindBow + "','" + \
                            str(round(eosu.convert.windspeed(4,EOS.APWindSpeed),2)) + "','N','" + \
                            str(round(eosu.convert.windspeed(2,EOS.APWindSpeed),2)) + "','M','" + \
                            str(round(eosu.convert.windspeed(1,EOS.APWindSpeed),2)) + "','K','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','" + \
                            "" + "','','CSUM')"

    def core_data(self, AOS):
        return "INSERT INTO CORE_DATA VALUES('" \
                            + AOS.we_date + "', '" \
                            + AOS.we_time + "', '" \
                            + str(AOS.t_avg) + "', '" \
                            + str(AOS.t_max) + "', '" \
                            + str(AOS.t_min) + "', '" \
                            + str(AOS.h_avg) + "', '" \
                            + str(AOS.d_avg) + "','" \
                            + str(AOS.w_avg) + "','" \
                            + str(AOS.w_rose) + "','" \
                            + str(AOS.windrun) + "','" \
                            + str(AOS.w_max) + "','" \
                            + str(AOS.windchill) + "','" \
                            + str(AOS.heatout) + "','" \
                            + str(AOS.thw) + "','" \
                            + str(AOS.thws) + "','" \
                            + str(AOS.p_avg) + "','" \
                            + str(AOS.ts_sum) + "','" \
                            + str(AOS.r_max) + "','" \
                            + str(AOS.sl_avg) + "','" \
                            + str(AOS.su_max) + "','" \
                            + str(AOS.sr_avg) + "', '" \
                            + str(AOS.se_sum) + "', '" \
                            + str(AOS.sh_max) + "', '" \
                            + str(AOS.solarmax) + "', '" \
                            + str(AOS.cloudy) + "', '" \
                            + str(AOS.heat_dd) + "','" \
                            + str(AOS.cool_dd) + "','" \
                            + str(AOS.we_Interval) + "','" \
                            + AOS.we_datetime + "')"

    def core_ext(self, AOS):
        return "INSERT INTO CORE_EXT VALUES('" \
                            + AOS.we_datetime + "','" \
                            + AOS.we_date + "','" \
                            + AOS.we_time + "','" \
                            + str(AOS.r_tips) + "','" \
                            + str(AOS.p_lat) + "','" \
                            + str(AOS.p_long) + "','" \
                            + str(AOS.p_cog) + "','" \
                            + str(AOS.p_sog) + "','" \
                            + str(AOS.v_source)  + "','" \
                            + str(AOS.v_battery)  + "','" \
                            + str(AOS.b_avg) + "')"

    def core_date(self, AOS, row):
        return "INSERT INTO CORE_DATE values('" \
                            + AOS.we_date + "', '" \
                            + str(row["TEMP_AVG"]) + "', '" \
                            + str(row["TEMP_HI"]) + "', '" \
                            + str(row["TEMP_LOW"]) + "', '" \
                            + str(row["HUM_AVG"]) + "', '" \
                            + str(row["DEW_AVG"]) + "', '" \
                            + str(row["WIND_AVG"]) + "', '" \
                            + str(row["WIND_RUN"]) + "', '---','" \
                            + str(row["WIND_HI"]) + "', '" \
                            + str(row["WIND_CHILL"]) + "', '" \
                            + str(row["HEAT_OUT"]) + "', '" \
                            + str(row["THW"]) + "', '" \
                            + str(row["THWS"]) + "', '" \
                            + str(row["BAR"]) + "', '" \
                            + str(row["BAR_LOW"]) + "', '" \
                            + str(row["BAR_HI"]) + "', '" \
                            + str(row["RAIN"]) + "', '" \
                            + str(row["SOLAR_RAD_HI"]) + "', '" \
                            + str(row["SOLAR_UV"]) + "', '" \
                            + str(row["SOLAR_ENERGY"]) + "', '---','" \
                            + str(row["HEAT_DD"]) + "', '" \
                            + str(row["COOL_DD"]) + "')"

    
    
    

    
