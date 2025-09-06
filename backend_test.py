import requests
import sys
import json
from datetime import datetime

class QuantumPromptAPITester:
    def __init__(self, base_url="https://quantum-prompt-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        return self.run_test(
            "Health Check",
            "GET",
            "",
            200
        )

    def test_enhancement_styles(self):
        """Test getting available enhancement styles"""
        success, response = self.run_test(
            "Get Enhancement Styles",
            "GET",
            "enhancement-styles",
            200
        )
        
        if success and 'styles' in response:
            styles = response['styles']
            expected_styles = ['creative', 'technical', 'artistic', 'cinematic', 'detailed']
            found_styles = [style['id'] for style in styles]
            
            print(f"   Found styles: {found_styles}")
            if all(style in found_styles for style in expected_styles):
                print("   ✅ All expected styles found")
            else:
                print(f"   ⚠️  Missing styles: {set(expected_styles) - set(found_styles)}")
        
        return success, response

    def test_enhance_prompt(self, original_prompt, style="creative"):
        """Test prompt enhancement"""
        success, response = self.run_test(
            f"Enhance Prompt ({style})",
            "POST",
            "enhance-prompt",
            200,
            data={
                "original_prompt": original_prompt,
                "enhancement_style": style
            },
            timeout=60  # Longer timeout for AI processing
        )
        
        if success:
            required_fields = ['id', 'original_prompt', 'enhanced_prompt', 'enhancement_style', 'enhancement_reasoning']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print("   ✅ All required fields present")
                print(f"   Original: {response.get('original_prompt', '')[:50]}...")
                print(f"   Enhanced: {response.get('enhanced_prompt', '')[:100]}...")
                print(f"   Style: {response.get('enhancement_style')}")
        
        return success, response

    def test_enhancement_history(self):
        """Test getting enhancement history"""
        success, response = self.run_test(
            "Get Enhancement History",
            "GET",
            "enhancement-history",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   Found {len(response)} history items")
                if len(response) > 0:
                    first_item = response[0]
                    required_fields = ['id', 'original_prompt', 'enhanced_prompt', 'enhancement_style', 'timestamp']
                    missing_fields = [field for field in required_fields if field not in first_item]
                    
                    if missing_fields:
                        print(f"   ⚠️  Missing fields in history items: {missing_fields}")
                    else:
                        print("   ✅ History items have all required fields")
            else:
                print("   ⚠️  Expected list response for history")
        
        return success, response

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing Edge Cases...")
        
        # Test empty prompt
        success, _ = self.run_test(
            "Empty Prompt",
            "POST",
            "enhance-prompt",
            400,  # Should return 400 for empty prompt
            data={
                "original_prompt": "",
                "enhancement_style": "creative"
            }
        )
        
        # Test invalid style
        success2, _ = self.run_test(
            "Invalid Style",
            "POST",
            "enhance-prompt",
            200,  # Should still work, might default to creative
            data={
                "original_prompt": "test prompt",
                "enhancement_style": "invalid_style"
            }
        )
        
        # Test very long prompt
        long_prompt = "a" * 5000
        success3, _ = self.run_test(
            "Very Long Prompt",
            "POST",
            "enhance-prompt",
            200,
            data={
                "original_prompt": long_prompt,
                "enhancement_style": "creative"
            },
            timeout=90
        )
        
        return success or success2 or success3

def main():
    print("🚀 Starting Quantum AI Prompt Enhancer API Tests")
    print("=" * 60)
    
    tester = QuantumPromptAPITester()
    
    # Test 1: Health Check
    health_success, _ = tester.test_health_check()
    if not health_success:
        print("❌ Health check failed, API might be down")
        return 1
    
    # Test 2: Enhancement Styles
    styles_success, styles_data = tester.test_enhancement_styles()
    
    # Test 3: Prompt Enhancement - Test each style
    test_prompt = "a cat sitting on a chair"
    enhancement_results = []
    
    if styles_success and 'styles' in styles_data:
        available_styles = [style['id'] for style in styles_data['styles']]
    else:
        available_styles = ['creative', 'technical', 'artistic', 'cinematic', 'detailed']
    
    for style in available_styles[:3]:  # Test first 3 styles to save time
        success, result = tester.test_enhance_prompt(test_prompt, style)
        if success:
            enhancement_results.append(result)
    
    # Test 4: Enhancement History
    history_success, _ = tester.test_enhancement_history()
    
    # Test 5: Edge Cases
    edge_case_success = tester.test_edge_cases()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Detailed analysis
    critical_tests = [health_success, styles_success]
    if all(critical_tests):
        print("✅ All critical API endpoints are working")
    else:
        print("❌ Some critical API endpoints are failing")
    
    if len(enhancement_results) > 0:
        print(f"✅ Prompt enhancement working for {len(enhancement_results)} styles")
        
        # Check if enhancements are actually different
        enhanced_prompts = [result.get('enhanced_prompt', '') for result in enhancement_results]
        if len(set(enhanced_prompts)) == len(enhanced_prompts):
            print("✅ Different styles produce different enhancements")
        else:
            print("⚠️  Some styles might be producing similar results")
    else:
        print("❌ Prompt enhancement not working")
    
    if history_success:
        print("✅ Enhancement history endpoint working")
    else:
        print("❌ Enhancement history endpoint failing")
    
    # Return exit code
    return 0 if tester.tests_passed >= tester.tests_run * 0.8 else 1

if __name__ == "__main__":
    sys.exit(main())