import os
import random
import tempfile
import time
from io import BytesIO
from pathlib import Path

import requests
from locust import HttpUser, task, between
from PIL import Image
import numpy as np


def generate_synthetic_images():
    """Generate synthetic furniture images for testing"""
    furniture_types = ['almirah', 'chair', 'fridge', 'table', 'tv']
    synthetic_images = []
    
    for furniture_type in furniture_types:
        for i in range(5):  
            # Create a colored rectangle representing furniture
            color_map = {
                'almirah': (139, 69, 19),    # brown
                'chair': (160, 82, 45),      # saddle brown  
                'fridge': (192, 192, 192),   # silver
                'table': (205, 133, 63),     # peru
                'tv': (0, 0, 0)              # black
            }
            
            # Create image
            img = Image.new('RGB', (224, 224), color_map[furniture_type])
            
            # Add some noise/texture
            pixels = np.array(img)
            noise = np.random.randint(-30, 30, pixels.shape, dtype=np.int16)
            pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(pixels)
            
            # Convert to bytes
            img_byte_array = BytesIO()
            img.save(img_byte_array, format='JPEG')
            img_byte_array.seek(0)
            
            synthetic_images.append((
                f"test_{furniture_type}_{i}.jpg",
                img_byte_array.getvalue()
            ))
    
    return synthetic_images


class FurnitureAPIUser(HttpUser):
    """Normal user behavior - simulates typical usage"""
    wait_time = between(2, 5)
    weight = 3
    
    def on_start(self):
        """Initialize user session"""
        self.synthetic_images = generate_synthetic_images()
    
    @task(3)
    def predict_furniture(self):
        """Upload image for prediction"""
        try:
            image_name, image_data = random.choice(self.synthetic_images)
            
            with self.client.post(
                "/predict",
                files={"file": (image_name, image_data, "image/jpeg")},
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    result = response.json()
                    print(f"Prediction successful - {result.get('prediction', 'Unknown')} ({result.get('confidence', 0):.2f})")
                else:
                    print(f" Prediction failed - Status: {response.status_code} - Image: {image_name}")
                    response.failure(f"Prediction failed: {response.status_code}")
        except Exception as e:
            print(f"💥 Exception during prediction: {e}")

    @task(1)
    def health_check(self):
        """Check API health"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                print("🏠 Health check successful")
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(1) 
    def view_analytics(self):
        """Check analytics endpoint"""
        with self.client.get("/analytics", catch_response=True) as response:
            if response.status_code == 200:
                print("📊 Analytics accessed successfully")
            else:
                response.failure(f"Analytics failed: {response.status_code}")


class HeavyLoadUser(HttpUser):
    """Heavy load user - makes rapid predictions"""
    wait_time = between(0.5, 2)
    weight = 2
    
    def on_start(self):
        """Initialize user session"""
        self.synthetic_images = generate_synthetic_images()
    
    @task(5)
    def rapid_predict(self):
        """Make rapid predictions"""
        try:
            image_name, image_data = random.choice(self.synthetic_images)
            
            with self.client.post(
                "/predict",
                files={"file": (image_name, image_data, "image/jpeg")},
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    result = response.json()
                    print(f"⚡ Rapid prediction - {result.get('prediction', 'Unknown')}")
                else:
                    print(f"� Failed request: {response.status_code} - Time: {response.elapsed.total_seconds()*1000:.2f}ms")
                    response.failure(f"Failed: {response.status_code}")
        except Exception as e:
            print(f" Exception during rapid prediction: {e}")
    
    @task(1)
    def check_health(self):
        """Quick health checks"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")


# Configuration for different load testing scenarios
class StressTestUser(HttpUser):
    """Stress test user - minimal wait time between requests"""
    wait_time = between(0.1, 0.5)
    weight = 1
    
    def on_start(self):
        """Initialize user session"""
        self.synthetic_images = generate_synthetic_images()
    
    @task(10)
    def stress_predict(self):
        """Stress test with continuous predictions"""
        try:
            image_name, image_data = random.choice(self.synthetic_images)
            
            with self.client.post(
                "/predict",
                files={"file": (image_name, image_data, "image/jpeg")},
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    # Don't print every success to avoid spam
                    pass
                else:
                    print(f" Failed request: {response.status_code} - Time: {response.elapsed.total_seconds()*1000:.2f}ms")
                    response.failure(f"Failed: {response.status_code}")
        except Exception as e:
            print(f"� Exception during stress test: {e}")
    
    @task(1)
    def stress_health(self):
        """Stress test health endpoint"""  
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health failed: {response.status_code}")
