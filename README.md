Python helper for Raspberry RPI Cam control + Web tweaks

RPI Cam control is an easy to set up Raspberry Camera set up with web interface

http://elinux.org/RPi-Cam-Web-Interface

It ties in with motion as a motion detector and accepts commands via a named PIPE which
is used by the web interface.

RaspiCam.py is a simple utility to provide a bit more automation using the same PIPE commands.

Main goal is to switch on and off the motion detection so that it is active mainly during the day.
It also switches the camera into night mode during dusk and dawn to help extend its utility.

It is set up so that it is easy to modify to send different commands.

The timing of the commands is arranged around a calculation of sun-rise and sunset.
This is based upon the latitude and longtitude of the site and the time of year.
This means it will adjust automatically as daylight changes.

INSTALL

There are 3 python files, RaspiCam.py and two support libraries which should all be placed in
/home/pi/python

The program can be run manually by python RaspiCam.py when in that folder but it is more convenient
to make it start automatically at boot time. To do this use the RaspiCam file in the boot folder.
Copy it into home and then from there issue the following commands

sudo cp RaspiCam /etc/init.d/RaspiCam

sudo chmod 755 /etc/init.d/RaspiCam

sudo update-rc.d RaspiCam defaults

It will then start at boot or can be manually started and stopped by

sudo /etc/init.d/RaspiCam start

sudo /etc/init.d/RaspiCam stop

To remove it from the boot then

sudo update-rc.d -f RaspiCam remove

The motion detection then needs to be altered so that it is directed through RaspiCam.py
To do this edit /etc/motion/motion.conf and change the two event lines

on_event_start echo -n '1' >/home/pi/python/FIFO

on_event_end echo -n '0' >/home/pi/python/FIFO

RUNNING

When RaspiCam.py is running it is monitoring the capture commands from motion and also the
period of the day it is in. This is split into 4 periods Night, Dawn,Day and Dusk.

Actions are then performed when the period of the day changes and also the capture start and end
commands can also be varied. So for example, motion detecton could be used just for the day period,
or it could be used during Dawn, Dusk and Day. Similarly video could be used during day and
time lapse or single image during dawn and dusk.

RaspiCam creates and uses a FIFO to get the motion requests and sends commands to the normal RPi Cam
FIFO

It also logs its activity to RaspiCamLog in the python folder.

CONFIG

This is done just by editing the RaspiCam.py file. If it is running then it will need to be stopped
and started to take effect. See Install.
LATITUDE, LONGTITUDE need to be set for the location + is N and E, - is S and W
DUSK and DAWN extend the periods from Sunrise and Sunset in seconds. So if DUSK is 3600 then it will be the 1 hour
from Sunset, and if Dawn is 3600 then it will be 1 hour before Sunrise.

Three Command arrays then determine what is sent to RaspiMJPEG
COMMANDS_PERIODS determines the commands sent during the transition to the 4 daily periods
Night, Dawn, Day, Dusk

COMMANDS_ON determines the capture command sent for a motion trigger during each of the daily periods

COMMANDS_OFF determines what capture off command is sent determined by the last COMMANDS_ON used.

Note that if there is a transition between say day and dusk whilst capture is active then the COMMAND_OFF
still corresponds to the start command used to begin the capture.

The RaspiMJPEG-Commands.txt lists the possible commands that can be sent.

WEB TWEAKS
This is independent of the Python helper. Either can be used separately or both together.
The www folder contains an updated preview.php to replace the existing one in /var/www
together with a couple of icon files.

This changes the look of the file list you get when
pushing the Download files. Instead of a list of the filenames. This is parsed into a table
making it a little clearer and allowing more rapid delete of individual files.
Images recorded are displayed as thumbnails.

Videos recorded after motion detection can also have a thumbnail of their first capture frame.
To do this requires a couple of config lines in motion.conf to be edited.

output_normal first

target_dir /var/www/media

jpeg_filename vthumb_%Y%m%d_%H%M%S

These allow motion to put a thumbnail into the media folder when triggered.
The new preview.php associates these with the corresponding recording.


Changes 14th Feb 2015
Added web tweaks files to give a tabular view of recorded material.

Changes 15th Feb 2015
More web tweaks. Thumbnails are now generated for manually recorded images
and videos using ffmpeg. This avoids downloading and resizing images in the
browser. It can give a delay when going into the list if new material needs
to be thumbnailed, but after that it is faster.
