# -*- coding: utf-8 -*-
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.label import Label
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout

import paho.mqtt.client as paho
import logging
import pika
import stomp
import time
from time import ctime
#import threading
import ntplib
#from stomp_conncetion_actions import StompConnectionActions as Stomp


Builder.load_file("main2.kv")
connectedAMQP = False
'''diff = None
while diff == None:
    try:
        client_ntp = ntplib.NTPClient()
        response = client_ntp.request('0.pool.ntp.org', version=3)
        now = time.time()
        diff = now-(response.tx_time + response.delay)
        time.sleep(1)
    except:
        continue'''
conn = None # stomp

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK Returned code=",rc)
        client.subscribe("testtopic")
        print "subscribed"
    else:
        print("Bad connection Returned code=",rc)

    
def on_message(client, userdata, message):
    time_received = time.time()
    response = None
    while response == None:
        try:
            client_ntp = ntplib.NTPClient()
            response = client_ntp.request('0.pool.ntp.org', version=3)
            print "prietaiso ir ntp laiko skirtumas", response.offset
        
            time_received += response.offset
            
            #print "sent at: ", float(message.payload)
            print "received at: ", time_received
            print 'message %s' % message.payload
            #print "diff", format(time_received-float(message.payload), '.12g') # 12 significant digits
            output_file = open("mqtt_result.csv", "a")

            if message.payload=="end":
                output_file.write(message.payload + " at: " + ctime(time.time()+response.offset)+"\n")
                output_file.close()
                print message.payload
            elif message.payload=="begin":
                output_file.write("begin at: "+ctime(time.time()+response.offset)+"\n")
                output_file.close()
            else:
                output_file.write(message.payload+
                                  ","+format(time_received, '.12f')+
                                  ","+format(time_received-float(message.payload), '.12f')+"\n")
                print "written"
                output_file.close()
        except ntplib.NTPException:
            print ntplib.NTPException


def callback_amqp(ch, method, properties, body):
    time_received = time.time()
    response = None
    while response == None:
        try:
            client_ntp = ntplib.NTPClient()
            response = client_ntp.request('0.pool.ntp.org', version=3)
            print "prietaiso ir ntp laiko skirtumas", response.offset

            time_received += response.offset
            
            #print "sent at: ", float(message.payload)
            print "received at: ", time_received
            print 'message %s' % body
            #print "diff", format(time_received-float(message.payload), '.12g') # 12 significant digits
            output_file = open("amqp_result.csv", "a")

            if body=="end":
                output_file.write(body + " at: " + ctime(time.time()+response.offset)+"\n")
                output_file.close()
                ch.stop_consuming()
                print body
            elif body=="begin":
                output_file.write("begin at: "+ctime(time.time()+response.offset)+"\n")
                output_file.close()
            else:
                output_file.write(body+
                                  ","+format(time_received, '.12f')+
                                  ","+format(time_received-float(body), '.12f')+"\n")
                print "written"
                output_file.close()
        except ntplib.NTPException:
            print ntplib.NTPException


class StompListener(object): # STOMP protokolui
    
    def on_error(self, headers, message):
        print 'received an error %s' % message

    def on_connected(self, headers, body):
        conn.subscribe('testtopic', 1)
        print "connected stomp"
    
    def on_message(self, headers, message):
        time_received = time.time() 
        response = None
        while response == None:
            try:
                client_ntp = ntplib.NTPClient()
                response = client_ntp.request('0.pool.ntp.org', version=3)
                print "prietaiso ir ntp laiko skirtumas", response.offset
            
                time_received += response.offset
                
                #print "sent at: ", float(message.payload)
                print "received at: ", time_received
                print 'message %s' % message
                #print "diff", format(time_received-float(message.payload), '.12g') # 12 significant digits
                output_file = open("stomp_result.csv", "a")

                if message=="end":
                    output_file.write(message + " at: " + ctime(time.time()+response.offset)+"\n")
                    output_file.close()
                    print message
                elif message=="begin":
                    output_file.write("begin at: "+ctime(time.time()+response.offset)+"\n")
                    output_file.close()
                else:
                    output_file.write(message+
                                      ","+format(time_received, '.12f')+
                                      ","+format(time_received-float(message), '.12f')+"\n")
                    print "written"
                    output_file.close()
            except ntplib.NTPException:
                print ntplib.NTPException

class ConnectionManager(FloatLayout):

    mqttClient = paho.Client("e9efac60-bc25-43cc-a40b-2998ef879eb8")    
    mqttClient.clean_session = True
    mqttClient.transport = "tcp"
    
    popup_connected = Popup(title='Connected',
                          content=Label(text='Succsessfully connected to broker'),
                          size_hint=(1, .5))
    popup_connection_failed = Popup(title='Not connected',
                                    content=Label(text='Attempt to connect failed'),
                                    size_hint=(1, .5))
    

    
    mqttConnected = False

    credentials_amqp = pika.PlainCredentials('edita1', 'test')
    parameters_amqp = pika.ConnectionParameters('185.80.128.169',
                                                   5672,
                                                   '/',
                                                   credentials_amqp)
    connection_amqp = None
    channel_amqp = None
    #thread = PikaThread()
    
    # MQTT
    def connectMqtt(self):
        try:
            # clean session indicates non persistent session
            self.mqttClient.username_pw_set("ed_test", "ed_test_01")
            self.mqttClient.on_connect = on_connect
            self.mqttClient.on_message = on_message
            
            self.mqttClient.connect("185.80.128.169", 8883)
            self.mqttClient.loop_start()
            print "loop started"
            return 'down'
        except:
            self.popup_connection_failed.open()
            return 'normal'

    def disconnectMQTT(self):
        try:
            self.mqttClient.loop_stop()
            self.mqttClient.disconnect()
            self.mqttConnected = False
            print "Disconnected"
        except:
            print "failed to disconnect"
        
    # AMQP
    def connectAmqp(self):
        try:
            #self.thread.connect()
            print "ok2"
            self.connection_amqp = pika.BlockingConnection(self.parameters_amqp)
            print "ok1"
            self.channel_amqp = self.connection_amqp.channel()
            print "ok2"
            self.channel_amqp.queue_declare(queue='testtopic')
            print "ok3"
            self.channel_amqp.basic_consume(callback_amqp,
                      queue='testtopic',
                      no_ack=True)
            print "ok4"
            self.popup_connected.open()
            self.channel_amqp.start_consuming()
            return 'down'
        except:
            self.popup_connection_failed.open()
            return 'normal'
        '''while connectedAMQP:
            time.sleep(1)
            self.thread.check_for_message()'''

    '''def check_for_message_Amqp():
        self'''
    
    def disconnectAMQP(self):
        #self.tread.stop()
        #self.channel_amqp.stop_consuming()    
        self.connection_amqp.close()
    
    # STOMP    
    def connectStomp(self):
        try:
            global conn
            conn = stomp.Connection(host_and_ports=[('185.80.128.169', 61613)])
            # print 'ok1'
            lst = StompListener()
            conn.set_listener('', StompListener())
            conn.start()
            conn.connect('edita1', 'test', wait=True)
            
            self.popup_connected.open()
            return 'down'
        except:
            self.popup_connection_failed.open()
            return 'normal'

    def disconnectStomp(self):
        #time.sleep(2)
        global conn
        try:
            conn.disconnect()
        except:
            print "Maybe not connected"
        print "yes"


class ProtocolManager(App):
    def build(self):
        return ConnectionManager()


if __name__ == '__main__':
    ProtocolManager().run()
