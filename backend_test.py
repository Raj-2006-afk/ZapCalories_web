#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for ZapCalories
Tests all backend endpoints systematically according to review request
"""

import requests
import json
import base64
from datetime import datetime, timezone
import sys
import os
from io import BytesIO
from PIL import Image
import time

# Backend URL from frontend environment
BACKEND_URL = "https://foodlens-201.preview.emergentagent.com/api"

class ZapCaloriesTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.auth_token = None
        self.user_id = None
        self.log_id = None
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'response_data': response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def set_auth_token(self, token):
        """Set authentication token for subsequent requests"""
        self.auth_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_result("Health Check", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unexpected status: {data}")
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        try:
            user_data = {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@example.com",
                "password": "securepass123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.auth_token = data['access_token']
                    self.user_id = data['user']['id']
                    self.set_auth_token(self.auth_token)
                    self.log_result("User Registration", True, f"Registered user: {data['user']['name']}")
                    return True
                else:
                    self.log_result("User Registration", False, f"Missing token or user data: {data}")
                    return False
            else:
                # Try login if user already exists
                login_data = {"email": user_data["email"], "password": user_data["password"]}
                login_response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.auth_token = data['access_token']
                    self.user_id = data['user']['id']
                    self.set_auth_token(self.auth_token)
                    self.log_result("User Registration", True, f"User exists, logged in: {data['user']['name']}")
                    return True
                else:
                    self.log_result("User Registration", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_user_login(self):
        """Test user login"""
        try:
            login_data = {
                "email": "sarah.johnson@example.com",
                "password": "securepass123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.log_result("User Login", True, f"Logged in user: {data['user']['name']}")
                    return True
                else:
                    self.log_result("User Login", False, f"Missing token or user data: {data}")
                    return False
            else:
                self.log_result("User Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
            return False

    def test_get_current_user(self):
        """Test get current user endpoint"""
        try:
            if not self.auth_token:
                self.log_result("Get Current User", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/auth/me")
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'email' in data:
                    self.log_result("Get Current User", True, f"Retrieved user: {data.get('name', 'Unknown')}")
                    return True
                else:
                    self.log_result("Get Current User", False, f"Invalid user data: {data}")
                    return False
            else:
                self.log_result("Get Current User", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Get Current User", False, f"Exception: {str(e)}")
            return False

    def test_profile_update(self):
        """Test profile update"""
        try:
            if not self.auth_token:
                self.log_result("Profile Update", False, "No auth token available")
                return False
                
            profile_data = {
                "age": 30,
                "gender": "male",
                "height": 175,
                "weight": 75,
                "goal_weight": 70,
                "activity_level": "moderate"
            }
            
            response = self.session.put(f"{BACKEND_URL}/profile", json=profile_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('age') == 30 and data.get('gender') == 'male':
                    self.log_result("Profile Update", True, f"Updated profile: {data.get('height')}cm, {data.get('weight')}kg")
                    return True
                else:
                    self.log_result("Profile Update", False, f"Profile not updated correctly: {data}")
                    return False
            else:
                self.log_result("Profile Update", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Profile Update", False, f"Exception: {str(e)}")
            return False

    def test_tdee_calculation(self):
        """Test TDEE calculation"""
        try:
            if not self.auth_token:
                self.log_result("TDEE Calculation", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/calculate-tdee")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['bmr', 'tdee', 'goal_calories', 'goal_type', 'protein_goal', 'carbs_goal', 'fat_goal']
                if all(field in data for field in required_fields):
                    bmr = data.get('bmr')
                    tdee = data.get('tdee')
                    goal_calories = data.get('goal_calories')
                    
                    if 1000 <= bmr <= 3000 and tdee >= bmr and goal_calories > 0:
                        self.log_result("TDEE Calculation", True, 
                                      f"BMR: {bmr}, TDEE: {tdee}, Goal: {goal_calories} cal, Type: {data.get('goal_type')}")
                        return True
                    else:
                        self.log_result("TDEE Calculation", False, f"Unrealistic values: BMR={bmr}, TDEE={tdee}")
                        return False
                else:
                    self.log_result("TDEE Calculation", False, f"Missing required fields: {data}")
                    return False
            else:
                self.log_result("TDEE Calculation", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("TDEE Calculation", False, f"Exception: {str(e)}")
            return False

    def test_pricing_plans(self):
        """Test pricing plans endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/pricing")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 3:
                    # Check if promo is active
                    promo_active = any(plan.get('is_promo_active', False) for plan in data)
                    if promo_active:
                        self.log_result("Pricing Plans", True, f"Retrieved {len(data)} plans with promo active")
                        return True
                    else:
                        self.log_result("Pricing Plans", False, "Promo not active as expected")
                        return False
                else:
                    self.log_result("Pricing Plans", False, f"Expected 3+ plans, got: {len(data) if isinstance(data, list) else type(data)}")
                    return False
            else:
                self.log_result("Pricing Plans", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Pricing Plans", False, f"Exception: {str(e)}")
            return False

    def test_subscription_status(self):
        """Test subscription status"""
        try:
            if not self.auth_token:
                self.log_result("Subscription Status", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/subscription/status")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['has_subscription', 'free_scans_used', 'free_scans_remaining', 'can_scan']
                if all(field in data for field in required_fields):
                    self.log_result("Subscription Status", True, 
                                  f"Free scans: {data.get('free_scans_remaining')}, Can scan: {data.get('can_scan')}")
                    return True
                else:
                    self.log_result("Subscription Status", False, f"Missing required fields: {data}")
                    return False
            else:
                self.log_result("Subscription Status", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Subscription Status", False, f"Exception: {str(e)}")
            return False

    def test_subscription_activation(self):
        """Test subscription activation (mock)"""
        try:
            if not self.auth_token:
                self.log_result("Subscription Activation", False, "No auth token available")
                return False
                
            response = self.session.post(f"{BACKEND_URL}/subscription/activate?plan_id=monthly")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'subscription_end' in data:
                    self.log_result("Subscription Activation", True, f"Activated monthly plan: {data.get('message')}")
                    return True
                else:
                    self.log_result("Subscription Activation", False, f"Activation failed: {data}")
                    return False
            else:
                self.log_result("Subscription Activation", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Subscription Activation", False, f"Exception: {str(e)}")
            return False

    def create_test_food_image(self):
        """Create a test food image in base64 format"""
        try:
            # Create a realistic food image (apple with texture)
            img = Image.new('RGB', (300, 300), color='white')
            
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Draw apple body with gradient effect
            for i in range(50):
                color_intensity = 255 - i * 2
                draw.ellipse([50+i//2, 70+i//2, 250-i//2, 250-i//2], 
                           fill=(color_intensity, 50, 50), outline=None)
            
            # Draw apple stem
            draw.rectangle([145, 40, 155, 70], fill=(101, 67, 33))
            
            # Draw apple leaf
            draw.ellipse([155, 35, 185, 65], fill=(34, 139, 34))
            
            # Add some texture spots
            for i in range(20):
                x, y = 100 + i * 7, 120 + (i % 3) * 30
                draw.ellipse([x, y, x+3, y+3], fill=(200, 30, 30))
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_base64
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None

    def test_food_analysis(self):
        """Test AI food analysis with scan limit check"""
        try:
            if not self.auth_token:
                self.log_result("Food Analysis", False, "No auth token available")
                return False
                
            # Create test image
            img_base64 = self.create_test_food_image()
            if not img_base64:
                self.log_result("Food Analysis", False, "Failed to create test image")
                return False
            
            request_data = {
                "image_base64": img_base64
            }
            
            response = self.session.post(f"{BACKEND_URL}/analyze-food", json=request_data)
            if response.status_code == 200:
                data = response.json()
                required_fields = ['food_name', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'serving_size', 'confidence', 'details']
                
                if all(field in data for field in required_fields):
                    calories = data.get('calories', 0)
                    confidence = data.get('confidence', 0)
                    
                    if calories >= 0 and 0 <= confidence <= 1:
                        self.log_result("Food Analysis", True, 
                                      f"Analyzed: {data.get('food_name')}, {calories} cal, confidence: {confidence:.2f}")
                        return True
                    else:
                        self.log_result("Food Analysis", False, f"Invalid values: calories={calories}, confidence={confidence}")
                        return False
                else:
                    self.log_result("Food Analysis", False, f"Missing required fields: {data}")
                    return False
            elif response.status_code == 403:
                # Check if it's scan limit reached
                data = response.json()
                if "scan limit" in data.get('detail', '').lower():
                    self.log_result("Food Analysis", True, f"Scan limit working correctly: {data.get('detail')}")
                    return True
                else:
                    self.log_result("Food Analysis", False, f"Unexpected 403 error: {data}")
                    return False
            else:
                self.log_result("Food Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Food Analysis", False, f"Exception: {str(e)}")
            return False

    def test_food_log_creation(self):
        """Test food log creation"""
        try:
            if not self.auth_token:
                self.log_result("Food Log Creation", False, "No auth token available")
                return False
                
            food_data = {
                "food_name": "Grilled Chicken Breast",
                "calories": 165.0,
                "protein": 31.0,
                "carbs": 0.0,
                "fat": 3.6,
                "fiber": 0.0,
                "serving_size": "100g",
                "meal_type": "lunch"
            }
            
            response = self.session.post(f"{BACKEND_URL}/food-log", json=food_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('food_name') == food_data['food_name'] and 'id' in data:
                    self.log_id = data['id']  # Store for sharing test
                    self.log_result("Food Log Creation", True, f"Logged: {data.get('food_name')} - {data.get('calories')} cal")
                    return True
                else:
                    self.log_result("Food Log Creation", False, f"Data mismatch: {data}")
                    return False
            else:
                self.log_result("Food Log Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Food Log Creation", False, f"Exception: {str(e)}")
            return False

    def test_food_log_retrieval(self):
        """Test food log retrieval"""
        try:
            if not self.auth_token:
                self.log_result("Food Log Retrieval", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/food-log")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Food Log Retrieval", True, f"Retrieved {len(data)} food log entries")
                    return True
                else:
                    self.log_result("Food Log Retrieval", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("Food Log Retrieval", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Food Log Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_daily_progress(self):
        """Test daily progress calculation"""
        try:
            if not self.auth_token:
                self.log_result("Daily Progress", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/daily-progress")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['date', 'total_calories', 'total_protein', 'total_carbs', 'total_fat', 'meal_count']
                
                if all(field in data for field in required_fields):
                    calories = data.get('total_calories', 0)
                    meal_count = data.get('meal_count', 0)
                    
                    self.log_result("Daily Progress", True, 
                                  f"Date: {data.get('date')}, Calories: {calories}, Meals: {meal_count}")
                    return True
                else:
                    self.log_result("Daily Progress", False, f"Missing required fields: {data}")
                    return False
            else:
                self.log_result("Daily Progress", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Daily Progress", False, f"Exception: {str(e)}")
            return False

    def test_achievements(self):
        """Test achievements system"""
        try:
            if not self.auth_token:
                self.log_result("Achievements", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/achievements")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    unlocked = sum(1 for ach in data if ach.get('unlocked', False))
                    self.log_result("Achievements", True, f"Retrieved {len(data)} achievements, {unlocked} unlocked")
                    return True
                else:
                    self.log_result("Achievements", False, f"Expected achievement list, got: {data}")
                    return False
            else:
                self.log_result("Achievements", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Achievements", False, f"Exception: {str(e)}")
            return False

    def test_user_stats(self):
        """Test user stats"""
        try:
            if not self.auth_token:
                self.log_result("User Stats", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/stats")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_scans', 'current_streak', 'total_points', 'level']
                if all(field in data for field in required_fields):
                    self.log_result("User Stats", True, 
                                  f"Level: {data.get('level')}, Points: {data.get('total_points')}, Streak: {data.get('current_streak')}")
                    return True
                else:
                    self.log_result("User Stats", False, f"Missing required fields: {data}")
                    return False
            else:
                self.log_result("User Stats", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Stats", False, f"Exception: {str(e)}")
            return False

    def test_leaderboard(self):
        """Test leaderboard"""
        try:
            response = self.session.get(f"{BACKEND_URL}/leaderboard")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Leaderboard", True, f"Retrieved leaderboard with {len(data)} users")
                    return True
                else:
                    self.log_result("Leaderboard", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("Leaderboard", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Leaderboard", False, f"Exception: {str(e)}")
            return False

    def test_meal_sharing(self):
        """Test meal sharing"""
        try:
            if not self.auth_token or not self.log_id:
                self.log_result("Meal Sharing", False, "No auth token or log ID available")
                return False
                
            share_data = {
                "log_id": self.log_id,
                "message": "Check out my healthy lunch!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/share-meal", json=share_data)
            if response.status_code == 200:
                data = response.json()
                if 'share_id' in data and 'share_url' in data:
                    share_id = data['share_id']
                    
                    # Test retrieving shared meal
                    shared_response = self.session.get(f"{BACKEND_URL}/shared/{share_id}")
                    if shared_response.status_code == 200:
                        shared_data = shared_response.json()
                        if 'food_name' in shared_data and 'shared_by' in shared_data:
                            self.log_result("Meal Sharing", True, f"Shared meal ID: {share_id}")
                            return True
                        else:
                            self.log_result("Meal Sharing", False, f"Invalid shared meal data: {shared_data}")
                            return False
                    else:
                        self.log_result("Meal Sharing", False, f"Failed to retrieve shared meal: {shared_response.status_code}")
                        return False
                else:
                    self.log_result("Meal Sharing", False, f"Missing share data: {data}")
                    return False
            else:
                self.log_result("Meal Sharing", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Meal Sharing", False, f"Exception: {str(e)}")
            return False

    def test_meal_suggestions(self):
        """Test AI meal suggestions"""
        try:
            if not self.auth_token:
                self.log_result("Meal Suggestions", False, "No auth token available")
                return False
                
            response = self.session.get(f"{BACKEND_URL}/meal-suggestions?meal_type=lunch")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Meal Suggestions", True, f"Retrieved {len(data)} meal suggestions")
                    return True
                else:
                    self.log_result("Meal Suggestions", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_result("Meal Suggestions", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Meal Suggestions", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("ZAPCALORIES BACKEND API TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        # Test in logical order matching review request
        tests = [
            # Authentication Flow
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Current User", self.test_get_current_user),
            
            # Profile & TDEE
            ("Profile Update", self.test_profile_update),
            ("TDEE Calculation", self.test_tdee_calculation),
            
            # Subscription
            ("Pricing Plans", self.test_pricing_plans),
            ("Subscription Status", self.test_subscription_status),
            ("Subscription Activation", self.test_subscription_activation),
            
            # Food Analysis & Logging
            ("Food Analysis", self.test_food_analysis),
            ("Food Log Creation", self.test_food_log_creation),
            ("Food Log Retrieval", self.test_food_log_retrieval),
            ("Daily Progress", self.test_daily_progress),
            
            # Gamification
            ("Achievements", self.test_achievements),
            ("User Stats", self.test_user_stats),
            ("Leaderboard", self.test_leaderboard),
            
            # Social
            ("Meal Sharing", self.test_meal_sharing),
            
            # AI Suggestions
            ("Meal Suggestions", self.test_meal_suggestions),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Unexpected error: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        print()
        
        if failed > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['details']}")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = ZapCaloriesTester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    sys.exit(0 if failed == 0 else 1)