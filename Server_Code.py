#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import sqlite3
import os
from datetime import datetime, date

sel = selectors.DefaultSelector()
db = sqlite3.connect('mydb.db')
cursor = db.cursor()

def findRFID(RFIDcode):
    '''a function to search for an RFIDcode in the employee table
       if employee exists return the firstnamr and surname
       if employee does not exists return 'UNKNOWN'
    '''
    print('searching for',RFIDcode)
    db = sqlite3.connect('mydb.db')
    cursor = db.cursor()
    c = db.cursor()
    c.execute('SELECT * FROM {tn} WHERE RFIDcode = {cn} '.\
              format(tn='employee', cn=RFIDcode))
    all_rows = c.fetchall()
    db.close()
    if len(all_rows) == 0:
        return ('UNKNOWN')
    else:
        return (all_rows[0][2],all_rows[0][3])
    

def inorout(rfidCode):
    '''a function that will take an rfidCode and
       return 'OUT' if the employee is clocked out (or not in today)
       reuturn 'IN' if the employee is currently clocked in
    '''
    datetoday = str(date.today())
    c = db.cursor()
    c.execute('SELECT * FROM {tn} WHERE RFIDcode = {cn} AND clockdate = "{today}" order by clocktime'.\
              format(tn='clocking', cn=rfidCode, today = datetoday))
    all_rows = c.fetchall()
    if len(all_rows) == 0:
        return "OUT"
    else:
        return "OUT" if all_rows[-1][5]==0 else "IN"

def clockinorout(employeeID, inorout, clientID):
    datetoday = str(date.today())
    TimeNow = datetime.now()
    current_time = TimeNow.strftime("%H:%M:%S")
    c = db.cursor()
    c.execute('INSERT INTO clocking (RFIDcode, clientID, clockdate, clocktime, comingin)VALUES ({RFIDcode},"{cID}", "{today}", "{ct}", {io})'.\
              format(RFIDcode=employeeID, today = datetoday, ct = current_time, io=inorout,cID=clientID))
    db.commit()

#code ideas taken from https://realpython.com/python-sockets/ 
def accept_wrapper(sock):
  conn, addr = sock.accept() # Should be ready to read
  print("accepted connection from", addr)
  conn.setblocking(False)
  data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  sel.register(conn, events, data=data)

def service_connection(key, mask):
  sock = key.fileobj
  data = key.data
  if mask & selectors.EVENT_READ:
    recv_data = sock.recv(1024) # Should be ready to read
    if recv_data:
      data.outb += recv_data
    else:
      print("closing connection to", data.addr)
      sel.unregister(sock)
      sock.close()
  if mask & selectors.EVENT_WRITE:
    if data.outb:
      commCode = str(data.outb)
      print(commCode)
      commCode = commCode.split('$')
      commCommand = commCode[0][2:]
      print('Command:',commCommand)
      commData = commCode[1][:-1]
      print(commData)
      
      #make choice depending on what the commCode is
      #INIT - need to check if client is authorised
      #RFID - need to process an RFID code
      
      if commCommand == "INIT":
          print('Processing INIT command')
          #for now just return OK
          #really need to search to see if client is authorised
          data.outb = "OK$ ".encode()
      elif commCommand == "RFID":
          print('Processing RFID command')
          person = findRFID(commData)
          if person == "UNKNOWN":
            print('Unknown person')
            data.outb = f"ERROR$Unknown fob\nPlease see HR".encode()
          else:
            inout = inorout(commData)
            if inout == 'OUT':
                message = 'CLOCKED IN'
            else:
                message = 'CLOCKED OUT'
            inout = 1 if inout=='OUT' else 0
            data.outb = f"CLOCKED$Welcome {person[0]} {person[1]}\n{message}".encode()
            clockinorout(commData,inout,'192.168.1.3')
            print("echoing", repr(data.outb), "to", data.addr)
      sent = sock.send(data.outb) # Should be ready to write
      data.outb = data.outb[sent:]



if len(sys.argv) != 3:
  print("usage:", sys.argv[0], "<host> <port>")
  sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
  while True:
    events = sel.select(timeout=None)
    for key, mask in events:
      if key.data is None:
        accept_wrapper(key.fileobj)
      else:
        service_connection(key, mask)
except KeyboardInterrupt:
  print("caught keyboard interrupt, exiting")
finally:
  sel.close()
