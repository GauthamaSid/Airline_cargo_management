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
def show_admin_dashboard():

    st.header("Admin Dashboard")
    
    # Create tabs for better organization
    tabs = st.tabs(["Users", "Cargo", "Flights"])
    
    conn = get_database_connection()
    
    # Users Tab
    with tabs[0]:
        st.subheader("User Management")
        
        # Show all users with cargo count
        users_df = pd.read_sql("""
            SELECT
                u.username as Username,
                u.email as Email,
                r.role_name as Role,
                u.created_at as 'Created At',
                (
                    SELECT COUNT(*) 
                    FROM Cargo c
                    WHERE c.customer_id = u.user_id
                ) AS 'Cargo Count'
            FROM Users u
            JOIN UserRole ur ON u.user_id = ur.user_id
            JOIN Role r ON ur.role_id = r.role_id
        """, conn)
        display_dataframe(users_df)
        
        # Create new user in an expander
        with st.expander("➕ Create New User"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["admin", "cargo_handler", "customer"])

            if st.button("Create User", type="primary"):
                cursor = conn.cursor()
                try:
                    user_id = str(uuid.uuid4())
                    role_id = pd.read_sql(
                        f"SELECT role_id FROM Role WHERE role_name = '{role}'", 
                        conn
                    ).iloc[0]['role_id']

                    cursor.execute("""
                        INSERT INTO Users (user_id, username, password, email)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, username, password, email))

                    cursor.execute("""
                        INSERT INTO UserRole (user_role_id, user_id, role_id)
                        VALUES (%s, %s, %s)
                    """, (str(uuid.uuid4()), user_id, role_id))

                    conn.commit()
                    st.success("User created successfully!")
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error creating user: {e}")
                finally:
                    cursor.close()

    # Cargo Tab
    with tabs[1]:
        st.subheader("Cargo Overview")
        
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
        
        # Add cargo statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cargo Count", len(cargo_df))
        with col2:
            st.metric("Total Weight", f"{cargo_df['Weight'].sum():.2f} kg")
        with col3:
            st.metric("Total Value", f"${cargo_df['Price'].sum():.2f}")

    # Flights Tab
    with tabs[2]:
        st.subheader("Flight Management")
        
        # Show all flights
        flights_df = pd.read_sql("""
            SELECT
                flight_id as 'Flight ID',
                aircraft_id as 'Aircraft ID',
                origin_id as 'Origin Location ID',
                destination_id as 'Destination Location ID',
                departure_time as 'Departure Time',
                arrival_time as 'Arrival Time',
                flight_status as 'Flight Status'
            FROM Flight
        """, conn)
        display_dataframe(flights_df)
        
        # Create and Update flights in separate columns
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Create New Flight"):
                # Fetch available IDs
                aircraft_ids = pd.read_sql(
                    "SELECT aircraft_id FROM Aircraft", 
                    conn
                )['aircraft_id'].tolist()
                origin_ids = pd.read_sql(
                    "SELECT location_id FROM Location", 
                    conn
                )['location_id'].tolist()
                destination_ids = origin_ids

                flight_id = st.text_input("Flight ID")
                aircraft_id = st.selectbox("Aircraft ID", aircraft_ids)
                origin_id = st.selectbox("Origin Location ID", origin_ids)
                destination_id = st.selectbox("Destination Location ID", destination_ids)
                departure_time = st.text_input(
                    "Departure Time",
                    placeholder="YYYY-MM-DD HH:MM:SS"
                )
                arrival_time = st.text_input(
                    "Arrival Time",
                    placeholder="YYYY-MM-DD HH:MM:SS"
                )
                flight_status = st.selectbox(
                    "Flight Status",
                    ["Scheduled", "Delayed", "Cancelled", "Completed"]
                )

                if st.button("Create Flight", type="primary"):
                    if not all([flight_id, aircraft_id, origin_id, destination_id,
                              departure_time, arrival_time, flight_status]):
                        st.error("Please fill in all fields.")
                    else:
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                INSERT INTO Flight (
                                    flight_id, aircraft_id, origin_id,
                                    destination_id, departure_time,
                                    arrival_time, flight_status
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (flight_id, aircraft_id, origin_id,
                                 destination_id, departure_time,
                                 arrival_time, flight_status))
                            conn.commit()
                            st.success("Flight created successfully!")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error creating flight: {e}")
                        finally:
                            cursor.close()

        with col2:
            with st.expander("✏️ Update Flight"):
                flight_to_update = st.selectbox(
                    "Select Flight to Update",
                    flights_df['Flight ID'].tolist()
                )

                if flight_to_update:
                    flight_details = pd.read_sql(
                        f"SELECT * FROM Flight WHERE flight_id = '{flight_to_update}'",
                        conn
                    ).iloc[0]

                    new_departure = st.text_input(
                        "New Departure Time",
                        value=str(flight_details['departure_time']),
                        placeholder="YYYY-MM-DD HH:MM:SS"
                    )
                    new_arrival = st.text_input(
                        "New Arrival Time",
                        value=str(flight_details['arrival_time']),
                        placeholder="YYYY-MM-DD HH:MM:SS"
                    )
                    new_status = st.selectbox(
                        "New Flight Status",
                        ["Scheduled", "Delayed", "Cancelled", "Completed"],
                        index=["Scheduled", "Delayed", "Cancelled", "Completed"].index(
                            flight_details['flight_status']
                        )
                    )

                    if st.button("Update Flight"):
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                UPDATE Flight
                                SET departure_time = %s,
                                    arrival_time = %s,
                                    flight_status = %s
                                WHERE flight_id = %s
                            """, (new_departure, new_arrival,
                                 new_status, flight_to_update))
                            conn.commit()
                            st.success("Flight updated successfully!")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error updating flight: {e}")
                        finally:
                            cursor.close()

    conn.close()
    
    # Admin Dashboard Metrics

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
import numpy as np
from matplotlib.patches import Rectangle

