import requests
from typing import List, Dict, Optional, Union
from enum import Enum
import json
from urllib.parse import urljoin
from cachetools import cached, TTLCache
import logging


class ArtistLabel(Enum):
    BASE = "base"
    APPROVED = "approved"
    UNKNOWN = "unknown"
    PRIDE = "pride"
    BLOCKED = "blocked"
    WARNING = "warning"


class PhonkersBaseException(Exception):
    pass


class PhonkersBaseAPI:
    """
    A client for interacting with the PhonkersBase API.
    
    This client provides methods to search and retrieve artists from PhonkersBase,
    with support for filtering by label and country. It includes built-in caching
    and pagination helpers.
    
    Args:
        timeout (int): Request timeout in seconds. Defaults to 10.
        cache_ttl (int): Cache time-to-live in seconds. Defaults to 3600 (1 hour).
        cache_size (int): Maximum number of items to store in cache. Defaults to 2048.
    """
    
    BASE_URL = "https://www.phonkersbase.com/api/"
    
    def __init__(self, timeout: int = 10, cache_ttl: int = 3600, cache_size: int = 2048):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PhonkersBasePythonClient/0.2.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.timeout = timeout
        self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        self.logger = logging.getLogger(__name__)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        url = urljoin(self.BASE_URL, endpoint)
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            if not response.content:
                return {"items": [], "info": {}}
                
            data = response.json()
            return data.get("data", data)
            
        except requests.exceptions.Timeout:
            raise PhonkersBaseException(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise PhonkersBaseException("Connection error - check your internet connection")
        except requests.exceptions.HTTPError as e:
            raise PhonkersBaseException(f"HTTP {e.response.status_code}: {e.response.reason}")
        except json.JSONDecodeError:
            raise PhonkersBaseException("Invalid JSON response from API")
        except Exception as e:
            self.logger.error(f"Unexpected error in _make_request: {str(e)}")
            raise PhonkersBaseException("An unexpected internal error occurred")

    def get_artists(
        self,
        search: Optional[str] = None,
        label: Optional[Union[ArtistLabel, str]] = None,
        country: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
        locale: str = 'uk'
    ) -> Dict:
        """
        Retrieve artists from PhonkersBase with optional filtering.
        
        Args:
            search (str, optional): Search query to filter artists.
            label (Union[ArtistLabel, str], optional): Filter by artist label.
            country (str, optional): Filter by artist's country.
            limit (int): Number of results per page. Default is 25.
            offset (int): Number of results to skip. Default is 0.
            locale (str): Locale for results. Default is 'uk'.
            
        Returns:
            Dict: A dictionary containing artist items and pagination info.
            
        Raises:
            PhonkersBaseException: If the API request fails.
        """
        params = {
            "limit": min(max(1, limit), 100),
            "offset": max(0, offset),
            "locale": locale,
        }
        
        if search and search.strip():
            params["search"] = search.strip()
            
        if label:
            if isinstance(label, ArtistLabel):
                params["label"] = label.value
            elif isinstance(label, str) and label.lower() in [e.value for e in ArtistLabel]:
                params["label"] = label.lower()
                
        if country and country.strip():
            params["country"] = country.strip().lower()
        
        return self._make_request("artists", params)

    def get_countries(self) -> List[str]:
        """
        Retrieve a list of available countries from PhonkersBase.
        
        Returns:
            List[str]: A list of country codes.
            
        Note:
            Returns an empty list if the request fails instead of raising an exception.
        """
        try:
            data = self._make_request("countries")
            return data.get("countries", [])
        except PhonkersBaseException:
            return []

    def search_artists(self, query: str, **kwargs) -> Dict:
        """
        Search for artists by name or description.
        
        Args:
            query (str): The search query.
            **kwargs: Additional arguments to pass to get_artists.
            
        Returns:
            Dict: A dictionary containing artist items and pagination info.
            
        Raises:
            ValueError: If the search query is empty.
            PhonkersBaseException: If the API request fails.
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
            
        return self.get_artists(search=query.strip(), **kwargs)

    def get_artists_by_label(self, label: Union[ArtistLabel, str], **kwargs) -> Dict:
        return self.get_artists(label=label, **kwargs)

    def get_artists_by_country(self, country: str, **kwargs) -> Dict:
        if not country or not country.strip():
            raise ValueError("Country cannot be empty")
            
        return self.get_artists(country=country.strip(), **kwargs)

    def paginate_all_artists(self, **kwargs) -> List[Dict]:
        """
        Retrieve all artists by automatically handling pagination.
        
        This method will make multiple API calls to retrieve all available artists
        that match the given criteria.
        
        Args:
            **kwargs: Arguments to pass to get_artists.
            
        Returns:
            List[Dict]: A list of all artist items.
            
        Note:
            This method may take a while to complete if there are many results.
        """
        all_artists = []
        offset = 0
        limit = kwargs.get('limit', 25)
        
        while True:
            kwargs.update({'offset': offset, 'limit': limit})
            response = self.get_artists(**kwargs)
            
            items = response.get("items", [])
            if not items:
                break
                
            all_artists.extend(items)
            
            if len(items) < limit:
                break
                
            offset += limit
        
        return all_artists

    def clear_cache(self):
        self.cache.clear()

    def get_cache_info(self) -> Dict:
        return {
            "size": len(self.cache),
            "maxsize": self.cache.maxsize,
            "ttl": self.cache.ttl
        }


phonkerbase = PhonkersBaseAPI()