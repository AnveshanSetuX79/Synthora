"""Lightweight load test to verify basic functionality.

Starts with fewer users and ramps up gradually.
"""
import requests
import threading
import time
from datetime import datetime


class LightLoadTester:
    """Lightweight load tester with gradual ramp-up."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.success_count = 0
        self.error_count = 0
        self.response_times = []
        self.lock = threading.Lock()
    
    def make_request(self, endpoint):
        """Make a single request."""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            elapsed = time.time() - start_time
            
            with self.lock:
                if response.status_code == 200:
                    self.success_count += 1
                    self.response_times.append(elapsed)
                else:
                    self.error_count += 1
        except Exception as e:
            with self.lock:
                self.error_count += 1
            print(f"Error: {str(e)}")
    
    def simulate_user(self, user_id, num_requests=5):
        """Simulate a single user making a few requests."""
        for i in range(num_requests):
            # Use the fast health endpoint
            self.make_request("/api/health")
            time.sleep(0.5)  # Reduced wait between requests
    
    def run_test(self, max_users=100, ramp_up_time=10):
        """Run load test with gradual ramp-up."""
        print(f"\n{'='*60}")
        print(f"Lightweight Load Test")
        print(f"{'='*60}")
        print(f"Base URL: {self.base_url}")
        print(f"Max Concurrent Users: {max_users}")
        print(f"Ramp-up Time: {ramp_up_time} seconds")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Test single request first
        print("Testing single request...")
        start = time.time()
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=30)
            elapsed = time.time() - start
            print(f"✅ Single request successful: {elapsed:.3f}s (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Single request failed: {str(e)}")
            print("\nServer may not be ready. Please check:")
            print("  1. Is the server running?")
            print("  2. Check server logs for errors")
            return
        
        print(f"\nStarting gradual ramp-up to {max_users} users...")
        
        threads = []
        start_time = time.time()
        
        # Gradual ramp-up
        users_per_second = max_users / ramp_up_time
        
        for i in range(max_users):
            thread = threading.Thread(
                target=self.simulate_user,
                args=(i, 3)  # Each user makes 3 requests
            )
            threads.append(thread)
            thread.start()
            
            # Gradual ramp-up
            if (i + 1) % int(users_per_second) == 0:
                time.sleep(1)
                print(f"  Started {i + 1}/{max_users} users...")
        
        print(f"\nAll {max_users} users started. Waiting for completion...")
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Print results
        self.print_results(total_time, max_users)
    
    def print_results(self, total_time, max_users):
        """Print test results."""
        print(f"\n{'='*60}")
        print(f"Load Test Results")
        print(f"{'='*60}")
        print(f"Total Test Time: {total_time:.2f} seconds")
        print(f"Max Concurrent Users: {max_users}")
        print(f"Total Successful Requests: {self.success_count}")
        print(f"Total Failed Requests: {self.error_count}")
        
        total_requests = self.success_count + self.error_count
        if total_requests > 0:
            success_rate = (self.success_count / total_requests) * 100
            print(f"Success Rate: {success_rate:.2f}%")
            print(f"Requests/Second: {total_requests / total_time:.2f}")
        
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            min_time = min(self.response_times)
            max_time = max(self.response_times)
            
            print(f"\nResponse Times:")
            print(f"  Average: {avg_time:.3f}s")
            print(f"  Min: {min_time:.3f}s")
            print(f"  Max: {max_time:.3f}s")
            
            # Check target
            target = 1.0
            if avg_time <= target:
                print(f"  Target (1s): ✅ PASS")
            else:
                print(f"  Target (1s): ❌ FAIL")
        
        print(f"\n{'='*60}")
        if self.success_count >= max_users * 2 and self.error_count < total_requests * 0.05:
            print("✅ LOAD TEST PASSED")
            print(f"System handled {max_users} concurrent users successfully")
        else:
            print("⚠️ LOAD TEST NEEDS INVESTIGATION")
            print("High error rate or insufficient successful requests")
        print(f"{'='*60}\n")


def main():
    """Run the lightweight load test."""
    tester = LightLoadTester()
    
    # Start with 10 users, then try more
    print("Phase 1: Testing with 10 concurrent users...")
    tester.run_test(max_users=10, ramp_up_time=5)
    
    # If successful, try more
    if tester.success_count > 0 and tester.error_count < 5:
        print("\n" + "="*60)
        print("Phase 1 successful! Proceeding to Phase 2...")
        print("="*60)
        
        tester2 = LightLoadTester()
        print("\nPhase 2: Testing with 50 concurrent users...")
        tester2.run_test(max_users=50, ramp_up_time=10)
        
        if tester2.success_count > 0 and tester2.error_count < tester2.success_count * 0.1:
            print("\n" + "="*60)
            print("Phase 2 successful! Proceeding to Phase 3...")
            print("="*60)
            
            tester3 = LightLoadTester()
            print("\nPhase 3: Testing with 100 concurrent users...")
            tester3.run_test(max_users=100, ramp_up_time=20)


if __name__ == "__main__":
    main()
