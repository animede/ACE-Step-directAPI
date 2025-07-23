#!/usr/bin/env python3
"""
MP3アップロード機能をテストするスクリプト

使用方法:
1. gradio_compatible_api.pyサーバーを起動
2. このスクリプトを実行してMP3ファイルのアップロードをテスト
"""

import requests
import time
import base64
import os
import json

# APIサーバーの設定
API_BASE_URL = "http://localhost:8019"

def test_file_upload(mp3_file_path: str):
    """ファイルアップロード方式のテスト"""
    print(f"Testing file upload with: {mp3_file_path}")
    
    if not os.path.exists(mp3_file_path):
        print(f"Error: File not found: {mp3_file_path}")
        return None
    
    # ファイルをアップロード
    with open(mp3_file_path, 'rb') as f:
        files = {'audio_file': (os.path.basename(mp3_file_path), f, 'audio/mpeg')}
        data = {
            'format': 'wav',
            'audio_duration': 30.0,
            'prompt': 'remix, electronic, upbeat, dance',
            'lyrics': '[verse]\nDance to the beat\nFeel the rhythm\n[chorus]\nMusic flows through the night',
            'infer_step': 30,
            'guidance_scale': 12.0,
            'ref_audio_strength': 0.7,
            'return_file_data': False
        }
        
        response = requests.post(f"{API_BASE_URL}/generate_music_with_audio", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Upload successful: {result}")
        return result.get('request_id')
    else:
        print(f"Upload failed: {response.status_code} - {response.text}")
        return None

def test_base64_upload(mp3_file_path: str):
    """Base64アップロード方式のテスト（Form形式）"""
    print(f"Testing base64 upload with: {mp3_file_path}")
    
    if not os.path.exists(mp3_file_path):
        print(f"Error: File not found: {mp3_file_path}")
        return None
    
    # ファイルをBase64エンコード
    with open(mp3_file_path, 'rb') as f:
        audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    data = {
        'audio_base64': audio_base64,
        'format': 'wav',
        'audio_duration': 30.0,
        'prompt': 'jazz, smooth, saxophone, piano',
        'lyrics': '[verse]\nSmooth jazz vibes\nSoothing melodies\n[chorus]\nRelax and enjoy the sound',
        'infer_step': 30,
        'guidance_scale': 12.0,
        'ref_audio_strength': 0.6,
        'return_file_data': False
    }
    
    response = requests.post(f"{API_BASE_URL}/generate_music_with_audio_base64", data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Base64 upload successful: {result}")
        return result.get('request_id')
    else:
        print(f"Base64 upload failed: {response.status_code} - {response.text}")
        return None

def test_json_upload(mp3_file_path: str):
    """JSON形式でBase64アップロード方式のテスト"""
    print(f"Testing JSON base64 upload with: {mp3_file_path}")
    
    if not os.path.exists(mp3_file_path):
        print(f"Error: File not found: {mp3_file_path}")
        return None
    
    # ファイルをBase64エンコード
    with open(mp3_file_path, 'rb') as f:
        audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    data = {
        'audio_base64': audio_base64,
        'format': 'wav',
        'audio_duration': 30.0,
        'prompt': 'ambient, chill, atmospheric, synth',
        'lyrics': '[verse]\nFloating in space\nDrifting away\n[chorus]\nPeaceful moments',
        'infer_step': 30,
        'guidance_scale': 12.0,
        'ref_audio_strength': 0.5,
        'return_file_data': False
    }
    
    response = requests.post(f"{API_BASE_URL}/generate_music_with_audio_json", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"JSON upload successful: {result}")
        return result.get('request_id')
    else:
        print(f"JSON upload failed: {response.status_code} - {response.text}")
        return None

def test_mp3_output(mp3_file_path: str):
    """MP3形式で出力するテスト"""
    print(f"Testing MP3 output with: {mp3_file_path}")
    
    if not os.path.exists(mp3_file_path):
        print(f"Error: File not found: {mp3_file_path}")
        return None
    
    # ファイルをアップロード（MP3形式で出力）
    with open(mp3_file_path, 'rb') as f:
        files = {'audio_file': (os.path.basename(mp3_file_path), f, 'audio/mpeg')}
        data = {
            'audio_duration': 30.0,
            'prompt': 'electronic, remix, house music, bass',
            'lyrics': '[verse]\nDrop the beat\nFeel the bass\n[chorus]\nDance all night',
            'infer_step': 30,
            'guidance_scale': 12.0,
            'ref_audio_strength': 0.8
        }
        
        response = requests.post(f"{API_BASE_URL}/generate_music_with_audio_mp3", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"MP3 output upload successful: {result}")
        return result.get('request_id')
    else:
        print(f"MP3 output upload failed: {response.status_code} - {response.text}")
        return None

def test_json_mp3_output(mp3_file_path: str):
    """JSON形式でMP3出力するテスト"""
    print(f"Testing JSON MP3 output with: {mp3_file_path}")
    
    if not os.path.exists(mp3_file_path):
        print(f"Error: File not found: {mp3_file_path}")
        return None
    
    # ファイルをBase64エンコード
    with open(mp3_file_path, 'rb') as f:
        audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    data = {
        'audio_base64': audio_base64,
        'audio_duration': 30.0,
        'prompt': 'lo-fi, chill, hip hop, vintage',
        'lyrics': '[verse]\nLo-fi beats\nChill vibes\n[chorus]\nRelax and unwind',
        'infer_step': 30,
        'guidance_scale': 12.0,
        'ref_audio_strength': 0.6
    }
    
    response = requests.post(f"{API_BASE_URL}/generate_music_with_audio_json_mp3", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"JSON MP3 output successful: {result}")
        return result.get('request_id')
    else:
        print(f"JSON MP3 output failed: {response.status_code} - {response.text}")
        return None

def test_direct_mp3_output(mp3_file_path: str):
    """MP3形式で直接出力するテスト（同期）"""
    print(f"Testing direct MP3 output with: {mp3_file_path}")
    
    if not os.path.exists(mp3_file_path):
        print(f"Error: File not found: {mp3_file_path}")
        return None
    
    # ファイルをアップロード（直接MP3出力）
    with open(mp3_file_path, 'rb') as f:
        files = {'audio_file': (os.path.basename(mp3_file_path), f, 'audio/mpeg')}
        data = {
            'audio_duration': 30.0,
            'prompt': 'trap, hip hop, heavy bass, 808',
            'lyrics': '[verse]\nBass drops hard\nTrap beats flow\n[chorus]\nFeel the 808',
            'infer_step': 30,
            'guidance_scale': 12.0,
            'ref_audio_strength': 0.7
        }
        
        print("Sending request for direct MP3 output... (this may take a while)")
        response = requests.post(f"{API_BASE_URL}/generate_music_with_audio_direct_mp3", files=files, data=data, timeout=300)
    
    if response.status_code == 200:
        # 直接MP3ファイルが返される
        output_file = f"output_direct_mp3_{int(time.time())}.mp3"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Direct MP3 output successful: {output_file}")
        print(f"File size: {len(response.content)} bytes")
        return True
    else:
        print(f"Direct MP3 output failed: {response.status_code} - {response.text}")
        return False

def check_status(request_id: str):
    """リクエストのステータスをチェック"""
    response = requests.get(f"{API_BASE_URL}/status/{request_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Status check failed: {response.status_code} - {response.text}")
        return None

def wait_for_completion(request_id: str, timeout: int = 300):
    """処理完了まで待機"""
    print(f"Waiting for completion of request: {request_id}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status_data = check_status(request_id)
        if status_data:
            status = status_data.get('status')
            print(f"Status: {status}")
            
            if status == 'completed':
                print("Processing completed successfully!")
                return status_data
            elif status == 'failed':
                print(f"Processing failed: {status_data.get('error')}")
                return status_data
        
        time.sleep(5)  # 5秒待機
    
    print("Timeout waiting for completion")
    return None

def download_result(request_id: str, output_path: str):
    """結果をダウンロード"""
    response = requests.get(f"{API_BASE_URL}/result/{request_id}")
    
    if response.status_code == 200:
        if response.headers.get('content-type', '').startswith('audio/'):
            # オーディオファイルとして保存
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Audio saved to: {output_path}")
        else:
            # JSONレスポンスの場合
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print(f"Download failed: {response.status_code} - {response.text}")

def test_health_check():
    """ヘルスチェック"""
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        health_data = response.json()
        print(f"Health check: {health_data}")
        return health_data.get('pipeline_loaded', False)
    else:
        print(f"Health check failed: {response.status_code} - {response.text}")
        return False

def main():
    """メイン処理"""
    print("=== MP3 Upload API Test ===")
    
    # ヘルスチェック
    if not test_health_check():
        print("Warning: Pipeline may not be loaded. Please initialize the server first.")
        return
    
    # テスト用のMP3ファイルを指定（存在する場合）
    test_mp3_files = [
        "./data/test_track_001.mp3",  # プロジェクト内のテストファイル
        "./music.mp3",  # プロジェクト内のサンプルファイル
        "/path/to/your/test.mp3"  # 任意のMP3ファイルパスに変更してください
    ]
    
    mp3_file = None
    for file_path in test_mp3_files:
        if os.path.exists(file_path):
            mp3_file = file_path
            break
    
    if not mp3_file:
        print("No test MP3 file found. Please provide a valid MP3 file path.")
        print("Available files in current directory:")
        for file in os.listdir('.'):
            if file.endswith('.mp3'):
                print(f"  - {file}")
        return
    
    print(f"Using test file: {mp3_file}")
    
    # 1. ファイルアップロード方式のテスト
    print("\n--- Testing File Upload ---")
    request_id1 = test_file_upload(mp3_file)
    
    if request_id1:
        result1 = wait_for_completion(request_id1)
        if result1 and result1.get('status') == 'completed':
            download_result(request_id1, f"output_file_upload_{int(time.time())}.wav")
    
    # 2. Base64アップロード方式のテスト（Form形式）
    print("\n--- Testing Base64 Upload (Form) ---")
    request_id2 = test_base64_upload(mp3_file)
    
    if request_id2:
        result2 = wait_for_completion(request_id2)
        if result2 and result2.get('status') == 'completed':
            download_result(request_id2, f"output_base64_upload_{int(time.time())}.wav")
    
    # 3. JSON形式のBase64アップロード方式のテスト
    print("\n--- Testing JSON Base64 Upload ---")
    request_id3 = test_json_upload(mp3_file)
    
    if request_id3:
        result3 = wait_for_completion(request_id3)
        if result3 and result3.get('status') == 'completed':
            download_result(request_id3, f"output_json_upload_{int(time.time())}.wav")
    
    # 4. MP3形式で出力するテスト
    print("\n--- Testing MP3 Output ---")
    request_id4 = test_mp3_output(mp3_file)
    
    if request_id4:
        result4 = wait_for_completion(request_id4)
        if result4 and result4.get('status') == 'completed':
            download_result(request_id4, f"output_mp3_format_{int(time.time())}.mp3")
    
    # 5. JSON形式でMP3出力するテスト
    print("\n--- Testing JSON MP3 Output ---")
    request_id5 = test_json_mp3_output(mp3_file)
    
    if request_id5:
        result5 = wait_for_completion(request_id5)
        if result5 and result5.get('status') == 'completed':
            download_result(request_id5, f"output_json_mp3_{int(time.time())}.mp3")
    
    # 6. 直接MP3出力するテスト
    print("\n--- Testing Direct MP3 Output ---")
    test_direct_mp3_output(mp3_file)
    
    # 4. MP3形式で出力するテスト
    print("\n--- Testing MP3 Output ---")
    request_id4 = test_mp3_output(mp3_file)
    
    if request_id4:
        result4 = wait_for_completion(request_id4)
        if result4 and result4.get('status') == 'completed':
            download_result(request_id4, f"output_mp3_upload_{int(time.time())}.wav")
    
    # 5. JSON形式でMP3出力するテスト
    print("\n--- Testing JSON MP3 Output ---")
    request_id5 = test_json_mp3_output(mp3_file)
    
    if request_id5:
        result5 = wait_for_completion(request_id5)
        if result5 and result5.get('status') == 'completed':
            download_result(request_id5, f"output_json_mp3_upload_{int(time.time())}.wav")
    
    # 6. MP3形式で直接出力するテスト
    print("\n--- Testing Direct MP3 Output ---")
    direct_mp3_result = test_direct_mp3_output(mp3_file)
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    main()
