"""Test main entry point."""


def test_read_root(test_client):
    """Test the root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    response_data = response.json()
    assert "data" in response_data
    assert response_data["data"]["message"] == "Hello from the Web-App-Demo backend!"
    assert "timestamp" in response_data
    assert "success" in response_data
    assert response_data["success"] is True
