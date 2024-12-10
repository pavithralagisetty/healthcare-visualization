import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd
import sqlite3 as sql

# function to verify patient id
def verify_donor_id(donor_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM donor_record;
            """
        )
    for id in c.fetchall():
        if id[0] == donor_id:
            verify = True
            break
    conn.close()
    return verify

# function to generate unique patient id 
def generate_donor_id(reg_date, reg_time,):
    id_1 = datetime.now().strftime('%d%m%y')  
    id_2 = str(hash(datetime.now()))[-6:]  # Uses last 6 digits of the hash as a unique identifier
    id = f'P-{id_1}-{id_2}'
    return id

# function to calculate age using given date of birth
def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((dob.month, dob.day) > (today.month, today.day))
    return age

# function to show the details of patient(s) given in a list 
def show_donor_details(list_of_donors):
    donor_attributes = ['Patient ID', 'Name', 'Age', 'Gender', 'Date of birth (DD-MM-YYYY)',
                     'Blood group', 'Contact number',
                     'Verification-ID', 'Address',
                     'City', 'State', 'PIN code',
                     'Date of registration (DD-MM-YYYY)', 'Time of registration (hh:mm:ss)']
    if len(list_of_donors) == 0:
        st.warning('No data to show')
    elif len(list_of_donors) == 1:
        donor_details = [x for x in list_of_donors[0]]
        series = pd.Series(data = donor_details, index = donor_details)
        st.write(series)
    else:
        donor_details = []
        for donor in list_of_donors:
            donor_details.append([x for x in donor])
        df = pd.DataFrame(data = donor_details, columns = donor_details)
        st.write(df)

# class containing all the fields and methods required to work with the patients' table in the database
class Donor:

    def __init__(self):
        # Add custom CSS for input and output styling
        st.markdown("""
            <style>
            /* Style for text inputs */
            .stTextInput input, .stTextArea textarea {
                color: white !important;
            }
            
            /* Style for date input */
            .stDateInput input {
                color: white !important;
            }
            
            /* Style for radio buttons */
            .stRadio label {
                color: black !important;
            }
            
            /* Style for selectbox */
            .stSelectbox div[data-baseweb="select"] span {
                color: white !important;
            }
            
            /* Style for number inputs */
            .stNumberInput input {
                color: white !important;
            }

            /* Style for output text */
            .dataframe {
                color: black !important;
            }
            
            /* Style for success/info messages */
            .stSuccess, .stInfo {
                color: black !important;
            }
            
            /* Style for verification messages */
            .element-container div {
                color: black !important;
            }
            
            /* Style for displayed data */
            .stMarkdown p {
                color: black !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        self.name = str()
        self.id = str()
        self.gender = str()
        self.age = int()
        self.contact_number_1 = str()
        self.date_of_birth = str()
        self.blood_group = str()
        self.date_of_registration = str()
        self.time_of_registration = str()
        self.verification_id = str()
        self.address = str()
        self.city = str()
        self.state = str()
        self.pin_code = str()

    # method to add a new donor record to the database
    def add_donor(self):
        st.write('Enter details of the Donor:')
        self.name = st.text_input('Full name')
        gender = st.radio('Gender', ['Female', 'Male', 'Other'])
        if gender == 'Other':
            gender = st.text_input('Please mention')
        self.gender = gender
        dob = st.date_input(
            "Date of Birth (YYYY/MM/DD)",
            min_value=datetime(1950, 1, 1),  # Set minimum date to January 1, 1950
            max_value=datetime.now(),        # Set maximum date to current date
            value=datetime.now(),            # Default value
            format="YYYY/MM/DD"
        )
        self.date_of_birth = dob.strftime('%d-%m-%Y')       # converts DOB to the string format
        self.age = calculate_age(dob)
        self.blood_group = st.text_input('Blood group')
        self.contact_number_1 = st.text_input('Contact number')
        self.id = st.text_input('Verification-ID')
        self.address = st.text_area('Address')
        self.city = st.text_input('City')
        self.state = st.text_input('State')
        self.pin_code = st.text_input('PIN code')
        self.date_of_registration = datetime.now().strftime('%d-%m-%Y')
        self.time_of_registration = datetime.now().strftime('%H:%M:%S')
        self.verification_id = generate_donor_id(self.date_of_registration,
                    self.time_of_registration)
        save = st.button('Save')

        # executing SQLite statements to save the new patient record to the database
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO donor_record
                    (
                        id, name, age, gender, date_of_birth, blood_group,
                        contact_number_1, verification_id, address,city, state, pin_code,
                        date_of_registration, time_of_registration
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :blood_group,
                        :phone_1, :uid,
                        :address, :city, :state, :pin,
                        :reg_date, :reg_time
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'blood_group': self.blood_group,
                        'phone_1': self.contact_number_1,
                        'uid': self.verification_id, 'address': self.address,
                        'city': self.city, 'state': self.state,
                        'pin': self.pin_code,
                        'reg_date': self.date_of_registration,
                        'reg_time': self.time_of_registration
                    }
                )
            st.success('Donor details saved successfully!')
            st.write('Your Donor ID is: ', self.id)
            conn.close()

    # method to update an existing patient record in the database
    def update_donor(self):
        id = st.text_input('Enter ID of the Donor to be updated')
        if id == '':
            st.empty()
        elif not verify_donor_id(id):
            st.error('Invalid Donor ID!')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the patient before updating
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM donor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the current details of the donor:')
                show_donor_details(c.fetchall())

            st.write('Enter new details of the donor:')
            self.contact_number_1 = st.text_input('Contact number')
            self.address = st.text_area('Address')
            self.city = st.text_input('City')
            self.state = st.text_input('State')
            self.pin_code = st.text_input('PIN code')
            update = st.button('Update')

            # executing SQLite statements to update this patient's record in the database
            if update:
                with conn:
                    c.execute(
                        """
                        SELECT date_of_birth
                        FROM donor_record
                        WHERE id = :id;
                        """,
                        { 'id': id }
                    )

                    # converts date of birth to the required format for age calculation
                    dob = [int(d) for d in c.fetchone()[0].split('-')[::-1]]
                    dob = date(dob[0], dob[1], dob[2])
                    self.age = calculate_age(dob)

                with conn:
                    c.execute(
                        """
                        UPDATE donor_record
                        SET age = :age, contact_number_1 = :phone_1,
                        address = :address, city = :city,
                        state = :state, pin_code = :pin
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'age': self.age,
                            'phone_1': self.contact_number_1,
                            'address': self.address, 'city': self.city,
                            'state': self.state, 'pin': self.pin_code,
                        }
                    )
                st.success('Donor details updated successfully.')
                conn.close()

    # method to delete an existing patient record from the database
    def delete_donor(self):
        id = st.text_input('Enter ID of the donor to be deleted')
        if id == '':
            st.empty()
        elif not verify_donor_id(id):
            st.error('Invalid Donor ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the patient before deletion
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM donor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the donor to be deleted:')
                show_donor_details(c.fetchall())

                confirm = st.checkbox('**Check this box to confirm deletion**')
                if confirm:
                    delete = st.button('Delete')

                    # executing SQLite statements to delete this patient's record from the database
                    if delete:
                        c.execute(
                            """
                            DELETE FROM donor_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Donor details deleted successfully.')
            conn.close()

    # method to show the complete patient record
    def show_all_donors(self):
        conn, c = db.connection()
        
        try:
            c.execute("SELECT * FROM donor_record")
            donors = c.fetchall()
            
            if donors:
                df = pd.DataFrame(donors, columns=['ID', 'Name', 'Age', 'Gender', 'Date_of_Birth', 
                                                 'Blood_Group', 'Contact_Number_1', 'Verification_ID', 
                                                 'Address', 'City', 'State', 'PIN_Code', 
                                                 'Date_of_Registration', 'Time_of_Registration'])
                st.dataframe(df)
            else:
                st.info("No donors found in the database.")
                
        except Exception as e:
            st.error(f"Error retrieving donors: {e}")
        finally:
            conn.close()

    # method to search and show a particular patient's details in the database using patient id
    def search_donor(self):
        id = st.text_input('Enter ID of the donor to be searched')
        if id == '':
            st.empty()
        elif not verify_donor_id(id):
            st.error('Invalid Donor ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM donor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the donor you searched for:')
                show_donor_details(c.fetchall())
            conn.close()

    def find_nearby_donors(self, city, blood_group):
        conn = sql.connect('database_1A.db')
        c = conn.cursor()
        
        try:
            # Query to fetch donors based on city and blood group
            query = """
            SELECT id, name, blood_group, contact_number_1, address 
            FROM donor_record 
            WHERE LOWER(city) = LOWER(?) 
            AND blood_group = ?
            """
            
            c.execute(query, (city, blood_group))
            donors = c.fetchall()
            
            if donors:
                df = pd.DataFrame(donors, columns=['ID', 'Name', 'Blood Group', 'Contact', 'Address'])
                st.dataframe(df, hide_index=True)
                st.success(f"Found {len(donors)} donor(s) in {city} with blood group {blood_group}")
            else:
                st.info(f"No donors found in {city} with blood group {blood_group}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            conn.close()
