#!/usr/bin/env python

# usage:
#   RelaunchWatchdog.py <subfile>.py
 
# This program takes a .py file which it immediately executes in a subprocess.
# It kills the subprocess and relaunches it whenever the file changes.
#
# This program is independent of the python file it launches:
# If you accidentally introduce an error into the .py file, just fix that error and save it again, and it will be relaunched.
# Note that the subprocess shared the console with this process, so you will see its output.
 
import sys,time,subprocess,logging, os, sys, watchdog, watchdog.events, watchdog.observers,psutil
from neopixel import *
import argparse
import signal
import shutil

subfile = sys.argv[1]

# THIS IS SOURCE FILE
src_file = r'code.py'

def launch():
  global process
  # create a copy of file
  datetime_var = time.strftime("%m%d%y-%H%M")
  dst_file = r'archive/code-{}.py'.format(datetime_var)
  shutil.copy2(src_file, dst_file)
  time.sleep(.1)
  # restart code
  process = subprocess.Popen(subfile, shell=True)
 
def samefile(a,b):
  return os.stat(a) == os.stat(b)
 
def kill_or_do_nothing():
  global process
  try: # Process might already have terminated
    print process
    process = psutil.Process(process.pid)
    for proc in process.children(recursive=True):
      proc.kill()
    process.kill()
  except:
    pass
     
class Modified(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event):
        if not samefile(event.src_path, subfile):
            return
         
        print subfile, 'modified, will restart'
        kill_or_do_nothing()
        launch()
 
observer = watchdog.observers.Observer()
observer.schedule(Modified(), '.')
observer.start()
 
launch()
 
# Idle forever, listening on Modified.on_modified
while True:
  time.sleep(1)