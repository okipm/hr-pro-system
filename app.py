import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from io import BytesIO
import time

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="HR Management System",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "HR Management System v1.0"
    }
)

# =====================================================
# CUSTOM CSS STYLING
# =====================================================

st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    }
    
    /* Main Color Theme */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #667eea;
        --accent-color: #764ba2;
        --success-color: #28a745;
        --danger-color: #dc3545;
        --warning-color: #ffc107;
        --light-bg: #f8f9fa;
        --border-color: #e0e0e0;
    }
    
    /* ===== LOGIN PAGE STYLES ===== */
    .login-wrapper {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f5f5;
        padding: 20px;
    }
    
    .login-container {
        width: 100%;
        max-width: 380px;
    }
    
    .login-card {
        background: white;
        border-radius: 16px;
        padding: 45px 35px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
        animation: slideUp 0.5s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .login-header {
        margin-bottom: 35px;
        text-align: center;
    }
    
    .login-logo {
        font-size: 48px;
        margin-bottom: 18px;
        display: block;
    }
    
    .login-title {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    
    .login-subtitle {
        font-size: 14px;
        color: #999;
        line-height: 1.5;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-label {
        display: block;
        font-size: 13px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .form-input-wrapper {
        position: relative;
    }
    
    .stTextInput input,
    .stTextInput > div > div > input {
        width: 100% !important;
        padding: 12px 14px !important;
        border: 1.5px solid #e8e8e8 !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        background-color: #fafafa !important;
        transition: all 0.3s ease !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto' !important;
    }
    
    .stTextInput input:focus,
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4 !important;
        background-color: white !important;
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.08) !important;
    }
    
    .stTextInput input::placeholder,
    .stTextInput > div > div > input::placeholder {
        color: #bbb !important;
    }
    
    .login-button {
        width: 100%;
        padding: 12px !important;
        background: linear-gradient(135deg, #1f77b4 0%, #0056b3 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        margin-top: 8px !important;
        box-shadow: 0 3px 12px rgba(31, 119, 180, 0.25) !important;
    }
    
    .login-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 16px rgba(31, 119, 180, 0.35) !important;
    }
    
    .login-button:active {
        transform: translateY(0) !important;
    }
    
    .login-error {
        background-color: #fff5f5;
        border: 1.5px solid #ff6b6b;
        color: #d32f2f;
        padding: 12px 14px;
        border-radius: 8px;
        margin-bottom: 18px;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: shake 0.3s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .login-success {
        background-color: #f1f9f6;
        border: 1.5px solid #4caf50;
        color: #2e7d32;
        padding: 12px 14px;
        border-radius: 8px;
        margin-bottom: 18px;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Hide streamlit defaults on login */
    .login-view .stTabs,
    .login-view .nav-container,
    .login-view [data-testid="stSidebar"],
    .login-view header {
        display: none !important;
    }
    
    /* ===== MAIN APP STYLES ===== */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        font-weight: bold;
        border-left: 5px solid #1f77b4;
        padding-left: 1rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .form-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .dataframe-container {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .nav-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 2rem;
        justify-content: center;
    }
    
    .nav-button {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 2px solid #1f77b4;
        background-color: white;
        color: #1f77b4;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
    }
    
    .nav-button:hover {
        background-color: #1f77b4;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(31, 119, 180, 0.3);
    }
    
    .nav-button.active {
        background-color: #1f77b4;
        color: white;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #1f77b4;
    }
    
    .stTextInput, .stNumberInput, .stSelectbox, .stDateInput {
        border-radius: 8px;
    }
    
    .stDataFrame {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stInfo, .stWarning, .stError, .stSuccess {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    .user-info-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
        font-weight: 600;
    }

    .attendance-summary {
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }

    .attendance-card {
        flex: 1;
        min-width: 150px;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .present-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
    }

    .absent-card {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
    }

    .total-card {
        background: linear-gradient(135deg, #1f77b4 0%, #0056b3 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# GOOGLE SHEETS CONNECTION WITH ERROR HANDLING
# =====================================================

@st.cache_resource
def init_gspread_client():
    """Initialize Google Sheets client with proper error handling"""
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials_dict = st.secrets["gcp_service_account"]
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=scopes
        )
        
        client = gspread.authorize(credentials)
        return client
    
    except KeyError:
        st.error("❌ Error: 'gcp_service_account' not found in secrets. Please check .streamlit/secrets.toml")
        st.stop()
    except Exception as e:
        st.error(f"❌ Authentication Error: {str(e)}")
        st.stop()

@st.cache_resource
def get_worksheets():
    """Get worksheet references with error handling"""
    try:
        client = init_gspread_client()
        sheet_id = st.secrets["google_sheet"]["sheet_id"]
        
        spreadsheet = client.open_by_key(sheet_id)
        
        employees_ws = spreadsheet.worksheet("employees")
        attendance_ws = spreadsheet.worksheet("attendance")
        users_ws = spreadsheet.worksheet("users")
        
        return employees_ws, attendance_ws, users_ws
    
    except KeyError:
        st.error("❌ Error: 'google_sheet' -> 'sheet_id' not found in secrets")
        st.stop()
    except gspread.exceptions.WorksheetNotFound as e:
        st.error(f"❌ Worksheet not found: {str(e)}\n\nPlease ensure your Google Sheet has these worksheets: 'employees', 'attendance', 'users'")
        st.stop()
    except gspread.exceptions.APIError as e:
        st.error(f"❌ Google Sheets API Error: {str(e)}\n\n**Solutions:**\n1. Check that the service account email has access to the Google Sheet\n2. Share the Google Sheet with: `{st.secrets['gcp_service_account'].get('client_email', 'N/A')}`\n3. Verify the sheet_id is correct")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")
        st.stop()

try:
    employees_ws, attendance_ws, users_ws = get_worksheets()
except:
    st.stop()

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def load_sheet(ws):
    """Load worksheet data as DataFrame"""
    try:
        return pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"Error loading sheet: {str(e)}")
        return pd.DataFrame()

def append_row(ws, data):
    """Append new row to worksheet"""
    try:
        ws.append_row(data)
    except Exception as e:
        st.error(f"Error appending row: {str(e)}")
        raise

# =====================================================
# LOGIN SECTION
# =====================================================

def login():
    """Beautiful Modern Login Page - White Background, Narrow"""
    st.markdown('<div class="login-view">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 0.8, 1])
    
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-header">
                <div class="login-logo">🏢</div>
                <h1 class="login-title">Sign in</h1>
                <p class="login-subtitle">Enter your credentials to access the portal</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Employee ID / Username</label>', unsafe_allow_html=True)
        username = st.text_input(
            "Username",
            placeholder="10002 or admin",
            label_visibility="collapsed",
            key="login_username"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Password</label>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            label_visibility="collapsed",
            key="login_password"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Sign In", use_container_width=True, type="primary", key="login_btn"):
            users = load_sheet(users_ws)
            
            if users.empty:
                st.markdown(
                    '<div class="login-error">❌ No users found. Please check the users worksheet.</div>',
                    unsafe_allow_html=True
                )
            else:
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
                    
                    # For Staff users, store their employee_id
                    if user.iloc[0]["role"].lower() == "staff":
                        st.session_state["employee_id"] = str(username)
                    
                    st.markdown(
                        '<div class="login-success">✅ Login successful! Redirecting...</div>',
                        unsafe_allow_html=True
                    )
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.markdown(
                        '<div class="login-error">❌ Invalid Employee ID/Username or password. Please try again.</div>',
                        unsafe_allow_html=True
                    )
    
    st.markdown('</div>', unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# =====================================================
# NAVIGATION BUTTONS
# =====================================================

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

st.markdown(f"""
<div class="user-info-bar">
👤 {st.session_state['username']} | Role: {st.session_state['role']}
</div>
""", unsafe_allow_html=True)

# Determine which pages to show based on role
is_admin = st.session_state.get("role", "").lower() == "admin"
is_staff = st.session_state.get("role", "").lower() == "staff"

st.markdown('<div class="nav-container">', unsafe_allow_html=True)

if is_admin:
    # Admin sees all pages
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state["current_page"] = "Dashboard"
            st.rerun()
    
    with col2:
        if st.button("👥 Directory", use_container_width=True, key="nav_directory"):
            st.session_state["current_page"] = "Employee Directory"
            st.rerun()
    
    with col3:
        if st.button("➕ Add Employee", use_container_width=True, key="nav_add"):
            st.session_state["current_page"] = "Add New Employee"
            st.rerun()
    
    with col4:
        if st.button("📅 Attendance", use_container_width=True, key="nav_attendance"):
            st.session_state["current_page"] = "Attendance"
            st.rerun()
    
    with col5:
        if st.button("💰 Payroll", use_container_width=True, key="nav_payroll"):
            st.session_state["current_page"] = "Payroll"
            st.rerun()

elif is_staff:
    # Staff only sees their own data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👤 My Profile", use_container_width=True, key="nav_profile"):
            st.session_state["current_page"] = "Staff Profile"
            st.rerun()
    
    with col2:
        if st.button("📅 My Attendance", use_container_width=True, key="nav_my_attendance"):
            st.session_state["current_page"] = "Staff Attendance"
            st.rerun()
    
    with col3:
        if st.button("💰 My Payroll", use_container_width=True, key="nav_my_payroll"):
            st.session_state["current_page"] = "Staff Payroll"
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# PAGE ROUTING
# =====================================================

menu = st.session_state["current_page"]
df_emp = load_sheet(employees_ws)
df_att = load_sheet(attendance_ws)

# =====================================================
# ADMIN PAGES
# =====================================================

if is_admin:
    # DASHBOARD
    if menu == "Dashboard":
        st.markdown('<div class="main-header">📊 HR Dashboard</div>', unsafe_allow_html=True)
        
        if df_emp.empty:
            st.warning("⚠️ No employee data. Please add employees to get started.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_emp = len(df_emp)
                st.metric("👥 Total Employees", total_emp)
            
            with col2:
                active_emp = len(df_emp[df_emp["status"] == "Active"]) if not df_emp.empty else 0
                st.metric("✅ Active Employees", active_emp)
            
            with col3:
                today_present = 0
                if not df_att.empty:
                    today_att = df_att[(df_att["date"] == str(date.today())) & 
                                       (df_att["status"].astype(str).str.lower() == "present")]
                    present_ids = today_att["employee_id"].unique()
                    today_present = len([emp_id for emp_id in present_ids 
                                         if emp_id in df_emp["employee_id"].values])
                
                st.metric("📍 Present Today", today_present)
            
            with col4:
                departments = df_emp["department"].nunique() if not df_emp.empty else 0
                st.metric("🏢 Departments", departments)
    
    # EMPLOYEE DIRECTORY
    elif menu == "Employee Directory":
        st.markdown('<div class="main-header">👥 Employee Directory</div>', unsafe_allow_html=True)
        
        df = load_sheet(employees_ws)
        
        if df.empty:
            st.info("📭 No employees found. Start by adding new employees.")
            st.stop()
        
        st.markdown('<div class="section-header">🔍 Search & Filter</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 1.5])
        
        with col1:
            search_term = st.text_input("Search by Name or ID", placeholder="Enter name or employee ID")
        
        with col2:
            departments = ["All"] + sorted(df["department"].unique().tolist())
            filter_dept = st.selectbox("Filter by Department", departments)
        
        with col3:
            filter_status = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        
        filtered_df = df.copy()
        
        if search_term:
            filtered_df = filtered_df[
                (filtered_df["full_name"].str.contains(search_term, case=False, na=False)) |
                (filtered_df["employee_id"].astype(str).str.contains(search_term, na=False))
            ]
        
        if filter_dept != "All":
            filtered_df = filtered_df[filtered_df["department"] == filter_dept]
        
        if filter_status != "All":
            filtered_df = filtered_df[filtered_df["status"] == filter_status]
        
        st.markdown(f"**📋 Total Records: {len(filtered_df)}**")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown('<div class="section-header">⚙️ Manage Employee</div>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            employee_options = [
                f"{row['employee_id']} - {row['full_name']}"
                for _, row in filtered_df.iterrows()
            ]
            
            selected_option = st.selectbox("Select Employee", employee_options)
            selected_id = selected_option.split(" - ")[0]
            
            selected_emp = df[df["employee_id"].astype(str) == str(selected_id)].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✏️ Edit Employee", use_container_width=True, key="edit_btn"):
                    st.session_state["edit_mode"] = True
            
            with col2:
                if st.button("🗑️ Delete Employee", use_container_width=True, type="secondary", key="delete_btn"):
                    st.session_state["confirm_delete"] = True
            
            if "edit_mode" not in st.session_state:
                st.session_state["edit_mode"] = False
            
            if st.session_state["edit_mode"]:
                st.markdown("---")
                st.markdown('<div class="section-header">✏️ Edit Employee Information</div>', unsafe_allow_html=True)
                
                with st.form("edit_employee_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        full_name = st.text_input("Full Name", value=selected_emp["full_name"])
                        department = st.text_input("Department", value=selected_emp["department"])
                        position = st.text_input("Position", value=selected_emp["position"])
                    
                    with col2:
                        bank_account = st.text_input("Bank Account Number", value=str(selected_emp.get("bank_account_number", "")))
                        daily_rate_basic = st.number_input("Daily Rate Basic", value=float(selected_emp.get("daily_rate_basic", 0)))
                        daily_rate_transport = st.number_input("Daily Rate Transport", value=float(selected_emp.get("daily_rate_transport", 0)))
                    
                    daily_rate_meal = st.number_input("Daily Rate Meal Allowance", value=float(selected_emp.get("daily_rate_meal", 0)))
                    allowance_monthly = st.number_input("Monthly Allowance", value=float(selected_emp.get("allowance_monthly", 0)))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update = st.form_submit_button("💾 Update", use_container_width=True, type="primary")
                    with col2:
                        cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
                    
                    if update:
                        try:
                            row_number = int(df.index[df["employee_id"].astype(str) == str(selected_id)][0]) + 2
                            
                            updated_row = [
                                str(selected_id),
                                str(full_name),
                                str(selected_emp.get("place_of_birth", "")),
                                str(selected_emp.get("date_of_birth", "")),
                                str(selected_emp.get("national_id_number", "")),
                                str(selected_emp.get("gender", "")),
                                str(selected_emp.get("join_date", "")),
                                str(department),
                                str(position),
                                str(selected_emp.get("address", "")),
                                str(bank_account),
                                str(selected_emp.get("marital_status", "")),
                                str(selected_emp.get("mothers_maiden_name", "")),
                                float(daily_rate_basic),
                                float(daily_rate_transport),
                                float(daily_rate_meal),
                                float(allowance_monthly),
                                str(selected_emp["status"])
                            ]
                            
                            employees_ws.update(f"A{row_number}:R{row_number}", [updated_row])
                            st.success("✅ Employee Updated Successfully!")
                            st.session_state["edit_mode"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating employee: {str(e)}")
                    
                    if cancel:
                        st.session_state["edit_mode"] = False
                        st.rerun()
            
            if st.session_state.get("confirm_delete", False):
                st.markdown("---")
                st.warning(f"⚠️ Are you sure you want to delete {selected_emp['full_name']}? This action cannot be undone.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", use_container_width=True, type="secondary"):
                        try:
                            row_number = int(df.index[df["employee_id"].astype(str) == str(selected_id)][0]) + 2
                            employees_ws.delete_rows(row_number)
                            st.success("✅ Employee Deleted Successfully!")
                            st.session_state["confirm_delete"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting employee: {str(e)}")
                
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state["confirm_delete"] = False
                        st.rerun()
    
    # ADD NEW EMPLOYEE
    elif menu == "Add New Employee":
        st.markdown('<div class="main-header">➕ Add New Employee</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["👤 Personal Info", "💼 Job Info", "💰 Compensation"])
        
        with tab1:
            st.markdown('<div class="section-header">Personal Information</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                employee_id = st.text_input("Employee ID", placeholder="EMP001", key="emp_id")
                full_name = st.text_input("Full Name", placeholder="John Doe", key="full_name")
                date_of_birth = st.date_input("Date of Birth", min_value=date(1950, 1, 1), max_value=date.today(), key="dob")
                place_of_birth = st.text_input("Place of Birth", placeholder="New York", key="pob")
            
            with col2:
                national_id_number = st.text_input("National ID Number", placeholder="123456789", key="nid")
                gender = st.selectbox("Gender", ["Male", "Female"], key="gender")
                marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"], key="marital")
                mothers_maiden_name = st.text_input("Mother's Maiden Name", placeholder="Jane Smith", key="mmn")
        
        with tab2:
            st.markdown('<div class="section-header">Job Information</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                join_date = st.date_input("Join Date", key="join_date")
                department = st.text_input("Department", placeholder="Sales", key="department")
                position = st.text_input("Position", placeholder="Sales Manager", key="position")
            
            with col2:
                st.write("")
                address = st.text_area("Address", placeholder="123 Main St, City, Country", height=100, key="address")
        
        with tab3:
            st.markdown('<div class="section-header">Compensation & Banking</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                daily_rate_basic = st.number_input("Daily Rate (Basic)", min_value=0.0, step=0.01, key="drb")
            
            with col2:
                daily_rate_transport = st.number_input("Daily Rate (Transport)", min_value=0.0, step=0.01, key="drt")
            
            with col3:
                daily_rate_meal = st.number_input("Daily Rate (Meal Allowance)", min_value=0.0, step=0.01, key="drm")
            
            allowance_monthly = st.number_input("Monthly Allowance (Fixed)", min_value=0.0, step=0.01, key="am")
            bank_account_number = st.text_input("Bank Account Number", placeholder="1234567890", key="bank")
        
            st.markdown("---")

        if st.button("💾 Save New Employee", use_container_width=True, type="primary"):

            if not employee_id or not full_name or not department or not position:
                st.error("❌ Please fill in all required fields (ID, Name, Department, Position)")

            else:
                try:
                    df_existing = load_sheet(employees_ws)

                    existing_ids = df_existing["employee_id"].astype(str).tolist() if not df_existing.empty else []

                    if str(employee_id) in existing_ids:
                        st.warning(f"⚠️ Employee ID {employee_id} already exists in the system!")

                    else:
                        append_row(employees_ws, [
                            str(employee_id),
                            str(full_name),
                            str(place_of_birth),
                            str(date_of_birth),
                            str(national_id_number),
                            str(gender),
                            str(join_date),
                            str(department),
                            str(position),
                            str(address),
                            str(bank_account_number),
                            str(marital_status),
                            str(mothers_maiden_name),
                            float(daily_rate_basic),
                            float(daily_rate_transport),
                            float(daily_rate_meal),
                            float(allowance_monthly),
                            "Active"
                        ])

                        st.success(f"✅ Employee {full_name} successfully added!")

                except Exception as e:
                    st.error(f"❌ Error adding employee: {str(e)}")
    
    # ATTENDANCE
    elif menu == "Attendance":
        st.markdown('<div class="main-header">📅 Attendance</div>', unsafe_allow_html=True)
        
        if df_emp.empty:
            st.warning("⚠️ No employees registered in the system. Please add employees first.")
            st.stop()
        
        if df_att.empty:
            st.info("📭 No attendance records found.")
        else:
            if "date" in df_att.columns and "employee_id" in df_att.columns:
                dates = sorted(df_att["date"].unique(), reverse=True)
                selected_date = st.selectbox("Select Date", dates)
                
                df_filtered = df_att[df_att["date"] == selected_date].copy()
                
                df_filtered = df_filtered.merge(
                    df_emp[['employee_id', 'full_name']],
                    on='employee_id',
                    how='inner'
                )
                
                all_employees = df_emp[['employee_id', 'full_name']].copy()
                
                complete_attendance = []
                for _, emp in all_employees.iterrows():
                    emp_id = emp['employee_id']
                    emp_name = emp['full_name']
                    
                    emp_record = df_filtered[df_filtered['employee_id'] == emp_id]
                    
                    if not emp_record.empty:
                        status = emp_record.iloc[0]['status']
                    else:
                        status = 'Absent'
                    
                    complete_attendance.append({
                        'Employee ID': emp_id,
                        'Name': emp_name,
                        'Date': selected_date,
                        'Status': status
                    })
                
                df_complete = pd.DataFrame(complete_attendance)
                
                df_complete.insert(0, 'No.', range(1, len(df_complete) + 1))
                
                total_employees = len(df_complete)
                present_count = len(df_complete[df_complete['Status'].str.lower() == 'present'])
                absent_count = len(df_complete[df_complete['Status'].str.lower() == 'absent'])
                
                st.markdown(f"""
                <div class="attendance-summary">
                    <div class="attendance-card present-card">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Present</div>
                        <div style="font-size: 2.5rem; margin-top: 0.5rem;">{present_count}</div>
                    </div>
                    <div class="attendance-card absent-card">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Absent</div>
                        <div style="font-size: 2.5rem; margin-top: 0.5rem;">{absent_count}</div>
                    </div>
                    <div class="attendance-card total-card">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">👥</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">Total</div>
                        <div style="font-size: 2.5rem; margin-top: 0.5rem;">{total_employees}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**📋 Detailed Records for {selected_date}:**")
                st.dataframe(df_complete, use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ Attendance data format is incorrect. Missing 'date' or 'employee_id' columns.")
    
    # PAYROLL
    elif menu == "Payroll":
        st.markdown('<div class="main-header">💰 Payroll Management</div>', unsafe_allow_html=True)
        
        if df_att.empty:
            st.warning("⚠️ No attendance data available. Please add attendance records first.")
            st.stop()
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            month_list = sorted(df_att["date"].str[:7].unique(), reverse=True)
            selected_month = st.selectbox("Select Month", month_list)
        
        with col2:
            st.write("")
        
        with col3:
            edit_mode = st.toggle("✏️ Edit Mode")
        
        df_month = df_att[df_att["date"].str.startswith(selected_month)]
        
        payroll = []
        for _, emp in df_emp.iterrows():
            present_days = len(
                df_month[
                    (df_month["employee_id"] == emp["employee_id"]) &
                    (df_month["status"].astype(str).str.lower() == "present")
                ]
            )
            
            daily_basic = float(emp.get("daily_rate_basic", 0))
            daily_transport = float(emp.get("daily_rate_transport", 0))
            daily_meal = float(emp.get("daily_rate_meal", 0))
            allowance_monthly = float(emp.get("allowance_monthly", 0))
            
            salary_from_attendance = (daily_basic + daily_transport + daily_meal) * present_days
            
            payroll.append({
                "Employee ID": emp["employee_id"],
                "Name": emp["full_name"],
                "Bank Account": str(emp.get("bank_account_number", "")),
                "Present Days": present_days,
                "Daily Basic": daily_basic,
                "Daily Transport": daily_transport,
                "Daily Meal": daily_meal,
                "Monthly Allowance": allowance_monthly,
                "Salary from Attendance": salary_from_attendance,
                "Overtime": 0.0,
                "Bonus": 0.0
            })
        
        payroll_df = pd.DataFrame(payroll)
        
        column_order = [
            "Employee ID", "Name", "Bank Account", "Present Days",
            "Daily Basic", "Daily Transport", "Daily Meal", "Monthly Allowance",
            "Salary from Attendance", "Overtime", "Bonus"
        ]
        payroll_df = payroll_df[column_order]
        
        if edit_mode:
            st.markdown('<div class="section-header">✏️ Edit Payroll Data</div>', unsafe_allow_html=True)
            edited_df = st.data_editor(payroll_df, use_container_width=True, num_rows="dynamic", key="payroll_editor")
            
            st.markdown("---")
            
            if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                st.info("✅ Payroll changes saved successfully!")
                payroll_df = edited_df.copy()
        else:
            edited_df = payroll_df.copy()
        
        edited_df["Total Salary"] = (
            edited_df["Salary from Attendance"] +
            edited_df["Monthly Allowance"] +
            edited_df["Overtime"] +
            edited_df["Bonus"]
        )
        
        st.markdown("---")
        st.markdown('<div class="section-header">💼 Payroll Summary</div>', unsafe_allow_html=True)
        
        st.dataframe(edited_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Payroll", f"{edited_df['Total Salary'].sum():,.2f}")
        
        with col2:
            st.metric("📊 Avg Salary", f"{edited_df['Total Salary'].mean():,.2f}")
        
        with col3:
            st.metric("👥 Employee Count", len(edited_df))
        
        with col4:
            st.metric("📅 Month", selected_month)
        
        st.markdown("---")
        
        try:
            output = BytesIO()
            export_df = edited_df.copy()
            export_df["Bank Account"] = export_df["Bank Account"].astype(str)
            
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Payroll")
                worksheet = writer.sheets["Payroll"]
                for cell in worksheet["C"]:
                    cell.number_format = "@"
            
            output.seek(0)
            
            st.download_button(
                "⬇️ Download Payroll Excel",
                data=output,
                file_name=f"Payroll_{selected_month}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"Error exporting payroll: {str(e)}")

# =====================================================
# STAFF PAGES
# =====================================================

elif is_staff:
    staff_id = st.session_state.get("employee_id")
    staff_employee = df_emp[df_emp["employee_id"].astype(str) == str(staff_id)].iloc[0] if not df_emp.empty and staff_id else None
    
    if staff_employee is None:
        st.error("❌ Your employee record not found. Please contact admin.")
        st.stop()
    
    # STAFF PROFILE
    if menu == "Staff Profile":
        st.markdown('<div class="main-header">👤 My Profile</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 30px; border-radius: 10px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 10px;">👤</div>
                <h3 style="margin: 0; font-size: 20px;">{staff_employee["full_name"]}</h3>
                <p style="margin: 5px 0; opacity: 0.9;">{staff_employee["position"]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-header">📋 Personal Information</div>', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Employee ID:** {staff_employee['employee_id']}")
                st.write(f"**Full Name:** {staff_employee['full_name']}")
                st.write(f"**Date of Birth:** {staff_employee.get('date_of_birth', 'N/A')}")
                st.write(f"**Gender:** {staff_employee.get('gender', 'N/A')}")
            
            with col_b:
                st.write(f"**Department:** {staff_employee['department']}")
                st.write(f"**Position:** {staff_employee['position']}")
                st.write(f"**Join Date:** {staff_employee.get('join_date', 'N/A')}")
                st.write(f"**Status:** {staff_employee['status']}")
        
        st.markdown("---")
        
        # Edit Personal Details Button
        if st.button("✏️ Edit Personal Details", use_container_width=True, key="edit_personal_btn"):
            st.session_state["edit_personal_mode"] = True
        
        # Edit Personal Details Form
        if st.session_state.get("edit_personal_mode", False):
            st.markdown("---")
            st.markdown('<div class="section-header">✏️ Edit Personal Information</div>', unsafe_allow_html=True)
            
            with st.form("edit_personal_form"):
                col1, col2 = st.columns(2)
                
                # Set default values safely
                current_dob = staff_employee.get('date_of_birth', str(date.today()))
                try:
                    dob_value = pd.to_datetime(current_dob).date()
                except:
                    dob_value = date.today()
                
                current_gender = staff_employee.get('gender', 'Male')
                gender_index = 1 if current_gender.lower() == 'female' else 0
                
                current_marital = staff_employee.get('marital_status', 'Single')
                marital_options = ["Single", "Married", "Divorced", "Widowed"]
                try:
                    marital_index = marital_options.index(current_marital)
                except:
                    marital_index = 0
                
                with col1:
                    full_name = st.text_input("Full Name", value=staff_employee["full_name"], key="edit_full_name")
                    date_of_birth = st.date_input("Date of Birth", value=dob_value, key="edit_dob")
                    gender = st.selectbox("Gender", ["Male", "Female"], index=gender_index, key="edit_gender")
                
                with col2:
                    place_of_birth = st.text_input("Place of Birth", value=staff_employee.get('place_of_birth', ''), key="edit_pob")
                    national_id = st.text_input("National ID Number", value=staff_employee.get('national_id_number', ''), key="edit_nid")
                    marital_status = st.selectbox("Marital Status", marital_options, index=marital_index, key="edit_marital")
                
                address = st.text_area("Address", value=staff_employee.get('address', ''), height=80, key="edit_address")
                mothers_maiden_name = st.text_input("Mother's Maiden Name", value=staff_employee.get('mothers_maiden_name', ''), key="edit_mmn")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                with col2:
                    cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if submit:
                    try:
                        # Find the row number for this employee
                        df_all = load_sheet(employees_ws)
                        row_number = int(df_all.index[df_all["employee_id"].astype(str) == str(staff_id)][0]) + 2
                        
                        # Prepare updated row data (all columns)
                        updated_row = [
                            str(staff_id),
                            str(full_name),
                            str(place_of_birth),
                            str(date_of_birth),
                            str(national_id),
                            str(gender),
                            str(staff_employee.get('join_date', '')),
                            str(staff_employee['department']),
                            str(staff_employee['position']),
                            str(address),
                            str(staff_employee.get('bank_account_number', '')),
                            str(marital_status),
                            str(mothers_maiden_name),
                            float(staff_employee.get('daily_rate_basic', 0)),
                            float(staff_employee.get('daily_rate_transport', 0)),
                            float(staff_employee.get('daily_rate_meal', 0)),
                            float(staff_employee.get('allowance_monthly', 0)),
                            str(staff_employee['status'])
                        ]
                        
                        # Update the row in Google Sheets
                        employees_ws.update(f"A{row_number}:R{row_number}", [updated_row])
                        
                        st.success("✅ Personal details updated successfully!")
                        st.session_state["edit_personal_mode"] = False
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating details: {str(e)}")
                
                if cancel:
                    st.session_state["edit_personal_mode"] = False
                    st.rerun()
        
        st.markdown("---")
        st.markdown('<div class="section-header">💼 Compensation Information</div>', unsafe_allow_html=True)
        st.markdown("*This information cannot be edited by staff*")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Daily Basic Rate", f"{float(staff_employee.get('daily_rate_basic', 0)):,.2f}")
        
        with col2:
            st.metric("Daily Transport Rate", f"{float(staff_employee.get('daily_rate_transport', 0)):,.2f}")
        
        with col3:
            st.metric("Daily Meal Allowance", f"{float(staff_employee.get('daily_rate_meal', 0)):,.2f}")
        
        st.write(f"**Monthly Allowance:** {float(staff_employee.get('allowance_monthly', 0)):,.2f}")
        st.write(f"**Bank Account:** {staff_employee.get('bank_account_number', 'Not provided')}")
    
    # STAFF ATTENDANCE
    elif menu == "Staff Attendance":
        st.markdown('<div class="main-header">📅 My Attendance</div>', unsafe_allow_html=True)
        
        staff_attendance = df_att[df_att["employee_id"].astype(str) == str(staff_id)]
        
        if staff_attendance.empty:
            st.info("📭 No attendance records found.")
        else:
            # Get available months for staff
            staff_months = sorted(staff_attendance["date"].str[:7].unique(), reverse=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown('<div class="section-header">📅 Filter by Month</div>', unsafe_allow_html=True)
                selected_month = st.selectbox("Select Month", staff_months, key="staff_month_filter")
            
            with col2:
                st.write("")
            
            # Filter attendance for selected month
            monthly_attendance = staff_attendance[staff_attendance["date"].str.startswith(selected_month)]
            
            # Calculate summary for selected month
            total_records = len(monthly_attendance)
            present_count = len(monthly_attendance[monthly_attendance["status"].astype(str).str.lower() == "present"])
            absent_count = total_records - present_count
            
            st.markdown(f"""
            <div class="attendance-summary">
                <div class="attendance-card present-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Present Days</div>
                    <div style="font-size: 2.5rem; margin-top: 0.5rem;">{present_count}</div>
                </div>
                <div class="attendance-card absent-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Absent Days</div>
                    <div style="font-size: 2.5rem; margin-top: 0.5rem;">{absent_count}</div>
                </div>
                <div class="attendance-card total-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Total Records</div>
                    <div style="font-size: 2.5rem; margin-top: 0.5rem;">{total_records}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f'<div class="section-header">📋 Attendance Records for {selected_month}</div>', unsafe_allow_html=True)
            
            display_df = monthly_attendance[['date', 'status']].copy()
            display_df = display_df.sort_values('date', ascending=False).reset_index(drop=True)
            display_df.insert(0, 'No.', range(1, len(display_df) + 1))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # STAFF PAYROLL
    elif menu == "Staff Payroll":
        st.markdown('<div class="main-header">💰 My Payroll</div>', unsafe_allow_html=True)
        
        if df_att.empty:
            st.warning("⚠️ No attendance data available.")
            st.stop()
        
        # Get available months for staff
        staff_months = sorted(df_att[df_att["employee_id"].astype(str) == str(staff_id)]["date"].str[:7].unique(), reverse=True)
        
        if len(staff_months) == 0:
            st.warning("⚠️ No payroll data available for you.")
            st.stop()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown('<div class="section-header">📅 Filter by Month</div>', unsafe_allow_html=True)
            selected_month = st.selectbox("Select Month", staff_months, key="staff_payroll_month")
        
        with col2:
            st.write("")
        
        df_month = df_att[df_att["date"].str.startswith(selected_month)]
        
        present_days = len(
            df_month[
                (df_month["employee_id"].astype(str) == str(staff_id)) &
                (df_month["status"].astype(str).str.lower() == "present")
            ]
        )
        
        daily_basic = float(staff_employee.get("daily_rate_basic", 0))
        daily_transport = float(staff_employee.get("daily_rate_transport", 0))
        daily_meal = float(staff_employee.get("daily_rate_meal", 0))
        allowance_monthly = float(staff_employee.get("allowance_monthly", 0))
        
        salary_from_attendance = (daily_basic + daily_transport + daily_meal) * present_days
        total_salary = salary_from_attendance + allowance_monthly
        
        st.markdown('<div class="section-header">📊 Payroll Summary</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Present Days", present_days)
            st.metric("Daily Basic Rate", f"{daily_basic:,.2f}")
            st.metric("Daily Transport Rate", f"{daily_transport:,.2f}")
            st.metric("Daily Meal Allowance", f"{daily_meal:,.2f}")
        
        with col2:
            st.metric("Salary from Attendance", f"{salary_from_attendance:,.2f}")
            st.metric("Monthly Allowance", f"{allowance_monthly:,.2f}")
            st.metric("Overtime", "0.00")
            st.metric("Bonus", "0.00")
        
        st.markdown("---")
        st.markdown('<div class="section-header">💰 Total Salary</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                    color: white; padding: 30px; border-radius: 10px; text-align: center;">
            <div style="font-size: 18px; opacity: 0.9; margin-bottom: 10px;">Total Salary for {selected_month}</div>
            <div style="font-size: 48px; font-weight: bold;">{total_salary:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
