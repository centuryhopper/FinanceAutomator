import csv
import json
import datetime
import re
import pandas as pd
import numpy as np
import os
import glob
import shutil
import random
from time import sleep
from secrets import Secrets
from Models import Transaction, transaction_from_json
from datetime import date
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

'''
json.load => returns a dict obj from a json file
json.dump => writes a dict obj to a file in json format

Script Functionality: calculate the net total spent on the given month (add up all the 'debit' and subtract 'credit' from it)
Your personal profit, p, will be your monthly income, m, minus the net total spent, n, so p = m - n

TODO: get monthly income from checkings account csv

'''

# key: string, value: list of dicts
transactions = {}

# try:
#     with open('transactions.json') as json_file:
#         transactions = json.load(json_file)
# except Exception as e:
#     print(e)

#region appendToCSV
def appendToCSV(df,filePath):
    # if file does not exist write header
    if not os.path.isfile(filePath):
        df.to_csv(filePath,index=False)
    else: # else it exists so append without writing the header
        df.to_csv(filePath, index=False, mode='a', header=False)
#endregion

#region extractCSVs
def extractCSVs():
    driver = webdriver.Chrome(Secrets.CHROME_DRIVER_PATH)
    driver.get('https://www.truist.com')
    driver.implicitly_wait(random.uniform(1,2))
    driver.maximize_window()
    signIn = driver.find_element(By.XPATH, '//*[@id="signOnComp"]')
    signIn.click()


    loginUser = driver.find_element(By.XPATH, '//*[@id="login-user-id-Login-unique-id1234"]')
    loginUser.clear()
    loginUser.send_keys(Secrets.truistUserID)


    loginPassword = driver.find_element(By.XPATH, '//*[@id="login-password"]')
    loginPassword.clear()
    loginPassword.send_keys(Secrets.truistPassword)


    signInbutton = driver.find_element(By.XPATH, '//*[@id="login-form-Login-unique-id1234"]/div[2]/div/button')
    signInbutton.click()


    # get credit card transaction csv
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="router"]/main/truist-olb-cmp-dashboard/truist-olb-cmp-consumer-dashboard/tru-core-grid/div/truist-olb-cmp-component-loader/truist-olb-cmp-retail-account-list/div[2]/a[1]/truist-olb-cmp-account-card/div'))).click()
    # creditCardTab = driver.find_element(By.XPATH, '//*[@id="router"]/main/truist-olb-cmp-dashboard/truist-olb-cmp-consumer-dashboard/tru-core-grid/div/truist-olb-cmp-component-loader/truist-olb-cmp-retail-account-list/div[2]/a[1]/truist-olb-cmp-account-card/div')
    # creditCardTab.click()


    # downloadTab = driver.find_element(By.XPATH, '//*[@id="router"]/main/truist-olb-cmp-accounts/div/tru-core-grid/div[2]/truist-olb-cmp-internal-accounts/truist-olb-cmp-account-dep-transactions/div/tru-core-card/div/tru-core-card-header/tru-core-grid/tru-core-grid/tru-core-button-tertiary[1]/button')
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="router"]/main/truist-olb-cmp-accounts/div/tru-core-grid/div[2]/truist-olb-cmp-internal-accounts/truist-olb-cmp-account-dep-transactions/div/tru-core-card/div/tru-core-card-header/tru-core-grid/tru-core-grid/tru-core-button-tertiary[1]/button'))).click()


    # sort by 30 days
    monthlyOption = driver.find_element(By.XPATH, '//*[@id="mat-button-toggle-2-button"]')
    monthlyOption.click()

    sleep(random.uniform(1,2))

    # download csv
    # //*[@id="tru-core-modal-panel-29"]/div/truist-olb-cmp-download-transactions/form/tru-core-card-actions/tru-core-button-primary/button
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Download"]'))).click()
    download = driver.find_element(By.XPATH, '//button[text()=" Download "]')
    download.click()

    sleep(3)

    # move latest csv file in download folder to exports folder here (expected file is the one that was just downloaded)
    folder_path = Secrets.downloadsFolderPath
    file_type = '*csv'
    files = glob.glob(folder_path + file_type)
    renameCreditCardFile = f"{Secrets.creditCardFileName}_transactions_{datetime.date.today().strftime('%Y-%m-%d')}.csv"
    if files:
        max_file = max(files, key=os.path.getctime)
        fileName = os.path.basename(max_file)
        shutil.move(max_file, Secrets.destinationFolder)
        os.rename(Secrets.destinationFolder+fileName, Secrets.destinationFolder+renameCreditCardFile)
    else:
        driver.close()
        return None


    acctTab = driver.find_element(By.XPATH, '//button[starts-with(@id, "tru-core-select-trigger-3")]')
    acctTab.click()


    checkings = driver.find_element(By.XPATH, '//li[text()="Checking 7812"]')
    checkings.click()


    # sort by 30 days
    monthlyOption = driver.find_element(By.XPATH, '//*[@id="mat-button-toggle-2-button"]')
    monthlyOption.click()

    download = driver.find_element(By.XPATH, '//button[text()=" Download "]')
    download.click()

    sleep(3)

    files = glob.glob(folder_path + file_type)
    renameCheckingsFileName = f"{Secrets.checkingsFileName}_transactions_{datetime.date.today().strftime('%Y-%m-%d')}.csv"
    if files:
        max_file = max(files, key=os.path.getctime)
        fileName = os.path.basename(max_file)
        shutil.move(max_file, Secrets.destinationFolder)
        os.rename(Secrets.destinationFolder+fileName, Secrets.destinationFolder+renameCheckingsFileName)
    else:
        driver.close()
        return None

    driver.close()
    return (renameCreditCardFile, renameCheckingsFileName)

