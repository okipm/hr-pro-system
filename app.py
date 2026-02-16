import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
from io import BytesIO

st.set_page_config(page_title="HR PRO SYSTEM", layout="wide")

# =============================
# GOOGLE CONNECTION
# =============================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)

client = gspread.authorize(creds)
sheet_id = st.secrets["google_sheet"]["sheet_id"]

employees_ws = client.open_by_key(sheet_id).worksheet("employees")
attendance_ws = client.open_by_key(sheet_id).worksheet("attendance")
users_ws = client.open_by_key(sheet_id).worksheet("users")

# =============================
# FUNCTIONS
# =============================

def load_sheet(ws):
    data = ws.get_all_records()
    return pd.DataFrame(data)

def append_row(ws, data):
    ws.append_row(data)

# =============================
# LOGIN SYSTEM
# =============================

def login():
    st.title("🔐 HR PRO LOGIN")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_sheet(users_ws)

        users["username"] = users["username"].astype(str).str.strip()
        users["password"] = users["password"].astype(str).str.strip()

        username_input = str(username).strip()
        password_input = str(password).strip()

        user = users[
            (users["username"] == username_input) &
            (users["password"] == password_input)
        ]

        if not user.empty:
            st.session_state["logged_in"] = True
            st.session_state["role"] = user.iloc[0]["role"]
            st.session_state["username"] = username_input
            st.rerun()
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# =============================
# SIDEBAR
# =============================

st.sidebar.success(f"{st.session_state['username']} ({st.session_state['role']})")

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Employee Directory", "Attendance", "Payroll"]
)


# =============================
# DASHBOARD
# =============================

if menu == "Dashboard":
    df = load_sheet(employees_ws)
    st.metric("Total Employees", len(df))

# =============================
# EMPLOYEE DIRECTORY
# =============================

if menu == "Employee Directory":

    st.title("👥 Employee Directory")

    df = load_sheet(employees_ws)
    st.dataframe(df, use_container_width=True)

    if st.session_state["role"] in ["Admin", "HR"]:

        st.subheader("➕ Add New Employee")

        with st.form("employee_form"):

            employee_id = st.text_input("Employee ID")
            full_name = st.text_input("Full Name")
            place_of_birth = st.text_input("Place of Birth")

            date_of_birth = st.date_input(
                "Date of Birth",
                min_value=date(1950, 1, 1),
                max_value=date.today()
            )

            national_id_number = st.text_input("National ID Number")
            gender = st.selectbox("Gender", ["Male", "Female"])

            join_date = st.date_input(
                "Join Date",
                min_value=date(2000, 1, 1),
                max_value=date.today()
            )

            department = st.text_input("Department")
            position = st.text_input("Position")
            address = st.text_area("Address")
            bank_account_number = st.text_input("Bank Account Number")
            marital_status = st.selectbox("Marital Status", ["Single", "Married"])
            mothers_maiden_name = st.text_input("Mother's Maiden Name")

            daily_rate_basic = st.number_input("Daily Rate Basic", min_value=0)
            daily_rate_transport = st.number_input("Daily Rate Transportation", min_value=0)
            allowance_monthly = st.number_input("Allowance Monthly (Fixed)", min_value=0)

            status = "Active"

            submitted = st.form_submit_button("Save")

            if submitted:
                append_row(employees_ws, [
                    employee_id,
                    full_name,
                    place_of_birth,
                    str(date_of_birth),
                    national_id_number,
                    gender,
                    str(join_date),
                    department,
                    position,
                    address,
                    bank_account_number,
                    marital_status,
                    mothers_maiden_name,
                    daily_rate_basic,
                    daily_rate_transport,
                    allowance_monthly,
                    status
                ])
                st.success("Employee Added Successfully!")

# =============================
# ATTENDANCE
# =============================

if menu == "Attendance":
    df = load_sheet(attendance_ws)
    st.dataframe(df, use_container_width=True)


