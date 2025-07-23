#!/usr/bin/env python3
"""
メモリ不足対策でより短い音楽生成をテストする
"""
import requests

# テスト用のデータ（短い音楽で）
data = {
    "audio_duration": 15,  # 15秒に短縮
    "genre": "pop",
    "infer_step": 5,  # ステップ数も減らす
    "lyrics": "Test short song",  # 短い歌詞
    "guidance_scale": 10.0,  # ガイダンススケールを下げる
    "scheduler_type": "euler",
    "cfg_type": "apg",
    "omega_scale": 5.0,  # オメガスケールも下げる
    "guidance_interval": 0.5,
    "guidance_interval_decay": 0.0,
    "min_guidance_scale": 2.0,
    "guidance_scale_text": 0.0,
    "guidance_scale_lyric": 0.0,
    "format": "wav"
}

try:
    print("Sending low-memory test request...")
    response = requests.post("http://127.0.0.1:8019/generate_music_form", data=data, timeout=120)
    
    print(f"Status code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    if response.status_code == 200:
        print(f"Success! Audio data length: {len(response.content)} bytes")
        # 一時ファイルに保存
        with open("/tmp/test_short_music.wav", "wb") as f:
            f.write(response.content)
        print("Audio saved to /tmp/test_short_music.wav")
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")
