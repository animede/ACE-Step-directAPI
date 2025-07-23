"""
Gradio互換APIのテストスクリプト

このスクリプトは gradio_compatible_api.py サーバーをテストします。
"""

import requests
import json
import time
import os
from typing import Dict, Any

# 設定の読み込み機能
def load_test_config():
    """テスト設定を読み込み"""
    config_file = "test_config.json"
    default_config = {
        "base_url": "http://localhost:8019",
        "timeout_short": 30,
        "timeout_medium": 300,
        "timeout_long": 600,
        "test_audio_duration_short": 5.0,
        "test_audio_duration_medium": 15.0,
        "test_audio_duration_long": 30.0,
        "test_inference_steps": 20
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # デフォルト値で不足分を補完
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                print(f"設定ファイル {config_file} を読み込みました")
                return config
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}. デフォルト設定を使用します")
    
    return default_config

# グローバル設定
CONFIG = load_test_config()
BASE_URL = CONFIG["base_url"]

# APIエンドポイント設定
INITIALIZE_URL = f"{BASE_URL}/initialize"
GENERATE_URL = f"{BASE_URL}/generate_music"
GENERATE_DIRECT_URL = f"{BASE_URL}/generate_music_direct"
HEALTH_URL = f"{BASE_URL}/health"  # gradio_compatible_api.pyのヘルスエンドポイント

def test_server_health():
    """サーバーの稼働状況をチェック"""
    print("=== サーバーヘルスチェック ===")
    try:
        response = requests.get(HEALTH_URL, timeout=CONFIG["timeout_short"])
        if response.status_code == 200:
            print("✓ サーバーは正常に稼働中")
            return True
        else:
            print(f"✗ サーバーエラー: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ サーバーに接続できません。gradio_compatible_api.pyが起動しているか確認してください")
        return False
    except Exception as e:
        print(f"✗ ヘルスチェック失敗: {e}")
        return False

def test_initialize_pipeline():
    """パイプライン初期化テスト"""
    print("\n=== パイプライン初期化テスト ===")
    
    init_data = {
        "checkpoint_path": "",  # デフォルトパス使用
        "device_id": 0,
        "bf16": True,
        "torch_compile": False,
        "cpu_offload": False,
        "overlapped_decode": False
    }
    
    try:
        print("初期化リクエスト送信中...")
        response = requests.post(INITIALIZE_URL, json=init_data, timeout=CONFIG["timeout_medium"])
        
        if response.status_code == 200:
            result = response.json()
            print("✓ パイプライン初期化成功")
            print(f"レスポンス: {result}")
            return True
        else:
            print(f"✗ 初期化失敗: {response.status_code}")
            print(f"エラー詳細: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ 初期化タイムアウト（5分以上かかっています）")
        return False
    except Exception as e:
        print(f"✗ 初期化エラー: {e}")
        return False

def test_generate_music_simple():
    """シンプルな音楽生成テスト"""
    print("\n=== シンプル音楽生成テスト ===")
    
    # 最小限のパラメータでテスト
    request_data = {
        "format": "wav",
        "audio_duration": 15.0,  # 短めの時間で高速テスト
        "prompt": "acoustic guitar, calm, peaceful",
        "lyrics": "",
        "infer_step": 20,  # 少ないステップで高速化
        "guidance_scale": 15.0,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": 10.0,
        "guidance_interval": 0.5,
        "guidance_interval_decay": 0.0,
        "min_guidance_scale": 3.0,
        "use_erg_tag": True,
        "use_erg_lyric": False,
        "use_erg_diffusion": True,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0,
        "audio2audio_enable": False,
        "ref_audio_strength": 0.5,
        "lora_name_or_path": "none",
        "lora_weight": 1.0
    }
    
    try:
        print("音楽生成リクエスト送信中...")
        print(f"プロンプト: {request_data['prompt']}")
        print(f"継続時間: {request_data['audio_duration']}秒")
        
        start_time = time.time()
        response = requests.post(GENERATE_URL, json=request_data, timeout=CONFIG["timeout_long"])
        elapsed_time = time.time() - start_time
        
        print(f"処理時間: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ 音楽生成成功")
            print(f"成功: {result.get('success')}")
            print(f"音声ファイル: {result.get('audio_path')}")
            
            # 音声ファイルの存在確認
            audio_path = result.get('audio_path')
            if audio_path and os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"✓ 音声ファイル確認済み (サイズ: {file_size} bytes)")
            else:
                print(f"✗ 音声ファイルが見つかりません: {audio_path}")
            
            return True
        else:
            print(f"✗ 生成失敗: {response.status_code}")
            print(f"エラー詳細: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ 音楽生成タイムアウト（10分以上かかっています）")
        return False
    except Exception as e:
        print(f"✗ 音楽生成エラー: {e}")
        return False

