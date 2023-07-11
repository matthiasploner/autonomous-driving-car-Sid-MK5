import sys
import signal
import time
import os
from Raeder import ledAus
from Raeder import ledEin
from time import sleep
import RPi.GPIO as GPIO

frontLed = 37
backLed = 38


lightinp = 31
GPIO.setmode(GPIO.BOARD)    
GPIO.setup(lightinp, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(frontLed, GPIO.OUT)
GPIO.setup(backLed, GPIO.OUT)


def handler(signnum, frame):
    print("Got Signale")
    os.kill(os.getpid(), signal.SIGINT)
    
signal.signal(signal.SIGINT, handler)

ledAus()
def autonom_fert():
    ledAus()

def licht_eigen():
    print(getState())
    if(getState() == 0):
        ledEin()
    elif(getState() == 1):
        ledAus()
        
def licht():
    if(os.path.exists("autonom_config.txt")):
        print("autonom")
        ledEin()
    elif(os.path.exists("light_config.txt")):
         print("licht Automatisch")
         lichtA()
    else:
        print("licht_eigen wird ausgeführt")
        licht_eigen()
def lichtA():
    ledAus()
    previous=0
    while(os.path.exists("light_config.txt")):
        wert = GPIO.input(lightinp)
        print(wert)
        if (wert==1 and getState() ==0 and previous == 1):
            ledEin()
        elif (wert == 0 and getState() == 1 and previous == 0):
            ledAus()
        sleep(.7)
        previous = wert
    ledAus()

def getState():
    if GPIO.input(frontLed) == GPIO.HIGH:
      return 1
    else:
      return 0
    
def ledEin():
    GPIO.output(frontLed, GPIO.HIGH)
    GPIO.output(backLed, GPIO.HIGH)

def ledAus():
    GPIO.output(frontLed,GPIO.LOW)
    GPIO.output(backLed,GPIO.LOW)
licht()
