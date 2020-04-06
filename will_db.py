import sqlite3
import os
from datetime import datetime, date

DEBUG = True

db = sqlite3.connect('mydb.db')

cursor = db.cursor()



    
def CreateTableEmployee():
    try:
        cursor.execute('''
    CREATE TABLE employee( employeeID int PRIMARY KEY, RFIDcode varchar(10), firstname varchar(50),
    surname varchar(50), department varchar(50), jobtitle varchar(50))
    ''')
        db.commit()
    except:
        if DEBUG:
            print('\n [DEBUG] TableEmployee already exists. \n ')



def CreateTableHours():
    try:
        cursor.execute('''
        CREATE TABLE hours( hourID int PRIMARY KEY, weekID int, employeeID int, totalhoursforweek real)
        ''')
        db.commit()
    except:
        if DEBUG:
            print('\n [DEBUG] TableHours already exists. \n ')


def CreateTableClocking():
    try:
        cursor.execute('''
        CREATE TABLE clocking( clockingID integer PRIMARY KEY AUTOINCREMENT, RFIDcode varchar(10), clientID int, clockdate datetime,clocktime datetime, comingIn boolean)
        ''')
        db.commit()
    except:
        if DEBUG:
            print('\n [DEBUG] TableClocking already exists. \n ')

def CreateTableClients():
    try:
        cursor.execute('''
        CREATE TABLE clients( clientID int, MacAddress string, IpAddress string, Description string, LastSeen string)
        ''')
        db.commit()
    except:
        if DEBUG:
            print('\n [DEBUG] TableClients already exists. \n ')

def menu():
    importcsvdata()
    option = "x"
    while option != "0":
        print("Initialise Database")
        print("1. CreateTableEmployee ")
        print("2. CreateTableHours ")
        print("3. CreateTableClocking ")
        print("4. CreateTableClients ")
        print("4.5. Import newest csv data")
        print("5. Turn Debug mode off")
        print("0. Quit")
        option = input(":: ")
        if option == "1":
            init_suppliers()
        elif option == "2":
            create_supplier(check_number_of_suppliers())
        elif option == "3":
            debug = False
        elif option == "4":
            EmployeeHours()
        elif option == "4.5":
            importcsvdata()
        elif option == "0":
            db.commit()
        print()
        print()




def AddDataClocking(RFIDcode, clientID):
    '''server-code: having received RFID code from a client
        if RFID code does not exist send back error code to client
        otherwise add data to table
    '''
    sqlstring = f"SELECT * FROM employee WHERE RFIDcode = '{RFIDcode}'"
    #print(sqlstring)
    cursor.execute(sqlstring)
    user = cursor.fetchone()
    #print(user)
    if user[0] == None:
        if DEBUG:
            print('RFID code not in database')
    else:   #now add data
        TimeNow = datetime.now()
        current_time = TimeNow.strftime("%H:%M:%S")
        currentClockingID = 1
        clockingIDNOW = currentClockingID =+ 1
        today = date.today()
        currenttime = f'{today.day}/{today.month}/{today.year}'
        sqlstring = f"INSERT INTO clocking (RFIDcode, clientID, clockdate, clocktime, comingin) VALUES ({RFIDcode}, '{clientID}', '{today}', '{current_time}', 1)"
        #print(sqlstring)
        cursor.execute(sqlstring)
        print("test print")
        db.commit()


def importcsvdata():
    csvfile = open("data.csv", "r")
    csvfile.readline()
    data = csvfile.readlines()
    for lineofdata in data:
        lineofdata = lineofdata.split(",")
        AddDataClocking(lineofdata[0], lineofdata[1])
    csvfile.close()
    csvfile = open("data.csv","w")
    csvfile.write("RFID Code" + "," + "Client ID" + "," + "\n")
    csvfile.close()

def TestQuery():
    c = db.cursor()
    c.execute('SELECT * FROM {tn} WHERE employeeID = {cn} '.\
              format(tn='employee', cn=1))
    all_rows = c.fetchall()
    print('1):', all_rows)


def findRFID(RFIDcode):
    c = db.cursor()
    c.execute('SELECT * FROM {tn} WHERE employeeID = {cn} '.\
              format(tn='employee', cn=RFIDcode))
    all_rows = c.fetchall()
    #print(len(all_rows))
    #print(all_rows)
    if len(all_rows) == 0:
        return ('UNKNOWN')
    else:
        return (all_rows[0][2],all_rows[0][3])
    

def inorout(employeeID):
    datetoday = str(date.today())
    c = db.cursor()
    c.execute('SELECT * FROM {tn} WHERE RFIDcode = {cn} AND clockdate = "{today}" order by clocktime'.\
              format(tn='clocking', cn=employeeID, today = datetoday))
    all_rows = c.fetchall()
    print(datetoday)
    print(len(all_rows))
    print(all_rows)
    if len(all_rows) == 0:
        return "OUT"
    else:
        return "OUT" if all_rows[-1][5]==0 else "IN"
    
    


def EmployeeHours():
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
            
    
        
def clockinorout(employeeID, inorout, clientID):
    datetoday = str(date.today())
    TimeNow = datetime.now()
    current_time = TimeNow.strftime("%H:%M:%S")
    c = db.cursor()
    c.execute('INSERT INTO clocking (RFIDcode, clientID, clockdate, clocktime, comingin)VALUES ({RFIDcode},"{cID}", "{today}", "{ct}", {io})'.\
              format(RFIDcode=employeeID, today = datetoday, ct = current_time, io=inorout,cID=clientID))
    db.commit()


def hoursperday(employeeID, thedate):
    c = db.cursor()
    c.execute('SELECT * FROM clocking WHERE RFIDcode = {eID} AND clockdate = "{td}" order by clocktime'.\
            format(eID = employeeID, td = thedate))

    

    all_rows = c.fetchall()
    print(thedate)
    print(len(all_rows))
    print(all_rows)
    
    FMT = '%H:%M:%S'
    total = datetime.strptime("00:00:00",FMT)

    if len(all_rows)%2 != 0:
        print('HELP')
        

    for loop in range(0,len(all_rows)-1,2):
        print(all_rows[loop][4],all_rows[loop+1][4])
        
        difference = datetime.strptime(all_rows[loop+1][4], FMT)  - datetime.strptime(all_rows[loop][4], FMT)
        total += difference
        print('diff: ', difference)
    print('total: ',total)
#def AddData



