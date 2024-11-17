import sys
import RPi.GPIO as GPIO
import time

paws = 0.0
# collect the adjustable pause time to let the PIR calibrate
if len(sys.argv) > 1:
    paws = float(sys.argv[1])
else:
    paws = 10.0

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) # Initialization
# haveMotion = False

# def Movement(x):
#     print('Event Movement. Pin:' + str(x))
#     haveMotion = True

pirpin = 23  # Assign pin for PIR
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

print('create')
GPIO.setup(pirpin,GPIO.IN)
print('wait:' + str(paws))
time.sleep(paws)

# print('add event')
# GPIO.add_event_detect(pirpin, GPIO.RISING, callback=Movement)
count = 0
print('loop for Motion')
try:
    while 1:
        count = count + 1
        if (GPIO.input(pirpin)):
            print('motion:' + str(count))
            p.ChangeDutyCycle(7.5)
        else:
            p.ChangeDutyCycle(2.5)
        time.sleep(3)
       
except KeyboardInterrupt:
    print("Program ended")
    GPIO.cleanup()