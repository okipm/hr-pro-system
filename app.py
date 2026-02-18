# =====================================================
# PAYROLL (UPDATED WITH MEAL ALLOWANCE)
# =====================================================

elif menu == "Payroll":
    st.markdown('<div class="main-header">💰 Payroll Management</div>', unsafe_allow_html=True)

    df_emp = load_sheet(employees_ws)
    df_att = load_sheet(attendance_ws)

    if df_att.empty or df_emp.empty:
        st.warning("⚠️ Employee or attendance data not available.")
        st.stop()

    # -----------------------------
    # SAFE FLOAT FUNCTION
    # -----------------------------
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

    # -----------------------------
    # MONTH SELECTION
    # -----------------------------
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        month_list = sorted(df_att["date"].astype(str).str[:7].unique(), reverse=True)
        selected_month = st.selectbox("Select Month", month_list)

    with col3:
        edit_mode = st.toggle("✏️ Edit Mode")

    # Filter attendance by month
    df_month = df_att[df_att["date"].astype(str).str.startswith(selected_month)]

    # -----------------------------
    # BUILD PAYROLL DATA
    # -----------------------------
    payroll = []

    for _, emp in df_emp.iterrows():

        present_days = len(
            df_month[
                (df_month["employee_id"].astype(str) == str(emp["employee_id"])) &
                (df_month["status"].str.lower() == "present")
            ]
        )

        payroll.append({
            "Employee ID": emp["employee_id"],
            "Name": emp["full_name"],
            "Bank Account": str(emp.get("bank_account_number", "")),
            "Present Days": present_days,
            "Daily Basic": safe_float(emp.get("daily_rate_basic")),
            "Daily Transport": safe_float(emp.get("daily_rate_transport")),
            "Meal Allowance / Day": safe_float(emp.get("meal_allowance_daily")),
            "Fixed Allowance": safe_float(emp.get("allowance_monthly")),
            "Overtime": 0.0,
            "Bonus": 0.0
        })

    payroll_df = pd.DataFrame(payroll)

    # -----------------------------
    # EDIT MODE
    # -----------------------------
    if edit_mode:
        st.markdown('<div class="section-header">✏️ Edit Payroll Data</div>', unsafe_allow_html=True)
        edited_df = st.data_editor(
            payroll_df,
            use_container_width=True,
            num_rows="dynamic",
            key="payroll_editor"
        )

        if st.button("💾 Save Changes", use_container_width=True, type="primary"):
            st.success("✅ Payroll changes saved successfully!")
            payroll_df = edited_df.copy()
    else:
        edited_df = payroll_df.copy()

    # -----------------------------
    # CALCULATIONS
    # -----------------------------
    edited_df["Salary From Attendance"] = (
        edited_df["Present Days"] *
        (edited_df["Daily Basic"] + edited_df["Daily Transport"])
    )

    edited_df["Meal Allowance Total"] = (
        edited_df["Present Days"] *
        edited_df["Meal Allowance / Day"]
    )

    edited_df["Total Salary"] = (
        edited_df["Salary From Attendance"] +
        edited_df["Meal Allowance Total"] +
        edited_df["Fixed Allowance"] +
        edited_df["Overtime"] +
        edited_df["Bonus"]
    )

    # -----------------------------
    # DISPLAY
    # -----------------------------
    st.markdown("---")
    st.markdown('<div class="section-header">💼 Payroll Summary</div>', unsafe_allow_html=True)

    st.dataframe(edited_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # -----------------------------
    # SUMMARY METRICS
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Total Payroll", f"{edited_df['Total Salary'].sum():,.2f}")

    with col2:
        st.metric("📊 Avg Salary", f"{edited_df['Total Salary'].mean():,.2f}")

    with col3:
        st.metric("👥 Employee Count", len(edited_df))

    with col4:
        st.metric("📅 Month", selected_month)

    # -----------------------------
    # EXPORT EXCEL
    # -----------------------------
    try:
        output = BytesIO()
        export_df = edited_df.copy()
        export_df["Bank Account"] = export_df["Bank Account"].astype(str)

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Payroll")

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
