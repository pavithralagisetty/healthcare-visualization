import streamlit as st
import database as db
from donor import Donor
from department import Department
from doctor import Doctor
from prescription import Prescription
from medical_test import Medical_Test
from blood_bank import BloodBank
from blood_request import BloodRequest
import sqlite3 as sql

def create_button_with_description(icon, title, description, key, color="#ff4b4b"):
    st.markdown(f"""
        <style>
        .button-{key} {{
            background-color: white;
            border: 2px solid {color};
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        .button-{key}:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
            background: linear-gradient(45deg, {color}15, white);
        }}
        .button-{key}:hover .button-icon-{key} {{
            transform: scale(1.1);
        }}
        .button-icon-{key} {{
            font-size: 2.5em;
            margin-bottom: 10px;
            color: {color};
            transition: transform 0.3s ease;
        }}
        .button-title-{key} {{
            font-size: 1.3em;
            font-weight: 600;
            color: #000000;
            margin-bottom: 8px;
        }}
        .button-desc-{key} {{
            font-size: 0.9em;
            color: #000000;
            line-height: 1.4;
        }}
        .button-stats-{key} {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
            font-size: 0.8em;
            color: #666;
        }}
        </style>
        <div class="button-{key}" onclick="document.getElementById('{key}').click()">
            <div class="button-icon-{key}">{icon}</div>
            <div class="button-title-{key}">{title}</div>
            <div class="button-desc-{key}">{description}</div>
            <div class="button-stats-{key}">
                {get_button_stats(key)}
            </div>
        </div>
    """, unsafe_allow_html=True)
    return st.button("", key=key, help=description)

def get_button_stats(key):
    """Return relevant statistics based on button type"""
    try:
        conn = sql.connect('database_1A.db')
        cursor = conn.cursor()
        
        if key == "donor_btn":
            cursor.execute("SELECT COUNT(*) FROM donors")
            total_donors = cursor.fetchone()[0]
            cursor.execute("SELECT MAX(last_donation_date) FROM donors")
            last_date = cursor.fetchone()[0] or "No donations yet"
            return f"Active Donors: {total_donors} | Last Registration: {last_date}"
            
        elif key == "bank_btn":
            cursor.execute("SELECT COUNT(*) FROM blood_banks")
            total_banks = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(units_required) FROM blood_requests WHERE status='Pending'")
            total_required = cursor.fetchone()[0] or 0
            return f"Active Banks: {total_banks} | Required Units: {total_required}"
            
        elif key == "request_btn":
            cursor.execute("SELECT COUNT(*) FROM blood_requests WHERE status='Pending'")
            pending = cursor.fetchone()[0]
            return f"Pending Requests: {pending}"
            
        elif key == "nearby_btn":
            cursor.execute("SELECT COUNT(DISTINCT city) FROM blood_banks")
            locations = cursor.fetchone()[0]
            return f"Available Locations: {locations}"
            
    except Exception as e:
        return "Error fetching stats"
    finally:
        conn.close()
    
    return ""  # Default return for unhandled keys

def handle_donor_management(p):
    donor_option = st.selectbox(
        'Select Operation',
        ['Register Donor', 'Update Donor Info', 'Delete Donor', 'Show All Donors', 'Search Donor']
    )
    
    if donor_option == 'Register Donor':
        st.subheader('📝 REGISTER NEW DONOR')
        p.add_donor()
    elif donor_option == 'Update Donor Info':
        st.subheader('✏ UPDATE DONOR INFO')
        p.update_donor()
    elif donor_option == 'Delete Donor':
        st.subheader('🗑 DELETE DONOR')
        try:
            p.delete_donor()
        except sql.IntegrityError:
            st.error('This entry cannot be deleted as other records are using it.')
    elif donor_option == 'Show All Donors':
        st.subheader('📋 COMPLETE DONOR RECORD')
        p.show_all_donors()
    elif donor_option == 'Search Donor':
        st.subheader('🔍 SEARCH DONOR')
        p.search_donor()

def handle_nearby_donors(p):
    st.subheader('🔍 FIND NEARBY DONORS')
    
    # Blood group selection
    blood_group = st.selectbox(
        "Select Blood Group",
        ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        key="blood_group_select"
    )
    
    # City input
    city = st.text_input(
        "Enter City",
        placeholder="Boston",
        key="donor_city"
    )
    
    if st.button("Search Donors"):
        if city and blood_group:
            p.find_nearby_donors(city, blood_group)  # Update your Donor class method accordingly
        else:
            st.warning("Please enter both city and blood group to search")

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

