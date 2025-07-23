"""
Final validation test for ACE-Step legacy compatibility
Tests both legacy form-data requests and direct API requests
"""
import requests
import base64
import json
import sys
import os

# Server URL
BASE_URL = "http://localhost:8019"

def test_legacy_form_request():
    """Test legacy form-data request (like music.py uses)"""
    print("=== Testing Legacy Form-Data Request ===")
    
    url = f"{BASE_URL}/generate_music_form"
    
    # Legacy form data structure
    data = {
        'lyrics': '君への想いを音楽に込めて',
        'prompt': 'pop ballad, piano, emotional, japanese',
        'duration': '15',  # Short duration for test
        'guidance_scale': '3.5',
        'num_inference_steps': '5',  # Low steps for test
        'seed': '42'
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Request data: {data}")
        
        response = requests.post(url, data=data, timeout=120)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Check if response is JSON with audio data
            try:
                json_response = response.json()
                if 'audio' in json_response:
                    audio_data = base64.b64decode(json_response['audio'])
                    print(f"✓ Legacy form request successful!")
                    print(f"  - Audio data length: {len(audio_data)} bytes")
                    
                    # Save test file
                    with open('/home/animede/ACE-Step/test_legacy_output.wav', 'wb') as f:
                        f.write(audio_data)
                    print(f"  - Audio saved to: test_legacy_output.wav")
                    return True
                else:
                    print(f"✗ No audio data in response: {json_response}")
                    return False
            except json.JSONDecodeError:
                print(f"✗ Response is not valid JSON")
                print(f"Response content: {response.text[:500]}")
                return False
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception during legacy request: {e}")
        return False

def test_direct_api_request():
    """Test direct API request (JSON format)"""
    print("\n=== Testing Direct API Request ===")
    
    url = f"{BASE_URL}/generate_music"
    
    # Direct API JSON structure
    data = {
        "lyrics": "君への想いを音楽に込めて",
        "prompt": "pop ballad, piano, emotional, japanese",
        "duration": 15,
        "guidance_scale": 3.5,
        "num_inference_steps": 5,
        "seed": 42
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Request data: {data}")
        
        response = requests.post(url, json=data, timeout=120)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if 'audio' in json_response:
                    audio_data = base64.b64decode(json_response['audio'])
                    print(f"✓ Direct API request successful!")
                    print(f"  - Audio data length: {len(audio_data)} bytes")
                    
                    # Save test file
                    with open('/home/animede/ACE-Step/test_direct_output.wav', 'wb') as f:
                        f.write(audio_data)
                    print(f"  - Audio saved to: test_direct_output.wav")
                    return True
                else:
                    print(f"✗ No audio data in response: {json_response}")
                    return False
            except json.JSONDecodeError:
                print(f"✗ Response is not valid JSON")
                print(f"Response content: {response.text[:500]}")
                return False
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception during direct request: {e}")
        return False

def test_music_py_compatibility():
    """Test actual music.py integration"""
    print("\n=== Testing music.py Integration ===")
    
    # Add music.py path to sys.path
    music_py_path = "/home/animede/momo_song2_yutub"
    if music_py_path not in sys.path:
        sys.path.append(music_py_path)
    
    try:
        # Import and test music.py
        import music
        
        print("Testing music.generate_song function...")
        
        # Test parameters
        lyrics = "君への想いを音楽に込めて"
        prompt = "pop ballad, piano, emotional, japanese"
        
        # Call generate_song
        audio_data = music.generate_song(
            lyrics=lyrics,
            prompt=prompt,
            duration=15,
            guidance_scale=3.5,
            num_inference_steps=5,
            seed=42
        )
        
        if audio_data and isinstance(audio_data, bytes):
            print(f"✓ music.py integration successful!")
            print(f"  - Audio data type: {type(audio_data)}")
            print(f"  - Audio data length: {len(audio_data)} bytes")
            
            # Save test file
            with open('/home/animede/ACE-Step/test_music_py_output.wav', 'wb') as f:
                f.write(audio_data)
            print(f"  - Audio saved to: test_music_py_output.wav")
            return True
        else:
            print(f"✗ music.py returned invalid data: {type(audio_data)}")
            return False
            
    except Exception as e:
        print(f"✗ Exception during music.py test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("ACE-Step Final Validation Test")
    print("=" * 40)
    
    results = []
    
    # Test 1: Legacy form request
    results.append(("Legacy Form Request", test_legacy_form_request()))
    
    # Test 2: Direct API request
    results.append(("Direct API Request", test_direct_api_request()))
    
    # Test 3: music.py compatibility
    results.append(("music.py Integration", test_music_py_compatibility()))
    
    # Summary
    print("\n" + "=" * 40)
    print("FINAL TEST RESULTS:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Legacy compatibility is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