def test_generate_music_with_lyrics():
    """歌詞付き音楽生成テスト"""
    print("\n=== 歌詞付き音楽生成テスト ===")
    
    request_data = {
        "format": "wav",
        "audio_duration": 20.0,
        "prompt": "pop, upbeat, energetic, 120 BPM",
        "lyrics": """[verse]
Hello world this is a test
Making music with AI
Simple lyrics simple beat
Let the rhythm come alive

[chorus]
Test test test
This is just a test
AI making music
At its very best
""",
        "infer_step": 25,
        "guidance_scale": 15.0,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": 10.0,
        "use_erg_tag": True,
        "use_erg_lyric": True,  # 歌詞機能を有効化
        "use_erg_diffusion": True,
        "lora_name_or_path": "none",
        "lora_weight": 1.0
    }
    
    try:
        print("歌詞付き音楽生成リクエスト送信中...")
        print(f"プロンプト: {request_data['prompt']}")
        
        start_time = time.time()
        response = requests.post(GENERATE_URL, json=request_data, timeout=CONFIG["timeout_long"])
        elapsed_time = time.time() - start_time
        
        print(f"処理時間: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ 歌詞付き音楽生成成功")
            print(f"音声ファイル: {result.get('audio_path')}")
            return True
        else:
            print(f"✗ 歌詞付き生成失敗: {response.status_code}")
            print(f"エラー詳細: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 歌詞付き生成エラー: {e}")
        return False

def test_error_handling():
    """エラーハンドリングテスト"""
    print("\n=== エラーハンドリングテスト ===")
    
    # 無効なパラメータでテスト
    invalid_request = {
        "format": "invalid_format",
        "audio_duration": -1.0,  # 無効な値
        "infer_step": 0,  # 無効な値
        "guidance_scale": -10.0  # 無効な値
    }
    
    try:
        response = requests.post(GENERATE_URL, json=invalid_request, timeout=CONFIG["timeout_short"])
        
        if response.status_code != 200:
            print("✓ 無効なパラメータで適切にエラーハンドリング")
            return True
        else:
            result = response.json()
            if not result.get('success', True):
                print("✓ APIレベルでエラーハンドリング")
                print(f"エラーメッセージ: {result.get('error_message')}")
                return True
            else:
                print("✗ 無効なパラメータが受け入れられました")
                return False
                
    except Exception as e:
        print(f"エラーハンドリングテスト中の例外: {e}")
        return False

def test_different_schedulers():
    """異なるスケジューラーのテスト"""
    print("\n=== 異なるスケジューラーテスト ===")
    
    schedulers = ["euler", "dpm_solver_multistep", "ddim"]
    results = []
    
    for scheduler in schedulers:
        print(f"\n--- {scheduler} スケジューラーテスト ---")
        
        request_data = {
            "format": "wav",
            "audio_duration": 10.0,  # 短時間で高速テスト
            "prompt": "electronic, ambient, soft",
            "lyrics": "",
            "infer_step": 15,  # 最小ステップ
            "guidance_scale": 10.0,
            "scheduler_type": scheduler,
            "cfg_type": "apg",
            "omega_scale": 10.0,
            "use_erg_tag": True,
            "use_erg_lyric": False,
            "use_erg_diffusion": True,
            "lora_name_or_path": "none",
            "lora_weight": 1.0
        }
        
        try:
            start_time = time.time()
            response = requests.post(GENERATE_URL, json=request_data, timeout=CONFIG["timeout_medium"])
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✓ {scheduler}: 成功 ({elapsed_time:.2f}秒)")
                    results.append(f"✓ {scheduler}")
                else:
                    print(f"✗ {scheduler}: API失敗 - {result.get('error_message')}")
                    results.append(f"✗ {scheduler}")
            else:
                print(f"✗ {scheduler}: HTTP失敗 ({response.status_code})")
                results.append(f"✗ {scheduler}")
                
        except Exception as e:
            print(f"✗ {scheduler}: 例外 - {e}")
            results.append(f"✗ {scheduler}")
    
    print(f"\nスケジューラーテスト結果: {results}")
    return len([r for r in results if r.startswith("✓")]) > 0

