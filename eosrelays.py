import array
import sys
import os
from math import *
from decimal import Decimal 


import eospush as eosp


class Relays:
    Site = ""
    Cmd = ""
    Script = ""
    On_Trig = ""
    Value = 0
    State = False
    Off_Trig = ""
    Comp = ""
    Method = ""
    


def sendrelays(conn, AOS, eos_log):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * from RELAYS")

    if cur.rowcount > 0:
        rows = cur.fetchall()
        
        try:
            for row in rows:
                Relays.Site = row[1]
                Relays.Script = row[2]
                Relays.Cmd = row[3]
                Relays.Value = row[5]
                Relays.Comp = row[6]
                Relays.On_Trig = row[7]
                Relays.Off_Trig = row[8]
                Relays.Method = row[4]
                if Relays.Method == "TEMP":
                    if len(Relays.Site) > 0:
                        if Relays.Comp == ">=":
                            if  float(AOS.t_avg) >= Relays.Value:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.On_Trig)
                                if responce == True:
                                    eos_log.info("Temperature trigger sent :" + Relays.On_Trig)
                                else:
                                    eos_log.info("Temperature trigger NOT sent :" + reason)
                            else:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.Off_Trig)
                                if responce == True:
                                    eos_log.info("Temperature trigger sent :" + Relays.Off_Trig)
                                else:
                                    eos_log.info("Temperature trigger NOT sent :" + reason)

                        if Relays.Comp == "<=":
                            if  float(AOS.t_avg) <= Relays.Value:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.On_Trig)
                                if responce == True:
                                    eos_log.info("Temperature trigger sent :" + Relays.On_Trig)
                                else:
                                    eos_log.info("Temperature trigger NOT sent :" + reason)
                            else:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.Off_Trig)
                                if responce == True:
                                    eos_log.info("Temperature trigger sent :" + Relays.Off_Trig)
                                else:
                                    eos_log.info("Temperature trigger NOT sent :" + reason)
                if Relays.Method == "WIND":
                    if len(Relays.Site) > 0:
                        if Relays.Comp == ">=":
                            if  float(AOS.w_avg) >= Relays.Value:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.On_Trig)
                                if responce == True:
                                    eos_log.info("Wind trigger sent :" + Relays.On_Trig)
                                else:
                                    eos_log.info("Wind trigger NOT sent :" + reason)
                            else:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.Off_Trig)
                                if responce == True:
                                    eos_log.info("Wind trigger sent :" + Relays.Off_Trig)
                                else:
                                    eos_log.info("Wind trigger NOT sent :" + reason)

                        if Relays.Comp == "<=":
                            if  float(AOS.w_avg) <= Relays.Value:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.On_Trig)
                                if responce == True:
                                    eos_log.info("Wind trigger sent :" + Relays.On_Trig)
                                else:
                                    eos_log.info("Wind trigger NOT sent :" + reason)
                            else:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.Off_Trig)
                                if responce == True:
                                    eos_log.info("Wind trigger sent :" + Relays.Off_Trig)
                                else:
                                    eos_log.info("Wind trigger NOT sent :" + reason)

                if Relays.Method == "SOLAR":
                    if len(Relays.Site) > 0:
                        if Relays.Comp == ">=":
                            if  float(AOS.sr_avg) >= Relays.Value:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.On_Trig)
                                if responce == True:
                                    eos_log.info("Solar trigger sent :" + Relays.On_Trig)
                                else:
                                    eos_log.info("Solar trigger NOT sent :" + reason)
                            else:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.Off_Trig)
                                if responce == True:
                                    eos_log.info("Solar trigger sent :" + Relays.Off_Trig)
                                else:
                                    eos_log.info("Solar trigger NOT sent :" + reason)

                        if Relays.Comp == "<=":
                            if  float(AOS.sr_avg) <= Relays.Value:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.On_Trig)
                                if responce == True:
                                    eos_log.info("Solar trigger sent :" + Relays.On_Trig)
                                else:
                                    eos_log.info("Solar trigger NOT sent :" + reason)
                            else:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.Off_Trig)
                                if responce == True:
                                    eos_log.info("Solar trigger sent :" + Relays.Off_Trig)
                                else:
                                    eos_log.info("Solar trigger NOT sent :" + reason)                                                        
                if Relays.Method == "RAIN":
                    if len(Relays.Site) > 0:
                        if Relays.Comp == ">=":
                            if  float(AOS.ts_sum) >= Relays.Value:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.On_Trig)
                                if responce == True:
                                    eos_log.info("Rain trigger sent :" + Relays.On_Trig)
                                else:
                                    eos_log.info("Rain trigger NOT sent :" + reason)
                            else:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.Off_Trig)
                                if responce == True:
                                    eos_log.info("Rain trigger sent :" + Relays.Off_Trig)
                                else:
                                    eos_log.info("Rain trigger NOT sent :" + reason)

                        if Relays.Comp == "<=":
                            if  float(AOS.ts_sum) <= Relays.Value:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.On_Trig)
                                if responce == True:
                                    eos_log.info("Rain trigger sent :" + Relays.On_Trig)
                                else:
                                    eos_log.info("Rain trigger NOT sent :" + reason)
                            else:
                                responce, status, reason = eosp.sendrelay(Relays.Site, Relays.Cmd, Relays.Script, Relays.Off_Trig)
                                if responce == True:
                                    eos_log.info("Rain trigger sent :" + Relays.Off_Trig)
                                else:
                                    eos_log.info("Rain trigger NOT sent :" + reason)
        except Exception,e:
                        
            eos_log.error('On Sending Trigger: ' + str(e))
    cur.close()
    
                
            
