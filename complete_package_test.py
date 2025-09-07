#!/usr/bin/env python3
"""
Focused test for Complete Brand Package Generation fix
Tests the specific issue where complete package was only returning 2 assets instead of 6
"""

import requests
import json
import sys
from datetime import datetime

class CompletePackageTest:
    def __init__(self, base_url="https://bugfix-forge.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.project_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def create_test_project(self):
        """Create project with exact test data from review request"""
        self.log("Creating test project with specified data...")
        
        test_data = {
            "business_name": "TestFlow Inc",
            "business_description": "Test sustainable packaging for testing",
            "industry": "Technology",
            "target_audience": "Test customers", 
            "business_values": ["testing", "quality"],
            "preferred_style": "modern",
            "preferred_colors": "flexible"
        }
        
        try:
            url = f"{self.base_url}/projects"
            response = requests.post(url, json=test_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.project_id = data.get('id')
                self.log(f"✅ Project created successfully - ID: {self.project_id}")
                return True
            else:
                self.log(f"❌ Project creation failed - Status: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception during project creation: {str(e)}", "ERROR")
            return False
    
    def generate_brand_strategy(self):
        """Generate brand strategy for the test project"""
        if not self.project_id:
            self.log("❌ No project ID available for strategy generation", "ERROR")
            return False
            
        self.log("Generating brand strategy...")
        
        try:
            url = f"{self.base_url}/projects/{self.project_id}/strategy"
            response = requests.post(url, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Brand strategy generated successfully")
                
                # Verify strategy has required components
                required_fields = ['brand_personality', 'visual_direction', 'color_palette', 'messaging_framework']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log(f"⚠️ Strategy missing fields: {missing_fields}", "WARN")
                else:
                    self.log("✅ Strategy structure validated")
                    
                return True
            else:
                self.log(f"❌ Strategy generation failed - Status: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception during strategy generation: {str(e)}", "ERROR")
            return False
    
    def test_complete_package_generation(self):
        """
        CRITICAL TEST: Generate complete package and verify exactly 6 assets are returned
        This is the main test for the reported bug fix
        """
        if not self.project_id:
            self.log("❌ No project ID available for complete package test", "ERROR")
            return False
            
        self.log("🎯 TESTING COMPLETE PACKAGE GENERATION (CRITICAL TEST)")
        self.log("Expected: Exactly 6 assets with proper structure")
        
        try:
            url = f"{self.base_url}/projects/{self.project_id}/complete-package"
            response = requests.post(url, timeout=120)
            
            if response.status_code != 200:
                self.log(f"❌ Complete package generation failed - Status: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
                
            data = response.json()
            self.log("✅ Complete package endpoint returned 200 status")
            
            # CRITICAL VERIFICATION: Check for exactly 6 assets
            if 'generated_assets' not in data:
                self.log("❌ CRITICAL FAILURE: Response missing 'generated_assets' field", "ERROR")
                return False
                
            assets = data['generated_assets']
            asset_count = len(assets)
            
            self.log(f"📊 Assets returned: {asset_count}")
            
            if asset_count != 6:
                self.log(f"❌ CRITICAL FAILURE: Expected 6 assets, got {asset_count}", "ERROR")
                self.log("This indicates the bug is NOT fixed!", "ERROR")
                return False
            else:
                self.log("✅ CRITICAL SUCCESS: Exactly 6 assets returned", "SUCCESS")
            
            # Verify expected asset types
            expected_types = ['logo', 'business_card', 'letterhead', 'social_media_post', 'flyer', 'banner']
            actual_types = [asset.get('asset_type') for asset in assets]
            
            self.log("🔍 Verifying asset types...")
            missing_types = []
            for expected_type in expected_types:
                if expected_type in actual_types:
                    self.log(f"   ✅ {expected_type} - Present")
                else:
                    self.log(f"   ❌ {expected_type} - MISSING", "ERROR")
                    missing_types.append(expected_type)
            
            if missing_types:
                self.log(f"❌ CRITICAL FAILURE: Missing asset types: {missing_types}", "ERROR")
                return False
            
            # Verify each asset has required fields
            self.log("🔍 Verifying asset structure...")
            required_fields = ['id', 'project_id', 'asset_type', 'asset_url', 'metadata']
            
            for i, asset in enumerate(assets):
                asset_type = asset.get('asset_type', f'asset_{i}')
                missing_fields = [field for field in required_fields if field not in asset]
                
                if missing_fields:
                    self.log(f"   ❌ {asset_type} missing fields: {missing_fields}", "ERROR")
                    return False
                else:
                    # Verify asset_url format
                    asset_url = asset.get('asset_url', '')
                    if asset_url.startswith('data:image/png;base64,'):
                        self.log(f"   ✅ {asset_type} - Valid structure and URL format")
                    else:
                        self.log(f"   ⚠️ {asset_type} - Invalid URL format: {asset_url[:50]}...", "WARN")
            
            # Additional verification
            total_assets = data.get('total_assets', 0)
            if total_assets == 6:
                self.log("✅ total_assets field correctly reports 6")
            else:
                self.log(f"⚠️ total_assets field reports {total_assets}, expected 6", "WARN")
            
            self.log("🎉 COMPLETE PACKAGE TEST PASSED - All 6 assets generated successfully!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Exception during complete package test: {str(e)}", "ERROR")
            return False

def main():
    print("🚀 FOCUSED TEST: Complete Brand Package Generation Fix")
    print("=" * 70)
    print("Testing the specific fix for complete package returning only 2 assets instead of 6")
    print("=" * 70)
    
    tester = CompletePackageTest()
    
    # Execute test sequence
    test_steps = [
        ("Create Test Project", tester.create_test_project),
        ("Generate Brand Strategy", tester.generate_brand_strategy), 
        ("Test Complete Package Generation", tester.test_complete_package_generation)
    ]
    
    for step_name, step_func in test_steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 50)
        
        if not step_func():
            print(f"\n❌ FAILED at step: {step_name}")
            print("🛑 Test sequence aborted")
            return 1
        
        print(f"✅ Step completed: {step_name}")
    
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED - Complete Package Generation Fix Verified!")
    print("✅ The fix successfully ensures all 6 assets are returned")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())