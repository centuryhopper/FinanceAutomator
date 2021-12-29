import csv
import json
import datetime
import re
import pandas as pd
import numpy as np
import os
from Models import Transaction, transaction_from_json
from datetime import date

'''
json.load => returns a dict obj from a json file
json.dump => writes a dict obj to a file in json format

Script Functionality: calculate the net total spent on the given month (add up all the 'debit' and subtract 'credit' from it)
Your personal profit, p, will be your monthly income, m, minus the net total spent, n, so p = m - n

TODO: get monthly income from checkings account csv

'''

# key: string, value: list of dicts
transactions = {}

try:
    with open('transactions.json') as json_file:
        transactions = json.load(json_file)
except Exception as e:
    print(e)

df = pd.read_csv('exports/credit_card.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
df['Account_Number'] = '9190'
df.drop('Check Number', axis=1, inplace=True)
# print(len(df['Date'][0].strftime('%Y-%m-%d')),df['Date'][0].strftime('%Y-%m-%d'))

df['raw_amt'] = df['Amount'].copy()
df['raw_amt'] = df['raw_amt'].apply(lambda x: float(x[1:]) if x[0] == '$' else -float(x.strip('()')[1:]))
# print(df)
netTotalSpent = df['raw_amt'].sum()
print(f'netTotalSpent: {netTotalSpent}')
df.drop('raw_amt', axis=1, inplace=True)



monthlyIncome = 0
df2 = pd.read_csv('exports/checkings.csv')
df2['to_add'] = np.where(df2['Description'].str.startswith('EDI'), df2['Amount'].str[1:], '0.0')
df2['to_add'] = df2['to_add'].astype(float)
# print(df2)

monthlyIncome = df2['to_add'].sum()
print(f'monthly income: {monthlyIncome}')

print(f'personal profit: {monthlyIncome - netTotalSpent}')















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

for k,v in transactions.items():
    transactions[k] = sorted(v,key=lambda x:x['date'])

#region createTransactionsJson()
def createTransactionsJson():
    with open('transactions.json', 'w') as json_file:
        json.dump(transactions, json_file, sort_keys=True, indent=4)

#endregion

createTransactionsJson()


