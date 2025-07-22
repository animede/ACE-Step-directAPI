#!/usr/bin/env python3
"""
ダイレクトモード（ファイル保存なし）の総合テストスクリプト
"""

import requests
import json
import os
import time

# APIサーバーのベースURL
BASE_URL = "http://127.0.0.1:8019"

def test_direct_no_file_save():
    """ダイレクトモードでファイルが保存されないことを確認"""
    print("=== Testing Direct Mode (No File Save) ===")
    
    # outputs ディレクトリの初期状態
    initial_count = len(os.listdir("outputs/")) if os.path.exists("outputs/") else 0
    print(f"Initial files in outputs/: {initial_count}")
    
    # 1. 通常の音楽生成（ダイレクト）
    print("\n1. Testing /generate_music_direct...")
    response = requests.post(
        f"{BASE_URL}/generate_music_direct",
        json={
            "format": "wav",
            "audio_duration": 3.0,
            "prompt": "test music",
            "lyrics": "",
            "infer_step": 5
        },
        timeout=300
    )
    
    if response.status_code == 200:
        print(f"✓ Direct music generation successful, {len(response.content)} bytes received")
    else:
        print(f"✗ Direct music generation failed: {response.status_code}")
        return False
    
    # 2. 音楽アップロード（ダイレクト）
    print("\n2. Testing /generate_music_with_audio_direct_mp3...")
    test_audio_path = "/home/animede/ACE-Step/data/test_track_001.mp3"
    
    if os.path.exists(test_audio_path):
        with open(test_audio_path, 'rb') as f:
            files = {'audio_file': ('test.mp3', f, 'audio/mpeg')}
            data = {
                'audio_duration': 3.0,
                'prompt': 'test upload music',
                'lyrics': '',
                'infer_step': 5
            }
            
            response = requests.post(
                f"{BASE_URL}/generate_music_with_audio_direct_mp3",
                files=files,
                data=data,
                timeout=300
            )
        
        if response.status_code == 200:
            print(f"✓ Direct audio upload generation successful, {len(response.content)} bytes received")
        else:
            print(f"✗ Direct audio upload generation failed: {response.status_code}")
            return False
    else:
        print(f"⚠ Skipping audio upload test: {test_audio_path} not found")
    
    # outputs ディレクトリの最終状態
    final_count = len(os.listdir("outputs/")) if os.path.exists("outputs/") else 0
    print(f"\nFinal files in outputs/: {final_count}")
    
    if final_count == initial_count:
        print("✓ No files were saved to disk in direct mode!")
        return True
    else:
        print(f"✗ Files were saved to disk in direct mode (added {final_count - initial_count} files)")
        return False

def test_async_file_save():
    """非同期モードでファイルが保存されることを確認"""
    print("\n=== Testing Async Mode (With File Save) ===")
    
    # outputs ディレクトリの初期状態
    initial_count = len(os.listdir("outputs/")) if os.path.exists("outputs/") else 0
    print(f"Initial files in outputs/: {initial_count}")
    
    # 非同期リクエスト
    print("\n1. Testing /generate_music_async...")
    response = requests.post(
        f"{BASE_URL}/generate_music_async",
        json={
            "format": "wav",
            "audio_duration": 3.0,
            "prompt": "test async music",
            "lyrics": "",
            "infer_step": 5,
            "return_file_data": False  # ファイル保存モード
        },
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        request_id = result.get('request_id')
        print(f"✓ Async request queued: {request_id}")
        
        # ステータス確認
        for i in range(30):  # 最大30秒待機
            time.sleep(1)
            status_response = requests.get(f"{BASE_URL}/status/{request_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status')
                print(f"Status: {status}")
                
                if status == 'completed':
                    print("✓ Async generation completed")
                    break
                elif status == 'failed':
                    print(f"✗ Async generation failed: {status_data.get('error')}")
                    return False
        else:
            print("✗ Async generation timed out")
            return False
        
        # outputs ディレクトリの最終状態
        final_count = len(os.listdir("outputs/")) if os.path.exists("outputs/") else 0
        print(f"Final files in outputs/: {final_count}")
        
        if final_count > initial_count:
            print("✓ Files were correctly saved to disk in async mode!")
            return True
        else:
            print("✗ No files were saved to disk in async mode")
            return False
    else:
        print(f"✗ Async request failed: {response.status_code}")
        return False

def main():
    """メインテスト関数"""
    print("ACE-Step API Direct Mode Test")
    print("=" * 50)
    
    # ヘルスチェック
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get('pipeline_loaded'):
                print("✓ API server is healthy and pipeline is loaded")
            else:
                print("✗ Pipeline is not loaded")
                return
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Cannot connect to API server: {e}")
        return
    
    # テスト実行
    direct_test_passed = test_direct_no_file_save()
    async_test_passed = test_async_file_save()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Direct Mode (No File Save): {'PASS' if direct_test_passed else 'FAIL'}")
    print(f"Async Mode (With File Save): {'PASS' if async_test_passed else 'FAIL'}")
    
    if direct_test_passed and async_test_passed:
        print("\n🎉 All tests passed! Direct mode successfully avoids file saving.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
