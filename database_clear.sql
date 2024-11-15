-- First, connect to MySQL and use the database
-- mysql -u root -p
-- CREATE DATABASE IF NOT EXISTS cargo_db;
-- USE cargo_db;

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS CargoHandling;
DROP TABLE IF EXISTS Cargo;
DROP TABLE IF EXISTS Flight;
DROP TABLE IF EXISTS Aircraft;
DROP TABLE IF EXISTS UserRole;
DROP TABLE IF EXISTS Role;
DROP TABLE IF EXISTS Users; -- Changed from "User"
DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS CargoType;
DROP TABLE IF EXISTS CargoStatus;
DROP TABLE IF EXISTS HandlingAction;

-- Create tables (with Users instead of "User")
CREATE TABLE Role (
    role_id VARCHAR(36) PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE Users ( -- Changed from "User"
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
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
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
    FOREIGN KEY (customer_id) REFERENCES Users(user_id),
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
    FOREIGN KEY (handler_id) REFERENCES Users(user_id),
    FOREIGN KEY (action_id) REFERENCES HandlingAction(action_id)
);

-- Insert sample data
-- Roles
-- Insert sample data into the Role table
INSERT INTO Role (role_id, role_name, description) VALUES
('R1', 'admin', 'System administrator'),
('R2', 'cargo_handler', 'Handles cargo operations'),
('R3', 'customer', 'Books and tracks cargo');

-- Insert sample data into the Users table
INSERT INTO Users (user_id, username, password, email) VALUES
('U1', 'admin', 'password', 'admin@cargo.com'),
('U2', 'handler1', 'password', 'handler1@cargo.com'),
('U3', 'handler2', 'password', 'handler2@cargo.com'),
('U4', 'customer1', 'password', 'customer1@email.com'),
('U5', 'customer2', 'password', 'customer2@email.com');

-- Insert sample data into the UserRole table
INSERT INTO UserRole (user_role_id, user_id, role_id) VALUES
('UR1', 'U1', 'R1'),
('UR2', 'U2', 'R2'),
('UR3', 'U3', 'R2'),
('UR4', 'U4', 'R3'),
('UR5', 'U5', 'R3');

-- Insert sample data into the Location table
INSERT INTO Location (location_id, city, country, airport_code) VALUES
('L1', 'New York', 'USA', 'JFK'),
('L2', 'London', 'UK', 'LHR'),
('L3', 'Tokyo', 'Japan', 'HND'),
('L4', 'Dubai', 'UAE', 'DXB'),
('L5', 'Singapore', 'Singapore', 'SIN');

-- Insert sample data into the Aircraft table
INSERT INTO Aircraft (aircraft_id, model, max_cargo_capacity, registration_number) VALUES
('A1', 'Boeing 747F', 135000, 'N747CA'),
('A2', 'Airbus A330F', 70000, 'N330CA'),
('A3', 'Boeing 777F', 103000, 'N777CA');

-- Insert sample data into the CargoType table
INSERT INTO CargoType (cargo_type_id, type_name, base_rate_per_kg, requires_special_handling) VALUES
('CT1', 'Standard', 5.00, FALSE),
('CT2', 'Perishable', 8.00, TRUE),
('CT3', 'Hazardous', 12.00, TRUE),
('CT4', 'Express', 10.00, FALSE);

-- Insert sample data into the CargoStatus table
INSERT INTO CargoStatus (status_id, status_name, description) VALUES
('CS1', 'PENDING', 'Cargo booking confirmed, awaiting handling'),
('CS2', 'IN_TRANSIT', 'Cargo in transit'),
('CS3', 'DELIVERED', 'Cargo delivered to destination'),
('CS4', 'CANCELLED', 'Cargo booking cancelled');

-- Insert sample data into the HandlingAction table
INSERT INTO HandlingAction (action_id, action_name, description, requires_verification) VALUES
('HA1', 'PICKUP', 'Cargo picked up from origin', TRUE),
('HA2', 'LOAD', 'Cargo loaded onto aircraft', TRUE),
('HA3', 'UNLOAD', 'Cargo unloaded from aircraft', TRUE),
('HA4', 'DELIVER', 'Cargo delivered to destination', TRUE);

-- Insert sample data into the Flight table
INSERT INTO Flight (flight_id, aircraft_id, origin_id, destination_id, departure_time, arrival_time, flight_status) VALUES
('F1', 'A1', 'L1', 'L2', '2024-12-10 10:00:00', '2024-12-10 22:00:00', 'Scheduled'),
('F2', 'A2', 'L2', 'L3', '2024-12-11 14:00:00', '2024-12-12 06:00:00', 'Scheduled');

-- Insert sample data into the Cargo table
INSERT INTO Cargo (cargo_id, customer_id, cargo_type_id, status_id, flight_id, weight, origin_id, destination_id, calculated_price) VALUES
('C1', 'U4', 'CT1', 'CS1', 'F1', 1000.00, 'L1', 'L2', 5000.00),
('C2', 'U5', 'CT2', 'CS2', 'F2', 500.00, 'L2', 'L3', 4000.00);

-- User Creation and Privileges (Add after table creation and data insertion)
CREATE USER IF NOT EXISTS 'cargo_admin'@'localhost' IDENTIFIED BY 'admin_password';
CREATE USER IF NOT EXISTS 'cargo_handler'@'localhost' IDENTIFIED BY 'handler_password';
CREATE USER IF NOT EXISTS 'cargo_customer'@'localhost' IDENTIFIED BY 'customer_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON *.* TO 'cargo_admin'@'localhost';
GRANT SELECT, INSERT, UPDATE ON Cargo TO 'cargo_handler'@'localhost';
GRANT SELECT, INSERT, UPDATE ON CargoHandling TO 'cargo_handler'@'localhost';
GRANT SELECT ON Flight TO 'cargo_handler'@'localhost';
GRANT SELECT, INSERT ON Cargo TO 'cargo_customer'@'localhost';
GRANT SELECT ON Flight TO 'cargo_customer'@'localhost';

FLUSH PRIVILEGES;

-- Stored Procedures
DELIMITER //

-- 1. Create new cargo booking
CREATE PROCEDURE IF NOT EXISTS CreateCargoBooking(
    IN p_customer_id VARCHAR(36),
    IN p_cargo_type_id VARCHAR(36),
    IN p_flight_id VARCHAR(36),
    IN p_weight DECIMAL(10,2),
    IN p_origin_id VARCHAR(36),
    IN p_destination_id VARCHAR(36)
)
BEGIN
    DECLARE v_base_rate DECIMAL(10,2);
    DECLARE v_calculated_price DECIMAL(10,2);
    DECLARE v_cargo_id VARCHAR(36);

    -- Generate UUID for cargo_id
    SET v_cargo_id = UUID();

    -- Get base rate from cargo type
    SELECT base_rate_per_kg INTO v_base_rate
    FROM CargoType
    WHERE cargo_type_id = p_cargo_type_id;

    -- Calculate price
    SET v_calculated_price = p_weight * v_base_rate;

    -- Insert new cargo
    INSERT INTO Cargo (
        cargo_id,
        customer_id,
        cargo_type_id,
        status_id,
        flight_id,
        weight,
        origin_id,
        destination_id,
        calculated_price
    ) VALUES (
        v_cargo_id,
        p_customer_id,
        p_cargo_type_id,
        'CS1', -- PENDING status
        p_flight_id,
        p_weight,
        p_origin_id,
        p_destination_id,
        v_calculated_price
    );
END //

-- 2. Update cargo status with handling log
CREATE PROCEDURE IF NOT EXISTS UpdateCargoStatus(
    IN p_cargo_id VARCHAR(36),
    IN p_new_status_id VARCHAR(36),
    IN p_handler_id VARCHAR(36),
    IN p_action_id VARCHAR(36),
    IN p_notes TEXT
)
BEGIN
    -- Update cargo status
    UPDATE Cargo
    SET status_id = p_new_status_id
    WHERE cargo_id = p_cargo_id;

    -- Log handling action
    INSERT INTO CargoHandling (
        handling_id,
        cargo_id,
        handler_id,
        action_id,
        notes
    ) VALUES (
        UUID(),
        p_cargo_id,
        p_handler_id,
        p_action_id,
        p_notes
    );
END //

DELIMITER ;

-- Example Complex Queries (Can be run as needed)

-- 1. Nested Query: Find all handlers who have handled high-value cargo
SELECT DISTINCT u.username, u.email
FROM Users u
WHERE u.user_id IN (
    SELECT ch.handler_id
    FROM CargoHandling ch
    JOIN Cargo c ON ch.cargo_id = c.cargo_id
    WHERE c.calculated_price > (
        SELECT AVG(calculated_price)
        FROM Cargo
    )
);

-- 2. Join Query: Comprehensive cargo tracking information
SELECT
    c.cargo_id,
    ct.type_name AS cargo_type,
    cs.status_name,
    f.flight_id,
    orig.airport_code AS origin,
    dest.airport_code AS destination,
    u.username AS customer,
    GROUP_CONCAT(
        CONCAT(ha.action_name, ' by ', handler.username, ' at ', ch.handling_time)
        ORDER BY ch.handling_time
    ) AS handling_history
FROM Cargo c
JOIN CargoType ct ON c.cargo_type_id = ct.cargo_type_id
JOIN CargoStatus cs ON c.status_id = cs.status_id
JOIN Flight f ON c.flight_id = f.flight_id
JOIN Location orig ON c.origin_id = orig.location_id
JOIN Location dest ON c.destination_id = dest.location_id
JOIN Users u ON c.customer_id = u.user_id
LEFT JOIN CargoHandling ch ON c.cargo_id = ch.cargo_id
LEFT JOIN HandlingAction ha ON ch.action_id = ha.action_id
LEFT JOIN Users handler ON ch.handler_id = handler.user_id
GROUP BY
    c.cargo_id,
    ct.type_name,
    cs.status_name,
    f.flight_id,
    orig.airport_code,
    dest.airport_code,
    u.username;

-- 3. Aggregate Query: Cargo handling statistics by location
SELECT
    l.airport_code,
    l.city,
    COUNT(c.cargo_id) AS total_cargo_handled,
    SUM(c.weight) AS total_weight_handled,
    ROUND(AVG(c.calculated_price), 2) AS avg_cargo_value,
    COUNT(CASE WHEN ct.requires_special_handling THEN 1 END) AS special_handling_count
FROM Location l
LEFT JOIN Cargo c ON l.location_id = c.origin_id
LEFT JOIN CargoType ct ON c.cargo_type_id = ct.cargo_type_id
GROUP BY l.location_id, l.airport_code, l.city
HAVING total_cargo_handled > 0
ORDER BY total_cargo_handled DESC;

-- Example usage of stored procedures
-- To create a new cargo booking:
CALL CreateCargoBooking(
    'U4', -- customer_id
    'CT1', -- cargo_type_id
    'F1',  -- flight_id
    1500.00, -- weight
    'L1',    -- origin_id
    'L2'     -- destination_id
);

-- To update cargo status:
CALL UpdateCargoStatus(
    'C1',    -- cargo_id
    'CS2',   -- new_status_id (IN_TRANSIT)
    'U2',    -- handler_id
    'HA1',   -- action_id (PICKUP)
    'Cargo picked up from origin warehouse' -- notes
);

-- Auto trigger
DELIMITER //

CREATE TRIGGER IF NOT EXISTS after_flight_arrival
AFTER UPDATE ON Flight
FOR EACH ROW
BEGIN
    IF NEW.flight_status = 'ARRIVED' THEN
        UPDATE Cargo
        SET status_id = 'CS3' -- Assuming 'CS3' is the status_id for 'DELIVERED'
        WHERE flight_id = NEW.flight_id;
    END IF;
END //

DELIMITER ;
