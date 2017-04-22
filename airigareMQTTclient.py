#!/usr/bin/env python

import pexpect, sys, json, select, time, urlparse
import paho.mqtt.client as paho

# Constants
bluetooth_adr = "CB:FE:19:98:A0:EF"
sysid = "79cf6c22-dcc6-11e5-8e77-00113217113f"
url_str = 'mqtt://mikmak.cc:1883'

# LoPoSwitch
def floatfromhex(h):
    t = float.fromhex(h)
    if t > float.fromhex('7FFF'):
        t = -(float.fromhex('FFFF') - t)
        pass
    return t

class LoPoSwitch:
	pexpectCommandTimeOut = 3

	def __init__( self, bluetooth_adr ):
		self.bluetooth_adr = bluetooth_adr
		self.connect()


	def connect(self):
		r = 0
		self.con = pexpect.spawn('gatttool -b ' + self.bluetooth_adr + ' --interactive -t random --listen')
		#self.con.logfile = open(self.file, "a") #Dissable for Python3
		self.con.expect('\[LE\]>', timeout=self.pexpectCommandTimeOut)
		#print "Preparing to connect."
		self.con.sendline('connect')
		# test for success of connect
		r = self.con.expect(['Connection successful.*\[LE\]>', pexpect.TIMEOUT], timeout = self.pexpectCommandTimeOut)
		print("Connection successful.*\[LE\]>'", r)
		return r


		self.con.sendline('char-write-req 0x000e 0100')
		r = self.con.expect(['Characteristic value was written successfully', pexpect.TIMEOUT], timeout = self.pexpectCommandTimeOut)
		print("Characteristic value was written successfully", r)
		return r

	def turnOn(self):
		r = 0
		cmd = 'char-write-cmd 0x000b 5231' #Write 'R1' to second attribute
		self.con.sendline( cmd )
		r = self.con.expect(['Notification handle = 0x000d value: ', 'Command Failed: Disconnected', pexpect.TIMEOUT], timeout = self.pexpectCommandTimeOut)
		print(r)
		return r

	def turnOff(self):
		r = 0
		cmd = 'char-write-cmd 0x000b 5230' #Write 'R0' to second attribute
		#print cmd
		self.con.sendline( cmd )
		r = self.con.expect(['Notification handle = 0x000d value: ', 'Command Failed: Disconnected', pexpect.TIMEOUT], timeout = self.pexpectCommandTimeOut)
		print(r)
		return r


# Connect to BLE LoPoSwitch
AIrigarePump = LoPoSwitch(bluetooth_adr)

# Define Variable to be able to count Pumping Time (Duration)
sT = time.time()


# Define event callbacks
def on_connect(mosq, obj, rc):
	print("rc: " + str(rc))

def on_message(mosq, obj, msg):
	if msg.payload == "1":
		print("Turning on...")
		mqttc.publish(sysid + "/loposwitch/RX", "Turning on...")

		r = AIrigarePump.turnOn()
		if r == 0:
			mqttc.publish(sysid + "/loposwitch/RX", "OK")
		#elif r == 1:
		else:
			mqttc.publish(sysid + "/loposwitch/RX", "Not OK...")
	
	if msg.payload == "0": # Turn Off
		print("Turning off...")
		mqttc.publish(sysid + "/loposwitch/RX", "Turning off...")		
		AIrigarePump.turnOff()

		r = AIrigarePump.turnOff()
		if r == 0:
			mqttc.publish(sysid + "/loposwitch/RX", "OK")
			global sT	
			waT = time.time() - sT
			print("I was watering " + str(round(wT,0)) + " seconds")
			mqttc.publish(sysid + "/loposwitch/RX", "I was watering " + str(round(wT,0)) + " seconds")
		elif r == 1:
			mqttc.publish(sysid + "/loposwitch/RX", "Not OK...")
		elif r == 2:
			mqttc.publish(sysid + "/loposwitch/RX", "Some Other Error")
    	
	print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(mosq, obj, mid):
	print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
	print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
	print(string)

mqttc = paho.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
#mqttc.on_log = on_log

url = urlparse.urlparse(url_str)

# Connect
#mqttc.username_pw_set(url.username, url.password)
mqttc.connect(url.hostname, url.port)

# Start subscribe, with QoS level 0
mqttc.subscribe(sysid + "/loposwitch/TX", 0)

# Publish a message
mqttc.publish(sysid + "/loposwitch/RX", "Hello")

# Continue the network loop, exit when an error occurs
while True:
	rc = 0
	while rc == 0:
		rc = mqttc.loop()
		
	print("rc: " + str(rc))
	mqttc.connect(url.hostname, url.port)
	# Start subscribe, with QoS level 0
	mqttc.subscribe(sysid + "/loposwitch/TX", 0)

	# Publish a message
	mqttc.publish(sysid + "/loposwitch/RX", "Hello")