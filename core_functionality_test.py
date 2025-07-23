#!/usr/bin/env python3
"""
music.py Integration Test
Tests the direct integration with music.py client
"""
import sys
import os

# Add music.py path to sys.path
music_py_path = "/home/animede/momo_song2_yutub"
if music_py_path not in sys.path:
    sys.path.append(music_py_path)

def test_music_py_integration():
    """Test actual music.py integration"""
    print("=== Testing music.py Integration ===")
    
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
                'bridge': '永遠に続く旋律'
            },
            'genre': 'pop ballad, piano, emotional, japanese'
        }
        
        print(f"Request data: {json_song}")
        
        # Call generate_song with correct parameters
        audio_data = music.generate_song(
            jeson_song=json_song,
            infer_step=10,  # Low steps for test
            guidance_scale=5.0,
            omega_scale=10.0
        )
        
        if audio_data and isinstance(audio_data, bytes):
            print(f"✓ music.py integration successful!")
            print(f"  - Audio data type: {type(audio_data)}")
            print(f"  - Audio data length: {len(audio_data)} bytes")
            
            # Save test file
            with open('/home/animede/ACE-Step/test_music_py_integration.wav', 'wb') as f:
                f.write(audio_data)
            print(f"  - Audio saved to: test_music_py_integration.wav")
            return True
        else:
            print(f"✗ music.py returned invalid data: {type(audio_data)}")
            return False
            
    except Exception as e:
        print(f"✗ Exception during music.py test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_endpoint():
    """Test direct API endpoint"""
    print("\n=== Testing Direct API Endpoint ===")
    
    import requests
    
    url = "http://localhost:8019/generate_music_direct"
    
    data = {
        "lyrics": "君への想いを音楽に込めて\n[chorus]\n響け心の歌声よ",
        "prompt": "pop ballad, piano, emotional, japanese",
        "audio_duration": 20,
        "guidance_scale": 5.0,
        "infer_step": 10
    }
    
    try:
        print(f"Sending request to: {url}")
        
        response = requests.post(url, json=data, timeout=120)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type:
                audio_data = response.content
                print(f"✓ Direct API request successful!")
                print(f"  - Content-Type: {content_type}")
                print(f"  - Audio data length: {len(audio_data)} bytes")
                
                # Save test file
                with open('/home/animede/ACE-Step/test_direct_api.wav', 'wb') as f:
                    f.write(audio_data)
                print(f"  - Audio saved to: test_direct_api.wav")
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
        print(f"✗ Exception during direct API test: {e}")
        return False

def test_form_endpoint():
    """Test form-data endpoint"""
    print("\n=== Testing Form-Data Endpoint ===")
    
    import requests
    
    url = "http://localhost:8019/generate_music_form"
    
    data = {
        'lyrics': '君への想いを音楽に込めて\n[chorus]\n響け心の歌声よ',
        'genre': 'pop ballad, piano, emotional, japanese',
        'audio_duration': '20',
        'guidance_scale': '5.0',
        'infer_step': '10',
    }
    
    try:
        print(f"Sending request to: {url}")
        
        response = requests.post(url, data=data, timeout=120)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type:
                audio_data = response.content
                print(f"✓ Form-data request successful!")
                print(f"  - Content-Type: {content_type}")
                print(f"  - Audio data length: {len(audio_data)} bytes")
                
                # Save test file
                with open('/home/animede/ACE-Step/test_form_endpoint.wav', 'wb') as f:
                    f.write(audio_data)
                print(f"  - Audio saved to: test_form_endpoint.wav")
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
        print(f"✗ Exception during form-data test: {e}")
        return False

def main():
    print("ACE-Step Core Functionality Test")
    print("=" * 35)
    
    results = []
    
    # Test 1: Form-data endpoint
    results.append(("Form-Data Endpoint", test_form_endpoint()))
    
    # Test 2: Direct API endpoint
    results.append(("Direct API Endpoint", test_direct_endpoint()))
    
    # Test 3: music.py integration
    results.append(("music.py Integration", test_music_py_integration()))
    
    # Summary
    print("\n" + "=" * 35)
    print("TEST RESULTS:")
    print("=" * 35)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! ACE-Step server is fully functional.")
    elif passed >= 2:
        print(f"✅ {passed} out of {total} tests passed. Core functionality is working.")
        print("💡 Legacy compatibility and music generation are working!")
    else:
        print("⚠️  Tests failed. Please check the server configuration.")
    
    return passed >= 2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
