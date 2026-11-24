"""
STUDENT FINANCE GOVERNANCE
Web interface for the existing Python mini-project.
Uses the same JSON structure as main.py:
{"students": [...], "payments": [...]}
Run with: python app.py
"""

import json
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import Flask, request, redirect, url_for, session, flash, render_template_string

BASE_DIR = Path(__file__).resolve().parent
# Keep using the repository's existing root JSON file if it exists.
ROOT_DATA = BASE_DIR / "finance_records.json"
DATA_DIR_FILE = BASE_DIR / "data" / "finance_records.json"
DATA_FILE = ROOT_DATA if ROOT_DATA.exists() else DATA_DIR_FILE

DEFAULT_ADMIN = {"username": "admin", "password": "1234"}
app = Flask(__name__)
app.secret_key = "student-finance-governance-local-demo-key"

def load_data():
    if not DATA_FILE.exists():
        return {"students": [], "payments": []}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("students", [])
        data.setdefault("payments", [])
        for s in data["students"]:
            s.setdefault("college_fee", 0.0)
            s.setdefault("hostel_fee", 0.0)
            s.setdefault("mess_fee", 0.0)
            s.setdefault("other_expense", 0.0)
            s.setdefault("paid_amount", 0.0)
        return data
    except (json.JSONDecodeError, OSError):
        return {"students": [], "payments": []}

def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def find_student(data, roll):
    roll = str(roll).strip().casefold()
    return next((s for s in data["students"]
                 if str(s.get("roll_number", "")).casefold() == roll), None)

def total_fee(s):
    return round(float(s.get("college_fee", 0)) +
                 float(s.get("hostel_fee", 0)) +
                 float(s.get("mess_fee", 0)) +
                 float(s.get("other_expense", 0)), 2)

def paid(s):
    return round(float(s.get("paid_amount", 0)), 2)

def due(s):
    return max(0.0, round(total_fee(s) - paid(s), 2))

def status(s):
    return "Paid" if total_fee(s) > 0 and due(s) == 0 else "Pending"

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

