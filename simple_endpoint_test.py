#!/usr/bin/env python3
"""
簡単なHTTPテストでエンドポイントが正常に動作するかテスト
"""
import requests
import json

def simple_test():
    print("=== Simple endpoint test ===")
    
    # まず初期化をテスト
    try:
        print("Testing /initialize...")
        init_response = requests.post(
            "http://localhost:8019/initialize", 
            json={"model_name": "ACE-Step"},
            timeout=10
        )
        print(f"Initialize status: {init_response.status_code}")
        if init_response.status_code == 200:
            print("Pipeline initialized successfully")
        else:
            print(f"Initialize failed: {init_response.text}")
            return False
    except Exception as e:
        print(f"Initialize request failed: {e}")
        return False
    
    # 次に/generate_music_formをテスト
    try:
        print("\nTesting /generate_music_form...")
        
        # 最小限のデータでテスト
        data = {
            "audio_duration": -1,
            "genre": "pop",
            "infer_step": 5,  # 短時間で完了するように少なく設定
            "lyrics": "[verse]\ntest lyrics\n",
            "guidance_scale": 15,
            "scheduler_type": "euler",
            "cfg_type": "apg",
            "omega_scale": 10,
            "guidance_interval": 0.5,
            "guidance_interval_decay": 0.0,
            "min_guidance_scale": 3,
            "guidance_scale_text": 0.0,
            "guidance_scale_lyric": 0.0,
            "format": "wav"
        }
        
        print("Sending test request...")
        response = requests.post(
            "http://localhost:8019/generate_music_form", 
            data=data,
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"Success! Response length: {len(response.content)} bytes")
            return True
        else:
            print(f"Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Test request failed: {e}")
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n✓ エンドポイントテスト成功")
    else:
        print("\n✗ エンドポイントテスト失敗")
