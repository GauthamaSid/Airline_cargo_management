# tests/test_authentication.py
import pytest
from unittest.mock import patch, MagicMock
from app import authenticate  # Import the function from your main app

@patch("app.get_database_connection")
def test_authenticate_valid_user(mock_get_db_conn):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, "testuser", "admin")  # Mocked user data

    # Set our mock connection to be returned by get_database_connection
    mock_get_db_conn.return_value = mock_conn

    # Test with valid credentials
    result = authenticate("testuser", "correct_password")
    assert result == {"username": "testuser", "role_name": "admin"}

    # Close cursor and connection
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("app.get_database_connection")
def test_authenticate_valid_user(mock_get_db_conn):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, "testuser", "admin")  # Mocked user data
    
    # Set our mock connection to be returned by get_database_connection
    mock_get_db_conn.return_value = mock_conn
    
    # Test with valid credentials
    result = authenticate("testuser", "correct_password")
    
    # Compare with the expected tuple returned by the query
    assert result == (1, "testuser", "admin")
