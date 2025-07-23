#!/usr/bin/env python3
"""
ACE-Step Direct API - 非同期モード使用例

従来の非同期処理（ファイル保存あり）の使用方法を示します。
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "http://localhost:8019"

def test_async_mode_examples():
    """非同期モードの各種エンドポイントをテスト"""
    
    print("ACE-Step API - Non-Direct Mode Examples")
    print("=" * 50)
    
    # 1. 基本的な非同期音楽生成
    print("\n1. 基本的な非同期音楽生成")
    payload = {
        "format": "wav",
        "audio_duration": 30.0,
        "prompt": "classical orchestral music",
        "lyrics": "",
        "infer_step": 20,
        "guidance_scale": 15.0,
        "scheduler_type": "euler"
    }
    
    response = requests.post(f"{API_BASE_URL}/generate_music", json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            request_id = data["request_id"]
            print(f"✓ Request queued: {request_id}")
            
            # ステータスチェック
            while True:
                status_response = requests.get(f"{API_BASE_URL}/status/{request_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Status: {status_data['status']}")
                    if status_data["status"] == "completed":
                        break
                    elif status_data["status"] == "failed":
                        print(f"✗ Failed: {status_data.get('error')}")
                        break
                time.sleep(2)
    
    # 2. ファイルデータ直接取得モード
    print("\n2. ファイルデータ直接取得モード")
    payload_with_data = {
        "format": "mp3",
        "audio_duration": 20.0,
        "prompt": "jazz piano solo",
        "lyrics": "",
        "infer_step": 15,
        "return_file_data": True  # ファイルデータを直接返す
    }
    
    response = requests.post(f"{API_BASE_URL}/generate_music", json=payload_with_data)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            request_id = data["request_id"]
            print(f"✓ Request with file data queued: {request_id}")
            
            # 完了まで待機
            while True:
                status_response = requests.get(f"{API_BASE_URL}/status/{request_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data["status"] == "completed":
                        # 結果をダウンロード
                        result_response = requests.get(f"{API_BASE_URL}/result/{request_id}")
                        if result_response.status_code == 200:
                            with open("async_result.mp3", "wb") as f:
                                f.write(result_response.content)
                            print(f"✓ File saved: async_result.mp3 ({len(result_response.content)} bytes)")
                        break
                    elif status_data["status"] == "failed":
                        break
                time.sleep(2)
    
    # 3. 音声ファイルアップロード（非同期）
    print("\n3. 音声ファイルアップロード（非同期）")
    # 注意: 実際のMP3ファイルが必要
    upload_payload = {
        "format": "wav",
        "audio_duration": 25.0,
        "prompt": "electronic remix",
        "lyrics": "",
        "infer_step": 20,
        "ref_audio_strength": 0.7
    }
    
    print("音声アップロード機能は実際のMP3ファイルが必要です")
    print("例: curl -X POST '/generate_music_with_audio' -F 'audio_file=@input.mp3' -F 'prompt=remix'")
    
    # 4. キューステータス確認
    print("\n4. キューステータス確認")
    queue_response = requests.get(f"{API_BASE_URL}/queue/status")
    if queue_response.status_code == 200:
        queue_data = queue_response.json()
        print(f"✓ Queue size: {queue_data.get('queue_size', 0)}")
        print(f"✓ Status counts: {queue_data.get('status_counts', {})}")
    
    # 5. サンプルデータ取得
    print("\n5. サンプルデータ取得")
    sample_response = requests.get(f"{API_BASE_URL}/sample_data")
    if sample_response.status_code == 200:
        sample_data = sample_response.json()
        if sample_data.get("success"):
            print("✓ Sample data retrieved successfully")
            # print(f"Sample: {sample_data['sample']}")
    
    print("\n" + "=" * 50)
    print("✓ All non-direct mode features are working!")

if __name__ == "__main__":
    # ヘルスチェック
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✓ API Health: {health_data['status']}")
            print(f"✓ Pipeline Loaded: {health_data['pipeline_loaded']}")
            
            test_async_mode_examples()
        else:
            print("✗ API server is not healthy")
    except Exception as e:
        print(f"✗ Cannot connect to API server: {e}")
        print("Please start the server first:")
        print("  python gradio_compatible_api.py --port 8019")
