import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import uuid

# Set page configuration for wider layout
st.set_page_config(layout="wide")

# Database connection configuration
def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="cargo_admin",
        password="admin_password",
        database="cargo_db"
    )

# Helper function to format dataframes
def display_dataframe(df, height=400):
    st.dataframe(
        df,
        hide_index=True,
        height=height,
        use_container_width=True,
        column_config={
            "calculated_price": st.column_config.NumberColumn(
                "Price",
                format="$%.2f"
            ),
            "weight": st.column_config.NumberColumn(
                "Weight (kg)",
                format="%.2f"
            ),
            "created_at": st.column_config.DatetimeColumn(
                "Created At",
                format="DD/MM/YYYY HH:mm"
            ),
            "departure_time": st.column_config.DatetimeColumn(
                "Departure",
                format="DD/MM/YYYY HH:mm"
            ),
            "arrival_time": st.column_config.DatetimeColumn(
                "Arrival",
                format="DD/MM/YYYY HH:mm"
            )
        }
    )

# Authentication
def authenticate(username, password):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT u.user_id, u.username, r.role_name 
        FROM Users u
        JOIN UserRole ur ON u.user_id = ur.user_id
        JOIN Role r ON ur.role_id = r.role_id
        WHERE u.username = %s AND u.password = %s
    """, (username, password))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Admin Dashboard
def show_admin_dashboard():
    st.header("Admin Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Show all users
        st.subheader("Users")
        conn = get_database_connection()
        users_df = pd.read_sql("""
            SELECT 
                u.username as Username,
                u.email as Email,
                r.role_name as Role,
                u.created_at as 'Created At'
            FROM Users u
            JOIN UserRole ur ON u.user_id = ur.user_id
            JOIN Role r ON ur.role_id = r.role_id
        """, conn)
        display_dataframe(users_df)
    
    with col2:
        # Show all cargo
        st.subheader("All Cargo")
        cargo_df = pd.read_sql("""
            SELECT 
                c.cargo_id as 'Cargo ID',
                u.username as Customer,
                ct.type_name as 'Cargo Type',
                cs.status_name as Status,
                c.weight as Weight,
                c.calculated_price as Price,
                f.flight_id as 'Flight ID'
            FROM Cargo c
            JOIN Users u ON c.customer_id = u.user_id
            JOIN CargoType ct ON c.cargo_type_id = ct.cargo_type_id
            JOIN CargoStatus cs ON c.status_id = cs.status_id
            JOIN Flight f ON c.flight_id = f.flight_id
        """, conn)
        display_dataframe(cargo_df)
    conn.close()

# Cargo Handler Dashboard
def show_handler_dashboard():
    st.header("Cargo Handler Dashboard")
    
    conn = get_database_connection()
    
    # Show pending cargo
    st.subheader("Pending Cargo")
    pending_cargo_df = pd.read_sql("""
        SELECT 
            c.cargo_id as 'Cargo ID',
            ct.type_name as 'Cargo Type',
            c.weight as Weight,
            l_orig.airport_code as Origin,
            l_dest.airport_code as Destination,
            f.flight_id as 'Flight ID',
            f.departure_time as Departure
        FROM Cargo c
        JOIN CargoType ct ON c.cargo_type_id = ct.cargo_type_id
        JOIN Location l_orig ON c.origin_id = l_orig.location_id
        JOIN Location l_dest ON c.destination_id = l_dest.location_id
        JOIN Flight f ON c.flight_id = f.flight_id
        WHERE c.status_id = 'CS1'
        ORDER BY f.departure_time
    """, conn)
    display_dataframe(pending_cargo_df)
    
    # Update cargo status
    st.subheader("Update Cargo Status")
    col1, col2 = st.columns(2)
    
    with col1:
        cargo_id = st.selectbox("Select Cargo ID", pending_cargo_df['Cargo ID'].tolist())
        new_status = st.selectbox("Select New Status", ["IN_TRANSIT", "DELIVERED"])
    
    with col2:
        action = st.selectbox("Select Action", ["PICKUP", "LOAD", "UNLOAD", "DELIVER"])
        notes = st.text_area("Notes")
    
    if st.button("Update Status", type="primary"):
        cursor = conn.cursor()
        status_map = {"IN_TRANSIT": "CS2", "DELIVERED": "CS3"}
        action_map = {"PICKUP": "HA1", "LOAD": "HA2", "UNLOAD": "HA3", "DELIVER": "HA4"}
        
        cursor.callproc('UpdateCargoStatus', 
                       (cargo_id, status_map[new_status], 
                        st.session_state.user['user_id'], 
                        action_map[action], notes))
        conn.commit()
        st.success("Cargo status updated successfully!")
        st.rerun()
        cursor.close()
    
    conn.close()

# Customer Dashboard
def show_customer_dashboard():
    st.header("Customer Dashboard")
    
    conn = get_database_connection()
    
    # Show customer's cargo
    st.subheader("Your Cargo Shipments")
    customer_cargo_df = pd.read_sql("""
        SELECT 
            c.cargo_id as 'Cargo ID',
            ct.type_name as 'Cargo Type',
            cs.status_name as Status,
            c.weight as Weight,
            c.calculated_price as Price,
            l_orig.airport_code as Origin,
            l_dest.airport_code as Destination,
            f.flight_id as 'Flight ID',
            f.departure_time as Departure
        FROM Cargo c
        JOIN CargoType ct ON c.cargo_type_id = ct.cargo_type_id
        JOIN CargoStatus cs ON c.status_id = cs.status_id
        JOIN Location l_orig ON c.origin_id = l_orig.location_id
        JOIN Location l_dest ON c.destination_id = l_dest.location_id
        JOIN Flight f ON c.flight_id = f.flight_id
        WHERE c.customer_id = %s
        ORDER BY f.departure_time DESC
    """, conn, params=(st.session_state.user['user_id'],))
    display_dataframe(customer_cargo_df)
    
    # Book new cargo
    st.subheader("Book New Cargo")
    cargo_types = pd.read_sql("SELECT cargo_type_id, type_name FROM CargoType", conn)
    flights = pd.read_sql("""
        SELECT f.flight_id, 
               CONCAT(l_orig.airport_code, ' -> ', l_dest.airport_code, 
                     ' (', DATE_FORMAT(f.departure_time, '%%Y-%%m-%%d %%H:%%i'), ')') as flight_info
        FROM Flight f
        JOIN Location l_orig ON f.origin_id = l_orig.location_id
        JOIN Location l_dest ON f.destination_id = l_dest.location_id
        WHERE f.departure_time > NOW()
        ORDER BY f.departure_time
    """, conn)
    
    col1, col2 = st.columns(2)
    
    with col1:
        cargo_type = st.selectbox("Cargo Type", cargo_types['type_name'])
        weight = st.number_input("Weight (kg)", min_value=0.1, max_value=10000.0, value=100.0)
    
    with col2:
        flight = st.selectbox("Flight", flights['flight_info'])
        st.write("") # Spacing
        st.write("") # Spacing
        book_button = st.button("Book Cargo", type="primary")
    
    if book_button:
        cursor = conn.cursor()
        flight_id = flights.loc[flights['flight_info'] == flight, 'flight_id'].iloc[0]
        cargo_type_id = cargo_types.loc[cargo_types['type_name'] == cargo_type, 'cargo_type_id'].iloc[0]
        
        # Get flight origin and destination
        cursor.execute("""
            SELECT origin_id, destination_id 
            FROM Flight 
            WHERE flight_id = %s
        """, (flight_id,))
        origin_id, destination_id = cursor.fetchone()
        
        cursor.callproc('CreateCargoBooking', 
                       (st.session_state.user['user_id'], 
                        cargo_type_id, flight_id, weight, 
                        origin_id, destination_id))
        conn.commit()
        st.success("Cargo booked successfully!")
        st.rerun()
        cursor.close()
    
    conn.close()

# Main app
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Login section
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("Cargo Management System")
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", type="primary"):
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"Welcome {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    # Show appropriate dashboard based on role
    else:
        st.title("Cargo Management System")
        with st.sidebar:
            st.header(f"Welcome, {st.session_state.user['username']}!")
            st.write(f"Role: {st.session_state.user['role_name'].title()}")
            st.divider()
            if st.button("Logout", type="primary"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()
        
        role = st.session_state.user['role_name']
        if role == 'admin':
            show_admin_dashboard()
        elif role == 'cargo_handler':
            show_handler_dashboard()
        elif role == 'customer':
            show_customer_dashboard()

if __name__ == "__main__":
    main()