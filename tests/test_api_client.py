import pytest
from unittest.mock import Mock, patch
from app.api_client import SOCAPIClient

@pytest.fixture
def api_client():
    return SOCAPIClient()

def test_get_server_status_success(api_client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy"}
    
    with patch.object(api_client.session, 'get', return_value=mock_response):
        status, data = api_client.get_server_status()
        assert status is True
        assert data == {"status": "healthy"}

def test_get_server_status_failure(api_client):
    with patch.object(api_client.session, 'get', side_effect=Exception("Connection error")):
        status, data = api_client.get_server_status()
        assert status is False
        assert data is None

def test_get_incidents_success(api_client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"incidents": [{"id": "1"}]}
    
    with patch.object(api_client.session, 'get', return_value=mock_response):
        incidents = api_client.get_incidents()
        assert incidents == [{"id": "1"}]

def test_submit_alert_success(api_client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"incident_id": "123"}
    
    with patch.object(api_client.session, 'post', return_value=mock_response):
        result = api_client.submit_alert({"test": "data"})
        assert result == {"incident_id": "123"}