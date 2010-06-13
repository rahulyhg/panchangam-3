#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import math
import swisseph
from datetime import *
import pytz
from pytz import timezone
from skt_names import *

# FUNCTION DEFINITIONS

def sexa2deci(hour,minute=0.0,second=0.0):
  return hour*1.0+minute/60.0+second/3600.0

def sexastr2deci(str):
  if (str[0]=='-'):
    sgn = -1.0
    hms = str[1:].split(':')
  else:
    sgn = 1.0
    hms = str.split(':')
 
  decival = 0
  for i in range(0,len(hms)):
    decival = decival + float(hms[i])/(60.0**i)

  return decival*sgn

def deci2sexa(d):
  hour = math.floor(d)
  d = d-hour
  minute = math.floor(d*60.0)
  d = d-minute
  second = round(d*60)
  return [hour,minute,second]

def print_time (d):
  [h,m,s]=deci2sexa(d)
  return '%02d:%02d' % (h,m)

def get_last_dhanur_transit (jd_start,latitude,longitude):
  swisseph.set_sid_mode(swisseph.SIDM_LAHIRI) #Force Lahiri Ayanamsha
  for d in range(-25,0):
    jd = jd_start + d
    [y,m,d,t] = swisseph.revjul(jd)
  
    jd_rise=swisseph.rise_trans(jd_start=jd,body=swisseph.SUN,lon=longitude,
      lat=latitude,rsmi=swisseph.CALC_RISE|swisseph.BIT_DISC_CENTER)[1][0]
    jd_rise_tmrw=swisseph.rise_trans(jd_start=jd+1,body=swisseph.SUN,
      lon=longitude,lat=latitude,rsmi=swisseph.CALC_RISE|swisseph.BIT_DISC_CENTER)[1][0]
    jd_set =swisseph.rise_trans(jd_start=jd,body=swisseph.SUN,lon=longitude,
      lat=latitude,rsmi=swisseph.CALC_SET|swisseph.BIT_DISC_CENTER)[1][0]
  
    longitude_sun=swisseph.calc_ut(jd_rise,swisseph.SUN)[0]-swisseph.get_ayanamsa(jd_rise)
    longitude_sun_set=swisseph.calc_ut(jd_set,swisseph.SUN)[0]-swisseph.get_ayanamsa(jd_set)
    sun_month_rise = masa_names[int(1+math.floor(((longitude_sun)%360)/30.0))]
    sun_month = masa_names[int(1+math.floor(((longitude_sun_set)%360)/30.0))]
    longitude_sun_tmrw=swisseph.calc_ut(jd_rise+1,swisseph.SUN)[0]-swisseph.get_ayanamsa(jd_rise+1)
    sun_month_tmrw = masa_names[int(1+math.floor(((longitude_sun_tmrw)%360)/30.0))]

    if sun_month_rise!=sun_month_tmrw:
      if sun_month!=sun_month_tmrw:
        return jd+1
      else:
        return jd
  
def print_end_time (end_time, day_night_length, rise_time):
  if end_time/24.0>day_night_length:
    end_time_str = '\\textsf{अहोरात्रम्}'
  else:
    te=deci2sexa(rise_time+end_time)
    if te[0]>=24:
      suff = '(+1)'
      te[0] = te[0]-24
    else:
      suff = '\\hspace{2ex}'
    end_time_str = '%02d:%02d%s' % (te[0],te[1],suff)
  return end_time_str

