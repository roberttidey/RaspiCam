#!/usr/bin/env python
# 2015-02-10
# RaspiCam.py
# R.J. Tidey
"""
Support routine for Ras Pi Cam project
This is designed to be running all the time
It can send RPi commands to switch modes at different times of the day
The original triggers in /etc/motion/motion.conf
on_event_start echo 'ca 1'  > /var/www/FIFO
on_event_end echo 'ca 0' > /var/www/FIFO
should be replaced with
on_event_start echo '1' > /home/pi/RPI
on_event_end echo '0' > /home/pi/RPI
where this RPI fifo is in the home pi folder

This routine splits the 24 hour cycle up into the following periods
DUSK - from Sunset to Late at night
DAWN     - From Early in Morning to SunRise
DAYTIME  - From SunRise to Sunset
NIGHTTIME- From end of TWILIGHT to beginning of Dawn

The event triggers on and off can they behave differently in these periods.
A set of on  and off commands is provided for each period

Motion detection is left permanently enabled and for periods where no action is required then
this program sends no capture commands
"""
import time
import datetime
import sunrise
import os, sys
import logging

#Normally this should be True, Set it Falsee to test without sending controls to the RaspiMJPEG
SEND_CMDS = True

LATITUDE   = 51.7550
LONGTITUDE = -0.3360

# interface
FIFO_OUT   = '/var/www/FIFO'
FIFO_IN    = '/home/pi/python/FIFO'

#Duration of dusk and dawn in seconds
DUSK = 180 * 60
DAWN = 180 * 60

#Motion detection on Command Strings for different times
#COMMANDS_ON            = [[""],["tl 20"],["ca 1"],["tl 20"]]
COMMANDS_ON            = [[],[],["ca 1"],[]]
#Off commands to send in these states
COMMANDS_OFF           = [[],["tl 0", "md 1"],["ca 0"],["md 0", "tl 0", "md 1"]]

# Mode Commands to send in each period
#Night, Dawn, Day, Dusk
COMMANDS_PERIODS = [["md 0","em night"],["md 0","em night"],["md 0","em auto", "md 1"],["md 0","em night"]]

#Send one or more commands, Ensure a gap of 2 seconds between commands
def sendCmds(cmds):
   for cmd in cmds:
      if cmd != "":
         logging.info("Send " + cmd)
         if SEND_CMDS:
            fifo = open(FIFO_OUT, "w")
            fifo.write(cmd)
            fifo.close()
         time.sleep(2)

#Return period of day 0=Night,1=Dawn,2=Day,3=Dusk
def dayPeriod(d):
   oSun = sunrise.sun(lat=LATITUDE, long=LONGTITUDE)
   sr = oSun.sunrise(when=d)
   srSecs = ((sr.hour * 60) + sr.minute) * 60 + sr.second
   ss = oSun.sunset(when=d)
   ssSecs = ((ss.hour * 60) + ss.minute) * 60 + ss.second
   dSecs = ((d.hour * 60) + d.minute) * 60 + d.second
   if dSecs < (srSecs - DAWN):
      period = 0
   elif dSecs < srSecs:
      period = 1
   elif dSecs > (ssSecs + DUSK):
      period = 0
   elif dSecs > ssSecs:
      period = 3
   else:
      period = 2
   return period
   
def CheckOnOff():
    return True
    
def openPipe(pipeName):
   if not os.path.exists(pipeName):
      logging.info("Making Pipe to receive capture commands " + pipeName)
      os.mkfifo(pipeName)
   else:
      logging.info("Capture Pipe already exists " + pipeName)
   return os.open(pipeName, os.O_RDONLY|os.O_NONBLOCK)

def checkMotion(pipeHandle):
   try:
      ret = os.read(pipeHandle,1)
   except:
      ret = ""
   return ret

#Main code here, sets up, and runs forever, checking dayPeriod changes and motion detects
POLL = .03
TIME_CHECK = 10
MAX_CAPTURE = 30

logging.basicConfig(level=logging.DEBUG, filename="/home/pi/python/RaspiCamLog", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")
logging.info("RaspiCam support started")
timeCount = 0
captureCount = 0
pipeIn = openPipe(FIFO_IN)
lastDayPeriod = -1
lastOnCommand = -1

while True:
   time.sleep(POLL)
   #Check for incoming motion capture requests
   cmd = checkMotion(pipeIn)
   if cmd == "0":
      if lastOnCommand >= 0:
         logging.info("Stop capture requested")
         if not COMMANDS_OFF[lastOnCommand]:
            sendCmds(COMMANDS_OFF[lastOnCommand])
            lastOnCommand = -1
      else:
         logging.info("Stop capture request ignored, already stopped")
      captureCount = 0
   elif cmd == "1":
      if lastOnCommand < 0:
         logging.info("Start capture requested")
         if not COMMANDS_ON[lastDayPeriod]:
            sendCmds(COMMANDS_ON[lastDayPeriod])
            lastOnCommand = lastDayPeriod
      else:
         logging.info("Start capture request ignored, already started")
   elif cmd !="":
      logging.info("Ignore FIFO char " + cmd)
   
   #Action other items at TIME_CHECK intervals
   timeCount += POLL
   if timeCount > TIME_CHECK:
      timeCount = 0
      if lastOnCommand < 0:
         #No capture in progress, Check if day period changing
         captureCount = 0
         newDayPeriod = dayPeriod(datetime.datetime.now())
         if newDayPeriod != lastDayPeriod:
            logging.info("New period detected " + `newDayPeriod`)
            sendCmds(COMMANDS_PERIODS[newDayPeriod])
            lastDayPeriod = newDayPeriod
      else:
         #Capture in progress, Check for maximum
         captureCount += TIME_CHECK
         if captureCount > MAX_CAPTURE:
            logging.info("Maximum Capture reached. Sending off")
            sendCmds(COMMANDS_OFF[lastOnCommand])
            lastOnCommand = -1
            captureCount = 0
      
      
   
   
