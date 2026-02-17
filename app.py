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
    
    /* Main Header */
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
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        font-weight: bold;
        border-left: 5px solid #1f77b4;
        padding-left: 1rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Form Container */
    .form-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Success Message */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Dataframe Styling */
    .dataframe-container {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Sidebar Styling */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Navigation Buttons */
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
    
    /* Buttons */
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
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #1f77b4;
    }
    
    /* Input Fields */
    .stTextInput, .stNumberInput, .stSelectbox, .stDateInput {
        border-radius: 8px;
    }
    
    /* Table Styling */
    .stDataFrame {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Info/Warning Boxes */
    .stInfo, .stWarning, .stError, .stSuccess {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* User Info Bar */
    .user-info-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
        font-weight: 600;
    }

    /* Attendance Summary Cards */
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
        # Define required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Get credentials from Streamlit secrets
        credentials_dict = st.secrets["gcp_service_account"]
        
        # Create credentials object using google.oauth2
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=scopes
        )
        
        # Authorize gspread client
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
        
        # Open spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        
        # Get worksheets
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

# Get worksheet references
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

def get_employee_display_name(emp_id, df):
    """Get employee display name from ID"""
    emp = df[df['employee_id'].astype(str) == str(emp_id)]
    if not emp.empty:
        return f"{emp_id} - {emp.iloc[0]['full_name']}"
    return str(emp_id)

# =====================================================
# LOGIN SECTION
# =====================================================

def login():
    """Login page"""
    st.markdown('<div class="main-header">🔐 HR PRO LOGIN</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
        
        if st.button("🔓 Login", use_container_width=True, type="primary"):
            users = load_sheet(users_ws)
            
            if users.empty:
                st.error("❌ No users found. Please check the 'users' worksheet in Google Sheets.")
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
                    st.session_state["employee_id"] = user.iloc[0].get("employee_id", "")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# =====================================================
# NAVIGATION - ROLE BASED
# =====================================================

# Initialize current_page session state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard" if st.session_state["role"] == "Admin" else "My Attendance"

# User Info Bar
st.markdown(f"""
<div class="user-info-bar">
👤 {st.session_state['username']} | Role: {st.session_state['role']}
</div>
""", unsafe_allow_html=True)

# =====================================================
# ADMIN NAVIGATION
# =====================================================

if st.session_state["role"] == "Admin":
    # Navigation Buttons for Admin
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
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
        if st.button("📂 Bulk Upload", use_container_width=True, key="nav_bulk"):
            st.session_state["current_page"] = "Bulk Upload Employees"
            st.rerun()
    
    with col5:
        if st.button("📅 Attendance", use_container_width=True, key="nav_attendance"):
            st.session_state["current_page"] = "Attendance"
            st.rerun()
    
    with col6:
        if st.button("💰 Payroll", use_container_width=True, key="nav_payroll"):
            st.session_state["current_page"] = "Payroll"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# STAFF NAVIGATION
# =====================================================

elif st.session_state["role"] == "Staff":
    # Navigation Buttons for Staff
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📅 My Attendance", use_container_width=True, key="nav_my_attendance"):
            st.session_state["current_page"] = "My Attendance"
            st.rerun()
    
    with col2:
        if st.button("💰 My Payroll", use_container_width=True, key="nav_my_payroll"):
            st.session_state["current_page"] = "My Payroll"
            st.rerun()
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True, type="secondary", key="logout_btn"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# PAGE ROUTING
# =====================================================

menu = st.session_state["current_page"]

# =====================================================
# ADMIN - DASHBOARD
# =====================================================

if menu == "Dashboard":
    st.markdown('<div class="main-header">📊 HR Dashboard</div>', unsafe_allow_html=True)
    
    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)
    
    if df_emp.empty:
        st.warning("⚠️ No employee data. Please add employees to get started.")
    else:
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_emp = len(df_emp)
            st.metric("👥 Total Employees", total_emp)
        
        with col2:
            active_emp = len(df_emp[df_emp["status"] == "Active"]) if not df_emp.empty else 0
            st.metric("✅ Active Employees", active_emp)
        
        with col3:
            today_present = len(df_att[df_att["date"] == str(date.today())]) if not df_att.empty else 0
            st.metric("📍 Present Today", today_present)
        
        with col4:
            departments = df_emp["department"].nunique() if not df_emp.empty else 0
            st.metric("🏢 Departments", departments)

