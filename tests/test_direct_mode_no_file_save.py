#!/usr/bin/env python3
"""
ダイレクトモード（ファイル保存なし）のテストスクリプト
"""

import requests
import json
import time
import os

# APIサーバーのベースURL
BASE_URL = "http://localhost:8019"

def test_direct_mode_no_file_save():
    """ダイレクトモードでファイルが保存されないことをテスト"""
    print("🧪 ダイレクトモード（ファイル保存なし）をテスト中...")
    
    # 生成前の出力ディレクトリの状態を記録
    outputs_dir = "./outputs"
    generated_music_dir = "./generated_music"
    
    files_before = set()
    if os.path.exists(outputs_dir):
        files_before.update([os.path.join(outputs_dir, f) for f in os.listdir(outputs_dir)])
    if os.path.exists(generated_music_dir):
        files_before.update([os.path.join(generated_music_dir, f) for f in os.listdir(generated_music_dir)])
    
    # APIサーバーの初期化を確認
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ APIサーバーが利用できません")
            return False
        
        health_data = response.json()
        if not health_data.get("pipeline_loaded"):
            print("❌ パイプラインが初期化されていません")
            return False
            
    except requests.exceptions.RequestException:
        print("❌ APIサーバーが起動していません")
        return False
    
    # ダイレクトモードでの音楽生成をテスト（短い音楽で高速テスト）
    request_data = {
        "format": "wav",
        "audio_duration": 10.0,  # 短い時間でテスト
        "prompt": "simple test music",
        "lyrics": "test",
        "infer_step": 10,  # 少ないステップで高速化
        "guidance_scale": 10.0
    }
    
    try:
        print("📡 ダイレクトエンドポイントに音楽生成リクエストを送信中...")
        response = requests.post(f"{BASE_URL}/generate_music_direct", json=request_data, timeout=120)
        
        if response.status_code == 200:
            # レスポンスが音楽ファイルであることを確認
            content_type = response.headers.get('Content-Type', '')
            if content_type.startswith('audio/'):
                print(f"✅ 音楽データを直接受信 (Content-Type: {content_type})")
                print(f"📊 受信データサイズ: {len(response.content)} bytes")
                
                # 生成後の出力ディレクトリの状態を確認
                files_after = set()
                if os.path.exists(outputs_dir):
                    files_after.update([os.path.join(outputs_dir, f) for f in os.listdir(outputs_dir)])
                if os.path.exists(generated_music_dir):
                    files_after.update([os.path.join(generated_music_dir, f) for f in os.listdir(generated_music_dir)])
                
                new_files = files_after - files_before
                
                if len(new_files) == 0:
                    print("✅ ダイレクトモードでファイルが保存されませんでした（期待通り）")
                    return True
                else:
                    print(f"❌ 新しいファイルが作成されました: {new_files}")
                    return False
            else:
                print(f"❌ 予期しないContent-Type: {content_type}")
                print(f"レスポンス内容: {response.text[:200]}...")
                return False
        else:
            print(f"❌ リクエストが失敗しました (ステータス: {response.status_code})")
            print(f"エラー内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ リクエストがタイムアウトしました")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
        return False

def test_normal_mode_file_save():
    """通常モードでファイルが保存されることをテスト"""
    print("\n🧪 通常モード（ファイル保存あり）をテスト中...")
    
    # 生成前の出力ディレクトリの状態を記録
    outputs_dir = "./outputs"
    files_before = set()
    if os.path.exists(outputs_dir):
        files_before.update([os.path.join(outputs_dir, f) for f in os.listdir(outputs_dir)])
    
    # 通常モードでの音楽生成をテスト
    request_data = {
        "format": "wav",
        "audio_duration": 10.0,  # 短い時間でテスト
        "prompt": "simple test music",
        "lyrics": "test",
        "infer_step": 10,  # 少ないステップで高速化
        "guidance_scale": 10.0,
        "return_file_data": False  # ファイル保存モード
    }
    
    try:
        print("📡 通常エンドポイントに音楽生成リクエストを送信中...")
        response = requests.post(f"{BASE_URL}/generate_music", json=request_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                request_id = data.get("request_id")
                print(f"📝 リクエストID: {request_id}")
                
                # ステータスを確認
                max_wait = 120  # 最大2分待機
                wait_time = 0
                while wait_time < max_wait:
                    status_response = requests.get(f"{BASE_URL}/status/{request_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get("status")
                        print(f"📊 ステータス: {status}")
                        
                        if status == "completed":
                            # 生成後の出力ディレクトリの状態を確認
                            files_after = set()
                            if os.path.exists(outputs_dir):
                                files_after.update([os.path.join(outputs_dir, f) for f in os.listdir(outputs_dir)])
                            
                            new_files = files_after - files_before
                            
                            if len(new_files) > 0:
                                print(f"✅ ファイルが正常に保存されました: {new_files}")
                                
                                # クリーンアップ
                                for file_path in new_files:
                                    try:
                                        os.remove(file_path)
                                        print(f"🧹 テストファイルを削除: {file_path}")
                                    except:
                                        pass
                                
                                return True
                            else:
                                print("❌ ファイルが保存されませんでした")
                                return False
                        elif status == "failed":
                            print(f"❌ 音楽生成が失敗しました: {status_data.get('error', 'Unknown error')}")
                            return False
                    
                    time.sleep(5)
                    wait_time += 5
                
                print("❌ 処理がタイムアウトしました")
                return False
            else:
                print(f"❌ リクエストが失敗しました: {data.get('error_message')}")
                return False
        else:
            print(f"❌ リクエストが失敗しました (ステータス: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ダイレクトモード（ファイル保存なし）テストを開始")
    print("=" * 60)
    
    # ダイレクトモードのテスト
    direct_result = test_direct_mode_no_file_save()
    
    # 通常モードのテスト（比較用）
    normal_result = test_normal_mode_file_save()
    
    print("\n" + "=" * 60)
    print("📋 テスト結果:")
    print(f"  ダイレクトモード（ファイル保存なし）: {'✅ 成功' if direct_result else '❌ 失敗'}")
    print(f"  通常モード（ファイル保存あり）: {'✅ 成功' if normal_result else '❌ 失敗'}")
    
    if direct_result and normal_result:
        print("\n🎉 すべてのテストが成功しました！")
        print("ダイレクトモードではファイルが保存されず、通常モードではファイルが保存されます。")
        exit(0)
    else:
        print("\n❌ テストで失敗がありました。")
        exit(1)
