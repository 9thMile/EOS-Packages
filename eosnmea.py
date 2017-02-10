from array import *
import sys
import os
import re
import string
from datetime import date, datetime, time, timedelta
from time import sleep
import serial
import MySQLdb as mdb
import threading
import httplib, urllib
import pynmea2

import eosutils as eosu
import eospush as eosp
import eossql as eoss

EOS_String = ""
has_db = False
has_serial_in = False
has_serial_out = False
ser = serial.Serial()
serout = serial.Serial()
Buff = ""
Buff2 = ""
E1 = ""
cur = None
db = None



        
class Station:
    inPort = '' ##"/dev/ttyUSB1"    # Expected port
    outPort = '' ##"/dev/ttyUSB0"

    inBaudrate = 4800 
    outBaudrate = 4800
    bytesize = serial.EIGHTBITS
    parity = serial.PARITY_NONE
    stopbits = serial.STOPBITS_ONE
    timeout = 0.1
    xonoff = 0
    rtscts = 0
    #interCharTimeout = none
    App_Token = ""
    User_Key = ""
    Wait_On = 1
    Error_Level = 0
    NMEA_ON = False
    NMEA_GGA = 0
    NMEA_RMC = 0
    NMEA_HDT = 0
    NMEA_HDM = 0
    NMEA_MDA = False
    NMEA_MWD = False
    NMEA_MWV = False
    NMEA_VWR = False
    
    

class ADR:
    B1 = ''
    B2 = ''
    B3 = ''
    B4 = ''
    B5 = ''
    B6 = ''
    B7 = ''
    B8 = ''
    B9 = ''
    B10 = ''
    B11 = ''
    B12 = ''
    B13 = ''
    B14 = ''
    B15 = ''
    B16 = ''
    B17 = ''
    B18 = ''
    B19 = ''
    B20 = ''
    CS = ''
    Count = 0
    
class eos_reader(object):

    
    def __init__(self):
        print "Reader Initialized" 

    def Up(self):
        global has_db
        global has_serial
        if has_db and (has_serial_in or has_serial_out):
            return True
        else:
            return False

    def Update(self):
        return True

class StationPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global ser #bring it in scope
    global serout
    global has_serial_in
    global has_serial_out

    self.inrunning = False
    self.outrunning = False


    if has_serial_in:
        try:
            ser.open() #starting the stream of info
            #Set Time/date on initial start
            d = datetime.now()
            dd = d.strftime("%d%m%y")
            dt = d.strftime("%H%M")

            ser.flushInput()

            self.current_value = None
            self.inrunning = True #setting the thread running to true
        except:
            self.inrunning = False
    if has_serial_out:
        try:
            serout.open() #starting the stream of info
            #Set Time/date on initial start
            self.current_value = None
            self.outrunning = True #setting the thread running to true
        except:
            self.outrunning = False 

  def run(self):
    global ser
    global serout
    global ADR
    global Station
    global cur
    global db
    global has_serial_in
    global has_serial_out
    global Buff
    global NMEA_Good
    

    Sentence = ''
    CheckSum = ''
    re = ''

    while (self.inrunning or self.outrunning):
            NMEA_Good = False
            if self.inrunning:
                try:
                    Buff = ser.readline()
                    if Buff.startswith('$'):
                            for line in Buff.split('\n\r'):
                                if eosu.nmea.checksumnmea(ADR, line):
                                    NMEA_Good = False
                                    if line.count("*") ==1:
                                        Sentence, CheckSum = line.strip().split('*')
                                        Sentence = Sentence.strip('$')
                                        if line.startswith('GGA', 3)and Station.NMEA_GGA > 0:
                                                NMEA_Good = eosu.nmea.split_sentence(ADR,Sentence)
        
                                        if line.startswith('RMC', 3) and Station.NMEA_RMC > 0:
                                                NMEA_Good = eosu.nmea.split_sentence(ADR,Sentence)

                                        if line.startswith('HDM', 3)and Station.NMEA_HDM > 0:
                                                NMEA_Good = eosu.nmea.split_sentence(ADR,Sentence)

                                        if line.startswith('HDT', 3)and Station.NMEA_HDT > 0:
                                                NMEA_Good = eosu.nmea.split_sentence(ADR,Sentence)
                                         
                                        if NMEA_Good == True:
                                            #Truncate records
                                            cur.execute("SELECT MAX(RECID) as R, COUNT(RECID) as C FROM NMEA")
                                            row = cur.fetchone()
                                            if row is not None:
                                                C = row['C']
                                                RECID = row['R']
                                                if C > 20:
                                                    cur.execute("DELETE FROM NMEA where RECID < " + str(RECID -15))
                                                    db.commit()
                                            cur.execute(eosu.nmea.get_sentence(ADR, line, CheckSum))
                                            db.commit()
                                            sleep(.5)
      
                            Buff = ''
                            sleep(.05)

                except Exception, e:
                    print str(e)
                    print Buff
                    print line
                    print Sentence
                    print CheckSum
                    ser.flush()