def test_different_durations():
    """異なる継続時間のテスト"""
    print("\n=== 異なる継続時間テスト ===")
    
    durations = [5.0, 15.0, 30.0]  # 短、中、長
    results = []
    
    for duration in durations:
        print(f"\n--- {duration}秒 継続時間テスト ---")
        
        request_data = {
            "format": "wav",
            "audio_duration": duration,
            "prompt": "piano, classical, peaceful",
            "lyrics": "",
            "infer_step": 20,
            "guidance_scale": 15.0,
            "scheduler_type": "euler",
            "cfg_type": "apg",
            "omega_scale": 10.0,
            "use_erg_tag": True,
            "use_erg_lyric": False,
            "use_erg_diffusion": True,
            "lora_name_or_path": "none",
            "lora_weight": 1.0
        }
        
        try:
            start_time = time.time()
            response = requests.post(GENERATE_URL, json=request_data, timeout=CONFIG["timeout_long"])
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    audio_path = result.get('audio_path')
                    if audio_path and os.path.exists(audio_path):
                        file_size = os.path.getsize(audio_path)
                        print(f"✓ {duration}秒: 成功 ({elapsed_time:.2f}秒, {file_size}bytes)")
                        results.append(f"✓ {duration}秒")
                    else:
                        print(f"✗ {duration}秒: ファイル未作成")
                        results.append(f"✗ {duration}秒")
                else:
                    print(f"✗ {duration}秒: API失敗")
                    results.append(f"✗ {duration}秒")
            else:
                print(f"✗ {duration}秒: HTTP失敗")
                results.append(f"✗ {duration}秒")
                
        except Exception as e:
            print(f"✗ {duration}秒: 例外 - {e}")
            results.append(f"✗ {duration}秒")
    
    print(f"\n継続時間テスト結果: {results}")
    return len([r for r in results if r.startswith("✓")]) > 0

def test_guidance_scales():
    """異なるガイダンススケールのテスト"""
    print("\n=== ガイダンススケールテスト ===")
    
    guidance_scales = [5.0, 10.0, 15.0, 20.0]
    results = []
    
    for scale in guidance_scales:
        print(f"\n--- ガイダンススケール {scale} テスト ---")
        
        request_data = {
            "format": "wav",
            "audio_duration": 8.0,
            "prompt": "rock, guitar, energetic",
            "lyrics": "",
            "infer_step": 15,
            "guidance_scale": scale,
            "scheduler_type": "euler",
            "cfg_type": "apg",
            "omega_scale": 10.0,
            "use_erg_tag": True,
            "use_erg_lyric": False,
            "use_erg_diffusion": True,
            "lora_name_or_path": "none",
            "lora_weight": 1.0
        }
        
        try:
            start_time = time.time()
            response = requests.post(GENERATE_URL, json=request_data, timeout=CONFIG["timeout_medium"])
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✓ スケール{scale}: 成功 ({elapsed_time:.2f}秒)")
                    results.append(f"✓ {scale}")
                else:
                    print(f"✗ スケール{scale}: 失敗")
                    results.append(f"✗ {scale}")
            else:
                print(f"✗ スケール{scale}: HTTP失敗")
                results.append(f"✗ {scale}")
                
        except Exception as e:
            print(f"✗ スケール{scale}: 例外 - {e}")
            results.append(f"✗ {scale}")
    
    print(f"\nガイダンススケールテスト結果: {results}")
    return len([r for r in results if r.startswith("✓")]) > 0

def test_api_endpoints():
    """利用可能なAPIエンドポイントを確認"""
    print("\n=== APIエンドポイント確認 ===")
    
    endpoints_to_test = [
        ("/health", "ヘルスチェック"),
        ("/docs", "FastAPI ドキュメント"),
        ("/generate_music", "音楽生成 (Gradio互換API)"),
        ("/initialize", "パイプライン初期化"),
        ("/sample_data", "サンプルデータ (Gradio互換)")
    ]
    
    available_endpoints = []
    
    for endpoint, description in endpoints_to_test:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 405]:  # 405 = Method Not Allowed (POSTが期待される場合)
                print(f"✓ {endpoint} - {description} (ステータス: {response.status_code})")
                available_endpoints.append(endpoint)
            else:
                print(f"✗ {endpoint} - {description} (ステータス: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ {endpoint} - 接続エラー")
        except Exception as e:
            print(f"✗ {endpoint} - エラー: {e}")
    
    print(f"\n利用可能なエンドポイント: {available_endpoints}")
    
    # Gradio互換APIのみをサポート
    if "/generate_music" in available_endpoints:
        print("→ Gradio互換APIサーバーが動作中")
        return "gradio_compatible"
    else:
        print("→ Gradio互換APIサーバーが見つかりません")
        return "unknown"

