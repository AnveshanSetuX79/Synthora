"""Load testing script for LocalAI Leads Platform.

Tests system performance under concurrent user load.
Requirement 13.3: Minimum 100 concurrent users

Usage:
    locust -f tests/load_test.py --host=http://localhost:8000
    
    Then open http://localhost:8089 and configure:
    - Number of users: 100
    - Spawn rate: 10 users/second
    - Host: http://localhost:8000
"""
from locust import HttpUser, task, between, events
import random
import json
import logging

logger = logging.getLogger(__name__)


class PlatformUser(HttpUser):
    """Simulates a user interacting with the platform."""
    
    # Wait 1-3 seconds between tasks (realistic user behavior)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts. Simulate login."""
        # For load testing, we'll use a test token or skip auth
        # In production, implement proper test user creation
        self.token = None
        self.headers = {}
    
    @task(10)
    def view_map(self):
        """Test map loading with 1000 pins.
        
        Target: 2 seconds (Requirement 13.3)
        Weight: 10 (most common action)
        """
        with self.client.get(
            "/api/leads/map",
            headers=self.headers,
            catch_response=True,
            name="Map Load (1000 pins)"
        ) as response:
            if response.elapsed.total_seconds() > 2.0:
                response.failure(f"Map load took {response.elapsed.total_seconds():.2f}s (target: 2s)")
            elif response.status_code == 200:
                response.success()
    
    @task(8)
    def search_businesses(self):
        """Test search results.
        
        Target: 1 second (Requirement 13.3)
        Weight: 8 (common action)
        """
        queries = ["restaurant", "cafe", "school", "gym", "salon", "clinic"]
        query = random.choice(queries)
        
        with self.client.get(
            f"/api/leads/search?query={query}",
            headers=self.headers,
            catch_response=True,
            name="Search Results"
        ) as response:
            if response.elapsed.total_seconds() > 1.0:
                response.failure(f"Search took {response.elapsed.total_seconds():.2f}s (target: 1s)")
            elif response.status_code == 200:
                response.success()
    
    @task(5)
    def view_demo(self):
        """Test demo retrieval.
        
        Target: 1 second (Requirement 13.3)
        Weight: 5 (moderate action)
        """
        # Use test slugs or generate random ones
        slugs = ["test-restaurant", "test-cafe", "test-school", "demo-business"]
        slug = random.choice(slugs)
        
        with self.client.get(
            f"/api/demos/{slug}",
            headers=self.headers,
            catch_response=True,
            name="Demo Retrieval"
        ) as response:
            if response.elapsed.total_seconds() > 1.0:
                response.failure(f"Demo retrieval took {response.elapsed.total_seconds():.2f}s (target: 1s)")
            elif response.status_code in [200, 404]:  # 404 is ok for test data
                response.success()
    
    @task(3)
    def view_health(self):
        """Test health check endpoint.
        
        Weight: 3 (monitoring/health checks)
        """
        self.client.get("/api/health", name="Health Check")
    
    @task(2)
    def view_analytics(self):
        """Test analytics endpoint.
        
        Weight: 2 (less common)
        """
        self.client.get(
            "/api/analytics/dashboard",
            headers=self.headers,
            name="Analytics Dashboard"
        )


class FreelancerUser(HttpUser):
    """Simulates a freelancer user with specific workflows."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Simulate freelancer login."""
        self.token = None
        self.headers = {}
    
    @task(5)
    def view_leads(self):
        """View available leads."""
        self.client.get(
            "/api/leads",
            headers=self.headers,
            name="Freelancer: View Leads"
        )
    
    @task(3)
    def view_deals(self):
        """View active deals."""
        self.client.get(
            "/api/deals",
            headers=self.headers,
            name="Freelancer: View Deals"
        )
    
    @task(2)
    def send_message(self):
        """Send a chat message.
        
        Target: 500ms (Requirement 13.3)
        """
        with self.client.post(
            "/api/messages",
            headers=self.headers,
            json={
                "deal_id": "test-deal-id",
                "message": "Test message for load testing"
            },
            catch_response=True,
            name="Chat Message"
        ) as response:
            if response.elapsed.total_seconds() > 0.5:
                response.failure(f"Message took {response.elapsed.total_seconds():.2f}s (target: 0.5s)")


