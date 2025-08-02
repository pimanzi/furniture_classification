#!/usr/bin/env python3
"""
Quick Load Test Demo
A simplified demonstration of load testing the Furniture AI model
"""

import time
import requests
import threading
import tempfile
import numpy as np
from PIL import Image
from io import BytesIO
import json
from datetime import datetime
import statistics


class LoadTestDemo:
    def __init__(self, base_url="http://localhost:8515"):
        self.base_url = base_url
        self.results = []
        self.test_images = self.create_test_images()
    
    def create_test_images(self):
        """Create a few test images for load testing."""
        images = []
        
        for i in range(3):
            # Create synthetic image
            img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            images.append({
                'name': f'demo_test_{i}.jpg',
                'data': img_bytes.getvalue()
            })
        
        return images
    
    def single_request(self, user_id):
        """Simulate a single user making a request."""
        import random
        
        test_image = random.choice(self.test_images)
        start_time = time.time()
        
        try:
            # Test basic connectivity first
            response = requests.get(self.base_url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"App not available: {response.status_code}")
            
            # Measure just the app response time (not actual prediction since that requires Streamlit interaction)
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'response_time_ms': response_time,
                'success': True,
                'status_code': response.status_code,
                'image_name': test_image['name']
            }
            
            print(f" User {user_id}: {response_time:.1f}ms - {test_image['name']}")
            
        except requests.exceptions.Timeout:
            result = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'response_time_ms': 10000,  # Timeout
                'success': False,
                'status_code': 0,
                'error': 'timeout',
                'image_name': test_image['name']
            }
            print(f" User {user_id}: TIMEOUT - {test_image['name']}")
            
        except Exception as e:
            result = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'response_time_ms': 0,
                'success': False,
                'status_code': 0,
                'error': str(e),
                'image_name': test_image['name']
            }
            print(f" User {user_id}: ERROR - {str(e)}")
        
        self.results.append(result)
    
    def run_concurrent_test(self, num_users=5, requests_per_user=3):
        """Run a concurrent load test."""
        print(f" Starting Load Test Demo")
        print(f" Users: {num_users}")
        print(f" Requests per user: {requests_per_user}")
        print(f" Target URL: {self.base_url}")
        print("=" * 50)
        
        self.results = []
        threads = []
        
        start_time = time.time()
        
        # Create and start threads
        for user_id in range(num_users):
            for request_num in range(requests_per_user):
                thread = threading.Thread(
                    target=self.single_request,
                    args=(f"{user_id}-{request_num}",)
                )
                threads.append(thread)
                thread.start()
                
                # Small delay between starting threads to simulate realistic timing
                time.sleep(0.1)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Analyze results
        self.analyze_results(total_time)
    
    def analyze_results(self, total_time):
        """Analyze and display test results."""
        if not self.results:
            print(" No results to analyze")
            return
        
        print("\n" + "=" * 50)
        print(" LOAD TEST RESULTS")
        print("=" * 50)
        
        # Basic statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100
        
        print(f" Total Requests: {total_requests}")
        print(f" Successful: {successful_requests}")
        print(f" Failed: {failed_requests}")
        print(f" Success Rate: {success_rate:.1f}%")
        print(f" Total Test Time: {total_time:.2f} seconds")
        
        # Response time analysis
        successful_times = [r['response_time_ms'] for r in self.results if r['success']]
        
        if successful_times:
            avg_response_time = statistics.mean(successful_times)
            median_response_time = statistics.median(successful_times)
            min_response_time = min(successful_times)
            max_response_time = max(successful_times)
            
            print(f"\n⚡ Response Time Analysis:")
            print(f"   Average: {avg_response_time:.1f}ms")
            print(f"   Median: {median_response_time:.1f}ms")
            print(f"   Min: {min_response_time:.1f}ms")
            print(f"   Max: {max_response_time:.1f}ms")
            
            # Performance assessment
            if avg_response_time < 1000:
                print(f"🟢 Performance: EXCELLENT (< 1s)")
            elif avg_response_time < 3000:
                print(f"🟡 Performance: GOOD (1-3s)")
            elif avg_response_time < 5000:
                print(f"🟠 Performance: ACCEPTABLE (3-5s)")
            else:
                print(f"🔴 Performance: POOR (> 5s)")
        
        # Throughput calculation
        requests_per_second = total_requests / total_time
        print(f" Throughput: {requests_per_second:.2f} requests/second")
        
        # Error analysis
        if failed_requests > 0:
            print(f"\n Error Analysis:")
            error_types = {}
            for result in self.results:
                if not result['success']:
                    error = result.get('error', 'unknown')
                    error_types[error] = error_types.get(error, 0) + 1
            
            for error, count in error_types.items():
                print(f"   {error}: {count} occurrences")
        
        # Save results
        self.save_results()
        
        print("\n" + "=" * 50)
        print(" Load test completed!")
        
        # Recommendations
        self.provide_recommendations(success_rate, avg_response_time if successful_times else 0)
    
    def provide_recommendations(self, success_rate, avg_response_time):
        """Provide performance recommendations based on results."""
        print("\n RECOMMENDATIONS:")
        
        if success_rate < 95:
            print("🔧 Low success rate detected:")
            print("   - Check application stability")
            print("   - Verify server resources")
            print("   - Consider error handling improvements")
        
        if avg_response_time > 5000:
            print( " High response times detected:")
            print("   - Consider model optimization")
            print("   - Check system resources (CPU, Memory)")
            print("   - Implement caching mechanisms")
            print("   - Consider using a smaller/faster model")
        
        if avg_response_time > 2000:
            print("⚡ Response time optimization suggestions:")
            print("   - Profile the prediction pipeline")
            print("   - Optimize image preprocessing")
            print("   - Consider GPU acceleration")
            print("   - Implement request queuing")
        
        print(" For production deployment:")
        print("   - Run full Locust tests with the provided scripts")
        print("   - Monitor system resources continuously")
        print("   - Set up proper load balancing")
        print("   - Implement auto-scaling if possible")
    
    def save_results(self):
        """Save test results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_testing/demo_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f" Results saved to: {filename}")
        except Exception as e:
            print(f" Could not save results: {e}")


def main():
    print(" Furniture AI Load Testing Demo")
    print("=================================")
    
    # Check if app is running
    demo = LoadTestDemo()
    
    try:
        response = requests.get(demo.base_url, timeout=5)
        if response.status_code != 200:
            print(f" App not responding properly (status: {response.status_code})")
            print(" Please ensure the Streamlit app is running on port 8515")
            return
    except Exception as e:
        print(f" Cannot connect to app: {e}")
        print(" Please start the Streamlit app first:")
        print("   streamlit run app.py --server.port 8515")
        return
    
    print(f"✅ App is running at {demo.base_url}")
    print()
    
    # Run different test scenarios
    print(" Test Scenario 1: Light Load (5 users, 2 requests each)")
    demo.run_concurrent_test(num_users=5, requests_per_user=2)
    
    print("\n" + "="*50)
    input("Press Enter to continue to the next test scenario...")
    
    print(" Test Scenario 2: Medium Load (10 users, 3 requests each)")
    demo.run_concurrent_test(num_users=10, requests_per_user=3)


if __name__ == "__main__":
    main()
