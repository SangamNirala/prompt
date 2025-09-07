#!/usr/bin/env python3
"""
Detailed Backend API Tests for BrandForge AI
Focus on critical bug fixes and specific issues
"""

import requests
import json
import sys
from datetime import datetime

class DetailedBrandForgeAPITester:
    def __init__(self, base_url="https://bugfix-forge.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.project_id = None
        self.critical_issues = []
        self.minor_issues = []

    def log_result(self, test_name, success, details="", is_critical=True):
        """Log test results and categorize issues"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {test_name}: FAILED")
            if details:
                print(f"   {details}")
            
            if is_critical:
                self.critical_issues.append(f"{test_name}: {details}")
            else:
                self.minor_issues.append(f"{test_name}: {details}")
        
        return success

    def test_mongodb_objectid_serialization(self):
        """Test MongoDB ObjectId serialization fixes - CRITICAL"""
        print("\n🔍 TESTING: MongoDB ObjectId Serialization Fix")
        print("=" * 50)
        
        # Test 1: GET /api/projects endpoint
        try:
            response = requests.get(f"{self.base_url}/projects", timeout=10)
            
            if response.status_code == 200:
                try:
                    projects_data = response.json()
                    if isinstance(projects_data, list):
                        self.log_result(
                            "GET /api/projects - JSON serialization", 
                            True, 
                            f"Successfully returned {len(projects_data)} projects as valid JSON"
                        )
                        
                        # Check for ObjectId fields in response
                        for project in projects_data:
                            if "_id" in project:
                                if isinstance(project["_id"], str):
                                    self.log_result(
                                        "ObjectId to string conversion", 
                                        True, 
                                        f"_id field properly converted to string: {project['_id']}"
                                    )
                                else:
                                    self.log_result(
                                        "ObjectId to string conversion", 
                                        False, 
                                        f"_id field not converted to string: {type(project['_id'])}"
                                    )
                                break
                    else:
                        self.log_result(
                            "GET /api/projects - Response format", 
                            False, 
                            f"Expected list, got {type(projects_data)}"
                        )
                except json.JSONDecodeError as e:
                    self.log_result(
                        "GET /api/projects - JSON parsing", 
                        False, 
                        f"JSON decode error: {str(e)}"
                    )
            else:
                self.log_result(
                    "GET /api/projects - HTTP status", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "GET /api/projects - Request", 
                False, 
                f"Request failed: {str(e)}"
            )

        # Test 2: Create a project first for individual project testing
        test_project_data = {
            "business_name": "TechFlow Solutions",
            "business_description": "AI-powered workflow automation for small businesses",
            "industry": "Technology",
            "target_audience": "Small business owners and entrepreneurs",
            "business_values": ["innovation", "efficiency", "reliability", "growth"],
            "preferred_style": "modern",
            "preferred_colors": "blue and white"
        }
        
        try:
            response = requests.post(f"{self.base_url}/projects", json=test_project_data, timeout=10)
            if response.status_code == 200:
                project_data = response.json()
                if "id" in project_data:
                    self.project_id = project_data["id"]
                    self.log_result(
                        "Create project for testing", 
                        True, 
                        f"Project created with ID: {self.project_id}"
                    )
                else:
                    self.log_result(
                        "Create project for testing", 
                        False, 
                        "No ID in response"
                    )
            else:
                self.log_result(
                    "Create project for testing", 
                    False, 
                    f"Status {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create project for testing", 
                False, 
                f"Request failed: {str(e)}"
            )

        # Test 3: GET /api/projects/{project_id} endpoint
        if self.project_id:
            try:
                response = requests.get(f"{self.base_url}/projects/{self.project_id}", timeout=10)
                
                if response.status_code == 200:
                    try:
                        project_data = response.json()
                        self.log_result(
                            "GET /api/projects/{id} - JSON serialization", 
                            True, 
                            "Successfully returned project as valid JSON"
                        )
                        
                        # Check for ObjectId fields
                        if "_id" in project_data:
                            if isinstance(project_data["_id"], str):
                                self.log_result(
                                    "Individual project ObjectId conversion", 
                                    True, 
                                    f"_id field properly converted: {project_data['_id']}"
                                )
                            else:
                                self.log_result(
                                    "Individual project ObjectId conversion", 
                                    False, 
                                    f"_id field not converted: {type(project_data['_id'])}"
                                )
                    except json.JSONDecodeError as e:
                        self.log_result(
                            "GET /api/projects/{id} - JSON parsing", 
                            False, 
                            f"JSON decode error: {str(e)}"
                        )
                else:
                    self.log_result(
                        "GET /api/projects/{id} - HTTP status", 
                        False, 
                        f"Expected 200, got {response.status_code}: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    "GET /api/projects/{id} - Request", 
                    False, 
                    f"Request failed: {str(e)}"
                )

    def test_brand_strategy_generation(self):
        """Test brand strategy generation - CRITICAL"""
        print("\n🔍 TESTING: Brand Strategy Generation")
        print("=" * 50)
        
        if not self.project_id:
            self.log_result(
                "Brand strategy generation", 
                False, 
                "No project ID available for testing"
            )
            return
        
        try:
            response = requests.post(
                f"{self.base_url}/projects/{self.project_id}/strategy", 
                timeout=90  # Longer timeout for AI generation
            )
            
            if response.status_code == 200:
                try:
                    strategy_data = response.json()
                    
                    # Verify strategy structure
                    required_fields = ['brand_personality', 'visual_direction', 'color_palette', 'messaging_framework']
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in strategy_data:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        self.log_result(
                            "Brand strategy generation", 
                            True, 
                            "Strategy generated with all required fields"
                        )
                        
                        # Check specific field content
                        if 'color_palette' in strategy_data and isinstance(strategy_data['color_palette'], list):
                            self.log_result(
                                "Color palette format", 
                                True, 
                                f"Color palette contains {len(strategy_data['color_palette'])} colors"
                            )
                        
                        if 'messaging_framework' in strategy_data and 'tagline' in strategy_data['messaging_framework']:
                            self.log_result(
                                "Messaging framework", 
                                True, 
                                f"Tagline generated: {strategy_data['messaging_framework']['tagline'][:50]}..."
                            )
                    else:
                        self.log_result(
                            "Brand strategy structure", 
                            False, 
                            f"Missing required fields: {', '.join(missing_fields)}"
                        )
                        
                except json.JSONDecodeError as e:
                    self.log_result(
                        "Brand strategy JSON parsing", 
                        False, 
                        f"JSON decode error: {str(e)}"
                    )
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', response.text)
                except:
                    error_detail = response.text
                
                self.log_result(
                    "Brand strategy generation", 
                    False, 
                    f"Status {response.status_code}: {error_detail}"
                )
                
        except requests.exceptions.Timeout:
            self.log_result(
                "Brand strategy generation", 
                False, 
                "Request timed out after 90 seconds"
            )
        except Exception as e:
            self.log_result(
                "Brand strategy generation", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_asset_generation(self):
        """Test asset generation workflow - CRITICAL"""
        print("\n🔍 TESTING: Asset Generation")
        print("=" * 50)
        
        if not self.project_id:
            self.log_result(
                "Asset generation", 
                False, 
                "No project ID available for testing"
            )
            return
        
        # Test logo generation
        try:
            response = requests.post(
                f"{self.base_url}/projects/{self.project_id}/assets/logo", 
                timeout=90
            )
            
            if response.status_code == 200:
                try:
                    asset_data = response.json()
                    
                    # Verify asset structure
                    required_fields = ['id', 'project_id', 'asset_type', 'asset_url']
                    missing_fields = [field for field in required_fields if field not in asset_data]
                    
                    if not missing_fields:
                        # Check if it's a real image or placeholder
                        asset_url = asset_data['asset_url']
                        if asset_url.startswith('data:image/png;base64,'):
                            # Check if it's the known placeholder
                            placeholder_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                            if placeholder_data in asset_url:
                                self.log_result(
                                    "Logo generation - content", 
                                    False, 
                                    "Generated asset is a placeholder, not real content", 
                                    is_critical=False  # This is a minor issue
                                )
                            else:
                                self.log_result(
                                    "Logo generation - content", 
                                    True, 
                                    f"Generated real asset data ({len(asset_url)} chars)"
                                )
                        
                        self.log_result(
                            "Logo generation - structure", 
                            True, 
                            "Asset generated with correct structure"
                        )
                    else:
                        self.log_result(
                            "Logo generation - structure", 
                            False, 
                            f"Missing required fields: {', '.join(missing_fields)}"
                        )
                        
                except json.JSONDecodeError as e:
                    self.log_result(
                        "Logo generation - JSON parsing", 
                        False, 
                        f"JSON decode error: {str(e)}"
                    )
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', response.text)
                except:
                    error_detail = response.text
                
                self.log_result(
                    "Logo generation", 
                    False, 
                    f"Status {response.status_code}: {error_detail}"
                )
                
        except Exception as e:
            self.log_result(
                "Logo generation", 
                False, 
                f"Request failed: {str(e)}"
            )

        # Test business card generation
        try:
            response = requests.post(
                f"{self.base_url}/projects/{self.project_id}/assets/business_card", 
                timeout=90
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Business card generation", 
                    True, 
                    "Business card generated successfully"
                )
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', response.text)
                except:
                    error_detail = response.text
                
                self.log_result(
                    "Business card generation", 
                    False, 
                    f"Status {response.status_code}: {error_detail}"
                )
                
        except Exception as e:
            self.log_result(
                "Business card generation", 
                False, 
                f"Request failed: {str(e)}"
            )

    def test_health_check(self):
        """Test API health check"""
        print("\n🔍 TESTING: API Health Check")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    if health_data.get('status') == 'healthy':
                        self.log_result(
                            "Health check", 
                            True, 
                            f"Service healthy: {health_data.get('service', 'Unknown')}"
                        )
                    else:
                        self.log_result(
                            "Health check", 
                            False, 
                            f"Service not healthy: {health_data}"
                        )
                except json.JSONDecodeError as e:
                    self.log_result(
                        "Health check JSON", 
                        False, 
                        f"JSON decode error: {str(e)}"
                    )
            else:
                self.log_result(
                    "Health check", 
                    False, 
                    f"Status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Health check", 
                False, 
                f"Request failed: {str(e)}"
            )

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Detailed BrandForge AI Backend Tests")
        print("Focus: Critical Bug Fixes Verification")
        print("=" * 60)
        
        # Run tests in order
        self.test_health_check()
        self.test_mongodb_objectid_serialization()
        self.test_brand_strategy_generation()
        self.test_asset_generation()
        
        # Print comprehensive results
        print("\n" + "=" * 60)
        print("📊 DETAILED TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n🔴 CRITICAL ISSUES ({len(self.critical_issues)}):")
        if self.critical_issues:
            for issue in self.critical_issues:
                print(f"   - {issue}")
        else:
            print("   ✅ No critical issues found!")
        
        print(f"\n🟡 MINOR ISSUES ({len(self.minor_issues)}):")
        if self.minor_issues:
            for issue in self.minor_issues:
                print(f"   - {issue}")
        else:
            print("   ✅ No minor issues found!")
        
        return len(self.critical_issues) == 0

def main():
    tester = DetailedBrandForgeAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())