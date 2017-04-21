#!/usr/bin/env python

import pexpect, sys, json, select, time
import paho.mqtt.client as paho

# Constants
bluetooth_adr = "CB:FE:19:98:A0:EF"
sysid = "79cf6c22-dcc6-11e5-8e77-00113217113f"


# LoPoSwitch
def floatfromhex(h):
    t = float.fromhex(h)
    if t > float.fromhex('7FFF'):
        t = -(float.fromhex('FFFF') - t)
        pass
    return t

class LoPoSwitch:

	def __init__( self, bluetooth_adr ):
		self.con = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' --interactive -t random --listen')
		#self.con.logfile = open(self.file, "a") #Dissable for Python3
		self.con.expect('\[LE\]>', timeout=100)
		#print "Preparing to connect."
		self.con.sendline('connect')
		# test for success of connect
		self.con.expect('Connection successful.*\[LE\]>')
		# Earlier versions of gatttool returned a different message.  Use this pattern -
		#self.con.expect('\[CON\].*>')
		self.con.sendline('char-write-req 0x000e 0100')
		self.con.expect('Characteristic value was written successfully')
		return

    def turnOn(self):
		self.con.sendline('connect') # Reconnect if not connected
		self.cb = {}
		self.con.sendline('char-write-req 0x000e 0100')
		self.con.expect('Characteristic value was written successfully')

		cmd = 'char-write-cmd 0x000b 5231' #Write 'R1' to second attribute
		#print cmd
		self.con.sendline( cmd )
		index = self.con.expect(['Notification handle = 0x000d value: ', 'Command Failed: Disconnected'])
		if index == 0:
			print("OK")
		elif index == 1:
			print("Disconnected")
		return

	def turnOff(self):
		self.con.sendline('connect') # Reconnect if not connected
		self.con.sendline('char-write-req 0x000e 0100')
		self.con.expect('Characteristic value was written successfully')
		
		cmd = 'char-write-cmd 0x000b 5230' #Write 'R0' to second attribute
		#print cmd
		self.con.sendline( cmd )
		index = self.con.expect(['Notification handle = 0x000d value: ', 'Command Failed: Disconnected'])
		if index == 0:
			print("OK")
		elif index == 1:
			print("Disconnected")
		return


# Connect to BLE LoPoSwitch
try:
    AIrigarePump = LoPoSwitch(bluetooth_adr) 
except Exception:
	print("Not Connected to BLE")
	pass

# Define Variable to be able to count Pumping Time (Duration)
sT = time()


# Define event callbacks
def on_connect(mosq, obj, rc):
	print("rc: " + str(rc))

def on_message(mosq, obj, msg):
	if msg.payload == "1":
		print("Turning on...")
		mqttc.publish(sysid + "/loposwitch/RX", "Turning on...")
		try:
			global AIrigarePump
			AIrigarePump.turnOn() 
		except Exception:
			print("Not Connected to BLE")
			mqttc.publish(sysid + "/loposwitch/RX", "Not Connected")
			pass

		sT = time()
	
	if msg.payload == "0":
		print("Turning off...")
		mqttc.publish(sysid + "/loposwitch/RX", "Turning off...")
		try:
			global AIrigarePump
			AIrigarePump.turnOff() 
		except Exception:
			mqttc.publish(sysid + "/loposwitch/RX", "Not Connected")
			print("Not Connected to BLE")
			pass
		
		global sT	
		wT = time() - sT
		print("I was watering " + str(round(wT,0)) + " seconds")
		mqttc.publish(sysid + "/loposwitch/RX", "I was watering " + str(round(wT,0)) + " seconds")
    	
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

# Parse CLOUDMQTT_URL (or fallback to localhost)
url_str = os.environ.get('CLOUDMQTT_URL', 'mqtt://mikmak.cc:1883')
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

#mqttc.loop_forever()
