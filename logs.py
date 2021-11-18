import datetime


fileName="log.txt"

#function to writelog text file
def writeLog(str):
    str = str + ' =>>>> at:'+datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    with open(fileName, "a") as text_file:
      text_file.write(str)
      text_file.write("\n")
    print(str)