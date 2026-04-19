"""Simple load test without external dependencies.

Tests basic concurrent user handling using Python's threading.
Requirement 13.3: Minimum 100 concurrent users

Usage:
    python tests/simple_load_test.py
"""
import requests
import threading
import time
from datetime import datetime
from collections import defaultdict
import statistics


class LoadTester:
    """Simple load tester for concurrent requests."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = defaultdict(list)
        self.errors = []
        self.lock = threading.Lock()
    
    def make_request(self, endpoint, name):
        """Make a single request and record timing."""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            elapsed = time.time() - start_time
            
            with self.lock:
                self.results[name].append({
                    'elapsed': elapsed,
                    'status': response.status_code,
                    'success': response.status_code == 200
                })
        except Exception as e:
            with self.lock:
                self.errors.append({
                    'endpoint': endpoint,
                    'error': str(e)
                })
    
    def simulate_user(self, user_id, duration=30):
        """Simulate a single user for specified duration."""
        end_time = time.time() + duration
        
        while time.time() < end_time:
            # Simulate realistic user behavior
            actions = [
                ("/api/health", "Health Check"),
                ("/api/leads/map", "Map Load"),
                ("/api/leads/search?query=restaurant", "Search Results"),
            ]
            
            for endpoint, name in actions:
                self.make_request(endpoint, name)
                time.sleep(0.5)  # Small delay between actions
    
    def run_test(self, num_users=100, duration=30):
        """Run load test with specified number of concurrent users."""
        print(f"\n{'='*60}")
        print(f"Starting Load Test")
        print(f"{'='*60}")
        print(f"Base URL: {self.base_url}")
        print(f"Concurrent Users: {num_users}")
        print(f"Test Duration: {duration} seconds")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Create and start threads
        threads = []
        start_time = time.time()
        
        for i in range(num_users):
            thread = threading.Thread(
                target=self.simulate_user,
                args=(i, duration)
            )
            threads.append(thread)
            thread.start()
            
            # Ramp up: start 10 users per second
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        print(f"All {num_users} users started. Running test...")
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Print results
        self.print_results(total_time)
    
    def print_results(self, total_time):
        """Print test results and analysis."""
        print(f"\n{'='*60}")
        print(f"Load Test Results")
        print(f"{'='*60}")
        print(f"Total Test Time: {total_time:.2f} seconds\n")
        
        # Overall statistics
        total_requests = sum(len(results) for results in self.results.values())
        total_errors = len(self.errors)
        
        print(f"Total Requests: {total_requests}")
        print(f"Total Errors: {total_errors}")
        
        if total_requests > 0:
            print(f"Success Rate: {((total_requests - total_errors) / total_requests * 100):.2f}%")
            print(f"Requests/Second: {(total_requests / total_time):.2f}\n")
        else:
            print(f"Success Rate: 0.00% (No successful requests)")
            print(f"Requests/Second: 0.00\n")
            print(f"\n⚠️ WARNING: All requests failed!")
            print(f"Please check:")
            print(f"  1. Is the backend server running? (uvicorn app.main:app)")
            print(f"  2. Is it accessible at {self.base_url}?")
            print(f"  3. Check error details below.\n")
        
        # Per-endpoint statistics
        print(f"{'Endpoint':<30} {'Count':<8} {'Avg (s)':<10} {'Min (s)':<10} {'Max (s)':<10} {'Target':<10} {'Status'}")
        print(f"{'-'*100}")
        
        targets = {
            "Map Load": 2.0,
            "Search Results": 1.0,
            "Health Check": 1.0
        }
        
        for name, results in sorted(self.results.items()):
            if not results:
                continue
            
            times = [r['elapsed'] for r in results]
            successes = sum(1 for r in results if r['success'])
            
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            target = targets.get(name, 0)
            
            # Determine status
            if target > 0:
                if avg_time <= target:
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
            else:
                status = "N/A"
            
            print(f"{name:<30} {len(results):<8} {avg_time:<10.3f} {min_time:<10.3f} {max_time:<10.3f} {target:<10.1f} {status}")
        
        # Error summary
        if self.errors:
            print(f"\n{'='*60}")
            print(f"Errors ({len(self.errors)} total):")
            print(f"{'='*60}")
            error_counts = defaultdict(int)
            for error in self.errors:
                error_counts[error['error']] += 1
            
            for error, count in error_counts.items():
                print(f"  {error}: {count} occurrences")
        
        # Performance target analysis
        if total_requests > 0:
            print(f"\n{'='*60}")
            print(f"Performance Target Analysis (Requirement 13.3)")
            print(f"{'='*60}")
            
            all_passed = True
            for name, target in targets.items():
                if name in self.results and self.results[name]:
                    times = [r['elapsed'] for r in self.results[name]]
                    avg_time = statistics.mean(times)
                    passed = avg_time <= target
                    all_passed = all_passed and passed
                    
                    status = "✅ PASS" if passed else "❌ FAIL"
                    print(f"{name}: {avg_time:.3f}s (target: {target}s) {status}")
            
            print(f"\n{'='*60}")
            if all_passed and total_errors < total_requests * 0.01:  # Less than 1% error rate
                print("✅ LOAD TEST PASSED")
                print("System successfully handles 100+ concurrent users")
            else:
                print("⚠️ LOAD TEST NEEDS OPTIMIZATION")
                print("Some performance targets not met or high error rate")
            print(f"{'='*60}\n")
        else:
            print(f"\n{'='*60}")
            print("❌ LOAD TEST FAILED")
            print("No successful requests - server may not be running")
            print(f"{'='*60}\n")


def main():
    """Run the load test."""
    tester = LoadTester()
    
    # Test with 100 concurrent users for 30 seconds
    tester.run_test(num_users=100, duration=30)


if __name__ == "__main__":
    main()
