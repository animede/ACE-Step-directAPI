#!/usr/bin/env python3
"""
Debug script for 422 Unprocessable Entity error
"""

import requests
import json

def test_generate_music_debug():
    """Test /generate_music with detailed error analysis"""
    
    url = "http://127.0.0.1:8019/generate_music"
    
    # Test data matching ace_server_compatibility.py
    payload = {
        "format": "mp3",
        "audio_duration": -1,
        "prompt": "upbeat electronic music with synthesizers",  # genre -> prompt
        "lyrics": """[verse]
Digital dreams come alive tonight
Synth waves dancing in neon light
Electronic beats pulse through my veins
In this cyber world nothing remains

[chorus]
Turn up the volume let the bass drop
Feel the rhythm never gonna stop
In this digital paradise we fly
Electronic music reaching for the sky""",
        "infer_step": 27,
        "guidance_scale": 15,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": 10,
        "guidance_interval": 0.5,
        "guidance_interval_decay": 0.0,
        "min_guidance_scale": 3,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0,
        "return_file_data": True
    }
    
    print("=== Debug /generate_music 422 Error ===")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Health check first
        health_response = requests.get("http://127.0.0.1:8019/health")
        print(f"\nHealth check: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health data: {health_response.json()}")
        
        # Test the actual request
        print(f"\nSending POST request...")
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 422:
            print("\n=== 422 Error Analysis ===")
            try:
                error_detail = response.json()
                print(f"Error Detail: {json.dumps(error_detail, indent=2)}")
            except:
                print("Could not parse error JSON")
        
    except Exception as e:
        print(f"Request failed: {e}")

def test_openapi_schema():
    """Check the OpenAPI schema for /generate_music"""
    try:
        response = requests.get("http://127.0.0.1:8019/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            
            # Find /generate_music endpoint
            if 'paths' in schema and '/generate_music' in schema['paths']:
                endpoint = schema['paths']['/generate_music']
                print("\n=== /generate_music OpenAPI Schema ===")
                print(json.dumps(endpoint, indent=2))
            else:
                print("Could not find /generate_music in OpenAPI schema")
        else:
            print(f"Could not get OpenAPI schema: {response.status_code}")
    except Exception as e:
        print(f"OpenAPI schema check failed: {e}")

if __name__ == "__main__":
    test_generate_music_debug()
    test_openapi_schema()
