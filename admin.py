
import sqlite3
import os
from datetime import datetime, date
import csv
import uuid 
import socket


db = sqlite3.connect('mydb.db')
cursor = db.cursor()
currentversion = str('1.01.274')
theTime = datetime.now()


############################################################################################
############################################################################################
############################################################################################
############################################################################################


def get_Host_name_IP(): 
    try: 
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name) 
        print("The Hostname is:  ",host_name) 
        print("The IP address is: ",host_ip) 
    except: 
        print("Unable to get Hostname and IP") 
  
# Driver code 
    get_Host_name_IP() #Function call 
  
# joins elements of getnode() after each 2 digits. 
  
    print ("The MAC address is: ", end="") 
    print (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
    for ele in range(0,8*6,8)][::-1])) 

def mainMenu(): 
    host_name = socket.gethostname() 
    host_ip = socket.gethostbyname(host_name) 
    
    print('\n')
    print('==============================')
    print('Version ' + currentversion + ' BETA edition')
    print('==============================')
    print('\n')
    print('**************************************************')   
    print('    Administrator Program: Authorised use only')
    print('**************************************************')
    print('\n')
    print('IP   = ' + str(host_ip))
    print('Time = ' + str(theTime))
    print('\n')
    print('++++++++++++++++++++++++++++')
    print('1: Database Menu')
    print('2: User Access Controls')
    print('3: Client Hardware Controls')
    print('4: About')
    print('Q: Quit')
    print('++++++++++++++++++++++++++++')
    print('\n')

def dbMenu():
    doQuit = False
    while not doQuit:
        print('\n')
        print('*************')
        print('Database Menu')
        print('*************')
        print('\n')
        print('++++++++++++++++++++++++++++++++++++++++++++')
        print('1: Who is currently on site: ')
        print('2: Hours of a specific employee per month: ')
        print('3: Total hours of a specific employee: ')
        print('4: Where do employees clock in / out most: ')
        print('5: Live SQL mode')
        print('M: go back to main menu')
        print('++++++++++++++++++++++++++++++++++++++++++++')
        print('\n')
        print('\n')
        choice = input(': ').upper()
        if choice == '1':
            dbMenu1()
        elif choice == '2':
            dbMenu2()
        elif choice == '3':
            dbMenu3()
        elif choice == '4':
            dbMenu4()
        elif choice == '5':
            dbMenu5()
        elif choice == 'M':
            doQuit = True
        else:
            print('The character you inputted might not be fully supported yet: Please try again')   

def dbMenu1():
    print('\n \n')
    print('\n \n')
    #who is currently in the building or on site
    c = db.cursor()
    today = date.today()
    print(today)
    theTime = datetime.now()
    current_time = theTime.strftime("%H:%M")
    sqlQuery = "SELECT employee.rfidcode, employee.surname, employee.firstname, clocking.comingIn, clocking.clocktime FROM Clocking INNER JOIN employee ON employee.rfidcode = clocking.rfidcode WHERE  clockdate=? order by clocktime asc"
    c.execute( sqlQuery , (today,))
    allrows = c.fetchall()
    if len(allrows) == 0:
        print("There is no one clocked in currently at the time of " + str(theTime) )
        allrows = []
    else:
        #print(allrows)
        employee = []
        for row in allrows:
            if row[0] not in employee:
                employee.append(row[0])
                if row[3] ==1:
                    print(row[0], row[1], row[2], "is currently on site at the time of " + str(theTime) + " NOW")

    with open('ONSITE_EXPORT.csv', 'w', newline='') as f_handle:
        writer = csv.writer(f_handle)
        # Add the header/column names
        header = ['RFID Number', 'First Name', 'Second Name', 'Clocking Status (1 = IN)', 'Clocking in time']
        writer.writerow(header)
        # Iterate over `data`  and  write to the csv file
        for row in allrows:
            writer.writerow(row)

def dbMenu2():
    print('\n \n')
    print('\n \n')
    print('This function is not available yet:' )
    print('Stay tuned for version 1.02 (This version is version number ' + currentversion + ')')
    pass

