import pytest
import requests
from unittest.mock import Mock, patch
from phonkersbase import PhonkersBaseAPI, ArtistLabel, PhonkersBaseException

@pytest.fixture
def client():
    return PhonkersBaseAPI()

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.json.return_value = {
        "data": {
            "items": [
                {"id": 1, "name": "Test Artist 1"},
                {"id": 2, "name": "Test Artist 2"}
            ],
            "info": {"total": 2}
        }
    }
    mock.content = b'{"data": {"items": []}}'
    return mock

def test_init():
    client = PhonkersBaseAPI(timeout=20, cache_ttl=1800, cache_size=1000)
    assert client.timeout == 20
    assert client.cache.ttl == 1800
    assert client.cache.maxsize == 1000

@patch('requests.Session.get')
def test_get_artists(mock_get, client, mock_response):
    mock_get.return_value = mock_response
    mock_response.status_code = 200
    
    result = client.get_artists(search="test", label=ArtistLabel.APPROVED)
    
    assert "items" in result
    assert len(result["items"]) == 2
    mock_get.assert_called_once()

@patch('requests.Session.get')
def test_search_artists_empty_query(mock_get, client):
    with pytest.raises(ValueError):
        client.search_artists("")

@patch('requests.Session.get')
def test_get_artists_by_country_empty(mock_get, client):
    with pytest.raises(ValueError):
        client.get_artists_by_country("")

@patch('requests.Session.get')
def test_timeout_error(mock_get, client):
    mock_get.side_effect = requests.exceptions.Timeout
    
    with pytest.raises(PhonkersBaseException) as exc_info:
        client.get_artists()
    assert "timeout" in str(exc_info.value).lower()

@patch('requests.Session.get')
def test_connection_error(mock_get, client):
    mock_get.side_effect = requests.exceptions.ConnectionError
    
    with pytest.raises(PhonkersBaseException) as exc_info:
        client.get_artists()
    assert "connection" in str(exc_info.value).lower()

def test_artist_label_enum():
    assert ArtistLabel.APPROVED.value == "approved"
    assert ArtistLabel.BASE.value == "base"
    assert ArtistLabel.UNKNOWN.value == "unknown"

def test_cache_operations(client):
    cache_info = client.get_cache_info()
    assert cache_info["size"] == 0
    assert cache_info["maxsize"] == 2048
    assert cache_info["ttl"] == 3600

    # Test cache clear
    client.clear_cache()
    cache_info = client.get_cache_info()
    assert cache_info["size"] == 0

@patch('requests.Session.get')
def test_paginate_all_artists(mock_get, client):
    # Mock first page
    mock_response1 = Mock()
    mock_response1.json.return_value = {
        "data": {
            "items": [{"id": 1}, {"id": 2}],
            "info": {"total": 3}
        }
    }
    mock_response1.content = b'{}'
    
    # Mock second page
    mock_response2 = Mock()
    mock_response2.json.return_value = {
        "data": {
            "items": [{"id": 3}],
            "info": {"total": 3}
        }
    }
    mock_response2.content = b'{}'
    
    mock_get.side_effect = [mock_response1, mock_response2]
    
    results = client.paginate_all_artists(limit=2)
    assert len(results) == 3
    assert mock_get.call_count == 2
