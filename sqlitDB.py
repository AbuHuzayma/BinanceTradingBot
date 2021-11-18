import datetime
import sqlite3

from logs import writeLog

dataBaseName='RSIBotDB.db'

#function to insert orders to sqlite
def insertOrderDB(orderID,orderRef,Symbol,Quantity,Price,Side,Type,Profit,Lose,InPosition):
    try:
        sqliteConnection = sqlite3.connect(dataBaseName, timeout=20)
        
        sqlite_select_query = "INSERT INTO Orders (orderID,orderRef,Symbol,Quantity,Price,Side,Type,Profit,Lose,InPosition,CreateTime) \
        VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(str(orderID),str(orderRef),str(Symbol),str(Quantity),str(Price),str(Side),str(Type),str(Profit),str(Lose),str(InPosition),datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        writeLog(sqlite_select_query)
        sqliteConnection.execute(sqlite_select_query)
        sqliteConnection.commit()    
        sqliteConnection.close()  

    except sqlite3.Error as error:
       writeLog("an exception occured - {}".format(error))
       return False
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            
    return True

#function to read all orders from sqlite         
def readSqliteTable():
    try:
        sqliteConnection = sqlite3.connect(dataBaseName, timeout=20)
        
        sqlite_select_query = "SELECT * from Orders"
        data = sqliteConnection.execute(sqlite_select_query)
        
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The Sqlite connection is closed")
