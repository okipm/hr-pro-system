import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import plotly.express as px

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="HR 3.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# ENTERPRISE UI
# =====================================================

st.markdown("""
<style>
header {visibility:hidden;}
footer {visibility:hidden;}

.stApp {
    background: linear-gradient(135deg,#0f172a,#1e293b,#111827);
    color:white;
}

section[data-testid="stSidebar"] {
    background:#0f172a;
    border-right:1px solid #1e293b;
}

section[data-testid="stSidebar"] * {
    color:white !important;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}

.kpi {
    font-size: 40px;
    font-weight: bold;
}

.title {
    font-size:28px;
    font-weight:bold;
    margin-bottom:20px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# GOOGLE CONNECTION
# =====================================================

@st.cache_resource
def init_connection():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet_id = st.secrets["google_sheet"]["sheet_id"]
    sheet = client.open_by_key(sheet_id)

    return (
        sheet.worksheet("employees"),
        sheet.worksheet("attendance"),
        sheet.worksheet("users")
    )

employees_ws, attendance_ws, users_ws = init_connection()

def load_sheet(ws):
    return pd.DataFrame(ws.get_all_records())

# =====================================================
# LOGIN
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.markdown('<div class="title">🔐 HR 3.0 Enterprise Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):

        users = load_sheet(users_ws)

        user = users[
            (users["username"].astype(str)==username) &
            (users["password"].astype(str)==password)
        ]

        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.role = user.iloc[0]["role"]
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown("## 🏢 HR 3.0")
    st.markdown("---")

    role = st.session_state.role

    if role in ["Admin","HR"]:
        menu = st.radio("Navigation",
            ["Dashboard","Employees","Attendance","Payroll Analytics"]
        )
    else:
        menu = st.radio("Navigation",
            ["My Payroll"]
        )

    st.markdown("---")
    st.markdown(f"👤 {st.session_state.username}")
    st.markdown(f"🔐 {role}")

    if st.button("Logout"):
        st.session_state.logged_in=False
        st.rerun()

# =====================================================
# LOAD DATA
# =====================================================

df_emp = load_sheet(employees_ws)
df_att = load_sheet(attendance_ws)

# =====================================================
# DASHBOARD
# =====================================================

if menu == "Dashboard":

    st.markdown('<div class="title">Dashboard Overview</div>', unsafe_allow_html=True)

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.markdown(f'<div class="card"><div>Total Employees</div><div class="kpi">{len(df_emp)}</div></div>',unsafe_allow_html=True)

    with col2:
        active = len(df_emp[df_emp["status"]=="Active"])
        st.markdown(f'<div class="card"><div>Active Employees</div><div class="kpi">{active}</div></div>',unsafe_allow_html=True)

    with col3:
        today = len(df_att[df_att["date"]==str(date.today())])
        st.markdown(f'<div class="card"><div>Present Today</div><div class="kpi">{today}</div></div>',unsafe_allow_html=True)

    with col4:
        dept = df_emp["department"].nunique()
        st.markdown(f'<div class="card"><div>Departments</div><div class="kpi">{dept}</div></div>',unsafe_allow_html=True)

    st.markdown("---")

    # Attendance Trend
    if not df_att.empty:
        df_att["date"] = pd.to_datetime(df_att["date"])
        trend = df_att.groupby("date").size().reset_index(name="Present")
        fig = px.line(trend, x="date", y="Present", title="Attendance Trend")
        st.plotly_chart(fig, use_container_width=True)

    # Department Distribution
    dept_chart = df_emp["department"].value_counts().reset_index()
    dept_chart.columns=["Department","Count"]
    fig2 = px.pie(dept_chart, names="Department", values="Count", title="Department Distribution")
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# EMPLOYEES
# =====================================================

elif menu == "Employees":

    st.markdown('<div class="title">Employee Directory</div>', unsafe_allow_html=True)

    st.dataframe(df_emp, use_container_width=True)

# =====================================================
# ATTENDANCE
# =====================================================

elif menu == "Attendance":

    st.markdown('<div class="title">Attendance Records</div>', unsafe_allow_html=True)

    dates = sorted(df_att["date"].unique(), reverse=True)
    selected = st.selectbox("Select Date", dates)

    df_day = df_att[df_att["date"]==selected]

    merged = df_day.merge(
        df_emp[["employee_id","full_name"]],
        on="employee_id",
        how="left"
    )

    st.dataframe(merged, use_container_width=True)

# =====================================================
# PAYROLL ANALYTICS (HR/Admin)
# =====================================================

elif menu == "Payroll Analytics":

    st.markdown('<div class="title">Payroll Analytics</div>', unsafe_allow_html=True)

    month_list = sorted(df_att["date"].str[:7].unique(), reverse=True)
    selected_month = st.selectbox("Select Month", month_list)

    df_month = df_att[df_att["date"].str.startswith(selected_month)]

    payroll=[]

    for _,emp in df_emp.iterrows():
        present=len(
            df_month[
                (df_month["employee_id"]==emp["employee_id"]) &
                (df_month["status"]=="Present")
            ]
        )

        salary = present * (
            float(emp.get("daily_rate_basic",0)) +
            float(emp.get("daily_rate_transport",0))
        ) + float(emp.get("allowance_monthly",0))

        payroll.append({
            "Employee":emp["full_name"],
            "Salary":salary
        })

    payroll_df=pd.DataFrame(payroll)

    st.dataframe(payroll_df, use_container_width=True)

    fig = px.bar(payroll_df, x="Employee", y="Salary", title="Payroll Distribution")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# STAFF VIEW
# =====================================================

elif menu == "My Payroll":

    st.markdown('<div class="title">My Payroll</div>', unsafe_allow_html=True)

    emp_id = st.session_state.username  # assume username = employee_id

    employee = df_emp[df_emp["employee_id"].astype(str)==emp_id]

    if employee.empty:
        st.error("Employee not found")
    else:
        emp = employee.iloc[0]

        month_list = sorted(df_att["date"].str[:7].unique(), reverse=True)
        selected_month = st.selectbox("Select Month", month_list)

        df_month = df_att[
            (df_att["date"].str.startswith(selected_month)) &
            (df_att["employee_id"].astype(str)==emp_id)
        ]

        present=len(df_month)

        salary = present * (
            float(emp.get("daily_rate_basic",0)) +
            float(emp.get("daily_rate_transport",0))
        ) + float(emp.get("allowance_monthly",0))

        st.markdown(f'<div class="card"><div>Present Days</div><div class="kpi">{present}</div></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div>Total Salary</div><div class="kpi">{salary}</div></div>',unsafe_allow_html=True)
