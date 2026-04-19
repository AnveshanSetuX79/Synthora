"""Unit tests for Google Places API service.

Tests cover:
- Business search functionality
- Business details retrieval
- API error handling
- Rate limiting
- Response parsing
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from backend.app.services.google_places import (
    GooglePlacesService,
    BusinessData,
    GooglePlacesAPIError,
    RateLimitError
)


@pytest.fixture
def api_key():
    """Test API key."""
    return "test_api_key_12345"


@pytest.fixture
def service(api_key):
    """Create GooglePlacesService instance."""
    return GooglePlacesService(api_key)


@pytest.fixture
def mock_search_response():
    """Mock response for nearby search."""
    return {
        "status": "OK",
        "results": [
            {
                "place_id": "ChIJ1234567890",
                "name": "Test Restaurant",
                "vicinity": "123 Main St, Pune",
                "rating": 4.5,
                "user_ratings_total": 150,
                "types": ["restaurant", "food", "establishment"]
            },
            {
                "place_id": "ChIJ0987654321",
                "name": "Another Restaurant",
                "vicinity": "456 Park Ave, Pune",
                "rating": 4.2,
                "user_ratings_total": 89,
                "types": ["restaurant", "food"]
            }
        ]
    }


@pytest.fixture
def mock_details_response():
    """Mock response for place details."""
    return {
        "status": "OK",
        "result": {
            "place_id": "ChIJ1234567890",
            "name": "Test Restaurant",
            "formatted_address": "123 Main St, Pune, Maharashtra 411001, India",
            "formatted_phone_number": "+91 20 1234 5678",
            "rating": 4.5,
            "user_ratings_total": 150,
            "website": "https://testrestaurant.com",
            "types": ["restaurant", "food", "establishment"],
            "address_components": [
                {"long_name": "Pune", "types": ["locality", "political"]},
                {"long_name": "Maharashtra", "types": ["administrative_area_level_1"]},
                {"long_name": "India", "types": ["country"]}
            ]
        }
    }


@pytest.fixture
def mock_geocode_response():
    """Mock response for geocoding."""
    return {
        "status": "OK",
        "results": [
            {
                "geometry": {
                    "location": {
                        "lat": 18.5204,
                        "lng": 73.8567
                    }
                }
            }
        ]
    }


class TestGooglePlacesServiceInitialization:
    """Test service initialization."""
    
    def test_init_with_valid_api_key(self, api_key):
        """Should initialize with valid API key."""
        service = GooglePlacesService(api_key)
        assert service.api_key == api_key
        assert service._request_count == 0
    
    def test_init_without_api_key(self):
        """Should raise ValueError when API key is missing."""
        with pytest.raises(ValueError, match="API key is required"):
            GooglePlacesService("")
    
    def test_session_configured_with_retries(self, service):
        """Should configure session with retry strategy."""
        assert service.session is not None
        adapter = service.session.get_adapter("https://")
        assert adapter.max_retries.total == 3


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limit_not_exceeded(self, service):
        """Should not raise error when under limit."""
        service._request_count = 500
        service._check_rate_limit()  # Should not raise
    
    def test_rate_limit_exceeded(self, service):
        """Should raise RateLimitError when limit exceeded."""
        service._request_count = 1000
        with pytest.raises(RateLimitError, match="Daily API request limit"):
            service._check_rate_limit()
    
    def test_rate_limit_resets_after_24_hours(self, service):
        """Should reset counter after 24 hours."""
        import time
        service._request_count = 1000
        service._last_reset = time.time() - 86401  # 24 hours + 1 second ago
        
        service._check_rate_limit()  # Should not raise
        assert service._request_count == 0


class TestSearchBusinesses:
    """Test business search functionality."""
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_search_with_coordinates(self, mock_get, service, mock_search_response):
        """Should search businesses with coordinate location."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_search_response
        mock_get.return_value = mock_response
        
        results = service.search_businesses(
            location="18.5204,73.8567",
            category="restaurant"
        )
        
        assert len(results) == 2
        assert results[0].name == "Test Restaurant"
        assert results[0].place_id == "ChIJ1234567890"
        assert results[0].rating == 4.5
        assert results[0].review_count == 150
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_search_with_city_name(self, mock_get, service, mock_geocode_response, mock_search_response):
        """Should geocode city name before searching."""
        # First call: geocoding
        mock_geocode = Mock()
        mock_geocode.status_code = 200
        mock_geocode.json.return_value = mock_geocode_response
        
        # Second call: search
        mock_search = Mock()
        mock_search.status_code = 200
        mock_search.json.return_value = mock_search_response
        
        mock_get.side_effect = [mock_geocode, mock_search]
        
        results = service.search_businesses(
            location="Pune",
            category="restaurant"
        )
        
        assert len(results) == 2
        assert mock_get.call_count == 2
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_search_with_custom_radius(self, mock_get, service, mock_search_response):
        """Should use custom radius parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_search_response
        mock_get.return_value = mock_response
        
        service.search_businesses(
            location="18.5204,73.8567",
            category="restaurant",
            radius=10000
        )
        
        # Check that radius was passed in params
        call_args = mock_get.call_args
        assert call_args[1]['params']['radius'] == 10000
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_search_handles_zero_results(self, mock_get, service):
        """Should handle zero results gracefully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ZERO_RESULTS", "results": []}
        mock_get.return_value = mock_response
        
        results = service.search_businesses(
            location="18.5204,73.8567",
            category="restaurant"
        )
        
        assert len(results) == 0
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_search_handles_malformed_results(self, mock_get, service):
        """Should skip malformed results and continue."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [
                {"place_id": "valid123", "name": "Valid Place", "vicinity": "Address"},
                {"name": "No Place ID"},  # Missing place_id
                {"place_id": "valid456", "name": "Another Valid", "vicinity": "Address 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        results = service.search_businesses(
            location="18.5204,73.8567",
            category="restaurant"
        )
        
        assert len(results) == 2  # Only valid results


class TestGetBusinessDetails:
    """Test business details retrieval."""
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_get_details_success(self, mock_get, service, mock_details_response):
        """Should retrieve and parse business details."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_details_response
        mock_get.return_value = mock_response
        
        result = service.get_business_details("ChIJ1234567890")
        
        assert result is not None
        assert result.place_id == "ChIJ1234567890"
        assert result.name == "Test Restaurant"
        assert result.phone == "+91 20 1234 5678"
        assert result.has_website is True
        assert result.website_url == "https://testrestaurant.com"
        assert result.city == "Pune"
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_get_details_not_found(self, mock_get, service):
        """Should return None when place not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "result": None}
        mock_get.return_value = mock_response
        
        result = service.get_business_details("invalid_place_id")
        
        assert result is None
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_get_details_without_website(self, mock_get, service):
        """Should handle businesses without websites."""
        response = {
            "status": "OK",
            "result": {
                "place_id": "ChIJ1234567890",
                "name": "No Website Business",
                "formatted_address": "123 St, Pune",
                "rating": 4.0,
                "user_ratings_total": 50,
                "types": ["restaurant"],
                "address_components": [
                    {"long_name": "Pune", "types": ["locality"]}
                ]
            }
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = response
        mock_get.return_value = mock_response
        
        result = service.get_business_details("ChIJ1234567890")
        
        assert result.has_website is False
        assert result.website_url is None


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_handles_rate_limit_response(self, mock_get, service):
        """Should raise RateLimitError on 429 status."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            service.search_businesses("18.5204,73.8567", "restaurant")
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_handles_over_query_limit(self, mock_get, service):
        """Should raise RateLimitError on OVER_QUERY_LIMIT status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OVER_QUERY_LIMIT"}
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitError, match="quota exceeded"):
            service.search_businesses("18.5204,73.8567", "restaurant")
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_handles_request_denied(self, mock_get, service):
        """Should raise GooglePlacesAPIError on REQUEST_DENIED."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "REQUEST_DENIED",
            "error_message": "Invalid API key"
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(GooglePlacesAPIError, match="API request denied"):
            service.search_businesses("18.5204,73.8567", "restaurant")
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_handles_timeout(self, mock_get, service):
        """Should raise GooglePlacesAPIError on timeout."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(GooglePlacesAPIError, match="timeout"):
            service.search_businesses("18.5204,73.8567", "restaurant")
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_handles_connection_error(self, mock_get, service):
        """Should raise GooglePlacesAPIError on connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(GooglePlacesAPIError, match="Request failed"):
            service.search_businesses("18.5204,73.8567", "restaurant")


