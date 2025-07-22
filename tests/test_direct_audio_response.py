#!/usr/bin/env python3
"""
Gradio互換API - 音楽データ直接取得の使用例

このスクリプトは音楽データをファイル出力せずに直接取得する方法を示します。
"""

import requests
import time

# APIサーバーの設定
API_BASE_URL = "http://localhost:8019"

def test_direct_music_response():
    """音楽データを直接取得するテスト"""
    print("🎵 音楽データ直接取得テスト")
    
    # 1. 通常のエンドポイントで return_file_data=True を使用
    print("\n--- 方法1: /generate_music with return_file_data=True ---")
    request_data = {
        "format": "mp3",
        "audio_duration": 10.0,
        "prompt": "acoustic guitar, peaceful, calm",
        "lyrics": "",
        "infer_step": 20,
        "guidance_scale": 15.0,
        "return_file_data": True  # 音楽データを直接返す
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/generate_music",
            json=request_data,
            timeout=300
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            # 音楽データが直接返される
            content_type = response.headers.get('content-type', '')
            
            if 'audio' in content_type:
                # バイナリ音楽データを保存
                filename = f"direct_download_method1_{int(time.time())}.mp3"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                print(f"✓ 成功: {filename} ({file_size} bytes, {elapsed_time:.1f}秒)")
            else:
                print(f"✗ 予期しないContent-Type: {content_type}")
        else:
            print(f"✗ HTTP エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
            
    except Exception as e:
        print(f"✗ エラー: {e}")

    # 2. 専用エンドポイント /generate_music_direct を使用
    print("\n--- 方法2: /generate_music_direct (専用エンドポイント) ---")
    request_data_direct = {
        "format": "wav",
        "audio_duration": 8.0,
        "prompt": "electronic, upbeat, dance",
        "lyrics": "",
        "infer_step": 15,
        "guidance_scale": 12.0
        # return_file_data は自動的に True になる
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/generate_music_direct",
            json=request_data_direct,
            timeout=300
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            
            if 'audio' in content_type:
                # バイナリ音楽データを保存
                filename = f"direct_download_method2_{int(time.time())}.wav"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                print(f"✓ 成功: {filename} ({file_size} bytes, {elapsed_time:.1f}秒)")
            else:
                print(f"✗ 予期しないContent-Type: {content_type}")
        else:
            print(f"✗ HTTP エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
            
    except Exception as e:
        print(f"✗ エラー: {e}")

def test_traditional_json_response():
    """従来のJSONレスポンス方式との比較"""
    print("\n--- 方法3: 従来のJSONレスポンス (return_file_data=False) ---")
    
    request_data = {
        "format": "mp3",
        "audio_duration": 5.0,
        "prompt": "jazz, piano, smooth",
        "lyrics": "",
        "infer_step": 20,
        "guidance_scale": 15.0,
        "return_file_data": False  # JSONレスポンス
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/generate_music",
            json=request_data,
            timeout=300
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                audio_path = result.get("audio_path")
                print(f"✓ 成功: ファイルパス {audio_path} ({elapsed_time:.1f}秒)")
                print(f"  ファイルは './outputs/' ディレクトリに保存されています")
            else:
                print(f"✗ API失敗: {result.get('error_message')}")
        else:
            print(f"✗ HTTP エラー: {response.status_code}")
            
    except Exception as e:
        print(f"✗ エラー: {e}")

def check_server_health():
    """サーバーの稼働状況を確認"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ サーバー稼働中 (パイプライン: {'ロード済み' if result['pipeline_loaded'] else '未ロード'})")
            return True
        else:
            print(f"✗ サーバーエラー: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ サーバーに接続できません: {e}")
        return False

if __name__ == "__main__":
    print("🎼 ACE-Step 音楽データ直接取得テスト")
    print("=" * 60)
    
    # サーバー確認
    if not check_server_health():
        print("\n❌ サーバーが利用できません。gradio_compatible_api.py を起動してください。")
        exit(1)
    
    # 各方法をテスト
    test_direct_music_response()
    test_traditional_json_response()
    
    print("\n" + "=" * 60)
    print("🎯 テスト完了")
    print("=" * 60)
    print("""
📖 使用方法まとめ:

1. 音楽データを直接取得:
   - /generate_music に return_file_data=True を指定
   - /generate_music_direct を使用（自動的に直接返す）

2. 従来のファイルパス取得:
   - /generate_music に return_file_data=False を指定（デフォルト）

3. 利点:
   - ファイルI/Oを削減
   - ディスク容量を節約
   - レスポンス後にファイルが自動削除される
   - ネットワーク越しの音楽配信に最適
    """)