def show_admin_dashboard_metrics():
    conn = get_database_connection()
    cursor = conn.cursor()

    # Total Users
    cursor.execute("SELECT COUNT(*) FROM Users")
    total_users = cursor.fetchone()[0]

    # Users by Role
    cursor.execute("""
        SELECT r.role_name, COUNT(*)
        FROM Users u
        JOIN UserRole ur ON u.user_id = ur.user_id
        JOIN Role r ON ur.role_id = r.role_id
        GROUP BY r.role_name
    """)
    role_counts = cursor.fetchall()
    role_data = pd.DataFrame(role_counts, columns=['Role', 'Count'])

    # Total Cargo Shipments
    cursor.execute("SELECT COUNT(*) FROM Cargo")
    total_cargo = cursor.fetchone()[0]

    # Pending Cargo Shipments
    cursor.execute("SELECT COUNT(*) FROM Cargo WHERE status_id = 'CS1'")
    pending_cargo = cursor.fetchone()[0]

    # Upcoming Flights
    cursor.execute("SELECT COUNT(*) FROM Flight WHERE departure_time > NOW()")
    upcoming_flights = cursor.fetchone()[0]

    # Total Revenue from Cargo (Assuming `calculated_price` is stored in Cargo table)
    cursor.execute("SELECT COALESCE(SUM(calculated_price), 0) FROM Cargo")
    total_revenue = cursor.fetchone()[0]

    # Display Metrics
    st.subheader("Admin Dashboard Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Users", total_users)
        st.metric("Total Cargo Shipments", total_cargo)
        st.metric("Pending Cargo Shipments", pending_cargo)

    with col2:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
        st.metric("Upcoming Flights", upcoming_flights)

    with col3:
        st.write("Users by Role")
        fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
        fig.set_facecolor('#f1efe7')
        ax.set_facecolor('#f1efe7')

        # set the colors for each range
        colors = ['#d97857', '#ffa366', '#ffff99', '#99ff99']
        color_thresholds = [1, 25, 50, 75]

        # Plot the bars
        bars = ax.bar(
            role_data['Role'],
            role_data['Count'],
            color=[colors[c] for c in np.digitize(role_data['Count'], color_thresholds) - 1]
        )

        # Loop through the bars and fix the index issue
        for idx, bar in enumerate(bars):  # Use idx instead of 'i'
            # Add text on top of bars
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, role_data['Count'][idx],  # Use idx here
                    ha='center', va='bottom', color='white', weight='bold', fontsize=12)

            # Create a rounded rectangle to replace the bar's top
            bar.set_height(bar.get_height() * 0.9)  # Reduce the bar height slightly for a rounded effect
            ax.add_patch(Rectangle(
                (bar.get_x(), bar.get_height()), bar.get_width(), bar.get_height(),
                color=bar.get_facecolor(), zorder=2, clip_on=False,
                linewidth=0, edgecolor="none", linestyle="solid",
                facecolor=bar.get_facecolor(), alpha=1
            ))

        # Hide the spines and ticks
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='x', colors='black')
        ax.tick_params(axis='y', colors='black')

        st.pyplot(fig)

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

    # Calculate total cargo weight and total cost for this customer
    st.subheader("Cargo Summary")
    cargo_summary_df = pd.read_sql("""
        SELECT 
            COALESCE(SUM(c.weight), 0) AS 'Total Weight (kg)',
            COALESCE(SUM(c.calculated_price), 0) AS 'Total Cost'
        FROM Cargo c
        WHERE c.customer_id = %s
    """, conn, params=(st.session_state.user['user_id'],))

    # Display total weight and cost results
    if not cargo_summary_df.empty:
        total_weight = cargo_summary_df.iloc[0]['Total Weight (kg)']
        total_cost = cargo_summary_df.iloc[0]['Total Cost']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Cargo Weight", f"{total_weight:.2f} kg")
        with col2:
            st.metric("Total Cargo Cost", f"${total_cost:.2f}")

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
            show_admin_dashboard_metrics()
            show_admin_dashboard()
            
        elif role == 'cargo_handler':
            show_handler_dashboard()
        elif role == 'customer':
            show_customer_dashboard()

if __name__ == "__main__":
    main()