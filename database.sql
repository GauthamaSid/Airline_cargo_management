-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS CargoHandling;
DROP TABLE IF EXISTS Cargo;
DROP TABLE IF EXISTS Flight;
DROP TABLE IF EXISTS Aircraft;
DROP TABLE IF EXISTS UserRole;
DROP TABLE IF EXISTS Role;
DROP TABLE IF EXISTS "User";
DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS CargoType;
DROP TABLE IF EXISTS CargoStatus;
DROP TABLE IF EXISTS HandlingAction;

-- Create tables
CREATE TABLE Role (
    role_id VARCHAR(36) PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE "User" (
    user_id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE UserRole (
    user_role_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    role_id VARCHAR(36),
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
);

CREATE TABLE Location (
    location_id VARCHAR(36) PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    airport_code CHAR(3) UNIQUE NOT NULL
);

CREATE TABLE Aircraft (
    aircraft_id VARCHAR(36) PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    max_cargo_capacity DECIMAL(10,2) NOT NULL,
    registration_number VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE Flight (
    flight_id VARCHAR(36) PRIMARY KEY,
    aircraft_id VARCHAR(36),
    origin_id VARCHAR(36),
    destination_id VARCHAR(36),
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    flight_status VARCHAR(20) NOT NULL,
    FOREIGN KEY (aircraft_id) REFERENCES Aircraft(aircraft_id),
    FOREIGN KEY (origin_id) REFERENCES Location(location_id),
    FOREIGN KEY (destination_id) REFERENCES Location(location_id)
);

CREATE TABLE CargoType (
    cargo_type_id VARCHAR(36) PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    base_rate_per_kg DECIMAL(10,2) NOT NULL,
    requires_special_handling BOOLEAN DEFAULT FALSE
);

CREATE TABLE CargoStatus (
    status_id VARCHAR(36) PRIMARY KEY,
    status_name VARCHAR(20) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE HandlingAction (
    action_id VARCHAR(36) PRIMARY KEY,
    action_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    requires_verification BOOLEAN DEFAULT FALSE
);

CREATE TABLE Cargo (
    cargo_id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36),
    cargo_type_id VARCHAR(36),
    status_id VARCHAR(36),
    flight_id VARCHAR(36),
    weight DECIMAL(10,2) NOT NULL,
    origin_id VARCHAR(36),
    destination_id VARCHAR(36),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculated_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES User(user_id),
    FOREIGN KEY (cargo_type_id) REFERENCES CargoType(cargo_type_id),
    FOREIGN KEY (status_id) REFERENCES CargoStatus(status_id),
    FOREIGN KEY (flight_id) REFERENCES Flight(flight_id),
    FOREIGN KEY (origin_id) REFERENCES Location(location_id),
    FOREIGN KEY (destination_id) REFERENCES Location(location_id)
);

CREATE TABLE CargoHandling (
    handling_id VARCHAR(36) PRIMARY KEY,
    cargo_id VARCHAR(36),
    handler_id VARCHAR(36),
    action_id VARCHAR(36),
    handling_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (cargo_id) REFERENCES Cargo(cargo_id),
    FOREIGN KEY (handler_id) REFERENCES User(user_id),
    FOREIGN KEY (action_id) REFERENCES HandlingAction(action_id)
);

-- Insert sample data
-- Roles
INSERT INTO Role (role_id, role_name, description) VALUES
('R1', 'admin', 'System administrator'),
('R2', 'cargo_handler', 'Handles cargo operations'),
('R3', 'customer', 'Books and tracks cargo');

-- Users (password: 'password' for all users)
INSERT INTO User (user_id, username, password, email) VALUES
('U1', 'admin', 'password', 'admin@cargo.com'),
('U2', 'handler1', 'password', 'handler1@cargo.com'),
('U3', 'handler2', 'password', 'handler2@cargo.com'),
('U4', 'customer1', 'password', 'customer1@email.com'),
('U5', 'customer2', 'password', 'customer2@email.com');

-- UserRoles
INSERT INTO UserRole (user_role_id, user_id, role_id) VALUES
('UR1', 'U1', 'R1'),
('UR2', 'U2', 'R2'),
('UR3', 'U3', 'R2'),
('UR4', 'U4', 'R3'),
('UR5', 'U5', 'R3');

-- Locations
INSERT INTO Location (location_id, city, country, airport_code) VALUES
('L1', 'New York', 'USA', 'JFK'),
('L2', 'London', 'UK', 'LHR'),
('L3', 'Tokyo', 'Japan', 'HND'),
('L4', 'Dubai', 'UAE', 'DXB'),
('L5', 'Singapore', 'Singapore', 'SIN');

-- Aircraft
INSERT INTO Aircraft (aircraft_id, model, max_cargo_capacity, registration_number) VALUES
('A1', 'Boeing 747F', 135000, 'N747CA'),
('A2', 'Airbus A330F', 70000, 'N330CA'),
('A3', 'Boeing 777F', 103000, 'N777CA');

-- Cargo Types
INSERT INTO CargoType (cargo_type_id, type_name, base_rate_per_kg, requires_special_handling) VALUES
('CT1', 'Standard', 5.00, FALSE),
('CT2', 'Perishable', 8.00, TRUE),
('CT3', 'Hazardous', 12.00, TRUE),
('CT4', 'Express', 10.00, FALSE);

-- Cargo Status
INSERT INTO CargoStatus (status_id, status_name, description) VALUES
('CS1', 'PENDING', 'Cargo booking confirmed, awaiting handling'),
('CS2', 'IN_TRANSIT', 'Cargo in transit'),
('CS3', 'DELIVERED', 'Cargo delivered to destination'),
('CS4', 'CANCELLED', 'Cargo booking cancelled');

-- Handling Actions
INSERT INTO HandlingAction (action_id, action_name, description, requires_verification) VALUES
('HA1', 'PICKUP', 'Cargo picked up from origin', TRUE),
('HA2', 'LOAD', 'Cargo loaded onto aircraft', TRUE),
('HA3', 'UNLOAD', 'Cargo unloaded from aircraft', TRUE),
('HA4', 'DELIVER', 'Cargo delivered to destination', TRUE);

-- Sample Flights
INSERT INTO Flight (flight_id, aircraft_id, origin_id, destination_id, departure_time, arrival_time, flight_status) VALUES
('F1', 'A1', 'L1', 'L2', '2024-03-10 10:00:00', '2024-03-10 22:00:00', 'SCHEDULED'),
('F2', 'A2', 'L2', 'L3', '2024-03-11 14:00:00', '2024-03-12 06:00:00', 'SCHEDULED');

-- Sample Cargo
INSERT INTO Cargo (cargo_id, customer_id, cargo_type_id, status_id, flight_id, weight, origin_id, destination_id, calculated_price) VALUES
('C1', 'U4', 'CT1', 'CS1', 'F1', 1000.00, 'L1', 'L2', 5000.00),
('C2', 'U5', 'CT2', 'CS2', 'F2', 500.00, 'L2', 'L3', 4000.00);

