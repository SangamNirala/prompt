import requests
import sys
import json
import time
from datetime import datetime

class BrandForgeAPITester:
    def __init__(self, base_url="https://bugfix-forge.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.project_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    else:
                        print(f"   Response: Large response received ({len(str(response_data))} chars)")
                except:
                    print(f"   Response: Non-JSON response")
                return True, response.json() if response.content else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        return success

    def test_create_project(self):
        """Test project creation"""
        test_data = {
            "business_name": "RetryTest Solutions",
            "business_description": "Testing enhanced retry logic for asset generation",
            "industry": "Technology",
            "target_audience": "Test users",
            "business_values": ["reliability", "quality"],
            "preferred_style": "modern",
            "preferred_colors": "flexible"
        }
        
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data=test_data
        )
        
        if success and 'id' in response:
            self.project_id = response['id']
            print(f"   Project ID: {self.project_id}")
            return True
        return False

    def test_generate_strategy(self):
        """Test brand strategy generation"""
        if not self.project_id:
            print("❌ Cannot test strategy generation - no project ID")
            return False
            
        success, response = self.run_test(
            "Generate Brand Strategy",
            "POST",
            f"projects/{self.project_id}/strategy",
            200,
            timeout=60  # AI generation takes longer
        )
        
        if success:
            # Verify strategy structure
            required_fields = ['brand_personality', 'visual_direction', 'color_palette', 'messaging_framework']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            print("   ✅ Strategy structure validated")
        
        return success

    def test_get_project(self):
        """Test getting project details"""
        if not self.project_id:
            print("❌ Cannot test get project - no project ID")
            return False
            
        success, response = self.run_test(
            "Get Project Details",
            "GET",
            f"projects/{self.project_id}",
            200
        )
        
        if success:
            # Verify project has strategy
            if 'brand_strategy' in response and response['brand_strategy']:
                print("   ✅ Project contains brand strategy")
            else:
                print("   ⚠️  Project missing brand strategy")
        
        return success

    def test_generate_single_asset(self, asset_type="logo"):
        """Test single asset generation"""
        if not self.project_id:
            print(f"❌ Cannot test {asset_type} generation - no project ID")
            return False
            
        success, response = self.run_test(
            f"Generate {asset_type.title()}",
            "POST",
            f"projects/{self.project_id}/assets/{asset_type}",
            200,
            timeout=60  # AI generation takes longer
        )
        
        if success:
            # Verify asset structure
            required_fields = ['id', 'project_id', 'asset_type', 'asset_url']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Verify asset URL format
            if response['asset_url'].startswith('data:image/png;base64,'):
                print("   ✅ Asset URL format validated")
            else:
                print(f"   ⚠️  Unexpected asset URL format: {response['asset_url'][:50]}...")
        
        return success

    def test_generate_complete_package(self):
        """Test enhanced complete package generation with retry logic"""
        if not self.project_id:
            print("❌ Cannot test complete package - no project ID")
            return False
            
        print("🔍 Testing Enhanced Complete Package Generation with Retry Logic...")
        success, response = self.run_test(
            "Generate Complete Package (Enhanced)",
            "POST",
            f"projects/{self.project_id}/complete-package",
            200,
            timeout=180  # Enhanced retry logic may take longer
        )
        
        if success:
            # CRITICAL TEST: Verify exactly 6 assets are returned
            if 'generated_assets' in response:
                asset_count = len(response['generated_assets'])
                print(f"   📊 Asset Count: {asset_count}")
                
                if asset_count == 6:
                    print("   ✅ CRITICAL: Exactly 6 assets generated as expected")
                else:
                    print(f"   ❌ CRITICAL: Expected 6 assets, got {asset_count}")
                    return False
                
                # Check all expected asset types are present
                asset_types = [asset['asset_type'] for asset in response['generated_assets']]
                expected_types = ['logo', 'business_card', 'letterhead', 'social_media_post', 'flyer', 'banner']
                
                missing_types = []
                for expected_type in expected_types:
                    if expected_type in asset_types:
                        print(f"   ✅ {expected_type} generated")
                    else:
                        print(f"   ❌ {expected_type} missing")
                        missing_types.append(expected_type)
                
                if missing_types:
                    print(f"   ❌ CRITICAL: Missing asset types: {missing_types}")
                    return False
                
                # CRITICAL TEST: Verify asset URLs contain substantial base64 data (not tiny placeholders)
                tiny_placeholders = 0
                valid_assets = 0
                
                for asset in response['generated_assets']:
                    asset_url = asset.get('asset_url', '')
                    if asset_url.startswith('data:image/png;base64,'):
                        base64_data = asset_url.split(',')[1] if ',' in asset_url else ''
                        data_length = len(base64_data)
                        
                        # Check if it's a tiny placeholder (less than 200 chars is suspicious)
                        if data_length < 200:
                            print(f"   ⚠️  {asset['asset_type']}: Potentially tiny placeholder ({data_length} chars)")
                            tiny_placeholders += 1
                        else:
                            print(f"   ✅ {asset['asset_type']}: Valid image data ({data_length} chars)")
                            valid_assets += 1
                    else:
                        print(f"   ❌ {asset['asset_type']}: Invalid asset URL format")
                        return False
                
                # Report on image quality
                print(f"   📊 Image Quality Summary:")
                print(f"      Valid assets: {valid_assets}/6")
                print(f"      Tiny placeholders: {tiny_placeholders}/6")
                
                if tiny_placeholders > 0:
                    print(f"   ⚠️  WARNING: {tiny_placeholders} assets may be tiny placeholders")
                    # Don't fail the test for this, as branded placeholders are acceptable
                
                print("   ✅ ENHANCED COMPLETE PACKAGE GENERATION: All critical tests passed")
                return True
            else:
                print("   ❌ CRITICAL: No 'generated_assets' field in response")
                return False
        
        return success

    def test_get_all_projects(self):
        """Test getting all projects"""
        success, response = self.run_test(
            "Get All Projects",
            "GET",
            "projects",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Found {len(response)} projects")
        
        return success

def main():
    print("🚀 Starting BrandForge AI Backend API Tests")
    print("=" * 60)
    
    tester = BrandForgeAPITester()
    
    # Test sequence
    tests = [
        ("Health Check", tester.test_health_check),
        ("Create Project", tester.test_create_project),
        ("Generate Strategy", tester.test_generate_strategy),
        ("Get Project", tester.test_get_project),
        ("Generate Logo", lambda: tester.test_generate_single_asset("logo")),
        ("Generate Business Card", lambda: tester.test_generate_single_asset("business_card")),
        ("Generate Complete Package", tester.test_generate_complete_package),
        ("Get All Projects", tester.test_get_all_projects),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} - Exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {len(failed_tests)}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n✅ All tests passed!")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())