def handle_blood_request(p):
    request_option = st.selectbox(
        'Select Operation',
        ['Submit Blood Request', 'View Requests', 'Update Request Status']
    )
    
    if request_option == 'Submit Blood Request':
        p.add_request()
    elif request_option == 'View Requests':
        p.view_requests()
    elif request_option == 'Update Request Status':
        p.update_request_status()

def get_total_donors():
    try:
        conn = sql.connect('database_1A.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM donor_record")
        total = cursor.fetchone()[0]
        return total
    except Exception as e:
        st.error(f"Error fetching donor count: {e}")
        return 0
    finally:
        conn.close()

def get_active_blood_banks():
    try:
        conn = sql.connect('database_1A.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM blood_banks")
        total = cursor.fetchone()[0]
        return total
    except Exception as e:
        st.error(f"Error fetching blood bank count: {e}")
        return 0
    finally:
        conn.close()

def get_active_blood_requests():
    try:
        conn = sql.connect('database_1A.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM blood_requests WHERE status = 'Pending'")
        total = cursor.fetchone()[0]
        return total
    except Exception as e:
        st.error(f"Error fetching blood requests count: {e}")
        return 0
    finally:
        conn.close()

def get_critical_blood_groups():
    try:
        conn = sql.connect('database_1A.db')
        cursor = conn.cursor()
        
        # Get blood groups with pending requests and their required units
        cursor.execute("""
            SELECT blood_group, SUM(units_required) as needed
            FROM blood_requests 
            WHERE status = 'Pending'
            GROUP BY blood_group
            HAVING needed > 0
            ORDER BY needed DESC
            LIMIT 2
        """)
        
        critical_groups = cursor.fetchall()
        if critical_groups:
            # Format blood groups for display
            critical_text = ", ".join([group[0] for group in critical_groups])
            return critical_text
        return "None"
        
    except Exception as e:
        return "Error"
    finally:
        conn.close()

def home():
    db.db_init()

    # Page configuration
    st.set_page_config(
        page_title="Blood Bank Management System",
        page_icon="🩸",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to bottom right, #f5f5f5, #e6e6e6);
        }
        .main-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(to right, #ff4b4b, #ff8080);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .dashboard-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .button-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .button-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            background-color: #f8f8f8;
        }
        .button-icon {
            font-size: 2em;
            margin-right: 20px;
            color: #ff4b4b;
        }
        .button-content h3 {
            margin: 0;
            color: #000000;
            font-size: 1.2em;
            font-weight: 600;
        }
        .button-content p {
            margin: 5px 0 0 0;
            color: #000000;
            font-size: 0.9em;
        }
        .stats-card {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .stats-card h3 {
            color: #000000;
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 10px;
        }
        .stats-card h2 {
            color: #000000;
            font-size: 2em;
            margin: 10px 0;
        }
        .stats-card p {
            color: #000000;
            margin-bottom: 0;
            font-size: 0.9em;
        }
        .dashboard-card {
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            padding: 10px;
        }
        .footer {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-top: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            color: #000000;
        }
        /* Additional styles for Streamlit elements */
        .stSelectbox label {
            color: #000000 !important;
        }
        .stMarkdown {
            color: #000000;
        }
        /* Make all text inputs and labels black */
        .stTextInput label, .stTextInput input {
            color: #000000 !important;
        }
        /* Make all selectbox text black */
        .stSelectbox select {
            color: #000000 !important;
        }
        /* Make all headers and subheaders black */
        h1, h2, h3, h4, h5, h6, .stMarkdown, .streamlit-expanderHeader {
            color: #000000 !important;
        }
        
        /* Make subheader text black */
        .css-10trblm {
            color: #000000 !important;
        }
        /* Make all date input labels black */
        .stDateInput label {
            color: #000000 !important;
        }
        /* Make selectbox label and options black */
        .stSelectbox label, .stSelectbox select, .stSelectbox div[data-baseweb="select"] span {
            color: #000000 !important;
        }
        
        /* Make dropdown options black */
        div[data-baseweb="select"] ul li {
            color: #000000 !important;
        }
        
        /* Make selected option black */
        div[data-baseweb="select"] div div div {
            color: #000000 !important;
        }
        /* Make radio button labels black */
        .stRadio label, .stRadio div {
            color: #000000 !important;
        }
        
        /* Make radio button text black */
        .stRadio label span {
            color: #000000 !important;
        }
        /* Make text area labels and input black */
        .stTextArea label, .stTextArea textarea {
            color: #000000 !important;
        }
        
        /* Make text input labels and text black */
        .stTextInput label, .stTextInput input {
            color: #000000 !important;
        }
        /* Make input backgrounds white and text black */
        .stTextInput input, .stTextArea textarea {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        /* Style for radio buttons */
        .stRadio div[role="radiogroup"] {
            background-color: transparent !important;
        }
        
        /* Style for date input */
        .stDateInput div[data-baseweb="input"] {
            background-color: #FFFFFF !important;
        }
        /* Make all input backgrounds white */
        .stTextInput input, 
        .stTextArea textarea, 
        .stDateInput input,
        .stSelectbox select,
        div[data-baseweb="select"] div,
        div[data-baseweb="input"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        /* Style for selectbox dropdown */
        div[data-baseweb="select"] ul {
            background-color: #FFFFFF !important;
        }
        
        /* Style for date picker */
        div[data-baseweb="input"] {
            background-color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main Header
    st.markdown('<div class="main-header"><h1>🩸 BLOOD BANK MANAGEMENT SYSTEM</h1></div>', unsafe_allow_html=True)

    # Dashboard Overview
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    # Dashboard Cards
    with col1:
        total_donors = get_total_donors()
        st.markdown(f"""
            <div class="stats-card">
                <h3>👥 Total Donors</h3>
                <h2>{total_donors}</h2>
                <p>Registered donors</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_banks = get_active_blood_banks()
        st.markdown(f"""
            <div class="stats-card">
                <h3>🏥 Active Banks</h3>
                <h2>{str(active_banks)}</h2>
                <p>Registered blood banks</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending_requests = get_active_blood_requests()
        st.markdown(f"""
            <div class="stats-card">
                <h3>📋 Blood Requests</h3>
                <h2>{str(pending_requests)}</h2>
                <p>Active requests pending</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        critical_groups = get_critical_blood_groups()
        st.markdown(f"""
            <div class="stats-card">
                <h3>⚠ Critical Need</h3>
                <h2>{critical_groups}</h2>
                <p>Urgent requirement</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Main Navigation Buttons with enhanced layout
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px; color: #000000;'>  </h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if create_button_with_description("👥", "Donor Management", 
            "Register new donors, update information, and manage donor records", "donor_btn"):
            st.session_state.active_section = "donors"
            
    with col2:
        if create_button_with_description("🏥", "Blood Bank Management", 
            "Manage blood inventory and track available blood units", "bank_btn"):
            st.session_state.active_section = "banks"

    with col1:
        if create_button_with_description("📍", "Find Nearby Donors", 
            "Locate and contact nearby blood donors", "nearby_btn"):
            st.session_state.active_section = "nearby"

    with col2:
        if create_button_with_description("🩸", "Blood Requests", 
            "Submit and manage blood requests", "request_btn"):
            st.session_state.active_section = "requests"

    # Initialize session state if not exists
    if 'active_section' not in st.session_state:
        st.session_state.active_section = None

    # Display selected content based on button clicks
    if st.session_state.active_section == "donors":
        st.markdown("---")
        st.subheader("🩸 Donor Management")
        p = Donor()
        handle_donor_management(p)
        
    elif st.session_state.active_section == "banks":
        st.markdown("---")
        st.subheader("🏥 Blood Bank Management")
        p = BloodBank()
        handle_blood_bank_management(p)

    elif st.session_state.active_section == "nearby":
        st.markdown("---")
        st.subheader("📍 Find Nearby Donors")
        p = Donor()
        handle_nearby_donors(p)

    elif st.session_state.active_section == "requests":
        st.markdown("---")
        st.subheader("🩸 Blood Request Management")
        p = BloodRequest()
        handle_blood_request(p)

    # Footer
    st.markdown("""
        <div class="footer">
            <h3 style="color: #000000;">🚨 Emergency Contact</h3>
            <p>Helpline: 0000000000</p>
            <p>© Blood Bank Management System</p>
        </div>
    """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    home()
