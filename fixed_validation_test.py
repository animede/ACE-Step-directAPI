"""
Fixed validation test for ACE-Step legacy compatibility
Tests the correct endpoints based on server implementation
"""
import requests
import base64
import json
import sys
import os
import time

# Server URL
BASE_URL = "http://localhost:8019"

def test_legacy_form_request():
    """Test legacy form-data request using generate_music_form (returns WAV directly)"""
    print("=== Testing Legacy Form-Data Request (WAV Direct) ===")
    
    url = f"{BASE_URL}/generate_music_form"
    
    # Legacy form data structure - simplified for test
    data = {
        'lyrics': '君への想いを音楽に込めて',
        'genre': 'pop ballad, piano, emotional, japanese',  # Using genre parameter
        'audio_duration': '15',  # Short duration for test
        'guidance_scale': '3.5',
        'infer_step': '5',  # Low steps for test
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Request data: {data}")
        
        response = requests.post(url, data=data, timeout=120)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Check if response is WAV file (binary data)
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type:
                audio_data = response.content
                print(f"✓ Legacy form request successful!")
                print(f"  - Content-Type: {content_type}")
                print(f"  - Audio data length: {len(audio_data)} bytes")
                
                # Save test file
                with open('/home/animede/ACE-Step/test_legacy_form_output.wav', 'wb') as f:
                    f.write(audio_data)
                print(f"  - Audio saved to: test_legacy_form_output.wav")
                return True
            else:
                print(f"✗ Response is not audio data")
                print(f"Response content: {response.text[:500]}")
                return False
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception during legacy request: {e}")
        return False

def test_direct_sync_api_request():
    """Test direct synchronous API request (JSON format, returns audio directly)"""
    print("\n=== Testing Direct Sync API Request ===")
    
    url = f"{BASE_URL}/generate_music_with_audio_json"
    
    # Direct API JSON structure
    data = {
        "lyrics": "君への想いを音楽に込めて",
        "prompt": "pop ballad, piano, emotional, japanese",
        "audio_duration": 15,
        "guidance_scale": 3.5,
        "infer_step": 5
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
                    print(f"✓ Direct sync API request successful!")
                    print(f"  - Audio data length: {len(audio_data)} bytes")
                    
                    # Save test file
                    with open('/home/animede/ACE-Step/test_direct_sync_output.wav', 'wb') as f:
                        f.write(audio_data)
                    print(f"  - Audio saved to: test_direct_sync_output.wav")
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
        
        # Create proper json_song structure for music.py
        json_song = {
            'title': 'テスト楽曲',
            'lyrics': {
                'verse': '君への想いを音楽に込めて',
                'chorus': '響け心の歌声よ',
            },
            'genre': 'pop ballad, piano, emotional, japanese'
        }
        
        # Call generate_song with correct parameters
        audio_data = music.generate_song(
            jeson_song=json_song,
            infer_step=5,
            guidance_scale=3.5,
            omega_scale=10.0
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

def test_async_api_workflow():
    """Test async API workflow (request -> check status -> get result)"""
    print("\n=== Testing Async API Workflow ===")
    
    try:
        # Step 1: Submit request
        url = f"{BASE_URL}/generate_music"
        data = {
            "lyrics": "君への想いを音楽に込めて",
            "prompt": "pop ballad, piano, emotional, japanese",
            "audio_duration": 15,
            "guidance_scale": 3.5,
            "infer_step": 5
        }
        
        print("Step 1: Submitting async request...")
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code != 200:
            print(f"✗ Failed to submit request: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        result = response.json()
        if not result.get('success') or 'request_id' not in result:
            print(f"✗ Invalid response: {result}")
            return False
            
        request_id = result['request_id']
        print(f"  - Request submitted with ID: {request_id}")
        
        # Step 2: Check status and wait for completion
        status_url = f"{BASE_URL}/status/{request_id}"
        max_wait = 120  # Maximum wait time in seconds
        wait_time = 0
        
        print("Step 2: Waiting for completion...")
        while wait_time < max_wait:
            status_response = requests.get(status_url)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status')
                print(f"  - Status: {status}")
                
                if status == 'completed':
                    break
                elif status == 'failed':
                    print(f"✗ Request failed: {status_data.get('error')}")
                    return False
            
            time.sleep(2)
            wait_time += 2
        
        if wait_time >= max_wait:
            print(f"✗ Request timed out after {max_wait} seconds")
            return False
        
        # Step 3: Get result
        result_url = f"{BASE_URL}/result/{request_id}"
        print("Step 3: Getting result...")
        
        result_response = requests.get(result_url)
        if result_response.status_code != 200:
            print(f"✗ Failed to get result: {result_response.status_code}")
            return False
        
        result_data = result_response.json()
        if 'audio' in result_data:
            audio_data = base64.b64decode(result_data['audio'])
            print(f"✓ Async API workflow successful!")
            print(f"  - Audio data length: {len(audio_data)} bytes")
            
            # Save test file
            with open('/home/animede/ACE-Step/test_async_output.wav', 'wb') as f:
                f.write(audio_data)
            print(f"  - Audio saved to: test_async_output.wav")
            return True
        else:
            print(f"✗ No audio data in result: {result_data}")
            return False
            
    except Exception as e:
        print(f"✗ Exception during async test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("ACE-Step Fixed Validation Test")
    print("=" * 40)
    
    results = []
    
    # Test 1: Legacy form request (returns WAV directly)
    results.append(("Legacy Form Request", test_legacy_form_request()))
    
    # Test 2: Direct sync API request (returns JSON with audio)
    results.append(("Direct Sync API Request", test_direct_sync_api_request()))
    
    # Test 3: music.py compatibility
    results.append(("music.py Integration", test_music_py_compatibility()))
    
    # Test 4: Async API workflow
    results.append(("Async API Workflow", test_async_api_workflow()))
    
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
    elif passed > 0:
        print(f"✓ {passed} out of {total} tests passed. Some functionality is working.")
    else:
        print("⚠️  All tests failed. Please check the server configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
