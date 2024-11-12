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

```
### 3. Install streamlet and dependencies 

```python
pip install streamlit mysql-connector-python pandas
```

## Usage 

```bash
 streamlit run app.py
```

The password is `password` for all users, `customer1`, `handler1` and `customer1`.
