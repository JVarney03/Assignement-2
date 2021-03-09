from PCF8574 import PCF8574_GPIO 
from Adafruit_LCD1602 import Adafruit_CharLCD
import Freenove_DHT as DHT

import firebase_admin
from firebase_admin import credentials 
from firebase_admin import db
import json

import time

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

#firebase setup
cred = credentials.Certificate('home-41654-firebase-adminsdk-hv06j-35fb693ea7.json')
firebase_admin.initialize_app(cred, {
    'databaseURL':'https://home-41654-default-rtdb.europe-west1.firebasedatabase.app/'
})
ref = db.reference('/')

#class for button setup
class button:
    def __init__(self, pin): 
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


        
#GPIO pin allocation
buttonUp = button(18)
buttonDown = button(16)
DHTPin = 11
ledPin = 22

GPIO.setup(ledPin, GPIO.OUT)
GPIO.output(ledPin, GPIO.LOW)

#adds 1 to user set temperature
def tmpAdd(tmp):
    tmp = tmp + 1
    return tmp

#subtracts 1 from user set temperature
def tmpMinus(tmp):
    tmp = tmp - 1
    return tmp

#displays user set temperature
def displayTmp(tmpF):
    lcd.setCursor(0,0)
    tmpF = str(tmpF)
    lcd.message('tmp: ' + tmpF + ' C')

#gets room temperature from DHT, displays on lcd and updates 
#database
def displayDHT(dht):
    chk = dht.readDHT11()
    roomTemp = 0
    if (chk is dht.DHTLIB_OK):
        roomTemp = dht.temperature
    else:
        print ('dht failure')
    lcd.setCursor(0,1)
    lcd.message('room : %.2f'%(roomTemp))
    dataUpdateRoom(roomTemp)
    return (roomTemp)

#Updates 'room temperature' on database
def dataUpdateRoom(rmTmp):
    temperature = {
                'room temperature': rmTmp,
                }
    db.reference('temperature').update(temperature)

#updates 'heating temperature'(user set) to database
def dataUpdateHeating(htTmp):
    temperature = {
                'heating temperature': htTmp,
                }
    db.reference('temperature').update(temperature)

#gets heating temperature value from database
def getHeating():
    data = ref.get()
    tmp = data['temperature']['heating temperature']
    return (tmp)



#main loop, listens for button inputs, controls read and writes
#of the database and updates lcd screen
def loop(tmp): 
    mcp.output(3,1)
    lcd.begin(16,2) 
    dht = DHT.DHT(DHTPin)
    displayTmp(tmp)
    while (True):
        #listens for button press, updates tmp and database
        if GPIO.input(buttonUp.pin)==GPIO.LOW:
            value = tmpAdd(tmp)
            tmp = value
            dataUpdateHeating(tmp)
            time.sleep(0.25) 
        elif GPIO.input(buttonDown.pin)==GPIO.LOW:
            value = tmpMinus(tmp)
            tmp = value
            dataUpdateHeating(tmp)
            time.sleep(0.25)
    
        #runs function to display temperature and stores value
        value = displayDHT(dht)
        #updates tmp with database value incase of change made
        #using the web app
        tmp = getHeating()
        displayTmp(tmp)
        time.sleep(1)
        #compares value(room temperature) from dht with tmp
        #(user set value) to see if heating(LED) should be on
        if value < tmp:
            GPIO.output(ledPin, GPIO.HIGH)
        else:
            GPIO.output(ledPin, GPIO.LOW)

#Unasings GPIO pins and clears lcd
def destroy():
    GPIO.cleanup()
    lcd.clear()


#lcd set up
PCF8574_address = 0x27 #I2C address 
PCF8574A_address = 0x3F #I2C address

#Create PCF8574 GPIO adapter
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print ('I2C Adress Error!')
        exit(1)
#Create :CD
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
 


#Starts program 
if __name__ == '__main__':
    print ('Program is starting ...')
    #gets user set temperature from database
    temperature = getHeating()
    try:
        #starts program with database value as starting value
        loop(temperature)
    except KeyboardInterrupt:
        destroy()