#endregion

#region processBankInfo
def processBankInfo(creditCardFileName, checkingsFileName):
    df = pd.read_csv(f'exports/{creditCardFileName}')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df['Account_Number'] = '9190'
    df.drop('Check Number', axis=1, inplace=True)
    # print(len(df['Date'][0].strftime('%Y-%m-%d')),df['Date'][0].strftime('%Y-%m-%d'))

    df['raw_amt'] = df['Amount'].copy()
    df['raw_amt'] = df['raw_amt'].apply(lambda x: float(x[1:]) if x[0] == '$' else -float(x.strip('()')[1:]))
    # print(df)

    netTotalSpent = round(df['raw_amt'].sum(),2)
    print(f'netTotalSpent: {netTotalSpent}')
    df.drop('raw_amt', axis=1, inplace=True)

    monthlyIncome = 0
    df2 = pd.read_csv(f'exports/{checkingsFileName}')
    df2['to_add'] = np.where(df2['Description'].str.startswith('EDI'), df2['Amount'].str[1:], '0.0')
    df2['to_add'] = df2['to_add'].astype(float)
    # print(df2)

    monthlyIncome = round(df2['to_add'].sum(),2)
    print(f'monthly income: {monthlyIncome}')

    profit = round(monthlyIncome - netTotalSpent,2)
    print(f'personal profit: {profit}')

    monthlyAnalysisDF = pd.DataFrame({'date': [datetime.date.today().strftime('%Y-%m-%d')],'monthly_net_expenses':[netTotalSpent], 'monthly_income': [monthlyIncome], 'monthly_profit': [profit]})
    appendToCSV(monthlyAnalysisDF,f'{Secrets.outputFolderPath}monthly_finances_analysis.csv')

    # covert dataframe to json format
    for row in df.itertuples():
        # print(type(row),row)
        if row:
            date = row[1]
            transactionType = row[2]
            description = row[3]
            # drop any parentheses. They represent credit
            transaction_amount = row[4].strip('()')
            account_num = row[5]

            # transaction obj
            transaction = Transaction(
                description=description,
                transactionType=transactionType,
                amount=transaction_amount,
                date=date,
                account_number=account_num,
            )

            transactionName = transaction.description.split()[0]

            if transactionName not in transactions:
                transactions[transactionName] = []

            # maintain transaction uniqueness
            exists = False
            for transactionDict in transactions[transactionName]:
                if transactionDict.get('date') == transaction.date:
                    if transactionDict.get('transaction_type') == transaction.transactionType:
                        if transactionDict.get('amount') == transaction.amount:
                            exists = True
            if not exists:
                transactions[transactionName].append(transaction.serialize())

    # sort each list
    for k,v in transactions.items():
        transactions[k] = sorted(v,key=lambda x:x['date'])
#endregion

#region createTransactionsJson()
def createTransactionsJson():
    with open(f"outputs/transactions_{datetime.date.today().strftime('%Y-%m-%d')}.json", 'w') as json_file:
        json.dump(transactions, json_file, sort_keys=True, indent=4)

#endregion

def main():
    files = extractCSVs()
    if not files:
        print('could not extract all necessary files')
        return
    creditCardCSV, checksAccCSV = files
    processBankInfo(creditCardCSV, checksAccCSV)
    createTransactionsJson()

if __name__ == '__main__':
    main()