# =====================================================
# ADMIN - EMPLOYEE DIRECTORY
# =====================================================

elif menu == "Employee Directory":
    st.markdown('<div class="main-header">👥 Employee Directory</div>', unsafe_allow_html=True)
    
    df = load_sheet(employees_ws)
    
    if df.empty:
        st.info("📭 No employees found. Start by adding new employees.")
        st.stop()
    
    # Search and Filter Section
    st.markdown('<div class="section-header">🔍 Search & Filter</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1.5])
    
    with col1:
        search_term = st.text_input("Search by Name or ID", placeholder="Enter name or employee ID")
    
    with col2:
        departments = ["All"] + sorted(df["department"].unique().tolist())
        filter_dept = st.selectbox("Filter by Department", departments)
    
    with col3:
        filter_status = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
    
    # Apply Filters
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
        
        # Action Buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✏️ Edit Employee", use_container_width=True, key="edit_btn"):
                st.session_state["edit_mode"] = True
        
        with col2:
            if st.button("🗑️ Delete Employee", use_container_width=True, type="secondary", key="delete_btn"):
                st.session_state["confirm_delete"] = True
        
        # Edit Mode
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
                            float(allowance_monthly),
                            str(selected_emp["status"])
                        ]
                        
                        employees_ws.update(f"A{row_number}:Q{row_number}", [updated_row])
                        st.success("✅ Employee Updated Successfully!")
                        st.session_state["edit_mode"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating employee: {str(e)}")
                
                if cancel:
                    st.session_state["edit_mode"] = False
                    st.rerun()
        
        # Delete Confirmation
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

# =====================================================
# ADMIN - ADD NEW EMPLOYEE
# =====================================================

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
            st.write("")  # Spacer
            address = st.text_area("Address", placeholder="123 Main St, City, Country", height=100, key="address")
    
    with tab3:
        st.markdown('<div class="section-header">Compensation & Banking</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            daily_rate_basic = st.number_input("Daily Rate (Basic)", min_value=0.0, step=0.01, key="drb")
        
        with col2:
            daily_rate_transport = st.number_input("Daily Rate (Transport)", min_value=0.0, step=0.01, key="drt")
        
        with col3:
            allowance_monthly = st.number_input("Monthly Allowance (Fixed)", min_value=0.0, step=0.01, key="am")
        
        bank_account_number = st.text_input("Bank Account Number", placeholder="1234567890", key="bank")
    
    st.markdown("---")
    
    if st.button("💾 Save New Employee", use_container_width=True, type="primary"):
        if not employee_id or not full_name or not department or not position:
            st.error("❌ Please fill in all required fields (ID, Name, Department, Position)")
        else:
            try:
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
                st.success("✅ Employee Added Successfully!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding employee: {str(e)}")

# =====================================================
# ADMIN - BULK UPLOAD
# =====================================================

elif menu == "Bulk Upload Employees":
    st.markdown('<div class="main-header">📂 Bulk Upload Employees</div>', unsafe_allow_html=True)
    
    template_columns = [
        "employee_id", "full_name", "place_of_birth", "date_of_birth",
        "national_id_number", "gender", "join_date", "department",
        "position", "address", "bank_account_number", "marital_status",
        "mothers_maiden_name", "daily_rate_basic", "daily_rate_transport", "allowance_monthly"
    ]
    
    template_df = pd.DataFrame(columns=template_columns)
    buffer = BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)
    
    st.markdown('<div class="section-header">📥 Download Template</div>', unsafe_allow_html=True)
    st.download_button(
        "⬇️ Download Excel Template",
        buffer,
        "employee_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown('<div class="section-header">📤 Upload File</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx"])
    
    if uploaded_file:
        try:
            df_upload = pd.read_excel(uploaded_file)
            df_existing = load_sheet(employees_ws)
            
            st.info(f"📋 File contains {len(df_upload)} records")
            st.dataframe(df_upload, use_container_width=True)
            
            if st.button("✅ Process Upload", use_container_width=True, type="primary"):
                existing_ids = df_existing["employee_id"].astype(str).tolist()
                new_rows = []
                updated_count = 0
                
                for _, row in df_upload.iterrows():
                    emp_id = str(row["employee_id"])
                    
                    row_data = [
                        str(row["employee_id"]),
                        str(row["full_name"]),
                        str(row.get("place_of_birth", "")),
                        str(row.get("date_of_birth", "")),
                        str(row.get("national_id_number", "")),
                        str(row.get("gender", "")),
                        str(row.get("join_date", "")),
                        str(row["department"]),
                        str(row["position"]),
                        str(row.get("address", "")),
                        str(row.get("bank_account_number", "")),
                        str(row.get("marital_status", "")),
                        str(row.get("mothers_maiden_name", "")),
                        float(row.get("daily_rate_basic", 0)),
                        float(row.get("daily_rate_transport", 0)),
                        float(row.get("allowance_monthly", 0)),
                        "Active"
                    ]
                    
                    if emp_id in existing_ids:
                        row_number = int(df_existing.index[
                            df_existing["employee_id"].astype(str) == emp_id
                        ][0]) + 2
                        employees_ws.update(f"A{row_number}:Q{row_number}", [row_data])
                        updated_count += 1
                    else:
                        new_rows.append(row_data)
                
                if new_rows:
                    employees_ws.append_rows(new_rows)
                
                st.success(f"✅ Upload Complete!\n\n📊 Added: {len(new_rows)} | Updated: {updated_count}")
                st.rerun()
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# =====================================================
# ADMIN - ATTENDANCE
# =====================================================

