"""Test main entry point."""


def test_read_root(test_client):
    """Test the root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from the Web-App-Demo backend!"}
