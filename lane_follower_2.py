from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from picamera import PiCamera
import time
import cv2
import numpy as np
import math
from Raeder import *
from PIL import Image
import threading

def lane_assist(frame, speed, event):
    theta=0
    minLineLength = 5
    maxLineGap = 10
    threshold=7
    
    frame = Image.fromarray(frame)
    width, height = frame.size
    crop_area = (int(width * 0.14), int(height * 0.35), int(width * 0.84), int(height * 0.82)) 
    frame = frame.crop(crop_area)#Weitwinkelbild vom Stream auf Strassenlinienerkennung zuschneiden
    frame = np.array(frame)
    
    img = frame.copy() #frame wird bei der Strassenlinierkennung veraendert
    
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 85, 85)
    lines = cv2.HoughLinesP(edged,1,np.pi/180,10,minLineLength,maxLineGap)
    if lines is not None:
        for x in range(0, len(lines)):               #Winkel der erkannten Kanten im Bild berechnen, ist unabhaengig von der Farbe
            for x1,y1,x2,y2 in lines[x]:
                cv2.line(frame,(x1,y1),(x2,y2),(0,255,0),2)
                theta=theta+math.atan2((y2-y1),(x2-x1))
    
    if not event: #wenn man auf bushaltestellen oder aehnlichen reagieren soll
        img = Image.fromarray(img)    
        if turnLine(img):
            return "turnline"   
        elif bus_middle(img) and not bus_right(img):
            return "bus_middle"
        elif bus_right(img) and not bus_middle(img):
            return "bus_right"
    
    angle_converter(theta, threshold, speed) #lenken

def angle_converter(theta, threshold, speed):
    if(theta>threshold):
        turnL(speed+5)
        print("left")
    elif(theta<-threshold):
        turnR(speed+5)
        print("right")
    elif(abs(theta)<threshold):
        drive(speed)
        print ("straight")

def turnLine(img):
    width, height = img.size
    box = (0, height * 0.6, width, height) #unteren 40% vom Bild
    img = img.crop(box)
    img = np.array(img)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv_img, lower_red, upper_red)
    lower_red = np.array([170, 50, 50])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv_img, lower_red, upper_red)
    mask = cv2.bitwise_or(mask1, mask2)
    count = np.count_nonzero(mask, axis=None)
    if count > 1500:
            return True
    else:
        return False

def bus_middle(img):
    img = np.array(img)
    height, width, _ = img.shape
    left_width = int(width * 0.3)
    right_width = int(width * 0.65)
    img = img[:, left_width:right_width]
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower_blue = np.array([100, 50, 50])        #Farberkennung mit HSV
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv_img, lower_blue, upper_blue) # Masken bild wird zurueckgegeben, wo nur die blauen stellen weiss sind, sonst alles schwarz
    # img = Image.fromarray(mask)
    # img.save("mask.jpg") 
    count = np.count_nonzero(mask, axis=None) # Anzahl der blauen Pixel
    if count > 700:
        return True
    else:
        return False
  
def bus_right(img):
    width, height = img.size
    box = (int(width * 0.75), 0, width, height)     #rechten 25% vom Bild
    img = img.crop(box)
    img = np.array(img)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv_img, lower_blue, upper_blue)
    # img = Image.fromarray(mask)
    # img.save("mask.jpg") 
    count = np.count_nonzero(mask, axis=None)
    if count > 400:
        return True
    else:
        return False