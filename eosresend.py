import array
import sys
import os
from math import *
from decimal import Decimal 
from datetime import date, datetime, time, timedelta, tzinfo
from gps import *
import re
import MySQLdb as mdb
from array import *
import threading
import httplib, urllib
import logging
import logging.handlers

import eosutils as eosu
import eosformulas as eosf
import eospush as eosp
import eosdebug as eosd
import eossql as eoss
import eosrelays as eosr

class Station:
    Remote_Conn = ""
    Remote_PHP = ""
    Remote_ID = ""

##Archive data
class AOS:
    w_max = "---"
    w_min = "---"
    w_avg = "---"
    w_rose = "---"
    g_max = "---"
    g_min = "---"
    g_avg = "---"
    c_avg = "---"
    windrun = "---"
    t_max = "---"
    t_min = "---"
    t_avg = "---"
    d_max = "---"
    d_min = "---"
    d_avg = "---"
    h_max = "---"
    h_min = "---"
    h_avg = "---"
    windchill = "---"
    heatout = "---"
    thw = "---"
    thws = "---"
    heat_dd = "---"
    cool_dd = "---"
    r_max = "---"
    r_hrsum = "---"
    r_dsum = "---"
    r_min = "---"
    r_avg = "---"
    r_tips = "---"
    ts_sum = "---"
    a_max = "---"
    a_min = "---"
    a_avg = "---"
    p_max = "---"
    p_min = "---"
    p_avg = "---"
    p_trend = '---'
    sl_sum = "---"
    sl_avg = "---"
    su_max = "---"
    sr_avg = "---"              
    sh_max = "---" 
    sh_min = "---"
    sh_avg = "---"
    se_sum = "---"
    we_date = " "
    we_time = " "
    we_datetime = " "
    aw_date = ""
    aw_time = ""
    t = datetime(2000, 1, 1, 0, 0, 0)
    we_Interval = " "
    p_lat = "---"
    p_long = "---"
    p_cog = "---"
    p_sog = "---"
    v_source = "---"
    v_battery = "---"
    b_avg = "---"
    solarmax = "---"
    cloudy = "---"
    solar_segment = 0

def main():


    ## Make connection to MySQL 
    try:
        db = mdb.connect(host= eoss.SQL.server, port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
        ## Set up a local cursor to hold data and execute statments
        cur = db.cursor(mdb.cursors.DictCursor)
        Station.Remote_ID = eosu.getsetting(db, "Rem_ID", 0)
        if len(Station.Remote_ID) > 1:
            Station.Remote_Conn  = eosu.getsetting(db, "REM_CONN", 0)

            query = "Select * from CORE_DATA where WE_Date between '2016-01-01' and '2016-01-06'"
            cur.execute(query)
            result = cur.fetchall()    
            for record in result:
##                print record
                eosu.station.clearAOS(AOS)
                AOS.we_date = record["WE_Date"]
                AOS.we_time= record["WE_Time"]
                AOS.t_avg = record["TEMP_OUT"]
                AOS.t_max = record["TEMP_HI"]
                AOS.t_min = record["TEMP_LOW"]
                AOS.h_avg = record["HUM_OUT"]
                AOS.d_avg = record["DEW_OUT"]
                AOS.w_avg = record["WIND_SPEED"]
                AOS.w_rose = record["WIND_DIR"]
                AOS.windrun = record["WIND_RUN"]
                AOS.g_max = record["WIND_HI"]
                AOS.windchill = record["WIND_CHILL"]
                AOS.heatout = record["HEAT_OUT"]
                AOS.thw = record["THW"]
                AOS.thws = record["THWS"]
                AOS.p_avg = record["BAR"]
                AOS.ts_sum = record["RAIN"]
                AOS.r_avg = record["RAIN_RATE"]
                AOS.sr_avg = record["SOLAR_RAD"]
                AOS.se_sum = record["SOLAR_ENERGY"]
                AOS.sh_max = record["SOLAR_RAD_HI"]
                AOS.su_max = record["SOLAR_UV"]
                AOS.solarmax = record["SOLAR_MAX"]
                AOS.cloudy = record["CLOUDY"]
                AOS.heat_dd = record["HEAT_DD"]
                AOS.cool_dd = record["COOL_DD"]
                AOS.we_Interval = record["ARC_INT"]
                n = record["WE_DATE_TIME"]
                rowdate = re.sub("T"," ",n.isoformat())                
                AOS.we_datetime = rowdate
                responce,status,reason,message = eosp.sendremote(AOS, Station.Remote_ID, Station.Remote_Conn, "/remoteresend.php?")
                
                print rowdate
                time.sleep(.25)


                
                


    except:
        pass

if __name__ ==  '__main__':

    main()

    
