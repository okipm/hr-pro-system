import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from io import BytesIO

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(page_title="HR Management System", layout="wide")

# =====================================================
# GOOGLE SHEETS CONNECTION
# =====================================================

@st.cache_resource
def init_connection():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(credentials)
    sheet_id = st.secrets["google_sheet"]["sheet_id"]
    spreadsheet = client.open_by_key(sheet_id)

    return (
        spreadsheet.worksheet("employees"),
        spreadsheet.worksheet("attendance"),
        spreadsheet.worksheet("users")
    )

employees_ws, attendance_ws, users_ws = init_connection()

# =====================================================
# UTILITIES
# =====================================================

def load_sheet(ws):
    return pd.DataFrame(ws.get_all_records())

def safe_float(val):
    try:
        if val is None:
            return 0.0
        if isinstance(val, str):
            val = val.replace(",", "").replace("Rp", "").strip()
            if val == "":
                return 0.0
        return float(val)
    except:
        return 0.0

# =====================================================
# LOGIN
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 HR Management Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_sheet(users_ws)
        user = users[
            (users["username"] == username) &
            (users["password"] == password)
        ]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# =====================================================
# NAVIGATION
# =====================================================

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Employees", "Attendance", "Payroll"]
)

# =====================================================
# DASHBOARD
# =====================================================

if menu == "Dashboard":
    st.title("📊 Dashboard")

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Employees", len(df_emp))
    col2.metric("Departments", df_emp["department"].nunique() if not df_emp.empty else 0)
    col3.metric(
        "Present Today",
        len(df_att[df_att["date"] == str(date.today())]) if not df_att.empty else 0
    )

# =====================================================
# EMPLOYEES
# =====================================================

elif menu == "Employees":
    st.title("👥 Employee Management")

    df = load_sheet(employees_ws)

    st.subheader("Employee List")
    st.dataframe(df, use_container_width=True)

    st.subheader("Add Employee")

    emp_id = st.text_input("Employee ID")
    name = st.text_input("Full Name")
    dept = st.text_input("Department")
    position = st.text_input("Position")

    basic = st.number_input("Daily Basic", min_value=0.0)
    transport = st.number_input("Daily Transport", min_value=0.0)
    meal = st.number_input("Meal Allowance / Day", min_value=0.0)
    allowance = st.number_input("Fixed Monthly Allowance", min_value=0.0)

    if st.button("Save Employee"):
        employees_ws.append_row([
            emp_id,
            name,
            "",
            "",
            "",
            "",
            "",
            dept,
            position,
            "",
            "",
            "",
            "",
            basic,
            transport,
            allowance,
            meal,
            "Active"
        ])
        st.success("Employee Added")
        st.rerun()

# =====================================================
# ATTENDANCE
# =====================================================

elif menu == "Attendance":
    st.title("📅 Attendance")

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    if df_emp.empty:
        st.warning("No employees found")
        st.stop()

    selected_emp = st.selectbox(
        "Select Employee",
        df_emp["employee_id"].astype(str) + " - " + df_emp["full_name"]
    )

    emp_id = selected_emp.split(" - ")[0]
    status = st.selectbox("Status", ["Present", "Absent"])

    if st.button("Save Attendance"):
        attendance_ws.append_row([
            str(date.today()),
            emp_id,
            status
        ])
        st.success("Attendance Saved")
        st.rerun()

    st.subheader("Attendance Records")
    st.dataframe(df_att, use_container_width=True)

# =====================================================
# PAYROLL
# =====================================================

elif menu == "Payroll":
    st.title("💰 Payroll")

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    if df_emp.empty or df_att.empty:
        st.warning("Employee or attendance data missing")
        st.stop()

    month_list = sorted(df_att["date"].astype(str).str[:7].unique(), reverse=True)
    selected_month = st.selectbox("Select Month", month_list)

    df_month = df_att[df_att["date"].astype(str).str.startswith(selected_month)]

    payroll = []

    for _, emp in df_emp.iterrows():
        present_days = len(
            df_month[
                (df_month["employee_id"].astype(str) == str(emp["employee_id"])) &
                (df_month["status"] == "Present")
            ]
        )

        total_daily = (
            safe_float(emp.get("daily_rate_basic")) +
            safe_float(emp.get("daily_rate_transport")) +
            safe_float(emp.get("meal_allowance_daily"))
        )

        salary_from_attendance = present_days * total_daily

        total_salary = (
            salary_from_attendance +
            safe_float(emp.get("allowance_monthly"))
        )

        payroll.append({
            "Employee ID": emp["employee_id"],
            "Name": emp["full_name"],
            "Present Days": present_days,
            "Total Daily Rate": total_daily,
            "Salary From Attendance": salary_from_attendance,
            "Fixed Allowance": safe_float(emp.get("allowance_monthly")),
            "Total Salary": total_salary
        })

    payroll_df = pd.DataFrame(payroll)

    st.dataframe(payroll_df, use_container_width=True)

    st.metric("Total Payroll", f"{payroll_df['Total Salary'].sum():,.2f}")

    # Export
    output = BytesIO()
    payroll_df.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        "Download Payroll Excel",
        output,
        file_name=f"Payroll_{selected_month}.xlsx"
    )
