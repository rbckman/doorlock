from pad4pi import rpi_gpio
import RPi.GPIO as GPIO
import time
import json
import requests
import socket
import os
import pickle

#bygdis keypad dörrlås system

keypass = ''
passcodes = ['2222', '0550']
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)
folder = os.getcwd()
print(folder)
f = open(folder+"/apikey", "r")
apikey = f.readline().strip()
open_door = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT) #Grönled
GPIO.setup(20, GPIO.OUT) #Rödled
GPIO.setup(21, GPIO.OUT) #Piezo
GPIO.setup(26, GPIO.OUT) #Door
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Öppen knappen
GPIO.output(16,GPIO.LOW)
GPIO.output(20,GPIO.LOW)
GPIO.output(21,GPIO.LOW)
GPIO.output(26,GPIO.LOW)

def save_passcodes(passcodes):
    global folder
    with open(folder+'/.doorlock.p', 'wb') as f:
        pickle.dump(passcodes, f)
        print('save passcodes for offline mode')

def load_passcodes():
    global folder
    passcodes = pickle.load(open(folder+'/.doorlock.p', 'rb'))

def check_if_open():
    if GPIO.input(14):
        #print('open door')
        GPIO.output(26, GPIO.HIGH)
    else:
        GPIO.output(26, GPIO.LOW)

def is_webz_on():
    try:
        socket.create_connection(("google.com",80))
        return True
    except:
        pass
    print('no internet connection!')
    return False

def getcodes():
    global apikey
    url = 'https://bygdis.fi/dorrkoderapi?apikey='+apikey
    resp = requests.get(url=url)
    data = resp.json()
    return data

def keylogger(code):
    global apikey
    print('logging key ' + str(code))
    url = 'https://bygdis.fi/dorrkoderapi?apikey='+apikey+'&logger=' + str(code)
    resp = requests.get(url=url)
    print(resp)
    return

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
    global passcodes, open_door
    print(passcodes)
    if keypass in passcodes:
        successbeep()
        open_door = True
    else:
        failbeep()

def opendoor():
    GPIO.output(26, GPIO.HIGH)
    GPIO.output(16,GPIO.HIGH)
    GPIO.output(20,GPIO.HIGH)
    keylogger(keypass)
    time.sleep(5)

def closedoor():
    GPIO.output(26, GPIO.LOW)
    GPIO.output(16,GPIO.LOW)

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

start_time = time.time()
get_code_time = time.time()

while 1:
    run_time = time.time() - start_time
    update = time.time() - get_code_time
    time.sleep(0.2)
    if update > 5:
        get_code_time = time.time()
        if is_webz_on():
            passcodes = getcodes()
            save_passcodes(passcodes)
        else:
            passcodes = load_passcodes()
    if open_door == True:
        opendoor()
        closedoor()
        open_door = False
    check_if_open()

keypad.cleanup()
