# tests/test_dashboard_role_based_display.py
from unittest.mock import MagicMock, patch
from app import authenticate  # Import the authenticate function (adjust as necessary)

@patch("app.get_database_connection")
def test_dashboard_role_based_display(mock_get_db_conn):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1, "testuser", "admin")  # Mock admin user
    
    # Set the mock connection to be returned by get_database_connection
    mock_get_db_conn.return_value = mock_conn
    
    # Test that admin sees the admin dashboard
    user = authenticate("testuser", "correct_password")
    assert user[2] == "admin"  # Access the role by index (2 is the role in the tuple)
