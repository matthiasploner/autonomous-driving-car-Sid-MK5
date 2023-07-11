import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from picamera.array import PiRGBArray
import cv2
from lane_follower_2 import *
import os
import signal
import time
import threading
from Raeder import *
from Licht import *
from Ultra import *
from PIL import Image


#Der Code ist für den Videostream und für die autonome Navigation des Autos zuständig, 
#dies gehört zusammen, weil das autonome Fahren auf das selbe Kamerabild zugreifen muss, 
#das auch im Videostream zu sehen ist. Das Bild für die Linienerkennung wird jedoch zugeschnitten.
#Sobald der Stream gestartet wurde, wird auch ein Thread gestartet, der das autonome Fahren regelt. 
#Während dem autonomen Fahren wird auch auf die Ultraschallsensoren reagiert 
#und wenn sie ein Hindernis erkennen angehalten und ein Lichtzeichen gegeben. 
#Die Linienerkennung funktioniert durch die Kantenerkennung von OpenCV 
#und dadurch wird je nach Neigung der Kanten nach links oder rechts, entschieden wohin gelenkt werden muss. 
#Bushaltestellen und Wendelinien werden mithilfe des HSV Farbraums und OpenCV erkannt.

PAGE="""\
<html>
<head>
</head>
<body>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

ultra_s = False

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def ultra():
    global ultra_s
    while True:
        VL,VR, _ ,_ = getDistance()
        if VL < 20 or VR < 20:
            ultra_s = True
            stop()
            print("aus dem weg")
            ledAus()
            time.sleep(0.15)
            stop()
            ledEin()
            time.sleep(0.15)
            stop()
            ledAus()
            time.sleep(0.15)        #aufblenden
            stop()
            ledEin()
            time.sleep(0.15)
            stop()
            ledAus()
            time.sleep(0.15)
            stop()
            ledEin()
            time.sleep(1.5)
            stop()
            
        else:
            ultra_s = False
        time.sleep(0.1)

def send_frames(output):
    global ultra_s
    speed = 35
    thread = threading.Thread(target=ultra) #Ultraschallsensoren Erkennung als Thread
    thread.start()
    while True:
        if not ultra_s:
            if os.path.exists("autonom_config.txt"): #Datei fuer die Kommunikation unter den verschiedenen Python Skripts
                image = np.array(Image.open(io.BytesIO(output.frame))) 
                state = lane_assist(image, speed, False)
                
                if state == "bus_middle": #Bushaltestelle mitte
                    print("bushaltestelle mitte erkannt, fahre jetzt noch")

                    endzeit = time.time() + 2.5
                    while time.time() < endzeit:
                        image = np.array(Image.open(io.BytesIO(output.frame))) 
                        lane_assist(image, speed, True)             # Strassenlinien weiter folgen, ohne auf BusHalt. zu reagieren
                        time.sleep(0.01)

                    print("warte jetzt 5 sec auf fahrgaeste")
                    stop()
                    time.sleep(5)                               #warten
                    print("fahre jetzt wieder weiter")
                    
                    endzeit = time.time() + 4
                    while time.time() < endzeit:
                        image = np.array(Image.open(io.BytesIO(output.frame))) 
                        lane_assist(image, speed, True)         # Strassenlinien weiter folgen, ohne auf BusHalt. zu reagieren
                        time.sleep(0.01)

                elif state == "bus_right": #Bushaltestelle rechts
                    print("bushaltestelle rechts gesehen, fahre jetzt noch")

                    endzeit = time.time() + 1
                    while time.time() < endzeit:
                        image = np.array(Image.open(io.BytesIO(output.frame)))  
                        lane_assist(image, speed, True) # Strassenlinien weiter folgen, ohne auf BusHalt. zu reagieren
                        time.sleep(0.01)

                    turnR(speed+5)
                    time.sleep(2.2)     #links rein fahren
                    turnL(speed+5)
                    time.sleep(2.2)

                    stop()
                    print("warte jetzt 4 sec auf fahrgaeste")           #warten
                    time.sleep(4)

                    turnL(speed+5)
                    time.sleep(2.5)     #rechts wieder raus
                    turnR(speed+5)
                    time.sleep(1.7)

                elif state == "turnline": #Wendelinie
                    print("Wendelinie erkannt")
                    turnL(70)      #nach links drehen
                    time.sleep(2)
                else:
                    time.sleep(0.01)
                    
            else: #Nur der Stream wird angezeigt
                print("autonom aus")
                autonom_fert()
                time.sleep(1) #jede sekunde wird ueberprueft ob autonom zu fahren ist
        else:
            time.sleep(0.2) #falls die ultraschallsensoren etwas erkannt haben, wird alle 0.2 sekunden ueberprueft ob es noch da ist

if __name__ == '__main__':
    camera = picamera.PiCamera(resolution='640x480', framerate=30) #Ultraweitwinkel
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    time.sleep(1)
    thread = threading.Thread(target=send_frames, args=(output,)) #Strassenlinienerkennung als Thread
    thread.start()
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

