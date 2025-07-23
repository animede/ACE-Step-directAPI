#!/usr/bin/env python3
"""
Simple test for ACE-server compatibility with lighter parameters
"""

from ace_server_compatibility import ACEStepLegacyClient

def test_light():
    client = ACEStepLegacyClient()
    
    # Lighter test data
    test_data = {
        "audio_duration": 10.0,  # Shorter duration
        "genre": "simple piano melody",
        "infer_step": 10,  # Fewer steps
        "lyrics": "[verse]\nSimple test song\n[chorus]\nQuick melody",
        "guidance_scale": 10,  # Lower guidance
        "scheduler_type": "euler",
        "cfg_type": "apg", 
        "omega_scale": 5,  # Lower omega
        "guidance_interval": 0.5,
        "guidance_interval_decay": 0.0,
        "min_guidance_scale": 3,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0
    }
    
    print("=== Light Test for ACE-Server Compatibility ===\n")
    
    # Test API connectivity first
    try:
        import requests
        response = requests.get(f"{client.base_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✓ API Health: {health['status']}")
            print(f"✓ Pipeline Loaded: {health['pipeline_loaded']}")
        else:
            print(f"✗ API not healthy: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return
    
    print("\nTesting Direct Mode with light parameters:")
    try:
        audio_content = client.generate_direct(**test_data)
        
        with open("test_light_output.mp3", "wb") as f:
            f.write(audio_content)
            
        print(f"✓ Direct mode successful!")
        print(f"✓ File size: {len(audio_content):,} bytes")
        print(f"✓ Saved as: test_light_output.mp3")
        
    except Exception as e:
        print(f"✗ Direct mode failed: {e}")

if __name__ == "__main__":
    test_light()
