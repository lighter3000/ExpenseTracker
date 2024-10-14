import cmd
import json
import os
import argparse
import shlex
from datetime import datetime
import re


class ExpenseTracker(cmd.Cmd):

    prompt = 'ExpenseTracker> '
    intro = "Welcome to GitHub User Tracker! Type help to list commands."

    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()

    def do_add(self, arg):

        parser = argparse.ArgumentParser(prog="add")
        parser.add_argument("--description", type=str, required=True, help="Description of the expense")
        parser.add_argument("--amount", type=int, required=True, help="Amount of the expense")

        try:
            args = parser.parse_args(shlex.split(arg))
        except SystemExit:
            return

        description, amount = args.description, args.amount



        assert amount > 0, f"Amount {amount} must be greater than zero!"
        assert len(description) > 0, "There needs to be a description!"

        data = self.read_data()
        if not data:
            data = {"expense-counter": 0, "expenses": []}

        current_id = data["expense-counter"]+1

        new_expense = {
            "id": current_id,
            "description": description,
            "amount": amount,
            "Month": datetime.now().strftime("%m"),
            "createdAt": datetime.now().strftime("%Y-%m-%d"),
            "updatedAt": datetime.now().strftime("%Y-%m-%d")
        }

        data["expenses"].append(new_expense)
        data["expense-counter"] += 1

        print(data)
        self.write_data(data)

        print(f"Expenses added successfully:  {new_expense['id']}")





    def do_update(self, arg):
        parser = argparse.ArgumentParser(prog="update")
        parser.add_argument("--id", type=int, required=True, help="Id of the expense")
        parser.add_argument("--description", type=str, required=True, help="Description of the expense")
        parser.add_argument("--amount", type=int, required=True, help="Amount of the expense")

        try:
            args = parser.parse_args(shlex.split(arg))
        except SystemExit:
            return

        id = args.id
        description = args.description
        amount = args.amount

        data = self.read_data()
        expense_found = False

        for expense in data["expenses"]:
            if expense["id"] == id:
                expense_found = True
                expense["amount"] = amount
                expense["updatedAt"] = datetime.now().strftime("%Y-%m-%d")
                expense["description"] = description
                break

        if expense_found:
            print(f"Expense updated successfully {id}")
        else:
            print(f"Task {id} does not exist")

        self.write_data(data)

    def do_delete(self, arg):
        parser = argparse.ArgumentParser(prog="delete")
        parser.add_argument("--id", type=int, required=True, help="Id of the expense")

        try:
            args = parser.parse_args(shlex.split(arg))
        except SystemExit:
            return

        id = args.id

        data = self.read_data()

        expense_found = False

        for expense in data["expenses"]:
            if expense["id"] == id:
                expense_found = True
                data["expenses"].remove(expense)
                break

        if expense_found:
            print(f"Task deleted successfully: {id}")
        else:
            print(f"Task {id} does not exist")

        self.write_data(data)


    def do_list(self, arg=None):
        data = self.read_data()

        print("# ID\tDate\t\t\tDescription\t\tAmount")
        for expense in data["expenses"]:
            print(f"# {expense['id']}\t\t{expense['updatedAt']}\t\t{expense['description']}\t\t${expense['amount']}") # Works, but longer description shifts it

    # Without month, full summary, with month, only given summary
    def do_summary(self, arg):
        parser = argparse.ArgumentParser(prog="summary")
        parser.add_argument("--month", type=int, required=False, help="Month of the expenses")
        try:
            args = parser.parse_args(shlex.split(arg))
        except SystemExit:
            return

        month = args.month

        data = self.read_data()


        total_expenses = 0
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        if month is None:
            for expense in data["expenses"]:
                total_expenses += expense["amount"]
            print(f"Total expenses: {total_expenses}€")
        else:
            for expense in data["expenses"]:
                expense_month = int(re.search(r"-(\d{2})-", expense["createdAt"]).group(1))
                if expense_month == month:
                    total_expenses += expense["amount"]
            print(f"Total expenses in {months[month-1]}: {total_expenses}€")




    def do_quit(self, arg):
        return True

    def do_exit(self, arg):
        return True

    def postcmd(self, stop, line):
        self.refresh_json_numbers()
        return stop

    def refresh_json_numbers(self):
        data = self.read_data()

        if "expenses" not in data or not data["expenses"]:
            return

        for index, expense in enumerate(data["expenses"], start=1):
            # print(f"{index}. {expense['description']}")
            expense["id"] = index


        data["expense-counter"] = len(data["expenses"])

        self.write_data(data)


    def read_data(self):
        try:
            with open("expenses.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print("File does not exist")
            return {}
        return data

    def write_data(self, data):
        with open("expenses.json", "w") as f:
            json.dump(data, f, indent=4, default=str)


if __name__ == '__main__':
    ExpenseTracker().cmdloop()