# =============================
# PAYROLL (ENTERPRISE VERSION)
# =============================

if menu == "Payroll":

    st.title("💰 Payroll")

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    payroll_log_ws = client.open_by_key(sheet_id).worksheet("payroll_log")
    df_log = load_sheet(payroll_log_ws)

    if df_att.empty:
        st.warning("No attendance data")
        st.stop()

    month_list = df_att["date"].str[:7].unique()
    selected_month = st.selectbox("Select Month", month_list)

    # Check if month already finalized
    if not df_log.empty and selected_month in df_log["month"].values:
        st.success("✅ Payroll already finalized for this month")
        locked = True
    else:
        locked = False

    df_month = df_att[df_att["date"].str.startswith(selected_month)]

    # Department Filter
    departments = ["All"] + sorted(df_emp["department"].unique())
    selected_dept = st.selectbox("Filter by Department", departments)

    if selected_dept != "All":
        df_emp = df_emp[df_emp["department"] == selected_dept]

    # Search Employee
    search = st.text_input("Search Employee (Name or ID)")

    if search:
        df_emp = df_emp[
            df_emp["full_name"].str.contains(search, case=False) |
            df_emp["employee_id"].astype(str).str.contains(search)
        ]

    payroll = []

    for _, emp in df_emp.iterrows():

        emp_id = emp["employee_id"]
        name = emp["full_name"]
        department = emp["department"]

        basic = float(emp["daily_rate_basic"])
        transport = float(emp["daily_rate_transport"])
        allowance = float(emp["allowance_monthly"])

        present_days = len(
            df_month[
                (df_month["employee_id"] == emp_id) &
                (df_month["status"] == "Present")
            ]
        )

        payroll.append([
            emp_id,
            name,
            department,
            present_days,
            basic,
            transport,
            allowance,
            0,
            0
        ])

    payroll_df = pd.DataFrame(
        payroll,
        columns=[
            "Employee ID",
            "Name",
            "Department",
            "Present Days",
            "Daily Basic",
            "Daily Transport",
            "Allowance",
            "Overtime",
            "Bonus"
        ]
    )

# Toggle Edit Mode
edit_mode = False

if not locked:
    edit_mode = st.toggle("✏️ Edit Overtime & Bonus")

if locked:
    st.success("✅ Payroll already finalized for this month")
    edited_df = payroll_df.copy()

elif edit_mode:
    edited_df = st.data_editor(
        payroll_df,
        use_container_width=True,
        num_rows="fixed"
    )
else:
    edited_df = payroll_df.copy()


    # Recalculate
    edited_df["Salary From Attendance"] = (
        edited_df["Present Days"] *
        (edited_df["Daily Basic"] + edited_df["Daily Transport"])
    )

    edited_df["Total Salary"] = (
        edited_df["Salary From Attendance"] +
        edited_df["Allowance"] +
        edited_df["Overtime"] +
        edited_df["Bonus"]
    )

    st.subheader("Payroll Summary")
    st.dataframe(edited_df, use_container_width=True)

    total_cost = edited_df["Total Salary"].sum()
    st.metric("Total Payroll Cost", total_cost)

    # Finalize Payroll
    if not locked:
        if st.button("✅ Finalize Payroll"):

            from datetime import datetime

            for _, row in edited_df.iterrows():
                payroll_log_ws.append_row([
                    selected_month,
                    row["Employee ID"],
                    row["Name"],
                    row["Department"],
                    row["Present Days"],
                    row["Daily Basic"],
                    row["Daily Transport"],
                    row["Allowance"],
                    row["Overtime"],
                    row["Bonus"],
                    row["Total Salary"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])

            st.success("Payroll Finalized & Saved!")
            st.rerun()

    # Export Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_df.to_excel(writer, index=False)

    st.download_button(
        "Download Payroll Excel",
        output.getvalue(),
        file_name=f"Payroll_{selected_month}.xlsx"
    )