def get_angam_data_string(angam_names, arc_len, jd_rise, jd_rise_tmrw, 
  t_rise, longitude_moon, longitude_sun, longitude_moon_tmrw, 
  longitude_sun_tmrw, w):

  daily_motion_moon = (longitude_moon_tmrw-longitude_moon)%360
  daily_motion_sun = (longitude_sun_tmrw-longitude_sun)%360

  num_angas = int(360.0/arc_len)
  angam = [0]*3
  angam_str = ['']*3
  angam_end_str = ['']*3
  angam_end = [0]*3
  angam_remaining = [0]*3

  #Compute karanam details
  angam[0] = int(1+math.floor((longitude_moon*w[0]+longitude_sun*w[1])%360 / arc_len))
  angam_tmrw = int(1+math.floor((longitude_moon_tmrw*w[0]+longitude_sun_tmrw*w[1])%360 / arc_len))

  # There cannot be more than 3 angams (max=3 for karanams) in a day, 
  # because of total arc ~ 12 deg and arclen per angam
  for i in range(0,3):
    if ((angam_tmrw-angam[0])%num_angas > i) or (i==0): #i=0 must be considered, because the angam may not change till the next sunrise
      #multiple change
      angam[i]=((angam[0]+(i-1))%num_angas)+1
      angam_str[i] = angam_names[angam[i]]
      angam_remaining[i] = arc_len*(i+1)-(((longitude_moon*w[0]+
        longitude_sun*w[1])%360)%arc_len)
      angam_end[i] = angam_remaining[i]/(daily_motion_moon*w[0]+
        daily_motion_sun*w[1])*24.0
      angam_end_str[i] = print_end_time(angam_end[i],jd_rise_tmrw-jd_rise,t_rise)
    else:
      angam_str[i] = ''
      angam_end_str[i] = ''
      
    if (angam_end_str[i] == '\\textsf{अहोरात्रम्}' and i!=0):
      #needs correction, owing to the fact that we compute longitude every 24h,
      #rather than at next sunrise the second/third angam cannot be 'all day'!
      #It's ending will reflect in tomorrow's calendar
      angam_str[i] = ''
      angam_end_str[i] = ''


  angam_data_string=''
  for i in range(0,3):
    if angam_str[i] != '': 
      if i==2:
        angam_data_string = angam_data_string+'\\\\'
      angam_data_string = '%s\\mbox{\\textsf{%s} {\\tiny \\RIGHTarrow} %s}' \
        % (angam_data_string,angam_str[i],angam_end_str[i])
    
  return angam_data_string

#USEFUL 'constants'
yamakandam_octets  = [5,4,3,2,1,7,6]
rahukalam_octets = [8,2,7,5,6,4,3]
#wday = {'Mon':1, 'Tue':2,'Wed':3, 'Thu':4, 'Fri':5, 'Sat':6, 'Sun':0}
#daycol = {0:'red',1:'blue',2:'blue',3:'blue',4:'blue',5:'blue',6:'red'}
daycol = {0:'blue',1:'blue',2:'blue',3:'blue',4:'blue',5:'blue',6:'blue'}

month = {1:'JANUARY', 2:'FEBRUARY', 3:'MARCH', 4:'APRIL', 5:'MAY', 6:'JUNE', 7:'JULY', 8:'AUGUST', 9:'SEPTEMBER', 10:'OCTOBER', 11: 'NOVEMBER', 12:'DECEMBER'}

