import streamlit as st
import mysql.connector
import pandas as pd
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
        with st.expander("➕ Create New Cargo"):
            # Fetch Cargo Types and Flights
            cargo_types = pd.read_sql("SELECT cargo_type_id, type_name FROM CargoType", conn)
            flights = pd.read_sql("""
                SELECT f.flight_id,
                    CONCAT(l_orig.airport_code, ' -> ', l_dest.airport_code,
                            ' (', DATE_FORMAT(f.departure_time, '%Y-%m-%d %H:%i'), ')') as flight_info
                FROM Flight f
                JOIN Location l_orig ON f.origin_id = l_orig.location_id
                JOIN Location l_dest ON f.destination_id = l_dest.location_id
                WHERE f.departure_time > NOW()
                ORDER BY f.departure_time
            """, conn)

            # Cargo creation form
            customer = st.selectbox("Customer", pd.read_sql("SELECT username FROM Users", conn)['username'])
            cargo_type = st.selectbox("Cargo Type", cargo_types['type_name'])
            weight = st.number_input("Weight (kg)", min_value=0.1, max_value=10000.0, value=100.0)
            flight = st.selectbox("Flight", flights['flight_info'])

            # Book cargo button
            if st.button("Create Cargo"):
                cursor = conn.cursor()
                cargo_type_id = cargo_types.loc[cargo_types['type_name'] == cargo_type, 'cargo_type_id'].iloc[0]
                flight_id = flights.loc[flights['flight_info'] == flight, 'flight_id'].iloc[0]

                # Get customer_id
                customer_id = pd.read_sql(f"SELECT user_id FROM Users WHERE username = '{customer}'", conn).iloc[0]['user_id']

                # Insert new cargo record
                try:
                    cursor.execute("""
                        INSERT INTO Cargo (cargo_id, customer_id, cargo_type_id, weight, flight_id, status_id, calculated_price)
                        VALUES (%s, %s, %s, %s, %s, 'CS1', %s)
                    """, (str(uuid.uuid4()), customer_id, cargo_type_id, weight, flight_id, weight * 10))  # Assuming price calculation
                    conn.commit()
                    st.success("Cargo created successfully!")
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error creating cargo: {e}")
                finally:
                    cursor.close()
        with st.expander("✏️ Update Cargo"):
            cargo_id = st.selectbox("Select Cargo ID", cargo_df['Cargo ID'].tolist())

            if cargo_id:
                # Get current cargo details
                cargo_details = pd.read_sql(f"""
                    SELECT c.*, ct.type_name, cs.status_name, f.flight_id
                    FROM Cargo c
                    JOIN CargoType ct ON c.cargo_type_id = ct.cargo_type_id
                    JOIN CargoStatus cs ON c.status_id = cs.status_id
                    JOIN Flight f ON c.flight_id = f.flight_id
                    WHERE c.cargo_id = '{cargo_id}'
                """, conn).iloc[0]

                # Display current cargo details
                st.write(f"Current Cargo: {cargo_id}")
                st.write(f"Cargo Type: {cargo_details['type_name']}")
                st.write(f"Weight: {cargo_details['weight']} kg")
                st.write(f"Flight: {cargo_details['flight_id']}")
                st.write(f"Status: {cargo_details['status_name']}")

                # Allow the admin to update fields
                new_weight = st.number_input("New Weight (kg)", value=cargo_details['weight'], min_value=0.1, max_value=10000.0)
                new_status = st.selectbox("New Status", ["CS1", "CS2", "CS3"], index=["CS1", "CS2", "CS3"].index(cargo_details['status_id']))

                # Select new flight (if needed)
                flights = pd.read_sql("""
                    SELECT f.flight_id,
                        CONCAT(l_orig.airport_code, ' -> ', l_dest.airport_code,
                                ' (', DATE_FORMAT(f.departure_time, '%Y-%m-%d %H:%i'), ')') as flight_info
                    FROM Flight f
                    JOIN Location l_orig ON f.origin_id = l_orig.location_id
                    JOIN Location l_dest ON f.destination_id = l_dest.location_id
                    WHERE f.departure_time > NOW()
                    ORDER BY f.departure_time
                """, conn)
                new_flight = st.selectbox("New Flight", flights['flight_info'])
                new_flight_id = flights.loc[flights['flight_info'] == new_flight, 'flight_id'].iloc[0]

                if st.button("Update Cargo"):
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            UPDATE Cargo
                            SET weight = %s, status_id = %s, flight_id = %s
                            WHERE cargo_id = %s
                        """, (new_weight, new_status, new_flight_id, cargo_id))
                        conn.commit()
                        st.success("Cargo updated successfully!")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error updating cargo: {e}")
                    finally:
                        cursor.close()
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


import pandas as pd
import streamlit as st
import plotly.express as px

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
        # Plot the Users by Role chart using Plotly with rounded corners
        st.write("Users by Role")
        fig = px.bar(
            role_data,
            x='Role',
            y='Count',
            text='Count',
            color='Role',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        # Update layout for rounded corners and cleaner look
        fig.update_layout(
            plot_bgcolor="#f1efe7",
             paper_bgcolor="#f1efe7",
            font=dict(size=12),
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            barcornerradius=14  # Rounded corners with a radius of 15 pixels
        )

        # Update trace settings to add text on top of each bar without border
        fig.update_traces(textposition="outside")

        # Display the Plotly chart in Streamlit
        st.plotly_chart(fig)

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

    # Display cargo summary and customer's cargo in two columns
    col1, col2 = st.columns(2)

    with col1:
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

            st.metric("Total Cargo Weight", f"{total_weight:.2f} kg")
            st.metric("Total Cargo Cost", f"${total_cost:.2f}")

    with col2:
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
                     ' (', DATE_FORMAT(f.departure_time, '%Y-%m-%d %H:%i'), ')') as flight_info
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

    # Book cargo button
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

def delete_cargo():
    st.header("Delete Cargo")

    conn = get_database_connection()
    cursor = conn.cursor()

    # Fetch cargo data
    cursor.execute("""
        SELECT c.cargo_id, c.customer_id, c.cargo_type_id, cs.status_name, c.flight_id, c.weight, c.origin_id, c.destination_id, c.calculated_price, c.booking_date
        FROM Cargo c
        JOIN CargoStatus cs ON c.status_id = cs.status_id
        WHERE c.customer_id = %s AND cs.status_name IN ('SCHEDULED', 'PENDING')
    """, (st.session_state.user['user_id'],))

    cargo = cursor.fetchall()
    cargo_df = pd.DataFrame(cargo, columns=["Cargo ID", "Customer ID", "Cargo Type ID", "Status", "Flight ID", "Weight", "Origin ID", "Destination ID", "Calculated Price", "Booking Date"])

    if not cargo_df.empty:
        display_dataframe(cargo_df)
    else:
        st.info("No scheduled or pending cargo available for deletion.")

    # Delete cargo
    cargo_id = st.selectbox("Select Cargo ID", cargo_df["Cargo ID"])

    if st.button("Delete Cargo", type="primary"):
        try:
            cursor.execute("DELETE FROM Cargo WHERE cargo_id = %s", (cargo_id,))
            conn.commit()
            st.success("Cargo deleted successfully!")
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Error deleting cargo: {e}")

    cursor.close()
    conn.close()


# Function to display cargo status
def show_cargo_status():
    st.header("Cargo Status")

    conn = get_database_connection()
    cursor = conn.cursor()

    # Fetch cargo status for the logged-in customer
    cursor.execute("""
        SELECT c.cargo_id, c.customer_id, c.cargo_type_id, cs.status_name, c.flight_id, c.weight, c.origin_id, c.destination_id, c.calculated_price, c.booking_date
        FROM Cargo c
        JOIN CargoStatus cs ON c.status_id = cs.status_id
        WHERE c.customer_id = %s
    """, (st.session_state.user['user_id'],))

    cargo_status = cursor.fetchall()
    cargo_status_df = pd.DataFrame(cargo_status, columns=["Cargo ID", "Customer ID", "Cargo Type ID", "Status", "Flight ID", "Weight", "Origin ID", "Destination ID", "Calculated Price", "Booking Date"])

    if not cargo_status_df.empty:
        display_dataframe(cargo_status_df)
    else:
        st.info("No cargo available.")

    cursor.close()
    conn.close()


# Main app
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
   # Login section
    if not st.session_state.logged_in:
        # Set background color and layout
        st.markdown(
            """
            <style>
                .login-container {
                    background-color: #f0f4f8;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
                }
                .login-title {
                    font-size: 36px;
                    font-weight: bold;
                    color: #2c3e50;
                    text-align: center;
                }
                .login-subtitle {
                    font-size: 18px;
                    color: #7f8c8d;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .login-button {
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    width: 100%;
                }
                .login-button:hover {
                    background-color: #2980b9;
                }
                .error-message {
                    color: #e74c3c;
                    text-align: center;
                    font-size: 14px;
                    margin-top: 10px;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Add title and subtitle
            st.markdown('<div class="login-title">Cargo Management System</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Please enter your login credentials</div>', unsafe_allow_html=True)

            # Username and Password Inputs
            username = st.text_input("Username", label_visibility="collapsed", placeholder="Enter your username")
            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter your password")

            # Login button
            if st.button("Login", type="primary", help="Click to log in", key="login_button"):
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"Welcome {user['username']}!")
                    st.rerun()
                else:
                    st.markdown('<div class="error-message">Invalid username or password</div>', unsafe_allow_html=True)
    
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
            show_cargo_status() 
            delete_cargo() 

if __name__ == "__main__":
    main()