"""
STUDENT FINANCE GOVERNANCE
Mini Project - Python 3.10
A menu-based application matching the modules described in the project report.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).parent / "data" / "finance_records.json"
DEFAULT_ADMIN = {"username": "admin", "password": "1234"}

def load_data():
    if not DATA_FILE.exists():
        return {"students": [], "payments": []}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        data.setdefault("students", [])
        data.setdefault("payments", [])
        return data
    except (json.JSONDecodeError, OSError):
        print("Warning: Data file could not be read. Starting with empty records.")
        return {"students": [], "payments": []}

def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def read_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")

def read_amount(prompt, allow_zero=True):
    while True:
        try:
            value = float(input(prompt).strip())
            if value < 0 or (not allow_zero and value == 0):
                print("Enter a valid positive amount.")
                continue
            return round(value, 2)
        except ValueError:
            print("Please enter a numeric amount.")

def find_student(data, name=None, roll=None):
    for student in data["students"]:
        if roll is not None and student["roll_number"].casefold() == roll.casefold():
            return student
        if name is not None and student["name"].casefold() == name.casefold():
            return student
    return None

def login_user():
    print("\n========== USER LOGIN ==========")
    username = input("Enter Username: ").strip()
    password = input("Enter Password: ").strip()
    if username == DEFAULT_ADMIN["username"] and password == DEFAULT_ADMIN["password"]:
        print("Login Successful...")
        return True
    print("Invalid Username or Password")
    return False

def logout_user():
    print("\nYou have been logged out.")

def add_student(data):
    print("\n====== ADD STUDENT DETAILS ======")
    name = read_text("Enter Student Name: ")
    while not all(ch.isalpha() or ch.isspace() or ch in ".-' " for ch in name):
        print("Student name should contain letters only.")
        name = read_text("Enter Student Name: ")
    roll = read_text("Enter Roll Number: ")
    if find_student(data, roll=roll):
        print("This roll number already exists.")
        return
    branch = read_text("Enter Branch: ").upper()
    student = {
        "name": name,
        "roll_number": roll,
        "branch": branch,
        "college_fee": 0.0,
        "hostel_fee": 0.0,
        "mess_fee": 0.0,
        "other_expense": 0.0,
        "paid_amount": 0.0
    }
    data["students"].append(student)
    save_data(data)
    print("Student Added Successfully")

def view_students(data):
    print("\n====== STUDENT DETAILS ======")
    if not data["students"]:
        print("No student records found.")
        return
    print(f"{'Name':25} {'Roll Number':15} {'Branch':12}")
    print("-" * 55)
    for s in data["students"]:
        print(f"{s['name'][:25]:25} {s['roll_number'][:15]:15} {s['branch'][:12]:12}")

def fee_management(data):
    print("\n====== FEE MANAGEMENT ======")
    roll = read_text("Enter Student Roll Number: ")
    student = find_student(data, roll=roll)
    if not student:
        print("Student not found. Add student details first.")
        return
    print(f"Student: {student['name']} ({student['roll_number']})")
    student["college_fee"] = read_amount("Enter College Fee: ")
    student["hostel_fee"] = read_amount("Enter Hostel Fee: ")
    student["mess_fee"] = read_amount("Enter Mess Fee: ")
    save_data(data)
    print("Fee Details Updated Successfully")
    print(f"Total Fee: Rs. {calculate_total_fee(student):.2f}")

def calculate_total_fee(student):
    return round(
        student["college_fee"] + student["hostel_fee"] +
        student["mess_fee"] + student["other_expense"], 2
    )

def update_fee_status(student):
    due = max(0.0, calculate_total_fee(student) - student["paid_amount"])
    if due == 0 and calculate_total_fee(student) > 0:
        return "Paid"
    return "Pending"

def record_payment(data):
    print("\n====== PAYMENT TRACKING ======")
    roll = read_text("Enter Student Roll Number: ")
    student = find_student(data, roll=roll)
    if not student:
        print("Student not found.")
        return
    total = calculate_total_fee(student)
    due = max(0.0, total - student["paid_amount"])
    print(f"Student Name : {student['name']}")
    print(f"Total Fee    : Rs. {total:.2f}")
    print(f"Paid Amount  : Rs. {student['paid_amount']:.2f}")
    print(f"Due Amount   : Rs. {due:.2f}")
    if due <= 0:
        print("No pending amount.")
        return
    amount = read_amount("Enter Paid Amount: ", allow_zero=False)
    if amount > due:
        print("Payment cannot be greater than the pending amount.")
        return
    mode = read_text("Enter Payment Mode (Cash/UPI/Bank): ")
    payment = {
        "roll_number": student["roll_number"],
        "student_name": student["name"],
        "amount": amount,
        "mode": mode,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    student["paid_amount"] = round(student["paid_amount"] + amount, 2)
    data["payments"].append(payment)
    save_data(data)
    print("Payment Recorded Successfully")
    print(f"Updated Due Amount: Rs. {max(0, total - student['paid_amount']):.2f}")
    print(f"Payment Status: {update_fee_status(student)}")

def add_expense(data):
    print("\n====== OTHER EXPENSES ======")
    roll = read_text("Enter Student Roll Number: ")
    student = find_student(data, roll=roll)
    if not student:
        print("Student not found.")
        return
    amount = read_amount("Enter Other Expense Amount: ", allow_zero=False)
    student["other_expense"] = round(student["other_expense"] + amount, 2)
    save_data(data)
    print("Other Expense Added Successfully")
    print(f"Total Other Expenses: Rs. {student['other_expense']:.2f}")

def track_payment(data):
    print("\n====== PAYMENT HISTORY ======")
    roll = read_text("Enter Student Roll Number: ")
    student = find_student(data, roll=roll)
    if not student:
        print("Student not found.")
        return
    records = [p for p in data["payments"] if p["roll_number"].casefold() == roll.casefold()]
    if not records:
        print("No payment records found.")
    else:
        for p in records:
            print(f"{p['date']} | Rs. {p['amount']:.2f} | {p['mode']}")
    print(f"Current Status: {update_fee_status(student)}")

def student_report(data):
    print("\n====== STUDENT FINANCIAL REPORT ======")
    roll = read_text("Enter Student Roll Number: ")
    student = find_student(data, roll=roll)
    if not student:
        print("Student not found.")
        return
    total = calculate_total_fee(student)
    paid = student["paid_amount"]
    due = max(0.0, total - paid)
    status = update_fee_status(student)
    print("-" * 43)
    print("       STUDENT FINANCIAL REPORT")
    print("-" * 43)
    print(f"Name          : {student['name']}")
    print(f"Roll Number   : {student['roll_number']}")
    print(f"Branch        : {student['branch']}")
    print(f"College Fee   : Rs. {student['college_fee']:.2f}")
    print(f"Hostel Fee    : Rs. {student['hostel_fee']:.2f}")
    print(f"Mess Fee      : Rs. {student['mess_fee']:.2f}")
    print(f"Other Expense : Rs. {student['other_expense']:.2f}")
    print(f"Total Fee     : Rs. {total:.2f}")
    print(f"Paid Amount   : Rs. {paid:.2f}")
    print(f"Due Amount    : Rs. {due:.2f}")
    print(f"Payment Status: {status}")
    print("-" * 43)

def generate_report(data):
    print("\n====== FINANCIAL SUMMARY REPORT ======")
    if not data["students"]:
        print("No student records available.")
        return
    total_fee = sum(calculate_total_fee(s) for s in data["students"])
    total_paid = sum(s["paid_amount"] for s in data["students"])
    total_due = max(0.0, total_fee - total_paid)
    print(f"Total Students : {len(data['students'])}")
    print(f"Total Fee      : Rs. {total_fee:.2f}")
    print(f"Total Paid     : Rs. {total_paid:.2f}")
    print(f"Total Due      : Rs. {total_due:.2f}")
    print("\nStudent-wise Status")
    for s in data["students"]:
        due = max(0.0, calculate_total_fee(s) - s["paid_amount"])
        print(f"{s['name']} ({s['roll_number']}) - Paid: Rs. {s['paid_amount']:.2f}, Due: Rs. {due:.2f}, Status: {update_fee_status(s)}")

def main_menu(data):
    while True:
        print("\n====== STUDENT FINANCE GOVERNANCE MENU ======")
        print("1. Add Student Details")
        print("2. Fee Management")
        print("3. Payment Tracking")
        print("4. Other Expenses")
        print("5. Report Generation")
        print("6. View Student Details")
        print("7. Logout / Exit")
        choice = input("Enter Your Choice: ").strip()
        if choice == "1":
            add_student(data)
        elif choice == "2":
            fee_management(data)
        elif choice == "3":
            record_payment(data)
            # Show payment history and current status after recording.
        elif choice == "4":
            add_expense(data)
        elif choice == "5":
            print("\n1. Student Report\n2. Overall Report")
            sub = input("Enter Your Choice: ").strip()
            if sub == "1":
                student_report(data)
            elif sub == "2":
                generate_report(data)
            else:
                print("Invalid choice.")
        elif choice == "6":
            view_students(data)
        elif choice == "7":
            logout_user()
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    print("=" * 12 + " STUDENT FINANCE GOVERNANCE " + "=" * 12)
    while not login_user():
        retry = input("Try login again? (y/n): ").strip().lower()
        if retry != "y":
            print("Exiting system.")
            return
    data = load_data()
    main_menu(data)

if __name__ == "__main__":
    main()
