import streamlit as st
import database as db
from patient import Patient
from department import Department
from doctor import Doctor
from prescription import Prescription
from medical_test import Medical_Test
import config
import sqlite3 as sql

# function to verify edit mode password
def verify_edit_mode_password():
    edit_mode_password = st.sidebar.text_input('Enter edit mode password', type = 'password')
    if edit_mode_password == config.edit_mode_password:
        st.sidebar.success('Verified')
        return True
    elif edit_mode_password == '':
        st.empty()
    else:
        st.sidebar.error('Invalid edit mode password')
        return False

# function to verify doctor/medical lab scientist access code
def verify_dr_mls_access_code():
    dr_mls_access_code = st.sidebar.text_input('Enter doctor/medical access code', type = 'password')
    if dr_mls_access_code == config.dr_mls_access_code:
        st.sidebar.success('Verified')
        return True
    elif dr_mls_access_code == '':
        st.empty()
    else:
        st.sidebar.error('Invalid access code')
        return False

# function to perform operations of the patient module 
def patients():
    st.header('Donors')
    option_list = ['', 'Add Donor', 'Update Donor', 'Delete Donor', 'Show complete Donors', 'Search Donor']
    option = st.sidebar.selectbox('Select function', option_list)
    p = Patient()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]):
        if option == option_list[1]:
            st.subheader('ADD DONOR')
            p.add_patient()
        elif option == option_list[2]:
            st.subheader('UPDATE DONOR')
            p.update_patient()
        elif option == option_list[3]:
            st.subheader('DELETE DONOR')
            try:
                p.delete_patient()
            except sql.IntegrityError:      # foreign key constraint failure issue fix (integrity error)
                st.error('This entry cannot be deleted as other records are using it.')
    elif option == option_list[4]:
        st.subheader('COMPLETE DONOR RECORD')
        p.show_all_patients()
    elif option == option_list[5]:
        st.subheader('SEARCH DONOR')
        p.search_patient()

# function to perform operations of the doctor module 
def doctors():
    st.header('BLOOD BANKS')
    option_list = ['', 'Add doctor', 'Update doctor', 'Delete doctor', 'Show complete doctor record', 'Search doctor']
    option = st.sidebar.selectbox('Select function', option_list)
    dr = Doctor()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]) and verify_edit_mode_password():
        if option == option_list[1]:
            st.subheader('ADD DOCTOR')
            dr.add_doctor()
        elif option == option_list[2]:
            st.subheader('UPDATE DOCTOR')
            dr.update_doctor()
        elif option == option_list[3]:
            st.subheader('DELETE DOCTOR')
            try:
                dr.delete_doctor()
            except sql.IntegrityError:      # foreign key constraint failure issue fix (integrity error)
                st.error('This entry cannot be deleted as other records are using it.')
    elif option == option_list[4]:
        st.subheader('COMPLETE DOCTOR RECORD')
        dr.show_all_doctors()
    elif option == option_list[5]:
        st.subheader('SEARCH DOCTOR')
        dr.search_doctor()


