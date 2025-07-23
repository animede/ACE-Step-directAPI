#!/usr/bin/env python3
"""
ACE-Step 非同期API 簡単な使用例
"""

import requests
import time

def simple_async_example():
    """シンプルな非同期API使用例"""
    
    API_BASE_URL = "http://localhost:8019"
    
    print("🎵 ACE-Step 非同期API 使用例")
    print("=" * 50)
    
    # 1. 非同期リクエストを送信
    print("1. 音楽生成リクエストを送信中...")
    
    request_data = {
        "format": "mp3",
        "audio_duration": 15.0,
        "prompt": "relaxing piano, jazz, smooth, calm",
        "lyrics": "",
        "infer_step": 30,
        "guidance_scale": 15.0,
        "return_file_data": True
    }
    
    response = requests.post(f"{API_BASE_URL}/generate_music_async", json=request_data)
    
    if response.status_code != 200:
        print(f"❌ エラー: {response.status_code}")
        return
    
    result = response.json()
    request_id = result["request_id"]
    
    print(f"✅ リクエスト送信完了")
    print(f"   リクエストID: {request_id}")
    print(f"   ステータス: {result['status']}")
    
    # 2. 生成の進行状況を監視
    print("\n2. 生成進行状況を監視中...")
    
    start_time = time.time()
    
    while True:
        # ステータスを確認
        status_response = requests.get(f"{API_BASE_URL}/status/{request_id}")
        status_data = status_response.json()
        
        current_status = status_data["status"]
        elapsed_time = time.time() - start_time
        
        print(f"   [{elapsed_time:.1f}s] ステータス: {current_status}")
        
        if current_status == "completed":
            print("✅ 音楽生成完了!")
            break
        elif current_status == "failed":
            error_msg = status_data.get("error", "Unknown error")
            print(f"❌ 生成失敗: {error_msg}")
            return
        
        # 2秒待機してから再確認
        time.sleep(2)
    
    # 3. 結果を取得
    print("\n3. 生成された音楽を取得中...")
    
    result_response = requests.get(f"{API_BASE_URL}/result/{request_id}")
    
    if result_response.status_code == 200:
        # 音楽ファイルとして保存
        filename = f"generated_music_async_{int(time.time())}.mp3"
        
        with open(filename, 'wb') as f:
            f.write(result_response.content)
        
        file_size_kb = len(result_response.content) // 1024
        total_time = time.time() - start_time
        
        print(f"✅ 音楽ファイル保存完了!")
        print(f"   ファイル名: {filename}")
        print(f"   ファイルサイズ: {file_size_kb} KB")
        print(f"   総処理時間: {total_time:.1f}秒")
        
    else:
        print(f"❌ 結果取得エラー: {result_response.status_code}")

def check_queue_status():
    """キューの状況を確認"""
    
    API_BASE_URL = "http://localhost:8019"
    
    print("\n📊 キューの状況確認")
    print("-" * 30)
    
    response = requests.get(f"{API_BASE_URL}/queue/status")
    
    if response.status_code == 200:
        queue_data = response.json()
        
        print(f"キューサイズ: {queue_data['queue_size']}")
        print(f"総リクエスト数: {queue_data['total_requests']}")
        print("\nステータス別件数:")
        
        for status, count in queue_data['status_counts'].items():
            print(f"  {status}: {count}")
    else:
        print(f"❌ キュー状況取得エラー: {response.status_code}")

def main():
    """メイン関数"""
    
    API_BASE_URL = "http://localhost:8019"
    
    # サーバーの接続確認
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            pipeline_status = "ロード済み" if health_data['pipeline_loaded'] else "未ロード"
            print(f"🟢 サーバー接続OK (パイプライン: {pipeline_status})")
        else:
            print(f"🔴 サーバーエラー: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"🔴 サーバーに接続できません: {e}")
        print("\n💡 解決方法:")
        print("   1. gradio_compatible_api.py が起動しているか確認")
        print("   2. ポート8019が利用可能か確認")
        print("   3. ファイアウォール設定を確認")
        return
    
    # キューの状況を確認
    check_queue_status()
    
    # 非同期音楽生成の実行
    simple_async_example()
    
    # 完了後のキューの状況を確認
    check_queue_status()
    
    print("\n🎉 使用例完了!")
    print("\n💡 その他の機能:")
    print("   - 複数リクエストの同時処理")
    print("   - リクエストのキャンセル")
    print("   - 詳細なステータス監視")
    print("\n📖 詳細はtest_async_api.pyとREADME_ASYNC_API.mdをご確認ください")

if __name__ == "__main__":
    main()
