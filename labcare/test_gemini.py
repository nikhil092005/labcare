#!/usr/bin/env python3
"""
Test script to verify Gemini API connection
Run this script to test if your API key is working
"""

import google.generativeai as genai
import sys

# Your API key (replace with your actual key)
API_KEY = "AIzaSyA-3Bqi2fRaIspLEPzBTXe6Bi-oJ9f087U"

def test_gemini_connection():
    """Test Gemini API connection"""
    try:
        print("🔧 Testing Gemini API connection...")
        print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
        
        # Configure Gemini
        genai.configure(api_key=API_KEY)
        
        # Initialize model (using available models)
        # Try different models for compatibility
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Using gemini-2.0-flash model")
        except Exception as e:
            print(f"⚠️ gemini-2.0-flash not available: {e}")
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ Using gemini-2.5-flash model")
            except Exception as e2:
                print(f"⚠️ gemini-2.5-flash not available: {e2}")
                try:
                    model = genai.GenerativeModel('gemini-flash-latest')
                    print("✅ Using gemini-flash-latest model")
                except Exception as e3:
                    print(f"⚠️ gemini-flash-latest not available: {e3}")
                    try:
                        model = genai.GenerativeModel('gemini-2.0-flash-001')
                        print("✅ Using gemini-2.0-flash-001 model")
                    except Exception as e4:
                        print(f"⚠️ All models failed: {e4}")
                        # Last resort - use the basic model
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        print("✅ Using fallback model")
        
        # Test with simple prompt
        test_prompt = "Hello, please respond with 'Connection successful' if you can read this."
        print("📤 Sending test message...")
        
        response = model.generate_content(test_prompt)
        
        if response and response.text:
            print("✅ SUCCESS! Gemini API is working")
            print(f"📥 Response: {response.text}")
            return True
        else:
            print("❌ FAILED: Empty response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Provide specific error guidance
        if "API_KEY_INVALID" in str(e) or "invalid" in str(e).lower():
            print("\n🔑 API Key Issue:")
            print("1. Check if your API key is correct")
            print("2. Make sure you have enabled the Gemini API in Google AI Studio")
            print("3. Visit: https://makersuite.google.com/app/apikey")
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            print("\n📊 Quota Issue:")
            print("1. You may have exceeded your API quota")
            print("2. Check your usage in Google AI Studio")
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            print("\n🌐 Network Issue:")
            print("1. Check your internet connection")
            print("2. Make sure you can access Google services")
        else:
            print("\n🔍 General troubleshooting:")
            print("1. Verify your API key is correct")
            print("2. Check if Gemini API is enabled in your Google account")
            print("3. Ensure you have sufficient quota")
        
        return False

if __name__ == "__main__":
    print("🤖 LABMentor AI Chat - Gemini API Test")
    print("=" * 50)
    
    if test_gemini_connection():
        print("\n🎉 Your AI chat should work now!")
        print("You can now use the AI chat feature in your LABMentor application.")
    else:
        print("\n⚠️  Please fix the issues above before using AI chat.")
        print("Once fixed, restart your Flask application.")
    
    print("\n" + "=" * 50)
