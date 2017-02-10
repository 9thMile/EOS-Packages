#!/usr/bin/env python
import sys
import subprocess
import eossql as eoss
import eosutils as eosu
import eospush as eosp
import MySQLdb as mdb
from datetime import date, datetime, time, timedelta, tzinfo
import csv

class Station:
    Remote_ID = ""
    Remote_Conn = ""
    Burst_USN = ""
    Burst_PWD = ""
    HasBurst = False
    Has_Core = 0
    Has_Cam = False
    WebCam = ""
    TideStation = ""
    UpdateOn = 0
    
dstart = datetime.utcnow()
dend = dstart + timedelta(minutes= 120)
dstart = dstart + timedelta(minutes =60)
startchar = dstart.strftime('%Y-%m-%d %H:00')
endchar = dend.strftime('%Y-%m-%d %H:00')
print startchar

GET_TIDE = "tide -l 'halifax' -f p -m g -gw 1200 -gh 230 -u ft -nc midnightblue -dc orange -em pMm -fg white -o '/var/www/reports/tide1.png'"

GET_TIDEDATA = 'tide -l "halifax" -b "'+ startchar + '" -e "' + endchar + '" -f c -m m -s 00:10 -u m -z -o "/var/www/reports/tide1.txt"'
DEL_TIDE = "rm '/var/www/reports/tide.png'"
DEL_TIDEDATA = "rm '/var/www/reports/tide.txt'"
RNM_TIDE = "mv '/var/www/reports/tide1.png' '/var/www/reports/tide.png'"
RNM_TIDEDATA = "mv '/var/www/reports/tide1.txt' '/var/www/reports/tide.txt'"

def run_cmd(cmd):
    subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    try:
        db = mdb.connect(host= eoss.SQL.server, port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)

        Station.Remote_ID = eosu.getsetting(db, "Rem_ID", 0)
        if len(Station.Remote_ID) > 1:
            if eosu.getsetting(db,"REM_BURST",1) == 1:
                Station.HasBurst = True
                Station.Remote_Conn  = eosu.getsetting(db, "REM_CONN", 0)
                Station.Burst_USN  = eosu.getsetting(db, "BURST_USN", 0)
                Station.Burst_PWD  = eosu.getsetting(db, "BURST_PWD", 0)

        
        Station.TideStation = eosu.getsetting(db, "TIDE_STATION", 0)
        Station.UpdateOn = eosu.getsetting(db, "UPDATE_ON", 1)
        if len(Station.TideStation) > 0:
            GET_TIDE = "tide -l '%s' -f p -m g -gw 1200 -gh 230 -u ft -nc midnightblue -dc orange -em pMm -fg white -o '/var/www/reports/tide1.png'" %Station.TideStation
            GET_TIDEDATA = 'tide -l "' + Station.TideStation + '" -b "'+ startchar + '" -e "' + endchar + '" -f c -m m -s 00:' + str(Station.UpdateOn) + ' -u m -z -o "/var/www/reports/tide1.txt"'
            
        run_cmd(GET_TIDE)
        run_cmd(DEL_TIDE)
        run_cmd(RNM_TIDE)
        run_cmd(GET_TIDEDATA)
        run_cmd(DEL_TIDEDATA)
        run_cmd(RNM_TIDEDATA)
        if len(Station.TideStation) > 0:
            with open('/var/www/reports/tide.txt','rb') as csvfile:
                depthreader = csv.reader(csvfile, delimiter=',')
                aa = []
                for row in depthreader:
                    loc = row[0]
                    d = row[1]
                    t = row[2]
                    dd = ((float(row[3])*100) - 10) * 1.2
                    t = t[:-4]
                    idate = datetime.strptime(d + ' ' + t,'%Y-%m-%d %I:%M %p')
                    aa.append ("INSERT INTO TIDE (W_TIME, LEVEL) VALUES ('" + idate.isoformat() + "'," + str(dd) + ")")
                if len(aa) > 0:
                    if eoss.sqlmupdate(db,aa) == False:
                        print "Failed to insert TIDE records"
                    else:
                        print "Tide records inserted"              
        if len(Station.Remote_ID) > 1:
            if Station.HasBurst:
                sent,reason = eosp.burstupload(Station, "/tide.png", '/var/www/reports/tide.png')


                


        print "Done"

    except Exception,e:
        print "died -" + str(e)

    

