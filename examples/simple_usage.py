#!/usr/bin/env python3
"""
ACE-Step Direct API - Simple Usage Example

This example demonstrates how to use the Direct API to generate music
without saving files to disk.
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "http://localhost:8019"

def test_health():
    """Test if the API server is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API Health: {data['status']}")
            print(f"✓ Pipeline Loaded: {data['pipeline_loaded']}")
            return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
    return False

def generate_music_direct():
    """Generate music using direct mode (no file save)"""
    print("\n=== Direct Mode Music Generation ===")
    
    # Request payload
    payload = {
        "format": "wav",
        "audio_duration": 30.0,
        "prompt": "upbeat electronic music with synthesizers",
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
        "infer_step": 20,
        "guidance_scale": 15.0,
        "scheduler_type": "euler"
    }
    
    try:
        print("Sending request to /generate_music_direct...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/generate_music_direct",
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            # Save the audio file
            output_file = "direct_generated_music.wav"
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            print(f"✓ Music generated successfully!")
            print(f"✓ File saved: {output_file}")
            print(f"✓ File size: {len(response.content):,} bytes")
            print(f"✓ Generation time: {end_time - start_time:.2f} seconds")
            return True
        else:
            print(f"✗ Request failed: {response.status_code}")
            print(f"✗ Error: {response.text}")
            
    except Exception as e:
        print(f"✗ Generation failed: {e}")
    
    return False

def generate_music_async():
    """Generate music using async mode (with file save)"""
    print("\n=== Async Mode Music Generation ===")
    
    # Request payload
    payload = {
        "format": "mp3",
        "audio_duration": 20.0,
        "prompt": "peaceful classical piano melody",
        "lyrics": "",
        "infer_step": 15,
        "guidance_scale": 12.0,
        "scheduler_type": "euler",
        "return_file_data": True  # Request file data in response
    }
    
    try:
        # Step 1: Submit generation request
        print("Submitting async generation request...")
        response = requests.post(f"{API_BASE_URL}/generate_music", json=payload)
        
        if response.status_code != 200:
            print(f"✗ Request submission failed: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get("success"):
            print(f"✗ Request failed: {data.get('error_message')}")
            return False
            
        request_id = data["request_id"]
        print(f"✓ Request queued with ID: {request_id}")
        
        # Step 2: Wait for completion
        print("Waiting for completion...")
        while True:
            status_response = requests.get(f"{API_BASE_URL}/status/{request_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data["status"]
                print(f"Status: {status}")
                
                if status == "completed":
                    print("✓ Generation completed!")
                    break
                elif status == "failed":
                    print(f"✗ Generation failed: {status_data.get('error')}")
                    return False
                    
            time.sleep(2)  # Check every 2 seconds
        
        # Step 3: Download result
        print("Downloading result...")
        result_response = requests.get(f"{API_BASE_URL}/result/{request_id}")
        
        if result_response.status_code == 200:
            output_file = "async_generated_music.mp3"
            with open(output_file, "wb") as f:
                f.write(result_response.content)
            
            print(f"✓ Music downloaded successfully!")
            print(f"✓ File saved: {output_file}")
            print(f"✓ File size: {len(result_response.content):,} bytes")
            return True
        else:
            print(f"✗ Download failed: {result_response.status_code}")
            
    except Exception as e:
        print(f"✗ Async generation failed: {e}")
    
    return False

def main():
    """Main example function"""
    print("ACE-Step Direct API - Usage Example")
    print("=" * 50)
    
    # Check API health
    if not test_health():
        print("\n✗ API server is not available. Please start the server first:")
        print("  python gradio_compatible_api.py --port 8019")
        return
    
    # Test direct mode
    success_direct = generate_music_direct()
    
    # Test async mode
    success_async = generate_music_async()
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"Direct Mode: {'✓ Success' if success_direct else '✗ Failed'}")
    print(f"Async Mode:  {'✓ Success' if success_async else '✗ Failed'}")
    
    if success_direct or success_async:
        print("\n🎵 Check the generated music files!")

if __name__ == "__main__":
    main()