def dbMenu3():
    print('\n \n')
    print('\n \n')
    c = db.cursor()
    print("Please enter the surname of the employee")
    enteredname = input(":: ")
    #c.execute("SELECT employee.surname, employee.employeeID FROM  employee WHERE employee.surname=?", (enteredname,))
    c.execute("SELECT surname, firstname, employeeID FROM employee WHERE surname=?", (enteredname,))
    allrows = c.fetchall()
    if len(allrows) == 0:
        print("Employee not found")
        allrows = []
    elif len(allrows) == 1:
        print("Only one employee of this name found, printing data for them now")
        c.execute("SELECT hours.totalhoursforweek, employee.surname, employee.firstname, employee.employeeID FROM hours INNER JOIN employee ON employee.employeeID = hours.employeeID WHERE employee.surname=?", (enteredname,))
        allrows = c.fetchall()
        print(allrows)
    else:
        print("There is more than one person with this surname, please type in their ID")
        for row in allrows:
            print("Name", row[1], row[0], "EmployeeID", row[2])
        enteredID = input(":: ")
        c.execute("SELECT hours.totalhoursforweek, employee.surname, employee.firstname, employee.employeeID FROM hours INNER JOIN employee ON employee.employeeID = hours.employeeID WHERE employee.employeeID=?", (enteredID,))
        allrows = c.fetchall()
        totalhours = 0
        for row in allrows:
            totalhours += row[0]
        if len(allrows) != 0:
            print("In their lifetime at the company", allrows[0][2], allrows[0][1], "has worked", totalhours, "hours")

    with open('TOTALHOURS_EXPORT.csv', 'w', newline='') as f_handle:
        writer = csv.writer(f_handle)
        # Add the header/column names
        header = ['Total Hours', 'Second Name', 'First Name', 'Employee ID']
        writer.writerow(header)
        # Iterate over `data`  and  write to the csv file
        for row in allrows:
            writer.writerow(row)

def dbMenu4():
    print('\n \n')
    print('\n \n')
    c = db.cursor()
    #What client station do employees use most

    sqlquery = ("SELECT COUNT(clientID) ,clientID FROM clocking group BY clientID")
    c.execute(sqlquery)
    allrows = c.fetchall()

    for row in allrows:
        print("Number of uses: " + str(row[0]) + "  " + "IP Address: " + str(row[1]))

    with open('CLIENT_MACHINE_EXPORT.csv', 'w', newline='') as f_handle:
        writer = csv.writer(f_handle)
        # Add the header/column names
        header = ['Number of uses', 'IP Address Number']
        writer.writerow(header)
        # Iterate over `data`  and  write to the csv file
        for row in allrows:
            writer.writerow(row)

def dbMenu5():
    c = db.cursor()
    adminsql = input("Please enter SQL commands to execute:  ")
    c.execute(adminsql)
    allrows = c.fetchall()
    print(allrows)

def clientMenu():
    print('\n \n')
    print('\n \n')
    print('Client Menu \n \n')
    print('This is coming in a future update:')
    print('Ability to restart, authorise and stop client machines')
    print('Stay tuned for version 1.02 (This version is version number ' + currentversion + ')')
    
def UserAccessMenu():
    print('\n \n')
    print('\n \n')
    print('User Access Menu \n \n')
    print('This is coming in a future update:')
    print('Ability to add, remove, edit users')
    print('Ability to add and remove RFID cards')
    print('Stay tuned for version 1.02 (This version is version number ' + currentversion + ')')

def About():
    print('\n \n')
    print('This version of the program is BETA ' + currentversion)
    print('Github link to the project and all of the code: https://github.com/williamd002/A-level-NEA')
    print("Copyright William Puchy 2020")
    print('\n \n')
    print(",--.   ,--.,--.,--.,--.,--.                      ,------.               ,--.               ")
    print("|  |   |  |`--'|  ||  |`--' ,--,--.,--,--,--.    |  .--. ',--.,--. ,---.|  ,---. ,--. ,--. ")
    print("|  |.'.|  |,--.|  ||  |,--.' ,-.  ||        |    |  '--' ||  ||  || .--'|  .-.  | \  '  /  ")
    print("|   ,'.   ||  ||  ||  ||  |\ '-'  ||  |  |  |    |  | --' '  ''  '\ `--.|  | |  |  \   '   ")
    print("'--'   '--'`--'`--'`--'`--' `--`--'`--`--`--'    `--'      `----'  `---'`--' `--'.-'  /    ")
    print("                                                                                 `---'     ")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print('\n \n')
    print('\n \n')

#main
doQuit = False
while not doQuit:
    mainMenu()
    choice = input(': ').upper()
    if choice == '1':
        dbMenu()
    elif choice == '2':
        UserAccessMenu()
    elif choice == '3':
        clientMenu()
    elif choice == '4':
        About()
    elif choice == 'Q':
        doQuit = True
    else:
        print('Sorry, this character is not currently implemented in the program, Try again...')
print('Closing Program')
print('It is now safe to close this window')