elif menu == "Attendance":
    st.markdown('<div class="main-header">📅 Attendance</div>', unsafe_allow_html=True)
    
    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)
    
    if df_emp.empty:
        st.warning("⚠️ No employees registered in the system. Please add employees first.")
        st.stop()
    
    if df_att.empty:
        st.info("📭 No attendance records found.")
    else:
        if "date" in df_att.columns and "employee_id" in df_att.columns:
            # Get unique dates from attendance records
            dates = sorted(df_att["date"].unique(), reverse=True)
            selected_date = st.selectbox("Select Date", dates)
            
            # Filter attendance for selected date
            df_filtered = df_att[df_att["date"] == selected_date].copy()
            
            # Merge with employee data to get employee names
            df_filtered = df_filtered.merge(
                df_emp[['employee_id', 'full_name']],
                on='employee_id',
                how='inner'
            )
            
            # Get all registered employees
            all_employees = df_emp[['employee_id', 'full_name']].copy()
            
            # Create a complete attendance table with all employees
            complete_attendance = []
            for _, emp in all_employees.iterrows():
                emp_id = emp['employee_id']
                emp_name = emp['full_name']
                
                # Check if employee has a record for this date
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
            
            # Add row number
            df_complete.insert(0, 'No.', range(1, len(df_complete) + 1))
            
            # Calculate attendance summary
            total_employees = len(df_complete)
            present_count = len(df_complete[df_complete['Status'].str.lower() == 'present'])
            absent_count = len(df_complete[df_complete['Status'].str.lower() == 'absent'])
            
            # Display summary cards
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

# =====================================================
# ADMIN - PAYROLL
# =====================================================

