#!/usr/bin/env python3
"""
ACE-Step Gradio互換API 使用例スクリプト

このスクリプトは gradio_compatible_api.py を使った様々な音楽生成例を示します。
"""

import requests
import json
import time
import os

# 設定
API_BASE_URL = "http://localhost:8019"
OUTPUT_DIR = "./examples/generated_music"

def setup_output_dir():
    """出力ディレクトリを作成"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

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

def generate_music(name, request_data):
    """音楽を生成し、結果を保存"""
    print(f"\n🎵 生成中: {name}")
    print(f"   プロンプト: {request_data.get('prompt', '')}")
    print(f"   継続時間: {request_data.get('audio_duration', 0)}秒")
    
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
                file_size = os.path.getsize(audio_path) if audio_path and os.path.exists(audio_path) else 0
                
                print(f"   ✓ 成功 ({elapsed_time:.1f}秒, {file_size//1024}KB)")
                print(f"   📁 ファイル: {audio_path}")
                
                return audio_path
            else:
                print(f"   ✗ 失敗: {result.get('error_message')}")
                return None
        else:
            print(f"   ✗ HTTPエラー: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ✗ エラー: {e}")
        return None

def example_1_basic_instrumental():
    """例1: 基本的なインストゥルメンタル音楽"""
    return generate_music("基本インストゥルメンタル", {
        "prompt": "acoustic guitar, peaceful, calm, folk",
        "audio_duration": 15.0,
        "infer_step": 30,
        "guidance_scale": 15.0,
        "scheduler_type": "euler"
    })

def example_2_electronic_music():
    """例2: エレクトロニック音楽"""
    return generate_music("エレクトロニック音楽", {
        "prompt": "electronic, synthesizer, upbeat, dance, 128 BPM",
        "audio_duration": 20.0,
        "infer_step": 40,
        "guidance_scale": 12.0,
        "omega_scale": 15.0
    })

def example_3_classical_orchestra():
    """例3: クラシック・オーケストラ"""
    return generate_music("クラシック・オーケストラ", {
        "prompt": "classical, orchestra, strings, dramatic, epic, symphonic",
        "audio_duration": 30.0,
        "infer_step": 60,
        "guidance_scale": 18.0,
        "scheduler_type": "euler"
    })

def example_4_with_lyrics():
    """例4: 歌詞付きポップス"""
    return generate_music("歌詞付きポップス", {
        "prompt": "pop, upbeat, cheerful, guitar, drums, 120 BPM",
        "lyrics": """[verse]
Walking down the street today
Sunshine brightens up my way
Music playing in my heart
This is just the perfect start

[chorus]  
Life is beautiful and bright
Everything will be alright
Singing songs of joy and love
Blessings raining from above""",
        "audio_duration": 25.0,
        "infer_step": 50,
        "guidance_scale": 15.0,
        "use_erg_lyric": True
    })

def example_5_jazz_improvisation():
    """例5: ジャズ即興演奏"""
    return generate_music("ジャズ即興演奏", {
        "prompt": "jazz, piano, saxophone, improvisation, swing, blues scale",
        "audio_duration": 20.0,
        "infer_step": 45,
        "guidance_scale": 14.0,
        "cfg_type": "apg"
    })

def example_6_ambient_soundscape():
    """例6: アンビエント・サウンドスケープ"""
    return generate_music("アンビエント", {
        "prompt": "ambient, atmospheric, drone, ethereal, meditation, nature sounds",
        "audio_duration": 35.0,
        "infer_step": 35,
        "guidance_scale": 10.0,
        "guidance_interval": 0.7
    })

def example_7_rock_energy():
    """例7: エネルギッシュなロック"""
    return generate_music("エネルギッシュロック", {
        "prompt": "rock, electric guitar, powerful drums, energetic, driving rhythm, 140 BPM",
        "audio_duration": 18.0,
        "infer_step": 35,
        "guidance_scale": 16.0,
        "omega_scale": 12.0
    })

def example_8_world_music():
    """例8: 世界音楽 (アフリカンドラム)"""
    return generate_music("アフリカンドラム", {
        "prompt": "african, percussion, djembe, tribal rhythms, world music, ethnic",
        "audio_duration": 22.0,
        "infer_step": 40,
        "guidance_scale": 13.0
    })

def run_all_examples():
    """全ての例を実行"""
    print("🎼 ACE-Step Gradio互換API 音楽生成例")
    print("=" * 60)
    
    # サーバー確認
    if not check_server_health():
        print("\n❌ サーバーが利用できません。gradio_compatible_api.py を起動してください。")
        return
    
    # 出力ディレクトリ準備
    setup_output_dir()
    
    # 各例を実行
    examples = [
        example_1_basic_instrumental,
        example_2_electronic_music,
        example_3_classical_orchestra,
        example_4_with_lyrics,
        example_5_jazz_improvisation,
        example_6_ambient_soundscape,
        example_7_rock_energy,
        example_8_world_music
    ]
    
    results = []
    total_start_time = time.time()
    
    for example_func in examples:
        result = example_func()
        results.append(result is not None)
    
    total_elapsed = time.time() - total_start_time
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 生成結果サマリー")
    print("=" * 60)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"成功: {success_count}/{total_count}")
    print(f"総処理時間: {total_elapsed:.1f}秒")
    print(f"平均処理時間: {total_elapsed/total_count:.1f}秒/曲")
    
    if success_count == total_count:
        print("🎉 全ての例が成功しました！")
    else:
        print("⚠️ 一部の例が失敗しました。")
    
    print(f"\n📁 生成された音楽ファイルは './outputs/' に保存されています。")

def interactive_mode():
    """インタラクティブモード"""
    print("\n🎯 インタラクティブ音楽生成モード")
    print("自由にプロンプトを入力して音楽を生成できます。")
    print("'quit' または 'exit' で終了します。")
    
    while True:
        print("\n" + "-" * 40)
        prompt = input("🎵 音楽のスタイル/ジャンルを入力: ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            print("👋 お疲れ様でした！")
            break
            
        if not prompt:
            print("プロンプトを入力してください。")
            continue
        
        try:
            duration = float(input("⏱️ 継続時間（秒）[15]: ") or "15")
            steps = int(input("🔧 推論ステップ数[30]: ") or "30")
        except ValueError:
            print("数値を正しく入力してください。")
            continue
        
        generate_music("カスタム音楽", {
            "prompt": prompt,
            "audio_duration": duration,
            "infer_step": steps,
            "guidance_scale": 15.0
        })

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_all_examples()
        
        # インタラクティブモードの提案
        print("\n💡 追加で音楽を生成したい場合:")
        print("   python examples_gradio_api.py --interactive")
