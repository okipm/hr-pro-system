import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
from io import BytesIO

st.set_page_config(page_title="HR PRO SYSTEM", layout="wide")

# =====================================================
# GOOGLE CONNECTION
# =====================================================

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

# =====================================================
# FUNCTIONS
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

    if st.button("Login"):
        users = load_sheet(users_ws)

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
            st.rerun()
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.success(f"{st.session_state['username']} ({st.session_state['role']})")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Employee Directory",
        "Employee Directory > Add New Employee",
        "Attendance",
        "Payroll"
    ]
)

# =====================================================
# DASHBOARD
# =====================================================

if menu == "Dashboard":
    df = load_sheet(employees_ws)
    st.metric("Total Employees", len(df))

# =====================================================
# EMPLOYEE DIRECTORY (VIEW + EDIT + DELETE)
# =====================================================

elif menu == "Employee Directory":

    st.title("👥 Employee Directory")
    df = load_sheet(employees_ws)

    if df.empty:
        st.info("No employees found.")
        st.stop()

    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("⚙ Manage Employee")

    selected_id = st.selectbox(
        "Select Employee",
        df["employee_id"].astype(str)
    )

    selected_emp = df[df["employee_id"].astype(str) == str(selected_id)].iloc[0]

    col1, col2 = st.columns(2)

    # ========== EDIT ==========
    with col1:
        if st.button("✏️ Edit Employee"):
            st.session_state["edit_mode"] = True

    if "edit_mode" not in st.session_state:
        st.session_state["edit_mode"] = False

    if st.session_state["edit_mode"]:

        with st.form("edit_employee_form"):

            full_name = st.text_input("Full Name", selected_emp["full_name"])
            department = st.text_input("Department", selected_emp["department"])
            position = st.text_input("Position", selected_emp["position"])
            bank_account = st.text_input(
                "Bank Account Number",
                str(selected_emp["bank_account_number"])
            )

            daily_rate_basic = st.number_input(
                "Daily Rate Basic",
                value=float(selected_emp["daily_rate_basic"])
            )

            daily_rate_transport = st.number_input(
                "Daily Rate Transport",
                value=float(selected_emp["daily_rate_transport"])
            )

            allowance_monthly = st.number_input(
                "Allowance Monthly",
                value=float(selected_emp["allowance_monthly"])
            )

            update = st.form_submit_button("💾 Update")

            if update:

                row_number = df.index[
                    df["employee_id"].astype(str) == str(selected_id)
                ][0] + 2

                updated_row = [
                    str(selected_id),
                    str(full_name),
                    str(selected_emp["place_of_birth"]),
                    str(selected_emp["date_of_birth"]),
                    str(selected_emp["national_id_number"]),
                    str(selected_emp["gender"]),
                    str(selected_emp["join_date"]),
                    str(department),
                    str(position),
                    str(selected_emp["address"]),
                    str(bank_account),
                    str(selected_emp["marital_status"]),
                    str(selected_emp["mothers_maiden_name"]),
                    float(daily_rate_basic),
                    float(daily_rate_transport),
                    float(allowance_monthly),
                    str(selected_emp["status"])
                ]

                employees_ws.update(
                    f"A{row_number}:Q{row_number}",
                    [updated_row]
                )

                st.success("Employee Updated Successfully!")
                st.session_state["edit_mode"] = False
                st.rerun()

    # ========== DELETE ==========
    with col2:
        if st.button("🗑 Delete Employee"):
            st.session_state["confirm_delete"] = True

    if "confirm_delete" not in st.session_state:
        st.session_state["confirm_delete"] = False

    if st.session_state["confirm_delete"]:

        st.warning("Are you sure you want to delete this employee?")

        col_yes, col_no = st.columns(2)

        with col_yes:
            if st.button("✅ Yes, Delete"):
                row_number = df.index[
                    df["employee_id"].astype(str) == str(selected_id)
                ][0] + 2
                employees_ws.delete_rows(row_number)
                st.success("Employee Deleted Successfully!")
                st.session_state["confirm_delete"] = False
                st.rerun()

        with col_no:
            if st.button("❌ Cancel"):
                st.session_state["confirm_delete"] = False
                st.rerun()

# =====================================================
# ADD NEW EMPLOYEE
# =====================================================

elif menu == "Employee Directory > Add New Employee":

    st.title("➕ Add New Employee")

    with st.form("add_employee_form"):

        col1, col2 = st.columns(2)

        with col1:
            employee_id = st.text_input("Employee ID")
            full_name = st.text_input("Full Name")
            place_of_birth = st.text_input("Place of Birth")
            date_of_birth = st.date_input("Date of Birth")
            national_id_number = st.text_input("National ID Number")
            gender = st.selectbox("Gender", ["Male", "Female"])
            join_date = st.date_input("Join Date")

        with col2:
            department = st.text_input("Department")
            position = st.text_input("Position")
            address = st.text_area("Address")
            bank_account_number = st.text_input("Bank Account Number")
            marital_status = st.selectbox("Marital Status", ["Single", "Married"])
            mothers_maiden_name = st.text_input("Mother's Maiden Name")
            daily_rate_basic = st.number_input("Daily Rate Basic", min_value=0)
            daily_rate_transport = st.number_input("Daily Rate Transportation", min_value=0)
            allowance_monthly = st.number_input("Allowance Monthly (Fixed)", min_value=0)

        save = st.form_submit_button("💾 Save Employee")

        if save:
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
                "Active"
            ])

            st.success("Employee Added Successfully!")
            st.rerun()

# =====================================================
# ATTENDANCE
# =====================================================

elif menu == "Attendance":
    st.title("📅 Attendance")
    df = load_sheet(attendance_ws)
    st.dataframe(df, use_container_width=True)

# =====================================================
# PAYROLL
# =====================================================

elif menu == "Payroll":

    st.title("💰 Payroll")

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    if df_att.empty:
        st.warning("No attendance data")
        st.stop()

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

        payroll.append([
            emp["employee_id"],
            emp["full_name"],
            str(emp["bank_account_number"]),
            present_days,
            float(emp["daily_rate_basic"]),
            float(emp["daily_rate_transport"]),
            float(emp["allowance_monthly"]),
            0,
            0
        ])

    payroll_df = pd.DataFrame(
        payroll,
        columns=[
            "Employee ID",
            "Name",
            "Bank Account Number",
            "Present Days",
            "Daily Basic",
            "Daily Transport",
            "Allowance",
            "Overtime",
            "Bonus"
        ]
    )

    edit_mode = st.toggle("✏️ Edit Overtime & Bonus")

    if edit_mode:
        edited_df = st.data_editor(payroll_df, use_container_width=True)
    else:
        edited_df = payroll_df.copy()

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
    st.metric("Total Payroll Cost", edited_df["Total Salary"].sum())

    output = BytesIO()
    export_df = edited_df.copy()
    export_df["Bank Account Number"] = export_df["Bank Account Number"].astype(str)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Payroll")
        worksheet = writer.sheets["Payroll"]
        for cell in worksheet["C"]:
            cell.number_format = "@"

    output.seek(0)

    st.download_button(
        "Download Payroll Excel",
        data=output,
        file_name=f"Payroll_{selected_month}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
