#!/usr/bin/env python3
"""
ACE-Step Legacy API Compatibility Sample

This sample demonstrates how to use ACE-Step-directAPI with the same 
input/output format as the original ace_server.py /generate endpoint.

Compatible with the music.py code from momo_song2_yutub project.
"""

import requests
import re
import time
from typing import Optional

class ACEStepLegacyClient:
    """Client that mimics the original ace_server.py /generate endpoint behavior"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8019"):
        self.base_url = base_url.rstrip('/')
        
    def generate_legacy(
        self,
        audio_duration: float = -1,
        genre: str = "",
        infer_step: int = 50,
        lyrics: str = "",
        guidance_scale: float = 15,
        scheduler_type: str = "euler",
        cfg_type: str = "apg",
        omega_scale: float = 10,
        guidance_interval: float = 0.5,
        guidance_interval_decay: float = 0.0,
        min_guidance_scale: float = 3,
        use_erg_tag: bool = True,
        use_erg_lyric: bool = True,
        use_erg_diffusion: bool = True,
        guidance_scale_text: float = 0.0,
        guidance_scale_lyric: float = 0.0
    ) -> bytes:
        """
        Legacy API compatible method using async mode (file save)
        Returns audio content as bytes, just like the original ace_server.py
        """
        
        # Step 1: Submit generation request
        payload = {
            "format": "mp3",
            "audio_duration": audio_duration,
            "prompt": genre,
            "lyrics": lyrics,
            "infer_step": infer_step,
            "guidance_scale": guidance_scale,
            "scheduler_type": scheduler_type,
            "cfg_type": cfg_type,
            "omega_scale": omega_scale,
            "guidance_interval": guidance_interval,
            "guidance_interval_decay": guidance_interval_decay,
            "min_guidance_scale": min_guidance_scale,
            "guidance_scale_text": guidance_scale_text,
            "guidance_scale_lyric": guidance_scale_lyric,
            "return_file_data": True
        }
        
        print(f"Submitting legacy generation request...")
        response = requests.post(f"{self.base_url}/generate_music", json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Request submission failed: {response.status_code} - {response.text}")
            
        data = response.json()
        if not data.get("success"):
            raise Exception(f"Request failed: {data.get('error_message')}")
            
        request_id = data["request_id"]
        print(f"Request queued with ID: {request_id}")
        
        # Step 2: Wait for completion
        print("Waiting for completion...")
        while True:
            status_response = requests.get(f"{self.base_url}/status/{request_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data["status"]
                print(f"Status: {status}")
                
                if status == "completed":
                    print("Generation completed!")
                    break
                elif status == "failed":
                    raise Exception(f"Generation failed: {status_data.get('error')}")
                    
            time.sleep(2)  # Check every 2 seconds
        
        # Step 3: Download result
        print("Downloading result...")
        result_response = requests.get(f"{self.base_url}/result/{request_id}")
        
        if result_response.status_code != 200:
            raise Exception(f"Download failed: {result_response.status_code}")
            
        return result_response.content
    
    def generate_direct(
        self,
        audio_duration: float = -1,
        genre: str = "",
        infer_step: int = 50,
        lyrics: str = "",
        guidance_scale: float = 15,
        scheduler_type: str = "euler",
        cfg_type: str = "apg",
        omega_scale: float = 10,
        guidance_interval: float = 0.5,
        guidance_interval_decay: float = 0.0,
        min_guidance_scale: float = 3,
        use_erg_tag: bool = True,
        use_erg_lyric: bool = True,
        use_erg_diffusion: bool = True,
        guidance_scale_text: float = 0.0,
        guidance_scale_lyric: float = 0.0
    ) -> bytes:
        """
        Direct API method (no file save)
        Returns audio content as bytes immediately
        """
        
        payload = {
            "format": "mp3",
            "audio_duration": audio_duration,
            "prompt": genre,
            "lyrics": lyrics,
            "infer_step": infer_step,
            "guidance_scale": guidance_scale,
            "scheduler_type": scheduler_type,
            "cfg_type": cfg_type,
            "omega_scale": omega_scale,
            "guidance_interval": guidance_interval,
            "guidance_interval_decay": guidance_interval_decay,
            "min_guidance_scale": min_guidance_scale,
            "guidance_scale_text": guidance_scale_text,
            "guidance_scale_lyric": guidance_scale_lyric
        }
        
        print(f"Submitting direct generation request...")
        response = requests.post(
            f"{self.base_url}/generate_music_direct",
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Direct request failed: {response.status_code} - {response.text}")
            
        print("Direct generation completed!")
        return response.content


def demo_legacy_compatibility():
    """Demonstration of legacy compatibility"""
    
    client = ACEStepLegacyClient()
    
    # Test data (same format as original music.py)
    test_data = {
        "audio_duration": -1,
        "genre": "upbeat electronic music with synthesizers",
        "infer_step": 27,
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
        "guidance_scale": 15,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": 10,
        "guidance_interval": 0.5,
        "guidance_interval_decay": 0.0,
        "min_guidance_scale": 3,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0
    }
    
    print("=== ACE-Step Legacy API Compatibility Demo ===\n")
    
    # Test Legacy Mode (Async with file save)
    print("1. Testing Legacy Mode (Async):")
    try:
        start_time = time.time()
        audio_content_legacy = client.generate_legacy(**test_data)
        end_time = time.time()
        
        with open("generated_music_legacy.mp3", "wb") as f:
            f.write(audio_content_legacy)
            
        print(f"✓ Legacy mode successful!")
        print(f"✓ File size: {len(audio_content_legacy):,} bytes")
        print(f"✓ Generation time: {end_time - start_time:.2f} seconds")
        print(f"✓ Saved as: generated_music_legacy.mp3\n")
        
    except Exception as e:
        print(f"✗ Legacy mode failed: {e}\n")
    
    # Test Direct Mode (No file save)
    print("2. Testing Direct Mode:")
    try:
        start_time = time.time()
        audio_content_direct = client.generate_direct(**test_data)
        end_time = time.time()
        
        with open("generated_music_direct.mp3", "wb") as f:
            f.write(audio_content_direct)
            
        print(f"✓ Direct mode successful!")
        print(f"✓ File size: {len(audio_content_direct):,} bytes")
        print(f"✓ Generation time: {end_time - start_time:.2f} seconds")
        print(f"✓ Saved as: generated_music_direct.mp3\n")
        
    except Exception as e:
        print(f"✗ Direct mode failed: {e}\n")


# Original music.py compatible function
def generate_song_legacy(
    jeson_song: dict,
    infer_step: int = 27,
    guidance_scale: float = 15,
    omega_scale: float = 10,
    use_direct: bool = False
) -> bytes:
    """
    Drop-in replacement for the original generate_song function
    Compatible with the music.py from momo_song2_yutub project
    
    Args:
        jeson_song: Dictionary containing 'lyrics' and 'genre'
        infer_step: Number of inference steps
        guidance_scale: Guidance scale for generation
        omega_scale: Omega scale parameter
        use_direct: If True, use direct mode; if False, use legacy async mode
    
    Returns:
        bytes: Audio content as bytes
    """
    
    client = ACEStepLegacyClient()
    
    # Extract data from jeson_song (same format as original)
    lyrics_dic = jeson_song['lyrics']
    
    # Convert lyrics dict to text (reuse original function logic)
    def convert_lyrics_dict_to_text(lyrics_dict):
        if not isinstance(lyrics_dict, dict):
            return lyrics_dict
        result = ""
        for key, value in lyrics_dict.items():
            if not isinstance(value, str):
                continue
            processed_key = re.sub(r"[（(].*?[）)]", "", key).strip()
            processed_value = re.sub(r"^[（(].*?[）)]\s*\n?", "", value)
            result += f"[{processed_key}]\n{processed_value}\n"
        return result
    
    lyrics = convert_lyrics_dict_to_text(lyrics_dic)
    genre = jeson_song['genre']
    
    # API parameters (same as original)
    params = {
        "audio_duration": -1,
        "genre": genre,
        "infer_step": infer_step,
        "lyrics": lyrics,
        "guidance_scale": guidance_scale,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": omega_scale,
        "guidance_interval": 0.5,
        "guidance_interval_decay": 0.0,
        "min_guidance_scale": 3,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0
    }
    
    # Choose generation method
    if use_direct:
        return client.generate_direct(**params)
    else:
        return client.generate_legacy(**params)


if __name__ == "__main__":
    demo_legacy_compatibility()
