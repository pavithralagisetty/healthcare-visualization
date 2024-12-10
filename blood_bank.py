import streamlit as st
import pandas as pd
import database as db
from datetime import datetime

class BloodBank:
    def add_blood_bank(self):
        st.subheader("Add New Blood Bank")
        
        col1, col2 = st.columns(2)
        with col1:
            bank_name = st.text_input("Blood Bank Name")
            address = st.text_area("Address")
            city = st.text_input("City")
            
        with col2:
            contact_number = st.text_input("Contact Number")
            email = st.text_input("Email")
            license_number = st.text_input("License Number")
        
        if st.button("Add Blood Bank"):
            try:
                db.execute_query("""
                    INSERT INTO blood_banks 
                    (bank_name, address, city, contact_number, email, license_number) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (bank_name, address, city, contact_number, email, license_number))
                st.success("Blood bank added successfully!")
            except Exception as e:
                st.error(f"Error adding blood bank: {str(e)}")

    def view_blood_banks(self):
        try:
            results = db.execute_query("""
                SELECT bank_name, address, city, contact_number, email, license_number 
                FROM blood_banks
                ORDER BY bank_name
            """, fetch=True)
            
            if results:
                df = pd.DataFrame(results, 
                    columns=['Bank Name', 'Address', 'City', 'Contact', 'Email', 'License Number'])
                st.dataframe(df, hide_index=True)
            else:
                st.info("No blood banks registered yet.")
                
        except Exception as e:
            st.error(f"Error viewing blood banks: {str(e)}")

    def update_blood_bank(self):
        st.subheader("Update Blood Bank")
        
        # First, let user select which bank to update
        banks = db.execute_query("SELECT bank_name FROM blood_banks", fetch=True)
        if not banks:
            st.info("No blood banks to update")
            return
            
        bank_names = [bank[0] for bank in banks]
        selected_bank = st.selectbox("Select Blood Bank to Update", bank_names)
        
        if selected_bank:
            col1, col2 = st.columns(2)
            with col1:
                contact_number = st.text_input("New Contact Number")
                email = st.text_input("New Email")
                
            with col2:
                address = st.text_area("New Address")
                city = st.text_input("New City")
            
            if st.button("Update Blood Bank"):
                try:
                    db.execute_query("""
                        UPDATE blood_banks 
                        SET contact_number=?, email=?, address=?, city=?
                        WHERE bank_name=?
                    """, (contact_number, email, address, city, selected_bank))
                    st.success("Blood bank updated successfully!")
                except Exception as e:
                    st.error(f"Error updating blood bank: {str(e)}")

def handle_blood_bank_management(p):
    bank_option = st.selectbox(
        'Select Operation',
        ['Add Blood Bank', 'View Blood Banks', 'Update Blood Bank']
    )
    
    if bank_option == 'Add Blood Bank':
        p.add_blood_bank()
    elif bank_option == 'View Blood Banks':
        p.view_blood_banks()
    elif bank_option == 'Update Blood Bank':
        p.update_blood_bank() 