##
##                    if len(Station.User_Key) > 0:
##                        Send_PushOver(Station.App_Token, Station.User_Key, str(e), -1)

        
            if self.outrunning:
                try:
                    if Station.NMEA_ON:
                        if Station.NMEA_RMC > 1:
                            cur.execute("SELECT * FROM NMEA WHERE SENTENCE LIKE '%RMC' order by WE_Date_Time desc limit 0,1")
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                a = eosu.nmea.put_sentence(row, '*', 12)
                                c = eosu.getchecksum(a)
                                a = a + c + '\n\r'
                                #print a  + ' output'                       
                                serout.write(unicode(a))
                                serout.flush()
                                cur.execute("DELETE FROM NMEA where SENTENCE LIKE '%RMC' and WE_Date_Time < '" + row['WE_Date_Time'].isoformat() + "'")
                                db.commit()
                        if Station.NMEA_GGA > 1:
                            cur.execute("SELECT * FROM NMEA WHERE SENTENCE LIKE '%GGA' order by WE_Date_Time desc limit 0,1")
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                a = eosu.nmea.put_sentence(row, '*', 14)
                                c = eosu.getchecksum(a)
                                a = a + c + '\n\r'
                                #print a  + ' output'                       
                                serout.write(unicode(a))
                                serout.flush()
                                cur.execute("DELETE FROM NMEA where SENTENCE LIKE '%GGA' and WE_Date_Time < '" + row['WE_Date_Time'].isoformat() + "'")
                                db.commit()
                        if Station.NMEA_HDT > 1:
                            cur.execute("SELECT * FROM NMEA WHERE SENTENCE LIKE '%HDT' order by WE_Date_Time desc limit 0,1")
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                a = eosu.nmea.put_sentence(row, '*', 2)
                                c = eosu.getchecksum(a)
                                a = a + c + '\n\r'
                                #print a  + ' output'                       
                                serout.write(unicode(a))
                                serout.flush()
                                cur.execute("DELETE FROM NMEA where SENTENCE LIKE '%HDT' and WE_Date_Time < '" + row['WE_Date_Time'].isoformat() + "'")
                                db.commit()
                        if Station.NMEA_HDM > 1:
                            cur.execute("SELECT * FROM NMEA WHERE SENTENCE LIKE '%HDM' order by WE_Date_Time desc limit 0,1")
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                a = eosu.nmea.put_sentence(row, '*', 2)
                                c = eosu.getchecksum(a)
                                a = a + c + '\n\r'
                                #print a  + ' output'                       
                                serout.write(unicode(a))
                                serout.flush()

                        if Station.NMEA_MDA:
                            cur.execute("SELECT * FROM NMEA WHERE SENTENCE LIKE '%MDA' order by WE_Date_Time desc limit 0,1")
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                a = eosu.nmea.put_sentence(row, '*', 20)
                                c = eosu.getchecksum(a)
                                a = a + c + '\n\r'
                                #print a  + ' output'                       
                                serout.write(unicode(a))
                                serout.flush()

                        if Station.NMEA_VWR:
                            cur.execute("SELECT * FROM NMEA WHERE SENTENCE LIKE '%VWR' order by WE_Date_Time desc limit 0,1")
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                a = eosu.nmea.put_sentence(row, '*', 8)
                                c = eosu.getchecksum(a)
                                a = a + c + '\n\r'
                                #print a  + ' output'                       
                                serout.write(unicode(a))
                                serout.flush()

                        if Station.NMEA_MWD:
                            cur.execute("SELECT * FROM NMEA WHERE SENTENCE LIKE '%MWD' order by WE_Date_Time desc limit 0,1")
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                a = eosu.nmea.put_sentence(row, '*',8)
                                c = eosu.getchecksum(a)
                                a = a + c + '\n\r'
                                #print a  + ' output'                       
                                serout.write(unicode(a))
                                serout.flush()

                        if Station.NMEA_MWV:
                            cur.execute("SELECT * FROM NMEA WHERE SENTENCE LIKE '%MWV' order by WE_Date_Time desc limit 0,1")
                            row = cur.fetchone()
                            db.commit()
                            if row is not None:
                                a = eosu.nmea.put_sentence(row, 'A*', 4)
                                c = eosu.getchecksum(a)
                                a = a + c + '\n\r'                      
                                serout.write(unicode(a))
                                serout.flush()

                        
                    sleep(1)

                except Exception, e:
                    print str(e)
                    serout.flush()