elif menu == "Payroll":
    st.markdown('<div class="main-header">💰 Payroll Management</div>', unsafe_allow_html=True)
    
    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)
    
    if df_att.empty:
        st.warning("⚠️ No attendance data available. Please add attendance records first.")
        st.stop()
    
    # Month Selection and Edit Mode
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        month_list = sorted(df_att["date"].str[:7].unique(), reverse=True)
        selected_month = st.selectbox("Select Month", month_list)
    
    with col2:
        st.write("")  # Spacer
    
    with col3:
        edit_mode = st.toggle("✏️ Edit Mode")
    
    # Calculate Payroll
    df_month = df_att[df_att["date"].str.startswith(selected_month)]
    
    payroll = []
    for _, emp in df_emp.iterrows():
        present_days = len(
            df_month[
                (df_month["employee_id"] == emp["employee_id"]) &
                (df_month["status"] == "Present")
            ]
        )
        
        payroll.append({
            "Employee ID": emp["employee_id"],
            "Name": emp["full_name"],
            "Bank Account": str(emp.get("bank_account_number", "")),
            "Present Days": present_days,
            "Daily Basic": float(emp.get("daily_rate_basic", 0)),
            "Daily Transport": float(emp.get("daily_rate_transport", 0)),
            "Allowance": float(emp.get("allowance_monthly", 0)),
            "Overtime": 0.0,
            "Bonus": 0.0
        })
    
    payroll_df = pd.DataFrame(payroll)
    
    # Edit or Display
    if edit_mode:
        st.markdown('<div class="section-header">✏️ Edit Payroll Data</div>', unsafe_allow_html=True)
        edited_df = st.data_editor(payroll_df, use_container_width=True, num_rows="dynamic", key="payroll_editor")
        
        st.markdown("---")
        
        if st.button("💾 Save Changes", use_container_width=True, type="primary"):
            st.info("✅ Payroll changes saved successfully!")
            payroll_df = edited_df.copy()
    else:
        edited_df = payroll_df.copy()
    
    # Calculate Totals
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
    
    st.markdown("---")
    st.markdown('<div class="section-header">💼 Payroll Summary</div>', unsafe_allow_html=True)
    
    st.dataframe(edited_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Summary Metrics
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
    
    # Export Button
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
# STAFF - MY ATTENDANCE
# =====================================================

elif menu == "My Attendance":
    st.markdown('<div class="main-header">📅 My Attendance</div>', unsafe_allow_html=True)
    
    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)
    
    # Get current logged-in employee's ID
    current_emp_id = st.session_state.get("employee_id", "")
    
    # Get employee details
    emp_details = df_emp[df_emp["employee_id"].astype(str) == str(current_emp_id)]
    
    if emp_details.empty:
        st.warning("⚠️ Employee record not found.")
        st.stop()
    
    emp_name = emp_details.iloc[0]["full_name"]
    
    st.markdown(f"**👤 Employee:** {emp_name}")
    st.markdown(f"**🆔 Employee ID:** {current_emp_id}")
    
    st.markdown("---")
    
    if df_att.empty:
        st.info("📭 No attendance records found.")
    else:
        # Filter attendance for current employee
        my_attendance = df_att[df_att["employee_id"] == current_emp_id].copy()
        
        if my_attendance.empty:
            st.info("📭 No attendance records for your account.")
        else:
            # Sort by date (latest first)
            my_attendance = my_attendance.sort_values("date", ascending=False)
            
            # Add row number
            my_attendance_display = my_attendance[["date", "status"]].copy()
            my_attendance_display.insert(0, 'No.', range(1, len(my_attendance_display) + 1))
            my_attendance_display.columns = ['No.', 'Date', 'Status']
            
            # Calculate stats
            total_records = len(my_attendance)
            present_count = len(my_attendance[my_attendance["status"].str.lower() == "present"])
            absent_count = len(my_attendance[my_attendance["status"].str.lower() == "absent"])
            
            # Display summary cards
            st.markdown(f"""
            <div class="attendance-summary">
                <div class="attendance-card present-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Days Present</div>
                    <div style="font-size: 2.5rem; margin-top: 0.5rem;">{present_count}</div>
                </div>
                <div class="attendance-card absent-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Days Absent</div>
                    <div style="font-size: 2.5rem; margin-top: 0.5rem;">{absent_count}</div>
                </div>
                <div class="attendance-card total-card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Total Records</div>
                    <div style="font-size: 2.5rem; margin-top: 0.5rem;">{total_records}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**📋 Your Attendance History:**")
            st.dataframe(my_attendance_display, use_container_width=True, hide_index=True)

# =====================================================
# STAFF - MY PAYROLL
# =====================================================

elif menu == "My Payroll":
    st.markdown('<div class="main-header">💰 My Payroll</div>', unsafe_allow_html=True)
    
    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)
    
    # Get current logged-in employee's ID
    current_emp_id = st.session_state.get("employee_id", "")
    
    # Get employee details
    emp_details = df_emp[df_emp["employee_id"].astype(str) == str(current_emp_id)]
    
    if emp_details.empty:
        st.warning("⚠️ Employee record not found.")
        st.stop()
    
    emp_name = emp_details.iloc[0]["full_name"]
    
    st.markdown(f"**👤 Employee:** {emp_name}")
    st.markdown(f"**🆔 Employee ID:** {current_emp_id}")
    
    st.markdown("---")
    
    if df_att.empty:
        st.warning("⚠️ No attendance data available.")
        st.stop()
    
    # Get available months
    month_list = sorted(df_att["date"].str[:7].unique(), reverse=True)
    
    if not month_list:
        st.warning("⚠️ No attendance records found.")
        st.stop()
    
    selected_month = st.selectbox("Select Month", month_list)
    
    # Filter attendance for current employee and selected month
    df_month = df_att[
        (df_att["date"].str.startswith(selected_month)) &
        (df_att["employee_id"] == current_emp_id)
    ]
    
    # Calculate payroll
    present_days = len(df_month[df_month["status"].str.lower() == "present"])
    
    emp_rec = emp_details.iloc[0]
    daily_basic = float(emp_rec.get("daily_rate_basic", 0))
    daily_transport = float(emp_rec.get("daily_rate_transport", 0))
    allowance_monthly = float(emp_rec.get("allowance_monthly", 0))
    
    salary_from_attendance = present_days * (daily_basic + daily_transport)
    total_salary = salary_from_attendance + allowance_monthly
    
    # Display payroll details
    st.markdown('<div class="section-header">💼 Payroll Summary</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Month:** {selected_month}")
        st.write(f"**Days Present:** {present_days}")
        st.write(f"**Daily Basic Rate:** {daily_basic:,.2f}")
        st.write(f"**Daily Transport Rate:** {daily_transport:,.2f}")
    
    with col2:
        st.write(f"**Monthly Allowance:** {allowance_monthly:,.2f}")
        st.write(f"**Bank Account:** {emp_rec.get('bank_account_number', 'N/A')}")
        st.write("")
    
    st.markdown("---")
    
    # Calculate and display salary breakdown
    st.markdown('<div class="section-header">📊 Salary Breakdown</div>', unsafe_allow_html=True)
    
    breakdown_data = {
        "Component": ["Attendance Salary", "Monthly Allowance", "Total Salary"],
        "Amount": [f"{salary_from_attendance:,.2f}", f"{allowance_monthly:,.2f}", f"{total_salary:,.2f}"]
    }
    
    breakdown_df = pd.DataFrame(breakdown_data)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💵 Attendance Salary", f"{salary_from_attendance:,.2f}")
    
    with col2:
        st.metric("💰 Total Allowance", f"{allowance_monthly:,.2f}")
    
    with col3:
        st.metric("💳 Total Salary", f"{total_salary:,.2f}")