def run_all_tests():
    """全テストを実行"""
    print("🎵 Gradio互換API テストスイート 🎵")
    print("=" * 50)
    
    test_results = []
    
    # 1. サーバーヘルスチェック
    if test_server_health():
        test_results.append("✓ ヘルスチェック")
        
        # 2. APIエンドポイント確認
        api_type = test_api_endpoints()
        
        if api_type == "gradio_compatible":
            print("\n→ Gradio互換APIテストを実行します")
            
            # 3. パイプライン初期化
            if test_initialize_pipeline():
                test_results.append("✓ パイプライン初期化")
                
                # 4. シンプル音楽生成
                if test_generate_music_simple():
                    test_results.append("✓ シンプル音楽生成")
                else:
                    test_results.append("✗ シンプル音楽生成")
                
                # 5. 直接音楽生成
                if test_generate_music_direct():
                    test_results.append("✓ 直接音楽生成")
                else:
                    test_results.append("✗ 直接音楽生成")
                
                # 6. 歌詞付き音楽生成
                if test_generate_music_with_lyrics():
                    test_results.append("✓ 歌詞付き音楽生成")
                else:
                    test_results.append("✗ 歌詞付き音楽生成")
                    
            else:
                test_results.append("✗ パイプライン初期化")
                test_results.append("- シンプル音楽生成（スキップ）")
                test_results.append("- 歌詞付き音楽生成（スキップ）")
                
        else:
            test_results.append("✗ Gradio互換APIサーバーが見つかりません")
            test_results.append("- 音楽生成テスト（スキップ）")
    else:
        test_results.append("✗ ヘルスチェック")
        test_results.append("- 他のテスト（スキップ）")
    
    # エラーハンドリング（独立してテスト可能）
    if test_error_handling():
        test_results.append("✓ エラーハンドリング")
    else:
        test_results.append("✗ エラーハンドリング")
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("🎯 テスト結果サマリー 🎯")
    print("=" * 50)
    
    for result in test_results:
        print(result)
    
    success_count = len([r for r in test_results if r.startswith("✓")])
    total_count = len([r for r in test_results if not r.startswith("-")])
    
    print(f"\n成功: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 全てのテストが成功しました！")
    else:
        print("⚠️  一部のテストが失敗しました。ログを確認してください。")

def run_extended_tests():
    """拡張テストを実行"""
    print("\n" + "=" * 50)
    print("🔬 拡張テストスイート 🔬")
    print("=" * 50)
    
    extended_results = []
    
    # 基本テストが成功している場合のみ実行
    if test_server_health():
        if test_different_schedulers():
            extended_results.append("✓ スケジューラーテスト")
        else:
            extended_results.append("✗ スケジューラーテスト")
            
        if test_different_durations():
            extended_results.append("✓ 継続時間テスト")
        else:
            extended_results.append("✗ 継続時間テスト")
            
        if test_guidance_scales():
            extended_results.append("✓ ガイダンススケールテスト")
        else:
            extended_results.append("✗ ガイダンススケールテスト")
    else:
        print("サーバーが利用できないため、拡張テストをスキップします")
        return
    
    print("\n" + "=" * 50)
    print("🔬 拡張テスト結果 🔬")
    print("=" * 50)
    
    for result in extended_results:
        print(result)
    
    success_count = len([r for r in extended_results if r.startswith("✓")])
    total_count = len(extended_results)
    
    print(f"\n拡張テスト成功: {success_count}/{total_count}")

def test_generate_music_direct():
    """直接音楽生成テスト（ファイル返却型）"""
    print("\n=== 直接音楽生成テスト ===")
    
    request_data = {
        "format": "wav",
        "audio_duration": CONFIG["test_audio_duration_short"],
        "prompt": "acoustic guitar, calm, peaceful",
        "lyrics": "",
        "infer_step": CONFIG["test_inference_steps"],
        "guidance_scale": 15.0,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": 10.0,
        "use_erg_tag": True,
        "use_erg_lyric": False,
        "use_erg_diffusion": True,
        "lora_name_or_path": "none",
        "lora_weight": 1.0,
        "return_file_data": True
    }
    
    print("直接音楽生成リクエスト送信中...")
    print(f"プロンプト: {request_data['prompt']}")
    print(f"継続時間: {request_data['audio_duration']}秒")
    
    try:
        start_time = time.time()
        response = requests.post(GENERATE_DIRECT_URL, json=request_data, timeout=CONFIG["timeout_long"])
        end_time = time.time()
        
        print(f"処理時間: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ 直接音楽生成成功")
            print(f"成功: {result.get('success')}")
            
            # 音声ファイルの存在確認
            audio_path = result.get('audio_path')
            if audio_path and os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"✓ 音声ファイル確認済み (サイズ: {file_size} bytes)")
            else:
                print(f"音声ファイル: {audio_path}")
                if result.get('success'):
                    print("ℹ️  ダイレクトモードでは一時ファイルが自動削除される場合があります")
            
            return True
        else:
            print(f"✗ 直接生成失敗: {response.status_code}")
            print(f"エラー詳細: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ 直接音楽生成タイムアウト")
        return False
    except Exception as e:
        print(f"✗ 直接音楽生成エラー: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--extended":
        # 拡張テストモード
        run_extended_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == "--basic":
        # 基本テストのみ
        run_all_tests()
    else:
        # デフォルト: 基本テスト実行
        print("基本テストを実行します。拡張テストを実行する場合は --extended オプションを使用してください。")
        print("例: python test_gradio_compatible_api.py --extended")
        print()
        run_all_tests()
