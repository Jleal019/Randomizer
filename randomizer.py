import pandas, os, secrets, datetime, sys, math, warnings
from configparser import ConfigParser

# This is for testing custom dates
# today = datetime.datetime(2027, 10, 7)

today = datetime.datetime.today()

# suppresses futureWarning for dataframe concat with NaN
warnings.simplefilter(action='ignore', category=FutureWarning)
# Updates the datePicked column in Personnel.csv
def update_PersonnelCSV(x):
    data.loc[x, "Date Picked"] = today.strftime("%m/%d/%Y")
    # print("This is the datePick", type(data.loc[x, "Date Picked"]))
    data.loc[x, "Eligible"] += 1
    
    data.to_csv("Personnel.csv",index=False)
    # print("Updated this: ", data.loc[x])


# Determines if the amount eligible is valid 
def elgblValue(x):

    eligbl = data.loc[x, "Eligible"]

    # if eligbl equals 2, returns False
    if eligbl == 2:
        # print("Not Valid.")
        return False
    
    elif eligbl < 2:
        # print("Valid, less than 2.")
        return True
    
    elif eligbl is None:
        # print("Valid. Is None.")
        return True


# Adds 1 year to Date Picked on column and saves to variable DateAfter1Yr.
# Compares today to DateAfter1Yr and if it's greater than DateAfter1Yr,
# It returns True. Else, it returns False. Catches TypeError (No date entered)
# Returns True and selects the person.
def isValidBoolean(x):

    try:
        # print("This is the Object we're checking.", x,data.loc[x, "Last Name"])
        datePick = datetime.datetime.strptime(data.loc[x,"Date Picked"], "%m/%d/%Y")
        dateAfter1Yr = datePick + datetime.timedelta(days=365)

        # If today is less than the picked date plus 1 year, return True so the person can be picked
        # else, return False. The person will not be picked.
        if today >= dateAfter1Yr:
            # print("Keeping record",x)
            # print(today, "is greater than the dateAfer1Yr",dateAfter1Yr)
            return True
            
        elif today < dateAfter1Yr:
            # print("Dropping record",x)
            # print(today, "is less than dateAfter1Yr", dateAfter1Yr)
            return False
            
    except TypeError:
        # A TypeError exception would imply no date entered. The selection would occur.
        # print("This object has never been picked before.")
        return True
    

# Filters data from dataframe that isn't possible for selection.
def filterData():
    dataLen = len(data)
    # print("numPpl in loop", numPpl)
    # Terminates program if the number of selections is greater than the amount of data.
    if numPpl > len(data):
        print("You want to select ", numPpl, " but there are only ", len(data)," possible choices in your list. Select less and try again.")
        sys.exit(1)


    # Iterates through the Index and passes each row to isValidBoolean.
    # If it returns True, it will simply decrement dataLen. Else,
    # it will drop the row and then decrement dataLen.
    for x in selektedData.index:
    
        eligbl = data.loc[x, "Eligible"]
        if math.isnan(eligbl) == True:
            data.loc[x, "Eligible"] = 0

        if isValidBoolean(x) == False and elgblValue(x) == False:
            # print("Not valid.")
            selektedData.drop(x, inplace=True)
            dataLen -= 1
            
    # print("Filtered DataSet: ", selektedData)
    print('Length of filtered dataframe', len(selektedData))

    
# Check config file
def resetTimer():
    conObject = ConfigParser()

    # thisYr = datetime.date.today().year
    thisYr = today.year
    try:
        # Read config file and update year setting.
        conObject.read("config.ini")
        settings = conObject["SETTINGS"]
        
        lastRunYr = int(settings["LastRan"])

        if lastRunYr < thisYr:
            for entry in data.index:
                data.loc[entry, "Date Picked"] = None
                data.loc[entry, "Eligible"] = 0

            settings["LastRan"] = str(thisYr)
            with open("config.ini","w") as config:
                conObject.write(config)
            data.to_csv("Personnel.csv",index=True)

    except KeyError:
        # Creates config file 
        conObject["SETTINGS"] = {
            "LastRan": thisYr
        }
        with open("config.ini","w") as config:
            conObject.write(config)


#############################################
##################################################
print("#####################################################")
print("###### Randomizer ######")
print("#####################################################\n")
print("Please remember, the file name should be Personnel.csv.")

filDir = ".\\Personnel.csv"
# filDir = input("Enter the directory the file is in Default file is Personnel.csv.\n")
# print("Enter the directory the file is in Default file is Personnel.csv.\n")

# if filDir == "":
#     filDir = ".\\Personnel.csv"
# else:
#     filDir = input

numPpl = input("Enter the number of entries to return.")
numPpl = int(numPpl)
# print("Enter the number of entries to return.")
# numPpl = 11

data = pandas.read_csv(filDir)
print("\nThe total number of entries in the file is: ", len(data))

# print("Today's Date:", datetime.date.today().strftime("%m/%d/%Y"))

resetTimer()

selektedData = data.copy()

filterData()

try:
    selektions = pandas.DataFrame(columns=data.columns)
    nuRows = []

    for y in range(numPpl):
        item = secrets.choice(selektedData.index)
        nuRows.append(selektedData.loc[item])
        # print("nuRows", nuRows)
        update_PersonnelCSV(item)
        selektedData.drop(item, inplace=True)

except IndexError:
    print("WARNING: You requested",numPpl, "but there aren't enough that meet the given criteria.")


# Append Dataframes and add that to the Selections.csv
df = pandas.DataFrame(nuRows)
selektions = pandas.concat([selektions,df], ignore_index=True)
selektionsFileName = "Selections " + today.strftime("%m-%d-%Y") + ".csv"

# print("Selections", selektions)
selektions.to_csv(selektionsFileName,columns=["Last Name", "First Name"],index=False)


input("\nYou may now close this window.")
