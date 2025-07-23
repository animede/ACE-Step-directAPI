#!/usr/bin/env python3
"""
music.py Compatibility Patch for ACE-Step-directAPI

This file provides drop-in replacements for the original music.py functions
to work with ACE-Step-directAPI instead of ace_server.py.

Usage:
1. Replace the ace_url in your music.py
2. Replace the generate_song function with generate_song_new
3. Optionally set use_direct=True for faster direct mode
"""

import requests
import re
import time
import json

# Configuration
ACE_STEP_BASE_URL = "http://127.0.0.1:8019"  # ACE-Step-directAPI URL

def convert_lyrics_dict_to_text(lyrics_dict):
    """
    Original function from music.py - unchanged
    """
    if not isinstance(lyrics_dict, dict):
        print(f"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  lyrics_dictは辞書型である必要があります。現在の型: {type(lyrics_dict)}")
        return lyrics_dict
    result=""
    for key, value in lyrics_dict.items():
        if not isinstance(value, str):
            print(f"警告: 値が文字列ではありません。スキップします。キー: {key}, 値: {value}")
            continue
        processed_key = re.sub(r"[（(].*?[）)]", "", key).strip()
        processed_value = re.sub(r"^[（(].*?[）)]\s*\n?", "", value)
        result += f"[{processed_key}]\n{processed_value}\n"
    return result


def generate_song_new(
    jeson_song: dict, 
    infer_step: int = 27,
    guidance_scale: float = 15,
    omega_scale: float = 10,
    use_direct: bool = True
) -> bytes:
    """
    New version of generate_song compatible with ACE-Step-directAPI
    
    Args:
        jeson_song: Dictionary containing 'lyrics' and 'genre' (same as original)
        infer_step: Number of inference steps (same as original)
        guidance_scale: Guidance scale for generation (same as original)
        omega_scale: Omega scale parameter (same as original)
        use_direct: If True, use direct mode (faster); if False, use async mode
    
    Returns:
        bytes: Audio content as bytes (same as original)
    """
    
    print("======>>>>>jeson_song=", jeson_song)
    lyrics_dic = jeson_song['lyrics']
    print("###### lyrics_dic >>>>", lyrics_dic)
    lyrics = convert_lyrics_dict_to_text(lyrics_dic)
    print("###### lyrics_text >>>>", lyrics)
    genre = jeson_song['genre']
    print("###### genre >>>>", genre)
    
    # APIに送信するデータの準備 (ACE-Step-directAPI format)
    payload = {
        "format": "mp3",
        "audio_duration": -1,
        "prompt": genre,  # genre -> prompt for new API
        "lyrics": lyrics,
        "infer_step": infer_step,
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
    
    if use_direct:
        # Direct Mode - faster, no file save
        print("Using Direct Mode (faster)...")
        response = requests.post(
            f"{ACE_STEP_BASE_URL}/generate_music_direct",
            json=payload,
            timeout=300
        )
        
        if response.status_code != 200:
            raise Exception(f"Direct generation failed: {response.status_code} - {response.text}")
            
        print("Direct generation completed!")
        return response.content
        
    else:
        # Legacy Async Mode - compatible with original behavior
        print("Using Legacy Async Mode...")
        payload["return_file_data"] = True
        
        # Step 1: Submit request
        response = requests.post(f"{ACE_STEP_BASE_URL}/generate_music", json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Request submission failed: {response.status_code}")
            
        data = response.json()
        if not data.get("success"):
            raise Exception(f"Request failed: {data.get('error_message')}")
            
        request_id = data["request_id"]
        print(f"Request queued with ID: {request_id}")
        
        # Step 2: Wait for completion
        print("Waiting for completion...")
        while True:
            status_response = requests.get(f"{ACE_STEP_BASE_URL}/status/{request_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data["status"]
                print(f"Status: {status}")
                
                if status == "completed":
                    print("Generation completed!")
                    break
                elif status == "failed":
                    raise Exception(f"Generation failed: {status_data.get('error')}")
                    
            time.sleep(2)
        
        # Step 3: Download result
        print("Downloading result...")
        result_response = requests.get(f"{ACE_STEP_BASE_URL}/result/{request_id}")
        
        if result_response.status_code != 200:
            raise Exception(f"Download failed: {result_response.status_code}")
            
        return result_response.content


def generate_song_with_filename(
    jeson_song: dict, 
    infer_step: int = 27,
    guidance_scale: float = 15,
    omega_scale: float = 10,
    use_direct: bool = True
) -> tuple[bytes, str]:
    """
    Enhanced version that also returns filename (for compatibility with original Response headers)
    
    Returns:
        tuple: (audio_content_bytes, filename)
    """
    
    audio_content = generate_song_new(jeson_song, infer_step, guidance_scale, omega_scale, use_direct)
    
    # Generate filename based on content (similar to original ace_server.py)
    import hashlib
    content_hash = hashlib.md5(audio_content).hexdigest()[:8]
    filename = f"generated_music_{content_hash}.mp3"
    
    return audio_content, filename


# Example usage and test function
def test_compatibility():
    """Test function to demonstrate compatibility"""
    
    # Sample data (same format as original music.py)
    test_song = {
        'title': 'テスト曲',
        'lyrics': {
            'verse': '夜空に輝く星たちが\n静かに歌を奏でてる\n心に響く優しいメロディー\n今夜は特別な夜',
            'chorus': '歌おう一緒に\n夢を追いかけて\n音楽の力で\n世界を変えよう',
            'bridge': '時には悲しい時もあるけれど\n音楽があれば乗り越えられる',
            'outro': 'この歌が終わっても\n心に残り続ける'
        },
        'genre': 'peaceful acoustic folk with guitar and piano',
        'theme': 'hope and dreams',
        'atmosphere': 'calm and uplifting'
    }
    
    print("=== ACE-Step-directAPI Compatibility Test ===\n")
    
    try:
        # Test Direct Mode
        print("Testing Direct Mode:")
        start_time = time.time()
        audio_content_direct = generate_song_new(test_song, use_direct=True)
        end_time = time.time()
        
        with open("test_direct_output.mp3", "wb") as f:
            f.write(audio_content_direct)
            
        print(f"✓ Direct mode successful!")
        print(f"✓ File size: {len(audio_content_direct):,} bytes")
        print(f"✓ Generation time: {end_time - start_time:.2f} seconds")
        print(f"✓ Saved as: test_direct_output.mp3\n")
        
    except Exception as e:
        print(f"✗ Direct mode failed: {e}\n")
    
    try:
        # Test Legacy Async Mode
        print("Testing Legacy Async Mode:")
        start_time = time.time()
        audio_content_legacy = generate_song_new(test_song, use_direct=False)
        end_time = time.time()
        
        with open("test_legacy_output.mp3", "wb") as f:
            f.write(audio_content_legacy)
            
        print(f"✓ Legacy async mode successful!")
        print(f"✓ File size: {len(audio_content_legacy):,} bytes")
        print(f"✓ Generation time: {end_time - start_time:.2f} seconds")
        print(f"✓ Saved as: test_legacy_output.mp3\n")
        
    except Exception as e:
        print(f"✗ Legacy async mode failed: {e}\n")


if __name__ == "__main__":
    test_compatibility()
