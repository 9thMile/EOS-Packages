"""Weather related formulas"""

import math


def dewpointF(T, R) :
    """Calculate dew point. 
    
    T: Temperature in Fahrenheit
    
    R: Relative humidity in percent.
    
    Returns: Dewpoint in Fahrenheit
    Examples:
    
    >>> print "%.1f" % dewpointF(68, 50)
    48.7
    >>> print "%.1f" % dewpointF(32, 50)
    15.5
    >>> print "%.1f" % dewpointF(-10, 50)
    -23.5
    """

    if T is None or R is None :
        return None

    TdC = dewpointC((T - 32.0)*5.0/9.0, R)

    return TdC * 9.0/5.0 + 32.0 if TdC is not None else None

def dewpointC(T, R):
    """Calculate dew point. From http://en.wikipedia.org/wiki/Dew_point
    
    T: Temperature in Celsius
    
    R: Relative humidity in percent.
    
    Returns: Dewpoint in Celsius
    """

    if T is None or R is None :
        return None
    R = R / 100.0
    try:
        _gamma = 17.27 * T / (237.7 + T) + math.log(R)
        TdC = 237.7 * _gamma / (17.27 - _gamma)
    except (ValueError, OverflowError):
        TdC = None
    return TdC

def windchillF(T_F, V_mph) :
    """Calculate wind chill. From http://www.nws.noaa.gov/om/windchill
    
    T_F: Temperature in Fahrenheit
    
    V_mph: Wind speed in mph
    
    Returns Wind Chill in Fahrenheit
    """
    
    if T_F is None or V_mph is None:
        return None

    # Formula only valid for temperatures below 50F and wind speeds over 3.0 mph
    if T_F >= 50.0 or V_mph <= 3.0 : 
        return T_F
    WcF = 35.74 + 0.6215 * T_F + (-35.75  + 0.4275 * T_F) * math.pow(V_mph, 0.16) 
    return WcF

def windchillC(T_C, V_kph):
    """Wind chill, metric version.
    
    T: Temperature in Celsius
    
    V: Wind speed in kph
    
    Returns wind chill in Celsius"""
    
    if T_C is None or V_kph is None:
        return None
    
    T_F = T_C * (9.0/5.0) + 32.0
    V_mph = 0.621371192 * V_kph
    
    WcF = windchillF(T_F, V_mph)
    
    return (WcF - 32.0) * (5.0 / 9.0) if WcF is not None else None
    
def heatindexF(T, R) :
    """Calculate heat index. From http://www.crh.noaa.gov/jkl/?n=heat_index_calculator
    
    T: Temperature in Fahrenheit
    
    R: Relative humidity in percent
    
    Returns heat index in Fahrenheit
    
    Examples:
    
    >>> print heatindexF(75.0, 50.0)
    75.0
    >>> print heatindexF(80.0, 50.0)
    80.8029049
    >>> print heatindexF(80.0, 95.0)
    86.3980618
    >>> print heatindexF(90.0, 50.0)
    94.5969412
    >>> print heatindexF(90.0, 95.0)
    126.6232036

    """
    if T is None or R is None :
        return None
    
    # Formula only valid for temperatures over 80F:
    if T < 80.0 or R  < 40.0:
        return T

    hiF = -42.379 + 2.04901523 * T + 10.14333127 * R - 0.22475541 * T * R - 6.83783e-3 * T**2\
    -5.481717e-2 * R**2 + 1.22874e-3 * T**2 * R + 8.5282e-4 * T * R**2 - 1.99e-6 * T**2 * R**2
    if hiF < T :
        hiF = T
    return hiF

def heatindexC(T_C, R):
    if T_C is None or R is None :
        return None
    T_F = T_C * (9.0/5.0) + 32.0
    hiF = heatindexF(T_F, R)
    return (hiF - 32.0) * (5.0/9.0)


def thwC(Ta,rh,Wf):
    if Ta is None or rh is None or Wf is None:
        return None
    e = rh/100 * 6.105 **(17.27 * Ta/(237.7 + Ta))
    AT = Ta + .33*e - .7 * Wf - 4.25
    return round(AT,1)

def thwsC(Ta, rh, Wf, Q):
    if Ta is None or rh is None or Wf is None or Q is None:
        return None
    e = rh/100 * 6.105 **(17.27 * Ta/(237.7 + Ta))
    AT = Ta + .348*e - .7 * Wf + .7 * Q/(Wf + 10) - 4.25
    return round(AT,1)

def heating_degrees(t, base, dInt):
    return max(round((float(base) - t) * dInt / 1440,3), 0) if t is not None else None

def cooling_degrees(t, base, dInt):
    return max(round((t - float(base)) * dInt / 1440,3), 0) if t is not None else None


def windrun(Ws,dInt):
    """Calculate wind run (speed for duration) """
    return round(float(Ws) * (float(dInt)/60),2) if Ws is not None else None

def _etterm(elev_meter, t_C):
    """Calculate elevation/temperature term for sea level calculation."""
    if elev_meter is None or t_C is None:
        return None
    t_K = t_C + 273.15
    return math.exp( - elev_meter / (t_K * 29.263))

def sealevel_pressure_Metric(sp_mbar, elev_meter, t_C):
    """Convert station pressure to sea level pressure.  This implementation
    was copied from wview.

    sp_mbar - station pressure in millibars

    elev_meter - station elevation in meters

    t_C - temperature in degrees Celsius

    bp - sea level pressure (barometer) in millibars
    """

    pt = _etterm(elev_meter, t_C)
    if sp_mbar is None or pt is None:
        return None
    bp_mbar = sp_mbar / pt if pt != 0 else 0
    return bp_mbar

def calculate_rain(newtotal, oldtotal):
    """Calculate the rain differential given two cumulative measurements."""
    if newtotal is not None and oldtotal is not None:
        if newtotal >= oldtotal:
            delta = newtotal - oldtotal
        else:
            delta = None
    else:
        delta = None
    return delta

def calculate_rain_rate(delta, curr_ts, last_ts):
    """Calculate the rain rate based on the time between two rain readings.

    delta: rainfall since last reading, in units of x

    curr_ts: timestamp of current reading, in seconds

    last_ts: timestamp of last reading, in seconds

    return: rain rate in x per hour

    If the period between readings is zero, ignore the rainfall since there
    is no way to calculate a rate with no period."""

    if curr_ts is None:
        return None
    if last_ts is None:
        last_ts = curr_ts
    if delta is not None:
        period = curr_ts - last_ts
        if period != 0:
            rate = 3600 * delta / period
        else:
            rate = None
    else:
        rate = None
    return rate

