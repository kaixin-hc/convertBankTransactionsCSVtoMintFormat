import pandas as pd;

# Define functions to do conversion for different banks
# Define function to do Standard Chartered conversion

def convertScCsv(source, outputFilePath):
    df=pd.read_csv(source,names=["Date", "Transaction", "Currency", "Deposit", "Withdrawal", "Running Balance", "SGD Equivalent Balance"])
    # Cleanup: Drop the non-data columns on top
    indToDropTo = df[df['Transaction']=='Transaction'].index.item()
    df = df.iloc[(indToDropTo + 1):]
    # Cleanup: Remove all the tabs from the date to clean the data, and change date format
    df["Date"] = df["Date"].map(lambda x: x[-7:-4] + x[-10:-7] + x[-4:])
    
    # Format mint CSV: Date,Description,Original Description,Amount,Transaction Type,Category,Account Name,Labels,Notes
    mintdf = pd.DataFrame({},columns=['Date','Description','Original Description','Amount','Transaction Type','Category','Account Name','Labels','Notes']);
    mintdf["Date"] = df["Date"]
    mintdf["Notes"] = df["Transaction"]
    for index, row in df.iterrows():
        if (pd.isna(row['Deposit'])):
            mintdf["Amount"][index] = row["Withdrawal"]
            mintdf["Transaction Type"][index] = "debit"
            if ("BUS/MRT" in row['Transaction']):
                mintdf["Category"][index] = "Auto & Transport:Public Transportation"
        else:
            mintdf["Amount"][index] = row["Deposit"]
            mintdf["Transaction Type"][index] = "credit"
    mintdf.to_csv(outputFilePath, header=False, index=False)

# Standard chartered credit card
def convertSCSimplyCashCsv(source, outputFilePath):
    # Import file
    df=pd.read_csv(source, names=["Date", "DESCRIPTION", "Foreign Currency Amount", "SGD Amount"])

    # Clean: Drop redundant rows at the top + bottom 6 which are metadata
    indToDropTo = df[df['Date']=='Date'].index.item()
    df = df.iloc[(indToDropTo + 1):-6]

    # Clean: Remove tabs from date
    df["Date"] = df["Date"].map(lambda x: x[-7:-4] + x[-10:-7] + x[-4:])

    # Clean: Amount spent
    df["SGD Amount"] = df["SGD Amount"].map(lambda x: x.split(" "))
    df["Transaction Type"] = df["SGD Amount"].map(lambda x: "credit" if x[-1]=="CR" else "debit")
    df["SGD Amount"] = df["SGD Amount"].map(lambda x: x[1])

    # Format of ideal CSV: Date,Description,Original Description,Amount,Transaction Type,Category,Account Name,Labels,Notes
    mintdf = pd.DataFrame({},columns=['Date','Description','Original Description','Amount','Transaction Type','Category','Account Name','Labels','Notes']);
    mintdf["Date"] = df["Date"]
    mintdf["Notes"] = df["DESCRIPTION"]
    mintdf["Amount"] = df["SGD Amount"]
    mintdf["Transaction Type"] = df["Transaction Type"]

    # Categorise as you like
    for index, row in mintdf.iterrows():
        if ("BUS/MRT" in row['Notes']):
            mintdf["Category"][index] = "Auto & Transport:Public Transportation"
    
    # Export file
    mintdf.to_csv(outputFilePath, header=False, index=False)


def convertDBSCsv(source, outputFilePath):
    df=pd.read_csv(source, names=["Date", "Reference", "Debit Amount", "Credit Amount", "Transaction Ref1", "Transaction Ref2","Transaction Ref3"])
    # Drop columns above the data
    headerInd = df[df['Reference']=='Reference'].index.item()
    df = df.iloc[(headerInd + 3):] # there are extra 2 rows below the header which are empty
    # Reformat dates)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date"] = df['Date'].dt.strftime('%m/%d/%Y')
    
    # Format mint CSV: Date,Description,Original Description,Amount,Transaction Type,Category,Account Name,Labels,Notes
    mintdf = pd.DataFrame({},columns=['Date','Description','Original Description','Amount','Transaction Type','Category','Account Name','Labels','Notes']);
    mintdf["Date"] = df["Date"]
    df.update(df[["Transaction Ref1", "Transaction Ref2", "Transaction Ref3"]].fillna(''))
    mintdf["Notes"] = df["Transaction Ref1"] + df["Transaction Ref2"] + df["Transaction Ref3"]
    for index, row in df.iterrows():
        if (row['Credit Amount'] == ' '):
            mintdf["Amount"][index] = row["Debit Amount"]
            mintdf["Transaction Type"][index] = "debit"
            if ("BUS/MRT" in mintdf["Notes"][index]):
                mintdf["Category"][index] = "Auto & Transport:Public Transportation"
        else:
            mintdf["Amount"][index] = row["Credit Amount"]
            mintdf["Transaction Type"][index] = "credit"
        
    
    mintdf.to_csv(outputFilePath, header=False, index=False)

# Write main script
source = input("Input the source file (expected to be a CSV of DBS or SC(jumpstart) or SC(simply cash) format): \n")
outputFileName = input("Input the name of the file you want to create: \n")
bank = input("Input SC or SCSC or DBS: \n")
while (bank != "SC" and bank != "DBS" and bank != "SCSC"):
    bank = input("Input was not valid. Input SC, DBS, or SCSC. \n")

if bank == "DBS":
    convertDBSCsv(source, outputFileName)
    print("Successfully created file from DBS csv at " + outputFileName)
elif bank == "SC":
    convertScCsv(source, outputFileName)
    print("Successfully created file from SC csv at " + outputFileName)
elif bank == "SCSC":
    convertSCSimplyCashCsv(source, outputFileName)
    print("Successfully created file from SC Simply Cash csv at " + outputFileName)
else:
    print("Some error occurred. Maybe use the jupyter notebook instead")
