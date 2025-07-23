#!/usr/bin/env python3
"""
フォームリクエストのテスト
"""
import requests

# テスト用のデータ
data = {
    "audio_duration": 30,
    "genre": "pop rock",
    "infer_step": 10,  # 短時間でテストするため
    "lyrics": "Test lyrics for debugging",
    "guidance_scale": 15.0,
    "scheduler_type": "euler",
    "cfg_type": "apg",
    "omega_scale": 10.0,
    "guidance_interval": 0.5,
    "guidance_interval_decay": 0.0,
    "min_guidance_scale": 3.0,
    "guidance_scale_text": 0.0,
    "guidance_scale_lyric": 0.0,
    "format": "wav"
}

try:
    print("Sending form request...")
    response = requests.post("http://127.0.0.1:8019/generate_music_form", data=data)
    
    print(f"Status code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    if response.status_code == 200:
        print(f"Success! Audio data length: {len(response.content)} bytes")
        # 一時ファイルに保存
        with open("/tmp/test_generated_music.wav", "wb") as f:
            f.write(response.content)
        print("Audio saved to /tmp/test_generated_music.wav")
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")