BASE_HTML = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Student Finance Governance</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#f3f6fb;color:#172033}
header{background:#142d4e;color:white;padding:17px 20px;font-size:20px;font-weight:bold}
nav{background:#fff;padding:12px 16px;display:flex;gap:9px;flex-wrap:wrap;box-shadow:0 2px 8px #0001}
nav a{color:#174a80;text-decoration:none;padding:8px 10px;border-radius:7px;background:#edf4fc;font-size:14px}
main{max-width:1000px;margin:22px auto;padding:0 14px}.card{background:white;padding:19px;border-radius:12px;margin-bottom:16px;box-shadow:0 3px 14px #142d4e12}
h2{margin-top:0;color:#173c67}label{display:block;font-weight:bold;margin:12px 0 5px}
input,select{width:100%;padding:11px;border:1px solid #ccd5e1;border-radius:7px;font-size:16px}
button,.btn{display:inline-block;background:#1769aa;color:white;border:0;border-radius:7px;padding:11px 16px;margin-top:14px;text-decoration:none;font-size:15px;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.stat{background:#eaf3fc;border-radius:10px;padding:16px}.stat small{color:#53677e}.stat strong{display:block;font-size:23px;margin-top:7px}
table{width:100%;border-collapse:collapse;display:block;overflow-x:auto}th,td{text-align:left;padding:10px;border-bottom:1px solid #e5eaf0;white-space:nowrap}
.msg{background:#e8f6ed;color:#176238;padding:10px;border-radius:7px;margin-bottom:12px}
.muted{color:#637187;font-size:14px}.danger{background:#a83232}
@media(min-width:700px){.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
</style></head><body>
<header>STUDENT FINANCE GOVERNANCE</header>
{% if session.get('logged_in') %}
<nav>
<a href="{{url_for('dashboard')}}">Dashboard</a>
<a href="{{url_for('students')}}">Students</a>
<a href="{{url_for('add_student_page')}}">Add Student</a>
<a href="{{url_for('fees_page')}}">Fee Management</a>
<a href="{{url_for('payment_page')}}">Payment Tracking</a>
<a href="{{url_for('expense_page')}}">Other Expenses</a>
<a href="{{url_for('reports')}}">Reports</a>
<a href="{{url_for('logout')}}">Logout</a>
</nav>{% endif %}
<main>
{% with messages=get_flashed_messages() %}{% for m in messages %}<div class="msg">{{m}}</div>{% endfor %}{% endwith %}
{{content|safe}}
</main></body></html>
"""

def page(content, **context):
    inner = render_template_string(content, **context)
    return render_template_string(BASE_HTML, content=inner)

@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("dashboard") if session.get("logged_in") else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (request.form.get("username", "").strip() == DEFAULT_ADMIN["username"]
            and request.form.get("password", "").strip() == DEFAULT_ADMIN["password"]):
            session["logged_in"] = True
            flash("Login successful.")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.")
    return page("""
    <div class="card" style="max-width:430px;margin:45px auto">
    <h2>Admin Login</h2><p class="muted">Student Finance Governance</p>
    <form method="post"><label>Username</label><input name="username" required>
    <label>Password</label><input name="password" type="password" required>
    <button type="submit">Login</button></form>
    <p class="muted">Demo login: admin / 1234</p></div>""")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    d = load_data()
    students = d["students"]
    total = sum(total_fee(s) for s in students)
    total_paid = sum(paid(s) for s in students)
    total_due = sum(due(s) for s in students)
    return page("""
    <h2>Dashboard</h2><div class="grid">
    <div class="stat"><small>Total Students</small><strong>{{n}}</strong></div>
    <div class="stat"><small>Total Fees</small><strong>₹{{"%.2f"|format(total)}}</strong></div>
    <div class="stat"><small>Total Paid</small><strong>₹{{"%.2f"|format(paid_total)}}</strong></div>
    <div class="stat"><small>Total Due</small><strong>₹{{"%.2f"|format(due_total)}}</strong></div>
    </div><div class="card"><h2>Project Modules</h2>
    Student Details Management · Fee Management · Payment Tracking · Other Expenses · Report Generation
    </div>""", n=len(students), total=total, paid_total=total_paid, due_total=total_due)

@app.route("/students")
@login_required
def students():
    d = load_data()
    return page("""
    <div class="card"><h2>Student Details</h2><a class="btn" href="{{url_for('add_student_page')}}">Add Student</a>
    <table><tr><th>Name</th><th>Roll Number</th><th>Branch</th><th>Total Fee</th><th>Paid</th><th>Due</th></tr>
    {% for s in students %}<tr><td>{{s.name}}</td><td>{{s.roll_number}}</td><td>{{s.branch}}</td>
    <td>₹{{"%.2f"|format(total_fee(s))}}</td><td>₹{{"%.2f"|format(paid(s))}}</td><td>₹{{"%.2f"|format(due(s))}}</td></tr>{% else %}
    <tr><td colspan="6">No student records found.</td></tr>{% endfor %}</table></div>
    """, students=d["students"], total_fee=total_fee, paid=paid, due=due)

@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student_page():
    if request.method == "POST":
        d = load_data()
        name = request.form.get("name", "").strip()
        roll = request.form.get("roll_number", "").strip()
        branch = request.form.get("branch", "").strip().upper()
        if not name or not roll or not branch:
            flash("Please fill all fields.")
        elif find_student(d, roll):
            flash("This roll number already exists.")
        else:
            d["students"].append({"name":name,"roll_number":roll,"branch":branch,
                "college_fee":0.0,"hostel_fee":0.0,"mess_fee":0.0,
                "other_expense":0.0,"paid_amount":0.0})
            save_data(d); flash("Student added successfully."); return redirect(url_for("students"))
    return page("""<div class="card"><h2>Add Student Details</h2><form method="post">
    <label>Student Name</label><input name="name" required>
    <label>Roll Number</label><input name="roll_number" required>
    <label>Branch</label><input name="branch" required>
    <button>Add Student</button></form></div>""")

@app.route("/fees", methods=["GET", "POST"])
@login_required
def fees_page():
    d = load_data()
    if request.method == "POST":
        s = find_student(d, request.form.get("roll_number", ""))
        if not s: flash("Student not found.")
        else:
            try:
                vals = [float(request.form.get(k, "0")) for k in ("college_fee","hostel_fee","mess_fee")]
                if any(v < 0 for v in vals): raise ValueError()
                s["college_fee"],s["hostel_fee"],s["mess_fee"] = vals
                save_data(d); flash("Fee details updated successfully.")
            except ValueError: flash("Enter valid non-negative amounts.")
        return redirect(url_for("fees_page"))
    return page("""<div class="card"><h2>Fee Management</h2><form method="post">
    <label>Student Roll Number</label><input name="roll_number" required>
    <label>College Fee</label><input name="college_fee" type="number" min="0" step="0.01" required>
    <label>Hostel Fee</label><input name="hostel_fee" type="number" min="0" step="0.01" required>
    <label>Mess Fee</label><input name="mess_fee" type="number" min="0" step="0.01" required>
    <button>Save Fees</button></form></div>""")

@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment_page():
    d = load_data()
    if request.method == "POST":
        s = find_student(d, request.form.get("roll_number", ""))
        try:
            amount = float(request.form.get("amount", "0"))
            mode = request.form.get("mode", "Cash")
            if not s: flash("Student not found.")
            elif amount <= 0: flash("Enter a payment greater than zero.")
            elif amount > due(s): flash("Payment cannot be greater than pending amount.")
            else:
                s["paid_amount"] = round(paid(s) + amount, 2)
                d["payments"].append({"roll_number":s["roll_number"],"student_name":s["name"],
                    "amount":amount,"mode":mode,"date":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                save_data(d); flash("Payment recorded successfully.")
        except ValueError: flash("Enter a valid payment amount.")
        return redirect(url_for("payment_page"))
    return page("""<div class="card"><h2>Payment Tracking</h2><form method="post">
    <label>Student Roll Number</label><input name="roll_number" required>
    <label>Paid Amount</label><input name="amount" type="number" min="0.01" step="0.01" required>
    <label>Payment Mode</label><select name="mode"><option>Cash</option><option>UPI</option><option>Bank</option></select>
    <button>Record Payment</button></form></div>""")

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expense_page():
    d = load_data()
    if request.method == "POST":
        s = find_student(d, request.form.get("roll_number", ""))
        try:
            amount = float(request.form.get("amount", "0"))
            if not s: flash("Student not found.")
            elif amount <= 0: flash("Enter an expense greater than zero.")
            else:
                s["other_expense"] = round(float(s.get("other_expense",0)) + amount, 2)
                save_data(d); flash("Other expense added successfully.")
        except ValueError: flash("Enter a valid amount.")
        return redirect(url_for("expense_page"))
    return page("""<div class="card"><h2>Other Expenses</h2><form method="post">
    <label>Student Roll Number</label><input name="roll_number" required>
    <label>Expense Amount</label><input name="amount" type="number" min="0.01" step="0.01" required>
    <button>Add Expense</button></form></div>""")

@app.route("/reports")
@login_required
def reports():
    d = load_data()
    students = d["students"]
    total = sum(total_fee(s) for s in students)
    total_paid = sum(paid(s) for s in students)
    total_due = sum(due(s) for s in students)
    return page("""
    <div class="card"><h2>Overall Financial Report</h2>
    <p>Total Students: <b>{{students|length}}</b></p>
    <p>Total Fee: <b>₹{{"%.2f"|format(total)}}</b></p>
    <p>Total Paid: <b>₹{{"%.2f"|format(total_paid)}}</b></p>
    <p>Total Due: <b>₹{{"%.2f"|format(total_due)}}</b></p></div>
    <div class="card"><h2>Student-wise Financial Report</h2>
    <table><tr><th>Name</th><th>Roll</th><th>Total Fee</th><th>Paid</th><th>Due</th><th>Status</th></tr>
    {% for s in students %}<tr><td>{{s.name}}</td><td>{{s.roll_number}}</td>
    <td>₹{{"%.2f"|format(total_fee(s))}}</td><td>₹{{"%.2f"|format(paid(s))}}</td>
    <td>₹{{"%.2f"|format(due(s))}}</td><td>{{status(s)}}</td></tr>{% endfor %}</table></div>
    """, students=students, total=total, total_paid=total_paid, total_due=total_due,
       total_fee=total_fee, paid=paid, due=due, status=status)

if __name__ == "__main__":
    print("Open the local address shown below in your mobile browser.")
    app.run(host="0.0.0.0", port=5000, debug=False)
