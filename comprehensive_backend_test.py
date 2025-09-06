import requests
import sys
import json
from datetime import datetime

class ComprehensivePromptTester:
    def __init__(self, base_url="https://quantum-prompt-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=60):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
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
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:300]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_specific_prompts_and_styles(self):
        """Test the specific prompts and styles mentioned in the review request"""
        test_cases = [
            ("a sunset over mountains", "creative"),
            ("a robot walking", "technical"),
            ("a flower in a garden", "artistic"),
            ("a car chase scene", "cinematic"),
            ("a medieval castle", "detailed")
        ]
        
        results = []
        
        for prompt, style in test_cases:
            print(f"\n🎯 Testing: '{prompt}' with {style} style")
            success, response = self.run_test(
                f"Enhance '{prompt}' ({style})",
                "POST",
                "enhance-prompt",
                200,
                data={
                    "original_prompt": prompt,
                    "enhancement_style": style
                },
                timeout=90
            )
            
            if success:
                enhanced = response.get('enhanced_prompt', '')
                original = response.get('original_prompt', '')
                
                # Check if enhancement is significantly longer
                enhancement_ratio = len(enhanced) / len(original) if len(original) > 0 else 0
                print(f"   📏 Enhancement ratio: {enhancement_ratio:.1f}x longer")
                print(f"   📝 Original ({len(original)} chars): {original}")
                print(f"   ✨ Enhanced ({len(enhanced)} chars): {enhanced[:150]}...")
                
                if enhancement_ratio >= 3:  # Should be at least 3x longer
                    print("   ✅ Enhancement is significantly more detailed")
                else:
                    print("   ⚠️  Enhancement might not be detailed enough")
                
                results.append({
                    'prompt': prompt,
                    'style': style,
                    'success': True,
                    'enhancement_ratio': enhancement_ratio,
                    'enhanced_prompt': enhanced
                })
            else:
                results.append({
                    'prompt': prompt,
                    'style': style,
                    'success': False,
                    'enhancement_ratio': 0,
                    'enhanced_prompt': ''
                })
        
        return results

    def test_style_differentiation(self):
        """Test that different styles produce noticeably different results"""
        test_prompt = "a beautiful landscape"
        styles = ["creative", "technical", "artistic", "cinematic", "detailed"]
        
        enhancements = {}
        
        print(f"\n🎨 Testing style differentiation with: '{test_prompt}'")
        
        for style in styles:
            success, response = self.run_test(
                f"Style Test ({style})",
                "POST",
                "enhance-prompt",
                200,
                data={
                    "original_prompt": test_prompt,
                    "enhancement_style": style
                }
            )
            
            if success:
                enhanced = response.get('enhanced_prompt', '')
                enhancements[style] = enhanced
                print(f"   {style.upper()}: {enhanced[:100]}...")
        
        # Check if all enhancements are different
        unique_enhancements = set(enhancements.values())
        if len(unique_enhancements) == len(enhancements):
            print("   ✅ All styles produce unique enhancements")
            return True
        else:
            print(f"   ⚠️  Only {len(unique_enhancements)}/{len(enhancements)} unique enhancements")
            return False

    def test_database_persistence(self):
        """Test that enhancements are properly saved to database"""
        # Get initial history count
        success1, initial_history = self.run_test(
            "Get Initial History Count",
            "GET",
            "enhancement-history",
            200
        )
        
        if not success1:
            return False
        
        initial_count = len(initial_history) if isinstance(initial_history, list) else 0
        print(f"   Initial history count: {initial_count}")
        
        # Create a new enhancement
        test_prompt = f"test persistence {datetime.now().strftime('%H%M%S')}"
        success2, response = self.run_test(
            "Create Test Enhancement",
            "POST",
            "enhance-prompt",
            200,
            data={
                "original_prompt": test_prompt,
                "enhancement_style": "creative"
            }
        )
        
        if not success2:
            return False
        
        enhancement_id = response.get('id')
        print(f"   Created enhancement with ID: {enhancement_id}")
        
        # Check if history count increased
        success3, new_history = self.run_test(
            "Get Updated History Count",
            "GET",
            "enhancement-history",
            200
        )
        
        if not success3:
            return False
        
        new_count = len(new_history) if isinstance(new_history, list) else 0
        print(f"   New history count: {new_count}")
        
        if new_count > initial_count:
            print("   ✅ Enhancement properly saved to database")
            
            # Check if our enhancement is in the history
            found_enhancement = any(
                item.get('id') == enhancement_id 
                for item in new_history 
                if isinstance(item, dict)
            )
            
            if found_enhancement:
                print("   ✅ Enhancement found in history")
                return True
            else:
                print("   ⚠️  Enhancement not found in history")
                return False
        else:
            print("   ❌ Enhancement not saved to database")
            return False

def main():
    print("🚀 Starting Comprehensive Quantum AI Prompt Enhancer Tests")
    print("=" * 70)
    
    tester = ComprehensivePromptTester()
    
    # Test 1: Specific prompts and styles from review request
    print("\n📋 TESTING SPECIFIC PROMPTS AND STYLES")
    print("=" * 50)
    specific_results = tester.test_specific_prompts_and_styles()
    
    # Test 2: Style differentiation
    print("\n🎨 TESTING STYLE DIFFERENTIATION")
    print("=" * 50)
    style_diff_success = tester.test_style_differentiation()
    
    # Test 3: Database persistence
    print("\n💾 TESTING DATABASE PERSISTENCE")
    print("=" * 50)
    persistence_success = tester.test_database_persistence()
    
    # Final Analysis
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    
    print(f"Total tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Analyze specific prompt results
    successful_prompts = [r for r in specific_results if r['success']]
    print(f"\nSpecific prompt tests: {len(successful_prompts)}/5 successful")
    
    if len(successful_prompts) == 5:
        avg_ratio = sum(r['enhancement_ratio'] for r in successful_prompts) / len(successful_prompts)
        print(f"Average enhancement ratio: {avg_ratio:.1f}x")
        
        if avg_ratio >= 3:
            print("✅ All prompts significantly enhanced")
        else:
            print("⚠️  Some prompts may need better enhancement")
    
    # Style differentiation
    if style_diff_success:
        print("✅ Different styles produce unique results")
    else:
        print("⚠️  Style differentiation needs improvement")
    
    # Database persistence
    if persistence_success:
        print("✅ Database persistence working correctly")
    else:
        print("❌ Database persistence issues detected")
    
    # Overall assessment
    overall_success = (
        tester.tests_passed >= tester.tests_run * 0.9 and
        len(successful_prompts) >= 4 and
        style_diff_success and
        persistence_success
    )
    
    if overall_success:
        print("\n🎉 OVERALL: All core functionality working excellently!")
        return 0
    else:
        print("\n⚠️  OVERALL: Some issues detected that need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())