# Airline Cargo Management System

This is a Streamlit-based Cargo Management System that allows users to manage cargo shipments, flights, and users. The system supports three roles: admin, cargo handler, and customer.

## Setup Instructions

### 1. Clone the repository:
```bash
git clone https://github.com/yourusername/cargo-management-system.git
cd cargo-management-system
```
### 2. Create the Database:

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

### 3.Create Virtual Environment:

```python

python3 -m venv cargo_env
source cargo_env/bin/activate  # or `cargo_env\Scripts\activate` on Windows

```
### 4. Install streamlet and dependencies 

```python
pip install -r requirements.txt
```

## Usage 

```bash
 streamlit run app.py
```

The password is `password` for all users (`customer1`, `handler1` and `customer1`).
