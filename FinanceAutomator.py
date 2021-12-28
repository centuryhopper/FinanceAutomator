import csv
import json
import datetime
import re
import pandas as pd
from Models import Transaction, Statement, statement_from_json, transaction_from_json
from datetime import date
'''
json.load => returns a dict obj from a json file
json.dump => writes a dict obj to a file in json format
'''
# transactions to statements (goal)
data = {}
transactions = []
try:
    with open('transactions.json') as json_file:
        data = json.load(json_file)
        for info in data["Transactions"]:
            transactions.append(transaction_from_json(info))
    with open('statements.json') as json_file:
        data = json.load(json_file)
        for info in data["Statements"]:
            statements.append(statement_from_json(info))
except:
    print("Exception")

#region getFloat(lst)
def getFloat(lst):
    try:
        list_ = lst.split(".")
        amount = ""
        for num in list_:
            amount = amount + num
        amount = amount.split(",")
        amount = float(amount[0] + "." + amount[1])
        return amount
    except:
        return 0.0
#endregion

df = pd.read_csv('exports/export.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
df['Account_Number'] = '9190'
df.drop('Check Number', axis=1, inplace=True)
# print(len(df['Date'][0].strftime('%Y-%m-%d')),df['Date'][0].strftime('%Y-%m-%d'))
# print(df)

for row in df.itertuples():
    # print(row)
    # print(row[0], row[1], row[2], row[3], row[4], row[5])
    if len(row) > 0:
        date_ = row[1]
        account_num = row[5]
        transactionType = row[2]
        # drop any parentheses. They represent credit
        # formatAmt = row[4].strip('()')
        # drop the dollar sign
        transaction_amount = row[4].strip('()')

        # transaction obj
        transaction = Transaction(
            name=transactionType,
            amount=transaction_amount,
            date=date_,
            account_number=account_num,
        )

        # maintain transaction uniqueness
        exists = False
        for transfer in transactions:
            if transfer.date == transaction.date:
                if transfer.name == transaction.name:
                    if transfer.amount == transaction.amount:
                        exists = True
        if exists != True:
                transactions.append(transaction)

for transaction in transactions:
    print(transaction)


states = []

#region  createTransactionsJson()
def createTransactionsJson():
    with open('transactions.json', 'w') as json_file:
        data = {}
        data["Transactions"] = []
        for transfer in transactions:
            date_day = datetime.datetime.strptime(transfer.date, "%Y-%M-%d").date().strftime("%Y%m")
            # statement object
            statement = Statement(date_day, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            data["Transactions"].append(transfer.serialize())
            exists = False
            for stat_ in states:
                if stat_.date == date_day:
                    statement = stat_
            statement.create_statement(transfer)
            statement.set_ending_balance_month()
            for state in states:
                if state.date == statement.date:
                    exists = True
            if not exists:
                states.append(statement)
        json.dump(data, json_file, sort_keys=True, indent=4)

#endregion

createTransactionsJson()

statements = sorted(
    states,
    key=lambda x: datetime.datetime.strptime(x.date, '%Y%m').date(), reverse=True
)

#region createStatementsJson()
def createStatementsJson():
    with open('statements.json', 'w') as json_file:
        data = {}
        data["Statements"] = []
        for stat_ in statements:
            data["Statements"].append(stat_.serialize())
        json.dump(data, json_file, sort_keys=True, indent=4)

#endregion

# createStatementsJson()

#region calculations()
def calculations():
    total_income = 0.0
    total_expenses = 0.0
    total_taxes = 0.0
    taxes_paid = 0.0
    salary_taken = 0.0
    total_withdrawls = 0.0
    for stat_ in statements:
        total_income = total_income + stat_.income
        total_expenses = total_expenses + stat_.buisiness_expenses
        salary_taken = salary_taken + stat_.salary
        taxes_paid = taxes_paid + stat_.tax_paid
        total_withdrawls = total_withdrawls + stat_.withdrew
    total_taxes = (salary_taken / 2) * 3 - taxes_paid
    # print(str(total_withdrawls) + " - " + str(taxes_paid) + " = " + str(total_withdrawls - taxes_paid))
    total_withdrawls = total_withdrawls - taxes_paid
    total_net_income = (total_income + total_expenses) + salary_taken + (total_taxes)
    potential_salary = (total_net_income + taxes_paid) * 0.4
    print("\n"*3)
    print("Total income: " + str(total_income))
    print("Total NET income: " + str(total_net_income))
    print("Total expenses: " + str(total_expenses))
    print("Total tax to pay: " + str(total_taxes))
    print("Potential salary: " + str(potential_salary))
    print("Salary taken: " + str(salary_taken))
    print("Total withdrawls: " + str(total_withdrawls))
    print("\n"*3)

#endregion

# calculations()
