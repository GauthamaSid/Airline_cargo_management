# Airline Cargo Management System

This repository contains the SQL schema, data, and stored procedures for a Cargo Management System. It allows for the management of cargo bookings, user roles, cargo handling actions, and flights.

## Setup Instructions

### 1. Create the Database

Execute the following SQL commands in your MySQL terminal to create the `cargo_db` database:

```sql
-- Drop the database if it exists
DROP DATABASE IF EXISTS cargo_db;

-- Create the new database
CREATE DATABASE cargo_db;

-- Select the database for use
USE cargo_db;

-- Load the SQL Script
source database_clear.sql;
```
The `database_clear.sql` script will create the required database schema, tables,etc.

### 2.Create Virtual Environment:

```python

python3 -m venv cargo_env
source cargo_env/bin/activate  # or `cargo_env\Scripts\activate` on Windows
Install Required Packages: Install Streamlit and MySQL connector:

```
### 3. Run streamlet
```python
pip install streamlit mysql-connector-python
```

## Usage 

### 1.Logining in as other users

you can login as an admin by:

```bash
mysql -u cargo_admin -p 
```
The password is `cargo_password`,similarly for `cargo_customer`, `cargo_handler` and `cargo_customer`.

Check `testing.md` to see what functionalites the code should have