import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from io import BytesIO

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="HR PRO SYSTEM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# GOOGLE CONNECTION
# =====================================================

@st.cache_resource
def init_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    return gspread.authorize(credentials)

@st.cache_resource
def get_worksheets():
    client = init_gspread_client()
    sheet_id = st.secrets["google_sheet"]["sheet_id"]
    spreadsheet = client.open_by_key(sheet_id)

    return (
        spreadsheet.worksheet("employees"),
        spreadsheet.worksheet("attendance"),
        spreadsheet.worksheet("users"),
    )

employees_ws, attendance_ws, users_ws = get_worksheets()

# =====================================================
# UTILITY
# =====================================================

def load_sheet(ws):
    return pd.DataFrame(ws.get_all_records())

def append_row(ws, data):
    ws.append_row(data)

# =====================================================
# LOGIN
# =====================================================

def login():
    st.title("🔐 HR PRO LOGIN")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        users = load_sheet(users_ws)

        if users.empty:
            st.error("No users found in Google Sheet.")
            return

        users["username"] = users["username"].astype(str).str.strip()
        users["password"] = users["password"].astype(str).str.strip()

        user = users[
            (users["username"] == username.strip()) &
            (users["password"] == password.strip())
        ]

        if not user.empty:
            st.session_state["logged_in"] = True
            st.session_state["role"] = user.iloc[0]["role"]
            st.session_state["username"] = username
            st.session_state["employee_id"] = user.iloc[0].get("employee_id", "")
            st.rerun()
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# =====================================================
# NAVIGATION
# =====================================================

role = st.session_state["role"]

if role == "Admin":
    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Dashboard",
            "Employee Directory",
            "Add New Employee",
            "Attendance",
            "Payroll"
        ]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

else:
    menu = st.sidebar.selectbox(
        "Menu",
        [
            "My Attendance",
            "My Payroll"
        ]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =====================================================
# DASHBOARD
# =====================================================

if menu == "Dashboard":
    st.title("📊 Dashboard")

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Employees", len(df_emp))
    col2.metric("Active Employees", len(df_emp[df_emp["status"] == "Active"]))
    col3.metric("Total Attendance Records", len(df_att))

# =====================================================
# EMPLOYEE DIRECTORY
# =====================================================

elif menu == "Employee Directory":
    st.title("👥 Employee Directory")

    df = load_sheet(employees_ws)

    if df.empty:
        st.warning("No employees found.")
        st.stop()

    st.dataframe(df, use_container_width=True)

# =====================================================
# ADD NEW EMPLOYEE
# =====================================================

elif menu == "Add New Employee":
    st.title("➕ Add New Employee")

    df_existing = load_sheet(employees_ws)

    col1, col2 = st.columns(2)

    with col1:
        employee_id = st.text_input("Employee ID")
        full_name = st.text_input("Full Name")
        department = st.text_input("Department")
        position = st.text_input("Position")

    with col2:
        join_date = st.date_input("Join Date")
        daily_rate_basic = st.number_input("Daily Rate Basic", min_value=0.0)
        daily_rate_transport = st.number_input("Daily Rate Transport", min_value=0.0)
        allowance_monthly = st.number_input("Allowance Monthly", min_value=0.0)

    if st.button("💾 Save Employee", use_container_width=True):

        if employee_id in df_existing["employee_id"].astype(str).tolist():
            st.error("❌ Employee ID already exists!")
            st.stop()

        append_row(employees_ws, [
            employee_id,
            full_name,
            "",
            "",
            "",
            "",
            str(join_date),
            department,
            position,
            "",
            "",
            "",
            "",
            daily_rate_basic,
            daily_rate_transport,
            allowance_monthly,
            "Active"
        ])

        st.success("Employee Added Successfully!")
        st.rerun()

# =====================================================
# ATTENDANCE (ADMIN)
# =====================================================

elif menu == "Attendance":
    st.title("📅 Attendance")

    df_att = load_sheet(attendance_ws)

    if df_att.empty:
        st.warning("No attendance data.")
        st.stop()

    df_att["date"] = df_att["date"].astype(str)

    dates = sorted(df_att["date"].unique(), reverse=True)
    selected_date = st.selectbox("Select Date", dates)

    st.dataframe(
        df_att[df_att["date"] == selected_date],
        use_container_width=True
    )

# =====================================================
# PAYROLL (ADMIN)
# =====================================================

elif menu == "Payroll":
    st.title("💰 Payroll")

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    if df_att.empty:
        st.warning("No attendance data.")
        st.stop()

    df_att["date"] = df_att["date"].astype(str)

    month_list = sorted(df_att["date"].str[:7].unique(), reverse=True)
    selected_month = st.selectbox("Select Month", month_list)

    df_month = df_att[df_att["date"].str.startswith(selected_month)]

    payroll = []

    for _, emp in df_emp.iterrows():
        present_days = len(
            df_month[
                (df_month["employee_id"] == emp["employee_id"]) &
                (df_month["status"] == "Present")
            ]
        )

        salary = present_days * (
            float(emp.get("daily_rate_basic", 0)) +
            float(emp.get("daily_rate_transport", 0))
        ) + float(emp.get("allowance_monthly", 0))

        payroll.append([
            emp["employee_id"],
            emp["full_name"],
            present_days,
            salary
        ])

    payroll_df = pd.DataFrame(
        payroll,
        columns=["Employee ID", "Name", "Present Days", "Total Salary"]
    )

    st.dataframe(payroll_df, use_container_width=True)

# =====================================================
# STAFF - MY ATTENDANCE
# =====================================================

elif menu == "My Attendance":
    st.title("📅 My Attendance")

    df_att = load_sheet(attendance_ws)
    df_att["date"] = df_att["date"].astype(str)

    my_id = st.session_state["employee_id"]

    my_att = df_att[df_att["employee_id"] == my_id]

    st.dataframe(
        my_att.sort_values("date", ascending=False),
        use_container_width=True
    )

# =====================================================
# STAFF - MY PAYROLL
# =====================================================

elif menu == "My Payroll":
    st.title("💰 My Payroll")

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    df_att["date"] = df_att["date"].astype(str)

    my_id = st.session_state["employee_id"]

    month_list = sorted(df_att["date"].str[:7].unique(), reverse=True)
    selected_month = st.selectbox("Select Month", month_list)

    df_month = df_att[
        (df_att["date"].str.startswith(selected_month)) &
        (df_att["employee_id"] == my_id)
    ]

    present_days = len(df_month[df_month["status"] == "Present"])

    emp = df_emp[df_emp["employee_id"] == my_id].iloc[0]

    total_salary = present_days * (
        float(emp.get("daily_rate_basic", 0)) +
        float(emp.get("daily_rate_transport", 0))
    ) + float(emp.get("allowance_monthly", 0))

    st.metric("Present Days", present_days)
    st.metric("Total Salary", f"{total_salary:,.2f}")
