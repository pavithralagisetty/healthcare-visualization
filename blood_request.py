import streamlit as st
import sqlite3 as sql
import pandas as pd
from datetime import datetime

class BloodRequest:
    def __init__(self):
        self.conn = sql.connect('database_1A.db')
        
    def add_request(self):
        # Add CSS for number input label at the start of the method
        st.markdown("""
            <style>
            /* Make number input label black */
            .stNumberInput label {
                color: #000000 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.subheader("Submit New Blood Request")
        
        # Form inputs in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Name")
            blood_group = st.selectbox(
                "Blood Group Required",
                ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            )
            units_required = st.number_input("Units Required", min_value=1, value=1)
            hospital_name = st.text_input("Hospital Name")
        
        with col2:
            urgency = st.selectbox(
                "Urgency Level",
                ['Critical', 'High', 'Medium', 'Low']
            )
            contact_number = st.text_input("Contact Number")
            required_by = st.date_input("Required By Date")
            
        if st.button("Submit Request", type="primary"):
            if patient_name and contact_number and hospital_name:
                try:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        INSERT INTO blood_requests 
                        (patient_name, blood_group, units_required, urgency,
                         hospital_name, contact_number, request_date, required_by, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (patient_name, blood_group, units_required, urgency,
                          hospital_name, contact_number, datetime.now().date(), 
                          required_by, 'Pending'))
                    self.conn.commit()
                    st.success("Blood request submitted successfully!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error submitting request: {e}")
            else:
                st.warning("Please fill in all required fields.")

    def view_requests(self):
        st.subheader("View Blood Requests")
        
        # Filter options
        status_filter = st.selectbox(
            "Filter by Status",
            ['All', 'Pending', 'Approved', 'Completed', 'Cancelled']
        )
        
        try:
            query = """
                SELECT 
                    request_id,
                    patient_name,
                    blood_group,
                    units_required,
                    urgency,
                    hospital_name,
                    contact_number,
                    request_date,
                    required_by,
                    status
                FROM blood_requests
            """
            if status_filter != 'All':
                query += f" WHERE status = '{status_filter}'"
            query += " ORDER BY request_date DESC"
            
            df = pd.read_sql_query(query, self.conn)
            
            if not df.empty:
                st.dataframe(df)
            else:
                st.info("No blood requests found.")
                
        except Exception as e:
            st.error(f"Error fetching requests: {e}")

    def update_request_status(self):
        st.subheader("Update Request Status")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT request_id, patient_name, blood_group, status, hospital_name 
                FROM blood_requests
            """)
            requests = cursor.fetchall()
            
            if requests:
                request_options = [
                    f"ID: {r[0]} - {r[1]} ({r[2]}) - {r[4]} - Current Status: {r[3]}" 
                    for r in requests
                ]
                selected_request = st.selectbox("Select Request to Update", request_options)
                
                if selected_request:
                    request_id = int(selected_request.split('-')[0].replace('ID:', '').strip())
                    new_status = st.selectbox(
                        "New Status",
                        ['Pending', 'Approved', 'Completed', 'Cancelled']
                    )
                    
                    if st.button("Update Status"):
                        cursor.execute('''
                            UPDATE blood_requests 
                            SET status = ? 
                            WHERE request_id = ?
                        ''', (new_status, request_id))
                        self.conn.commit()
                        st.success("Status updated successfully!")
                        st.experimental_rerun()
            else:
                st.info("No requests available to update.")
                
        except Exception as e:
            st.error(f"Error updating status: {e}")

    def __del__(self):
        self.conn.close() 