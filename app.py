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
    page_title="HR Nexus",
    layout="wide"
)

# =====================================================
# CUSTOM CSS (PROFESSIONAL UI)
# =====================================================

st.markdown("""
<style>

body {
    background-color: #f3f4f6;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}

/* Top Bar */
.topbar {
    background: white;
    padding: 15px 30px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.page-title {
    font-size: 24px;
    font-weight: 600;
}

/* Cards */
.card {
    background: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

/* Metric Card */
.metric-card {
    background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
    color: white;
    padding: 25px;
    border-radius: 14px;
}

/* Buttons */
.stButton>button {
    border-radius: 8px;
    font-weight: 600;
}

/* Dataframe */
.stDataFrame {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# GOOGLE SHEETS CONNECTION
# =====================================================

@st.cache_resource
def connect_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(credentials)
    sheet = client.open_by_key(st.secrets["google_sheet"]["sheet_id"])

    return (
        sheet.worksheet("employees"),
        sheet.worksheet("attendance"),
        sheet.worksheet("users")
    )

employees_ws, attendance_ws, users_ws = connect_sheets()

def load_sheet(ws):
    return pd.DataFrame(ws.get_all_records())

# =====================================================
# LOGIN SYSTEM
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 HR Nexus Login")

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
            st.session_state.role = user.iloc[0]["role"]
            st.session_state.page = "Dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("HR Nexus")

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

pages = [
    "Dashboard",
    "Employee Directory",
    "Add Employee",
    "Attendance",
    "Payroll"
]

for p in pages:
    if st.sidebar.button(p):
        st.session_state.page = p

if st.sidebar.button("Sign Out"):
    st.session_state.logged_in = False
    st.rerun()

# =====================================================
# TOP HEADER
# =====================================================

st.markdown(f"""
<div class="topbar">
    <div class="page-title">{st.session_state.page}</div>
    <div>👤 {st.session_state.username} ({st.session_state.role})</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# DASHBOARD
# =====================================================

if st.session_state.page == "Dashboard":

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    total_emp = len(df_emp)
    active_emp = len(df_emp[df_emp["status"] == "Active"]) if not df_emp.empty else 0
    today_present = len(df_att[df_att["date"] == str(date.today())]) if not df_att.empty else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Employees</h4>
            <h2>{total_emp}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <h4>Active Employees</h4>
            <h2>{active_emp}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <h4>Present Today</h4>
            <h2>{today_present}</h2>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# DIRECTORY
# =====================================================

elif st.session_state.page == "Employee Directory":

    df = load_sheet(employees_ws)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# ADD EMPLOYEE
# =====================================================

elif st.session_state.page == "Add Employee":

    employee_id = st.text_input("Employee ID")
    full_name = st.text_input("Full Name")
    department = st.text_input("Department")
    position = st.text_input("Position")

    if st.button("Save Employee"):

        df_existing = load_sheet(employees_ws)
        existing_ids = df_existing["employee_id"].astype(str).tolist()

        if employee_id in existing_ids:
            st.warning("Employee already exists")
        else:
            employees_ws.append_row([
                employee_id,
                full_name,
                "",
                "",
                "",
                "",
                str(date.today()),
                department,
                position,
                "",
                "",
                "",
                "",
                0,
                0,
                0,
                "Active"
            ])
            st.success("Employee added successfully")

# =====================================================
# ATTENDANCE
# =====================================================

elif st.session_state.page == "Attendance":

    df_att = load_sheet(attendance_ws)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df_att, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# PAYROLL
# =====================================================

elif st.session_state.page == "Payroll":

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

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

        payroll.append({
            "Employee ID": emp["employee_id"],
            "Name": emp["full_name"],
            "Present Days": present_days,
            "Total Salary": salary
        })

    payroll_df = pd.DataFrame(payroll)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(payroll_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.metric("Total Payroll Cost", f"{payroll_df['Total Salary'].sum():,.2f}")

    # Export
    output = BytesIO()
    payroll_df.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        "Download Payroll Excel",
        data=output,
        file_name=f"Payroll_{selected_month}.xlsx"
    )
