#!/usr/bin/env python3
"""
music.pyと同じ形式でHTTPリクエストを送信してテストする
"""
import requests
import json
import re
import tempfile
import os

def test_music_generation():
    print("=== Testing music generation with form data ===")
    
    # music.pyと同じデータ構造
    test_lyrics_dict = {
        "verse": "春の風に誘われて\n桜の花びらがひらり\n新しい季節の始まり",
        "chorus": "歩いていこう この道を\n希望を胸に抱いて\n未来へと続く道を",
        "bridge": "時には立ち止まっても\nまた歩き出せばいい",
        "outro": "いつまでも歌い続けよう\nこの美しい日々を"
    }
    
    # music.pyのconvert_lyrics_dict_to_text関数の処理を再現
    def convert_lyrics_dict_to_text(lyrics_dict):
        result = ""
        for key, value in lyrics_dict.items():
            processed_key = re.sub(r"[（(].*?[）)]", "", key).strip()
            processed_value = re.sub(r"^[（(].*?[）)]\s*\n?", "", value)
            result += f"[{processed_key}]\n{processed_value}\n"
        return result
    
    lyrics_text = convert_lyrics_dict_to_text(test_lyrics_dict)
    genre = "pop, ballad, emotional"
    
    print("Test data:")
    print(f"lyrics: {repr(lyrics_text[:100])}..." if len(lyrics_text) > 100 else f"lyrics: {repr(lyrics_text)}")
    print(f"genre: {genre}")
    
    # APIに送信するデータの準備（music.pyと同じ形式）
    data = {
        "audio_duration": -1,
        "genre": genre,
        "infer_step": 27,
        "lyrics": lyrics_text,
        "guidance_scale": 15,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": 10,
        "guidance_interval": 0.5,
        "guidance_interval_decay": 0.0,
        "min_guidance_scale": 3,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0
    }
    
    print("\nSending request to /generate_music_form...")
    
    try:
        # music.pyのURLを使用
        ace_url = "http://127.0.0.1:8019/generate_music_form"
        response = requests.post(ace_url, data=data, timeout=120)  # タイムアウトを120秒に設定
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"エラー: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        # サーバからのContent-Dispositionヘッダーからファイル名を抽出
        cd = response.headers.get("Content-Disposition", "")
        match = re.search(r'filename="?([^"]+)"?', cd)
        filename = match.group(1) if match else "output.wav"
        
        print(f"Received audio data, filename: {filename}")
        print(f"Response content length: {len(response.content)} bytes")
        
        # 音楽データを一時ファイルに保存
        temp_file = tempfile.NamedTemporaryFile(suffix=f".{filename.split('.')[-1]}", delete=False)
        temp_file.write(response.content)
        temp_file.close()
        
        print(f"音楽ファイルを保存しました: {temp_file.name}")
        
        # ファイルサイズを確認
        if os.path.exists(temp_file.name):
            file_size = os.path.getsize(temp_file.name)
            print(f"File size: {file_size} bytes")
            
            # ファイルの形式を確認（最初の数バイト）
            with open(temp_file.name, 'rb') as f:
                header = f.read(16)
                print(f"File header: {header}")
                
            return temp_file.name
        else:
            print("Warning: File does not exist")
            return None
            
    except requests.exceptions.Timeout:
        print("リクエストがタイムアウトしました。音楽生成には時間がかかる場合があります。")
        return None
    except Exception as e:
        print(f"Error during request: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_music_generation()
    if result:
        print(f"\n成功！音楽ファイル: {result}")
        # オプション: ファイルの詳細情報を表示
        try:
            import subprocess
            file_info = subprocess.run(['file', result], capture_output=True, text=True)
            print(f"File type: {file_info.stdout.strip()}")
        except:
            pass
    else:
        print("\n音楽生成に失敗しました。")
