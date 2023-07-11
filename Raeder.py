import sys
import signal
import time
import os
from time import sleep
import RPi.GPIO as GPIO

mode=GPIO.getmode()

GPIO.setwarnings(False)
HRPWM=32
HRIN1=8
HRIN2=10
VRPWM=12
VRIN1=3
VRIN2=5
HLPWM=35
HLIN1=11
HLIN2=16
VLPWM=33
VLIN1=15
VLIN2=13
sleeptime=3


frontLed = 37
backLed = 38
GPIO.setmode(GPIO.BOARD)
GPIO.setup(frontLed, GPIO.OUT)
GPIO.setup(backLed, GPIO.OUT)

GPIO.setup(HRIN1, GPIO.OUT)
GPIO.setup(HRIN2, GPIO.OUT)

GPIO.setup(VRIN1, GPIO.OUT)
GPIO.setup(VRIN2, GPIO.OUT)

GPIO.setup(HLIN1, GPIO.OUT)
GPIO.setup(HLIN2, GPIO.OUT)

GPIO.setup(VLIN1, GPIO.OUT)
GPIO.setup(VLIN2, GPIO.OUT)

GPIO.setup(VLPWM, GPIO.OUT)
GPIO.setup(HLPWM, GPIO.OUT)
GPIO.setup(VRPWM, GPIO.OUT)
GPIO.setup(HRPWM, GPIO.OUT)

vl = GPIO.PWM(VLPWM, 1000)
hl = GPIO.PWM(HLPWM, 1000)
vr = GPIO.PWM(VRPWM, 1000)
hr = GPIO.PWM(HRPWM, 1000)

vl.start(0)
hl.start(0)
vr.start(0)
hr.start(0)

def handler(signnum, frame):
    print("Got Signale")
    os.kill(os.getpid(), signal.SIGINT)
    

signal.signal(signal.SIGINT, handler)

def rueckw():  
    GPIO.output(HLIN1, GPIO.HIGH)
    GPIO.output(VLIN1, GPIO.HIGH)
    GPIO.output(VRIN2, GPIO.HIGH)
    GPIO.output(HRIN2, GPIO.HIGH)

    
    GPIO.output(HLIN2, GPIO.LOW)
    GPIO.output(VLIN2, GPIO.LOW)
    GPIO.output(HRIN1, GPIO.LOW)
    GPIO.output(VRIN1, GPIO.LOW)

def vorw():
    GPIO.output(VRIN1, GPIO.HIGH)
    GPIO.output(HLIN2, GPIO.HIGH)
    GPIO.output(VLIN2, GPIO.HIGH)
    GPIO.output(HRIN1, GPIO.HIGH)

    
    GPIO.output(HLIN1, GPIO.LOW)
    GPIO.output(VLIN1, GPIO.LOW)
    GPIO.output(VRIN2, GPIO.LOW)
    GPIO.output(HRIN2, GPIO.LOW)

def vorneLinks(wert):
    vl.ChangeDutyCycle(wert)
   

def hintenLinks(wert):
    hl.ChangeDutyCycle(wert)

def hintenRechts(wert):
    hr.ChangeDutyCycle(wert)

def vorneRechts(wert):
    vr.ChangeDutyCycle(wert)
    


def stop():
    vr.ChangeDutyCycle(0)
    hl.ChangeDutyCycle(0)
    vl.ChangeDutyCycle(0)
    hr.ChangeDutyCycle(0)
    # print("Das sogenannte stop wurde aufgerufen")

def drive(wert):
    stop()
    vorw()
    vorneRechts(wert)
    hintenRechts(wert)
    hintenLinks(wert)
    vorneLinks(wert)

def wenden(wert):
    stop()
    

def driveR(wert):
    stop()
    rueckw()
    vorneRechts(wert)
    hintenRechts(wert)
    hintenLinks(wert)
    vorneLinks(wert)

def turnL(wert):
    erg = (10-(wert/1.8))
    if(erg<0):
        erg=0
    stop()
    hintenLinks(erg)
    vorneLinks(erg)
    hintenRechts(wert)
    vorneRechts(wert)

def turnR(wert):
    erg = (10-(wert/1.8))
    if(erg<0):
        erg=0
    stop()
    hintenLinks(wert)
    vorneLinks(wert)
    hintenRechts(erg)
    vorneRechts(erg)

def turnHL(wert):
    erg = (50-(wert/1.8))
    if(erg<0):
        erg=0
    stop()
    hintenLinks(erg)
    vorneLinks(erg)
    hintenRechts(wert)
    vorneRechts(wert)

def turnHR(wert):
    erg = (50-(wert/1.8))
    if(erg<0):
        erg=0
    stop()
    hintenLinks(wert)
    vorneLinks(wert)
    hintenRechts(erg)
    vorneRechts(erg)

def straightR(wert):
    stop()
    GPIO.output(VRIN1, GPIO.LOW)
    GPIO.output(HLIN2, GPIO.LOW)
    GPIO.output(VLIN2, GPIO.HIGH)
    GPIO.output(HRIN1, GPIO.HIGH)
    
    GPIO.output(HLIN1, GPIO.HIGH)
    GPIO.output(VLIN1, GPIO.LOW)
    GPIO.output(VRIN2, GPIO.HIGH)
    GPIO.output(HRIN2, GPIO.LOW)

    vorneRechts(wert)
    hintenRechts(wert)
    hintenLinks(wert)
    vorneLinks(wert)

def straightL(wert):
    stop()
    GPIO.output(VRIN1, GPIO.HIGH)
    GPIO.output(HLIN2, GPIO.HIGH)
    GPIO.output(VLIN2, GPIO.LOW)
    GPIO.output(HRIN1, GPIO.LOW)

    
    GPIO.output(HLIN1, GPIO.LOW)
    GPIO.output(VLIN1, GPIO.HIGH)
    GPIO.output(VRIN2, GPIO.LOW)
    GPIO.output(HRIN2, GPIO.HIGH)

    vorneRechts(wert)
    hintenRechts(wert)
    hintenLinks(wert)
    vorneLinks(wert)

def diagVR(wert):
    stop()
    vorw()
    vorneRechts()
    hintenLinks()

def diagVL(wert):
    stop()
    vorw()
    vorneLinks()
    hintenRechts()

def diagVR(wert):
    stop()
    vorw()
    vorneRechts()
    hintenLinks()

def diagHL(wert):
    stop()
    rueckw()
    vorneRechts()
    hintenLinks()

def diagHR(wert):
    stop()
    rueckw()
    vorneLinks()
    hintenRechts()

def ledEin():
    GPIO.output(frontLed, GPIO.HIGH)
    GPIO.output(backLed, GPIO.HIGH)

def ledAus():
    GPIO.output(frontLed,GPIO.LOW)
    GPIO.output(backLed,GPIO.LOW)

