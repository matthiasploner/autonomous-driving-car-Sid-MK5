import sys
import signal
import time
import os
import RPi.GPIO as GPIO
 
#GPIO Modus (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)
 
#GPIO Pins zuweisen
Messung_max = 1
TRIGGER = 7
UVR = 21
UVL = 23
UHR = 40
UHL =36
 
#Richtung der GPIO-Pins festlegen (IN / OUT)
GPIO.setup(TRIGGER, GPIO.OUT)
GPIO.setup(UVR, GPIO.IN)
GPIO.setup(UVL, GPIO.IN)
GPIO.setup(UHL, GPIO.IN)
GPIO.setup(UHR, GPIO.IN)

def handler(signnum, frame):
    print("Got Signale")
    os.kill(os.getpid(), signal.SIGINT)
    
signal.signal(signal.SIGINT, handler)
pins = [UVL, UVR, UHL, UHR]

def getDistance():
	#while(True):
    #Alles wird von rechts nach links und oben nach unten angegeben
    #Array aufbau VL VR HL HR
    abV = [0,0,0,0]
    for var in range(0,4):
        GPIO.output(TRIGGER, GPIO.HIGH)
        
        time.sleep(0.00001)
        GPIO.output(TRIGGER, GPIO.LOW)
        
        StartZeit = time.time()
        MaxZeit= StartZeit+ Messung_max

        while StartZeit < MaxZeit and GPIO.input (pins[var]) == GPIO.LOW:
            StartZeit = time.time()

        StopZeit = StartZeit
        while StopZeit < MaxZeit and GPIO.input(pins[var]) == GPIO.HIGH:
            StopZeit = time.time()
            
        if StopZeit < MaxZeit:                                                                                                                  
            diff = StopZeit - StartZeit
            abV[var] =round((diff *34300)/2)
        else:
            abV[var] = 0
        time.sleep(0.1)
    
    #print("VR: " + str(abV[0]) + "      VL: " + str(abV[1]) + "     HL: " + str(abV[2]) + "     HR: " + str(abV[3]))
    
    return abV