#MAIN CODE
def main():
  city_name = sys.argv[1]
  latitude = sexastr2deci(sys.argv[2])
  longitude = sexastr2deci(sys.argv[3])
  tz = sys.argv[4]
  
  start_year = int(sys.argv[5])
  year = start_year
  jd=swisseph.julday(year,1,1,0)
  jd_start=jd
  
  swisseph.set_sid_mode(swisseph.SIDM_LAHIRI) #Force Lahiri Ayanamsha
  
  sun_month_day = jd-get_last_dhanur_transit(jd,latitude,longitude)
  
  month_start_after_set = 0
  
  template_file=open('cal_template_compre.tex')
  template_lines=template_file.readlines()
  for i in range(0,len(template_lines)-3):
    print template_lines[i][:-1]
  
  samvatsara_id = (year - 1568)%60 + 1; #distance from prabhava
  samvatsara_names = '%s–%s' % (year_names[samvatsara_id], 
    year_names[(samvatsara_id%60)+1])
  
  print '\\mbox{}'
  print '{\\font\\x="Warnock Pro" at 60 pt\\x %d\\\\[0.3cm]}' % year
  print '\\mbox{\\font\\x="Sanskrit 2003:script=deva" at 48 pt\\x %s}\\\\[0.5cm]' % samvatsara_names
  print '{\\font\\x="Warnock Pro" at 48 pt\\x \\uppercase{%s}\\\\[0.3cm]}' % city_name
  print '\hrule'


  #INITIALISE VARIABLES
  jd_rise=[None]*368
  jd_set=[None]*368
  longitude_moon=[None]*368
  longitude_sun=[None]*368
  longitude_sun_set=[None]*368
  sun_month=[None]*368
  sun_month_rise=[None]*368
  month_data=[None]*368
  tithi_data_string=[None]*368
  nakshatram_data_string=[None]*368
  karanam_data_string=[None]*368
  yogam_data_string=[None]*368
  weekday=[None]*368
  sunrise=[None]*368
  sunset=[None]*368
  madhya=[None]*368
  rahu=[None]*368
  yama=[None]*368
  
  weekday_start=swisseph.day_of_week(jd)+1
  #swisseph has Mon = 0, non-intuitively!
  
  for d in range(0,367):
    jd = jd_start-1+d
    [y,m,dt,t] = swisseph.revjul(jd)
    weekday = (weekday_start -1 + d)%7 
  
    local_time = pytz.timezone(tz).localize(datetime(y, m, dt, 6, 0, 0))
    #checking @ 6am local - can we do any better?
    tz_off=datetime.utcoffset(local_time).seconds/3600.0 
    #compute offset from UTC

    jd_rise[d+1]=swisseph.rise_trans(jd_start=jd+1,body=swisseph.SUN,
      lon=longitude,lat=latitude,rsmi=swisseph.CALC_RISE|swisseph.BIT_DISC_CENTER)[1][0]
    jd_set[d+1]=swisseph.rise_trans(jd_start=jd+1,body=swisseph.SUN,
      lon=longitude,lat=latitude,rsmi=swisseph.CALC_SET|swisseph.BIT_DISC_CENTER)[1][0]
  
    longitude_sun[d+1]=swisseph.calc_ut(jd_rise[d+1],swisseph.SUN)[0]-swisseph.get_ayanamsa(jd_rise[d+1])
    longitude_moon[d+1]=swisseph.calc_ut(jd_rise[d+1],swisseph.MOON)[0]-swisseph.get_ayanamsa(jd_rise[d+1])
    longitude_sun_set[d+1]=swisseph.calc_ut(jd_set[d+1],swisseph.SUN)[0]-swisseph.get_ayanamsa(jd_set[d+1])
    
    sun_month[d+1] = masa_names[int(1+math.floor(((longitude_sun_set[d+1])%360)/30.0))]

    sun_month_rise[d+1] = masa_names[int(1+math.floor(((longitude_sun[d+1])%360)/30.0))]

    if(d==0):
      continue

    t_rise=(jd_rise[d]-jd)*24.0+tz_off;
    t_set=(jd_set[d]-jd)*24.0+tz_off;

  
    #Solar month calculations
    if month_start_after_set==1:
      sun_month_day = 0
      month_start_after_set = 0
  
    if sun_month[d]!=sun_month[d+1]:
      sun_month_day = sun_month_day + 1

      if sun_month[d]!=sun_month_rise[d+1]:
        month_start_after_set=1
        sun_month_end_time = get_angam_data_string(masa_names, 30, jd_rise[d],
          jd_rise[d+1], t_rise, longitude_moon[d], longitude_sun[d], longitude_moon[d+1],
          longitude_sun[d+1], [0,1])
 
    elif sun_month_rise[d]!=sun_month[d]:
      #mAsa pirappu!
      #sun moves into next rAsi before sunset -- check rules!
      sun_month_day = 1

      sun_month_end_time = get_angam_data_string(masa_names, 30, jd_rise[d],
      jd_rise[d+1], t_rise, longitude_moon[d], longitude_sun[d], longitude_moon[d+1],
      longitude_sun[d+1], [0,1])
    
    else:
      sun_month_day = sun_month_day + 1
      sun_month_end_time = ''
    
    month_data[d] = '\\sunmonth{%s}{%d}{%s}' % (sun_month[d],sun_month_day,
      sun_month_end_time)
  
    #Sunrise/sunset and related stuff (like rahu, yama)
    [rh, rm, rs] = deci2sexa(t_rise) #rise_t hour, rise minute
    [sh, sm, ss] = deci2sexa(t_set) #set_t hour, set minute
  
    length_of_day = t_set-t_rise
    yamakandam_start = t_rise + (1/8.0)*(yamakandam_octets[weekday]-1)*length_of_day
    yamakandam_end = yamakandam_start + (1/8.0)*length_of_day
    rahukalam_start = t_rise + (1/8.0)*(rahukalam_octets[weekday]-1)*length_of_day
    rahukalam_end = rahukalam_start + (1/8.0)*length_of_day
    madhyahnikam_start = t_rise + (1/5.0)*length_of_day
  
    sunrise[d] = '%02d:%02d' % (rh,rm)
    sunset[d] = '%02d:%02d' % (sh,sm)
    madhya[d] = print_time(madhyahnikam_start)
    rahu[d] = '%s--%s' % (print_time(rahukalam_start), print_time(rahukalam_end))
    yama[d] = '%s--%s' % (print_time(yamakandam_start),print_time(yamakandam_end))
    
    tithi_data_string[d]=get_angam_data_string(tithi_names, 12, jd_rise[d],
      jd_rise[d+1], t_rise, longitude_moon[d], longitude_sun[d], longitude_moon[d+1],
      longitude_sun[d+1], [1,-1])
    nakshatram_data_string[d]=get_angam_data_string(nakshatra_names, (360.0/27.0),
      jd_rise[d], jd_rise[d+1], t_rise, longitude_moon[d], longitude_sun[d], 
      longitude_moon[d+1], longitude_sun[d+1], [1,0])
    karanam_data_string[d]=get_angam_data_string(karanam_names, 6, jd_rise[d],
      jd_rise[d+1], t_rise, longitude_moon[d], longitude_sun[d], longitude_moon[d+1],
      longitude_sun[d+1], [1,-1])
    yogam_data_string[d]=get_angam_data_string(yogam_names, (360.0/27.0), jd_rise[d],
      jd_rise[d+1], t_rise, longitude_moon[d], longitude_sun[d], longitude_moon[d+1],
      longitude_sun[d+1], [1,1])

  for d in range(1,367):
    jd = jd_start-1+d
    [y,m,dt,t] = swisseph.revjul(jd)
    weekday = (weekday_start -1 + d)%7 

    #Layout calendar in LATeX format
    if dt==1:
      if m>1:
        if weekday!=0: #Space till Sunday
          for i in range(weekday,6):
            print "{}  &"
          print "\\\\ \hline"
        print '\end{tabular}'
        print '\n\n'
  
      #Begin tabular
      print '\\begin{tabular}{|c|c|c|c|c|c|c|}'
      print '\multicolumn{7}{c}{\Large \\bfseries %s %s}\\\\[3mm]' % (month[m],y)
      print '\hline'
      print '\\textbf{SUN} & \\textbf{MON} & \\textbf{TUE} & \\textbf{WED} & \\textbf{THU} & \\textbf{FRI} & \\textbf{SAT} \\\\ \hline'
      #print '\\textbf{भानु} & \\textbf{इन्दु} & \\textbf{भौम} & \\textbf{बुध} & \\textbf{गुरु} & \\textbf{भृगु} & \\textbf{स्थिर} \\\\ \hline'
  
      #Blanks for previous weekdays
      for i in range(0,weekday):
        print "{}  &"

    print '\caldata{\\textcolor{%s}{%s}}{%s}{\\sundata{%s}{%s}{%s}}{\\tnyk{%s}{%s}{%s}{%s}}{\\textsf{राहु}~%s~~\\textsf{यम}~%s} ' % (daycol[weekday],
      dt,month_data[d],sunrise[d],sunset[d],madhya[d],tithi_data_string[d],nakshatram_data_string[d],
      yogam_data_string[d],karanam_data_string[d],rahu[d],yama[d])
  
    if weekday==6:
      print "\\\\ \hline"
    else:
      print "&"
  
    if m==12 and dt==31:
      break
  
    # For debugging specific dates
    #if m==4 and dt==10:
    #  break
  
  for i in range(weekday+1,6):
    print "{}  &"
  if weekday!=6:
    print "\\\\ \hline"
  print '\end{tabular}'
  print '\n\n'
  
  print template_lines[-2][:-1]
  print template_lines[-1][:-1]

if __name__=='__main__':
  main()
else:
  '''Imported as a module'''
