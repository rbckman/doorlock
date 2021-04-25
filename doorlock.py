from pad4pi import rpi_gpio
import RPi.GPIO as GPIO
import time

#bygdis keypad dörrlås system

keypass = ''
passcodes = ['2222', '0550']

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT) #Grönled
GPIO.setup(20, GPIO.OUT) #Rödled
GPIO.setup(21, GPIO.OUT) #Piezo
GPIO.setup(26, GPIO.OUT) #Door
GPIO.output(16,GPIO.LOW)
GPIO.output(20,GPIO.LOW)
GPIO.output(21,GPIO.LOW)
GPIO.output(26,GPIO.LOW)

def keybeep():
    GPIO.output(21,GPIO.HIGH)
    time.sleep(0.05)
    GPIO.output(21,GPIO.LOW)

def failbeep():
    p = 0
    while p < 100:
        GPIO.output(20,GPIO.HIGH)
        GPIO.output(21,GPIO.HIGH)
        GPIO.output(21,GPIO.LOW)
        GPIO.output(20,GPIO.LOW)
        time.sleep(0.05)
        p += 1

def successbeep():
    GPIO.output(21,GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(21,GPIO.LOW)

def processKey(key):
    global keypass
    keybeep()
    print(key)
    keypass += key
    if len(keypass) == 4:
        check(keypass)
        keypass = ''
    print(keypass)

def check(keypass):
    global passcodes
    if keypass in passcodes:
        successbeep()
        GPIO.output(26, GPIO.HIGH)
        GPIO.output(16,GPIO.HIGH)
        GPIO.output(20,GPIO.HIGH)
        time.sleep(5)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
    else:
        failbeep()

# Setup Keypad
KEYPAD = [
        ["*","0","#"],
        ["7","8","9"],
        ["4","5","6"],
        ["1","2","3"]
]

ROW_PINS = [11,23,24,25] # BCM numbering
COL_PINS = [17,27,22] # BCM numbering

factory = rpi_gpio.KeypadFactory()

keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

keypad.registerKeyPressHandler(processKey)
while 1:
    time.sleep(0.5)
    #GPIO.output(16,GPIO.LOW)
    #GPIO.output(20,GPIO.LOW)
    #GPIO.output(21,GPIO.LOW)

keypad.cleanup()