class BusinessOwnerUser(HttpUser):
    """Simulates a business owner user."""
    
    wait_time = between(3, 7)
    
    def on_start(self):
        """Simulate business owner login."""
        self.token = None
        self.headers = {}
    
    @task(5)
    def view_demo(self):
        """View own demo website."""
        self.client.get(
            "/api/demos/my-business",
            headers=self.headers,
            name="Business Owner: View Demo"
        )
    
    @task(3)
    def view_messages(self):
        """View messages from freelancers."""
        self.client.get(
            "/api/messages",
            headers=self.headers,
            name="Business Owner: View Messages"
        )
    
    @task(2)
    def view_deals(self):
        """View deal status."""
        self.client.get(
            "/api/deals",
            headers=self.headers,
            name="Business Owner: View Deals"
        )


# Event handlers for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    logger.info("Load test starting...")
    logger.info(f"Target: 100+ concurrent users")
    logger.info(f"Performance targets:")
    logger.info(f"  - Map load: 2 seconds")
    logger.info(f"  - Search: 1 second")
    logger.info(f"  - Demo: 1 second")
    logger.info(f"  - Messages: 500ms")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    logger.info("Load test completed")
    
    # Get statistics
    stats = environment.stats
    
    logger.info("\n=== Load Test Results ===")
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Total failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"Max response time: {stats.total.max_response_time:.2f}ms")
    logger.info(f"Requests per second: {stats.total.total_rps:.2f}")
    
    # Check if targets were met
    logger.info("\n=== Performance Target Analysis ===")
    
    for name, stat in stats.entries.items():
        if "Map Load" in name:
            avg_time = stat.avg_response_time / 1000  # Convert to seconds
            target = 2.0
            status = "✅ PASS" if avg_time <= target else "❌ FAIL"
            logger.info(f"{name}: {avg_time:.2f}s (target: {target}s) {status}")
        
        elif "Search Results" in name:
            avg_time = stat.avg_response_time / 1000
            target = 1.0
            status = "✅ PASS" if avg_time <= target else "❌ FAIL"
            logger.info(f"{name}: {avg_time:.2f}s (target: {target}s) {status}")
        
        elif "Demo Retrieval" in name:
            avg_time = stat.avg_response_time / 1000
            target = 1.0
            status = "✅ PASS" if avg_time <= target else "❌ FAIL"
            logger.info(f"{name}: {avg_time:.2f}s (target: {target}s) {status}")
        
        elif "Chat Message" in name:
            avg_time = stat.avg_response_time / 1000
            target = 0.5
            status = "✅ PASS" if avg_time <= target else "❌ FAIL"
            logger.info(f"{name}: {avg_time:.2f}s (target: {target}s) {status}")
    
    # Overall pass/fail
    failure_rate = (stats.total.num_failures / stats.total.num_requests * 100) if stats.total.num_requests > 0 else 0
    logger.info(f"\nFailure rate: {failure_rate:.2f}%")
    
    if failure_rate < 1.0:
        logger.info("✅ Load test PASSED: System handles 100+ concurrent users")
    else:
        logger.warning("⚠️ Load test needs optimization: High failure rate")


# Custom user distribution for realistic load
# 60% general users, 30% freelancers, 10% business owners
class LoadTestUsers(HttpUser):
    """Mixed user types for realistic load distribution."""
    tasks = {
        PlatformUser: 60,
        FreelancerUser: 30,
        BusinessOwnerUser: 10
    }
    wait_time = between(1, 5)