##
##                    if len(Station.User_Key) > 0:
##                        Send_PushOver(Station.App_Token, Station.User_Key, str(e), -1)  


def find_gps(b):
    for tport in range(3):
        try:
            serdev = None
            #print "trying USB%d" % (tport)
            a = '/dev/ttyUSB' + str(tport)
            serdev = serial.Serial(port=a,baudrate= b,timeout=2)
            #print "found serial port USB%d"%(tport)
            for n in range(3) :
                line = serdev.readline()
                #print "  serial:",line,
                head = line[0:3]
                if head == '$GP' or head == '$PG':
                    print "found GPS receiver on %s" % (a)
##                    for o in range(15):                 # show some GPS data
##                        print "  gps:",serdev.readline(),
                    return a
            serdev.close()
        except:
##            print "  error on COM%d, skipping" % (tport+1)
            if serdev: serdev.close()

    print "no GPS receiver found on serial ports, exiting"
    return ''

def main():
    global ADDRESS
    global Station
    global has_db
    global has_serial_in
    global has_serial_out
    global EOS_String
    global cur
    global db
    EOS_reader = eos_reader()
    sleep(1) #wait a couple of min for services to start
    try:

        db = mdb.connect(host= eoss.SQL.server, port = eoss.SQL.port, user= eoss.SQL.user,passwd= eoss.SQL.password, db= eoss.SQL.database)
        ## Set up a cursor to hold data and execute statments
        cur = db.cursor(mdb.cursors.DictCursor)

        Station.App_Token = eosu.getsetting(db, "APP_TOKEN", 0)
        Station.User_Key = eosu.getsetting(db, "USER_KEY", 0)
        Station.NMEA_GGA = eosu.getsetting(db, "NMEA_GGA", 1)
        Station.NMEA_RMC = eosu.getsetting(db, "NMEA_RMC", 1)
        Station.NMEA_HDT = eosu.getsetting(db, "NMEA_HDT", 1)
        Station.NMEA_HDM = eosu.getsetting(db, "NMEA_HDM", 1)
        Station.Wait_On = eosu.getsetting(db, "WAIT_ON", 1)
        nmea = eosu.getsetting(db, "NMEA_ON", 1)
        if nmea == 1:
            Station.NMEA_ON = True
        nmea = eosu.getsetting(db, "NMEA_MDA", 1)
        if nmea == 1:
            Station.NMEA_MDA = True
        nmea = eosu.getsetting(db, "NMEA_MWD", 1)
        if nmea == 1:
            Station.NMEA_MWD = True
        nmea = eosu.getsetting(db, "NMEA_MWV", 1)
        if nmea == 1:
            Station.NMEA_MWV = True
        nmea = eosu.getsetting(db, "NMEA_VWR", 1)
        if nmea == 1:
            Station.NMEA_VWR = True
            
        InPort  = eosu.getsetting(db, "NMEA_IN_PORT", 0)
        OutPort  = eosu.getsetting(db, "NMEA_OUT_PORT", 0)
        if OutPort <> '':
            Station.outPort, Station.outBaudrate = OutPort.strip().split(',')
            
        else:
            Station.outPort = ''        
        
        if InPort <> '':         
            Station.inPort, Station.inBaudrate = InPort.strip().split(',')
            gpsPort = find_gps(Station.inBaudrate)
            if gpsPort <> Station.inPort:
                if Station.outPort <> '':
                    ##Swap ports for this session
                    Station.outPort = Station.inPort
                Station.inPort = gpsPort
        has_db = True
