#!/usr/bin python3

'''


docker build -t modbus2mqtt:v1 .


'''

from pyModbusTCP.client import ModbusClient
#import context # Ensures paho is in PYTHONPATH
import paho.mqtt.client as mqtt
import time
import json
import sys
import os

topics = ['#']

# get addresses from env vars
#hostMQTT=os.environ.get('HOSTMQTT', 'unknown')
#hostMODBUS=os.environ.get('HOSTMODBUS', 'unknown')

hostMQTT = "192.168.2.15"
hostMODBUS = "192.168.1.2"

# Convert list with booleans to list with strings. Needs to publish the topic to MQTT Broker
def convert(obj):
    if isinstance(obj, bool):
        return str(obj).lower()
    if isinstance(obj, (list, tuple)):
        return [convert(item) for item in obj]
    if isinstance(obj, dict):
        return {convert(key):convert(value) for key, value in obj.items()}
    return obj

# TCP auto connect on first modbus request
c = ModbusClient(host=hostMODBUS, port=502, auto_open=True)


def on_connect(mqttc, obj, flags, rc):
	if (rc == 0):
		print("Connect to MQTT broker")

def on_disconnect(mqttc, obj, rc):
	if (rc == 1):
		connect_to_MQTT()
	print("rc="+ str(rc))

		
def on_message(mqttc, obj, msg):
	print(str(msg.payload))
	coils = []
	
	coils =   str(msg.payload)[3: len(str(msg.payload))-2 ].split(",")
	print(coils)
	
	for idx, coil in enumerate(  coils,1 ):
		print(coil)
		
		if(coil == "True"):
			is_ok = c.write_single_coil(idx-1, True)
		else:
			is_ok = c.write_single_coil(idx-1, False)
		
		
		if is_ok:
			print("bit #" + str(idx) + ": write to " + str(coil))
		else:
			print("bit #" + str(idx) + ": unable to write " + str(coil))
		time.sleep(0.2)


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)

def connect_to_MQTT():
	mqttConnect = 1
	while mqttConnect > 0:
		mqttConnect = mqttc.connect(hostMQTT, 1883, 60)
		print("Cannot connect to MQTT broker")
		time.sleep(5)
	return mqttConnect

	
	
# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client()
mqttc.username_pw_set("fpl", password="1234567890")
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
#mqttc.on_log = on_log



is_mqttConnect = connect_to_MQTT()

mqttc.loop_start()


mqttc.subscribe("modbus/holding")

while True:
	#Read the first 8 inputs via Modbus
	regs = c.read_discrete_inputs(0, 8)
	toBroker = "{"
	print(is_mqttConnect)
	if (is_mqttConnect == 0) :
		if regs:
			#print(f"Send to Broker ",  json.dumps(convert(regs)))
			for idx, reg in enumerate(regs):
				
				if reg == False:
					toBroker += "0"
				else:
					toBroker += "1"
					
				if idx < 7:
					toBroker += ","
			
			
			toBroker += "}"
			print(f"Send to Broker ",  toBroker)
			
			#(rc, mid) = mqttc.publish("modbus/coils", json.dumps(convert(regs)), qos=2)
			(rc, mid) = mqttc.publish("modbus/coils", toBroker, qos=2)
			
		else:
			print("read error")
	else:
		print("MQTT error")

	
	time.sleep(1)

infot.wait_for_publish()