class TestCategoryMapping:
    """Test category mapping functionality."""
    
    def test_map_restaurant_category(self, service):
        """Should map restaurant category correctly."""
        result = service._map_category_to_type("Restaurant")
        assert result == "restaurant"
    
    def test_map_school_category(self, service):
        """Should map school category correctly."""
        result = service._map_category_to_type("School")
        assert result == "school"
    
    def test_map_unknown_category(self, service):
        """Should return lowercase for unknown categories."""
        result = service._map_category_to_type("CustomType")
        assert result == "customtype"


class TestCityExtraction:
    """Test city extraction from address components."""
    
    def test_extract_city_from_locality(self, service):
        """Should extract city from locality component."""
        components = [
            {"long_name": "Pune", "types": ["locality", "political"]},
            {"long_name": "Maharashtra", "types": ["administrative_area_level_1"]}
        ]
        city = service._extract_city_from_components(components)
        assert city == "Pune"
    
    def test_extract_city_from_admin_area(self, service):
        """Should fallback to administrative_area_level_2."""
        components = [
            {"long_name": "Pune District", "types": ["administrative_area_level_2"]},
            {"long_name": "Maharashtra", "types": ["administrative_area_level_1"]}
        ]
        city = service._extract_city_from_components(components)
        assert city == "Pune District"
    
    def test_extract_city_from_address_string(self, service):
        """Should extract city from formatted address string."""
        address = "123 Main St, Pune, Maharashtra 411001"
        city = service._extract_city_from_address(address)
        assert city in address


class TestRefreshBusinessData:
    """Test business data refresh functionality."""
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_refresh_calls_get_details(self, mock_get, service, mock_details_response):
        """Should call get_business_details for refresh."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_details_response
        mock_get.return_value = mock_response
        
        result = service.refresh_business_data("ChIJ1234567890")
        
        assert result is not None
        assert result.place_id == "ChIJ1234567890"


class TestRequestCounting:
    """Test API request counting."""
    
    @patch('backend.app.services.google_places.requests.Session.get')
    def test_increments_request_count(self, mock_get, service, mock_search_response):
        """Should increment request count on each API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_search_response
        mock_get.return_value = mock_response
        
        initial_count = service._request_count
        service.search_businesses("18.5204,73.8567", "restaurant")
        
        assert service._request_count > initial_count
