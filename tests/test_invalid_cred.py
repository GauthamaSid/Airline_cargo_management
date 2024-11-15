from unittest.mock import patch, MagicMock
from app import authenticate  # Import the function you want to test

@patch("app.get_database_connection")
def test_authenticate_invalid_user(mock_get_db_conn):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # No user found
    
    # Set our mock connection to be returned by get_database_connection
    mock_get_db_conn.return_value = mock_conn
    
    # Test with invalid credentials
    result = authenticate("wronguser", "wrongpassword")
    
    assert result is None