##        cur.execute("DELETE FROM NMEA")
##        db.commit()
    except:
        print "No database connection"
        if len(Station.User_Key) > 0:
            eosp.sendpushover(Station.App_Token, Station.User_Key, "NMEA Server NOT Running No DB", -1)
        has_db = False
        sys.stdout.write("Not Starting\n")
    try:

        if Station.inPort <> '':
            ser.port = Station.inPort
            ser.baudrate = Station.inBaudrate
            ser.bytsize = Station.bytesize
            ser.parity = Station.parity
            ser.stopbits = Station.stopbits
            ser.timeout = Station.timeout
            ser.xonoff = Station.xonoff
            ser.rtscts = Station.rtscts
            #ser.interCharTimeout = STATION.interCharTimeout
            has_serial_in = True

    except serial.SerialException:
        has_serial_in = False
        print "Can't open in serial port : " + ser.port
    try:
        if Station.outPort <> '':
            serout.port = Station.outPort
            serout.baudrate = Station.outBaudrate
            serout.bytsize = Station.bytesize
            serout.parity = Station.parity
            serout.stopbits = Station.stopbits
            serout.timeout = Station.timeout
            serout.xonoff = Station.xonoff
            serout.rtscts = Station.rtscts
            #ser.interCharTimeout = STATION.interCharTimeout
            has_serial_out = True
    except serial.SerialException:
        has_serial_out = False
        print "Can't open outserial port : " + serout.port 
        if len(Station.User_Key) > 0:
            eosp.sendpushover(Station.App_Token, Station.User_Key, "NMEA Server NOT Running No Serial Ports", -1)

    if EOS_reader.Up():
        print "NMEA Starting"    
        gpsp = StationPoller()
        try:
            if len(Station.User_Key) > 0:
                eosp.sendpushover(Station.App_Token, Station.User_Key, "NMEA Server Running", -1)

            gpsp.run()
            if gpsp.inrunning == True:
              print "NMEA : input running"
            else:
              print "NMEA : input not running"
            if gpsp.outrunning == True:
              print "NMEA : output running"
            else:
              print "NMEA : output not running"

        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print "\nKilling Thread..."
            gpsp.outrunning = False
            gpsp.inrunning = False
            if ser.open():
                ser.close()
            if serout.open():
                serout.close()
            if len(Station.User_Key) > 0:
                eosp.sendpushover(Station.App_Token, Station.User_Key, "NMEA Server Stopped", 1)
            # wait for the thread to finish what it's doing                  
        except Exception,e:
            print str(e)
            gpsp.inrunning = False
            gpsp.outrunning = False
            if ser.open():
                ser.close()
            if serout.open():
                serout.close()
            
    print 'Exiting'
    if len(Station.User_Key) > 0:
        eosp.sendpushover(Station.App_Token, Station.User_Key, "NMEA Server Stopped", 1)

if __name__ ==  '__main__':

    main()



        
