#!/usr/bin/env python3
"""
Test script for original music.py compatibility with ace_server.py format
"""

import requests
import json

def test_ace_server_format():
    """Test the original ace_server.py /generate format"""
    
    # Test data using form format (like original music.py)
    data = {
        "audio_duration": -1,
        "genre": "electronic music with synthesizers",
        "infer_step": 20,  # Reduced for testing
        "lyrics": "[verse]\nSimple test song\n[chorus]\nQuick melody",
        "guidance_scale": 10,  # Reduced for testing
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": 5,  # Reduced for testing
        "guidance_interval": 0.5,
        "guidance_interval_decay": 0.0,
        "min_guidance_scale": 3,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0
    }
    
    print("=== Testing ace_server.py /generate compatibility ===")
    
    # Test health first
    try:
        health_response = requests.get("http://127.0.0.1:8019/health")
        print(f"Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Pipeline loaded: {health_data.get('pipeline_loaded')}")
        else:
            print("API server not available")
            return
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test /generate endpoint with form data
    try:
        print("\nTesting /generate endpoint with form data...")
        response = requests.post("http://127.0.0.1:8019/generate", data=data, timeout=120)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {response.headers.get('content-length')}")
        
        if response.status_code == 200:
            # Save the audio file
            with open("test_ace_server_format.mp3", "wb") as f:
                f.write(response.content)
            print(f"✓ Success! Audio saved as test_ace_server_format.mp3")
            print(f"✓ File size: {len(response.content):,} bytes")
        else:
            print(f"✗ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"✗ Request failed: {e}")

def test_generate_music_form():
    """Test the new /generate_music_form endpoint"""
    
    # Test with JSON format
    payload = {
        "format": "mp3",
        "audio_duration": 10.0,  # Short duration for testing
        "genre": "simple piano melody",
        "infer_step": 10,
        "lyrics": "[verse]\nTest lyrics\n[chorus]\nSimple song",
        "guidance_scale": 10,
        "omega_scale": 5,
        "return_file_data": True
    }
    
    print("\n=== Testing /generate_music with JSON ===")
    
    try:
        response = requests.post("http://127.0.0.1:8019/generate_music", json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✓ Request queued with ID: {result.get('request_id')}")
            else:
                print(f"✗ Request failed: {result.get('error_message')}")
        else:
            print(f"✗ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ JSON request failed: {e}")

if __name__ == "__main__":
    test_ace_server_format()
    test_generate_music_form()
