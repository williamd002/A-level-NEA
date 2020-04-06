#template for client

import PySimpleGUI as sg
import sys
import random
import socket
import selectors
import types
import datetime
import uuid 
import threading

SERVER = '127.0.0.1'    #current address of server
PORT = 1234             #current port used by server

#find client MAC address
myMac = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]))  

client_states=['INIT','WAIT','READY','READING','CLOCKING']
current_state = 0

sel = selectors.DefaultSelector()

rfid_read = False
rfid_value = ''
#for testing purposes before integration of RFID reader
test_rfids = [987612]

def fakeRfid(): #to be replaced with RFID reader code
    '''code to setup a test rfid value before RFID reader integrated'''
    global rfid_read, rfid_value
    print('fake RFID')
    rfid_read = True
    rfid_value = random.choice(test_rfids)
    

def rfid_thread():
    '''thread to run the processing of RFID values
       when a value is ready to be process rfid_read will be True
    '''
    global current_state, rfid_read, rfid_value
    print('start of RFID thread')
    server_addr = (SERVER, PORT)
    print('starting RFID connection to',server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)       
    while current_state == 3:
        if rfid_read:
            sel = selectors.DefaultSelector()
            print('RFID READING')
            rfid_read = False 
            print(rfid_value)
            message = "RFID$"+str(rfid_value)
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
    
            data = types.SimpleNamespace(
                connid = 1,
                msg_total = len(message),
                recv_total=0,
                messages=[message.encode()],
                outb=b"",
                )
            sel.register(sock, events, data=data)

 
            current_state = 4 #clocking
            try:
                done = False
                while (not done) and current_state == 4:
                    events = sel.select(timeout=1)
                    if events:
                        for key,mask in events:
                            service_connection(key,mask)
                            
            except:
                print('Caught keyboard - exiting')
            
            sel.close()
    print('end of RFID thread')


 


def init_thread():
    '''thread to make initial contact with the server'''
    global current_state
    print('start of init thread')
    init_connection()
    try:
        done = False
        while (not done) and current_state != 2:
            events = sel.select(timeout=1)
            if events:
                for key,mask in events:
                    service_connection(key,mask)
                    
    except:
        print('Caught keyboard - exitin')
    finally:
        pass
        sel.close()
    print('end of init thread')
    
    
def init_connection():    
    #init connection to server and await response
    print('start of init connection')
    server_addr = (SERVER, PORT)
    message = f'INIT${myMac}'
    print('starting INIT connection to',server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
        connid = 1,
        msg_total = len(message),
        recv_total=0,
        messages=[message.encode()],
        outb=b"",
        )
    sel.register(sock, events, data=data)
    print('end of init connection')
    
#code ideas taken from https://realpython.com/python-sockets/ 
def service_connection(key, mask):
    global current_state
    #print('start of service connection')
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
            
            recvData = recv_data.decode().split("$")
            recvCommand = recvData[0]
             
            print(recvData)
            print(recvCommand)
            if recvCommand == "OK":
                current_state = 2
                print(current_state)
            if recvCommand == "ERROR":
                current_state = 3
                window['_OUTPUT_'].update(recvData[1])
            if recvCommand == "CLOCKED":
                current_state = 3
                window['_OUTPUT_'].update(recvData[1])
            
            
        if not recv_data or data.recv_total == data.msg_total:
            print("closing connection", data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
    #print('end of service connection')

thread1 = threading.Thread(target=init_thread)
thread1.start()

today = datetime.date.today()
theTime = datetime.datetime.now()
current_time = theTime.strftime("%H:%M")
sg.theme('Dark')

host_ip="."  #initially we display dots as we initiate 

#Setup layout
layout = [
        [sg.Text(today, font=("Helvetica", 15), size=(9, 1)),sg.Text(current_time, font=("Helvetica", 15), size=(9, 1),key='_TIME_'),sg.Text(host_ip, font=("Helvetica", 15), size=(17, 1),key="_IP_")],
          [sg.Text('INITIATING', size=(25, 2), font=('Helvetica', 20), justification='left', key='_OUTPUT_')],
        [sg.Button('Read'), sg.Exit()]]

# Show the Window to the user
window = sg.Window('Clock In Client', layout, size=(320,240) )

#Main loop
while True:
    # Read the Window
    time = datetime.datetime.now()
    current_time = time.strftime("%H:%M:%S")
    if current_state <2:            #if initialising draw more dots
        host_ip = host_ip + "."
        if len(host_ip) == 5:
            host_ip="."
    else:
        host_ip = myMac             #otherwise show MAC address

    window['_IP_'].update(host_ip)            #update IP area of window
    window['_TIME_'].update(current_time)     #update TIME area of window
    event, value = window.read(timeout=100)   #read any event from the GUI
    if event in ('Quit', None):               #if window is closed then exit
        break
    if event in (None, 'Exit'):               #if EXIT button clicked then exit
        break
    if event in ('Read', None):               #if 'fake' read button clicked 
        fakeRfid()
    if current_state == 2:                    #if we are now in READY state move to READING state
        current_state = 3
        window['_OUTPUT_'].update('READY')   
        thread1 = threading.Thread(target=rfid_thread) #start the RFID processing thread
        thread1.start()

window.close()
