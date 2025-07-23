#!/usr/bin/env python3
"""
music.pyのgenerate_song機能を独立してテストする
"""
import requests
import re
import tempfile
import os

# music.pyから移植したconvert_lyrics_dict_to_text関数
def convert_lyrics_dict_to_text(lyrics_dict):
    if not isinstance(lyrics_dict, dict):
        print(f"lyrics_dictは辞書型である必要があります。現在の型: {type(lyrics_dict)}")
        return lyrics_dict
    result=""
    for key, value in lyrics_dict.items():
        if not isinstance(value, str):
            print(f"警告: 値が文字列ではありません。スキップします。キー: {key}, 値: {value}")
            continue
        processed_key = re.sub(r"[（(].*?[）)]", "", key).strip()
        processed_value = re.sub(r"^[（(].*?[）)]\s*\n?", "", value)
        result += f"[{processed_key}]\n{processed_value}\n"
    return result

# music.pyから移植したgenerate_song関数
def generate_song(jeson_song: dict, infer_step: int = 27, guidance_scale: float = 15, omega_scale: float = 10):
    ace_url = "http://127.0.0.1:8019/generate_music_form"
    
    # JSON 文字列化
    print("======>>>>>jeson_song=",jeson_song)
    lyrics_dic = jeson_song['lyrics']
    print("###### lyrics_dic >>>>",lyrics_dic)
    lyrics = convert_lyrics_dict_to_text(lyrics_dic)
    print("###### lyrics_text >>>>",lyrics)
    genre = jeson_song['genre']
    print("###### genre >>>>",genre)
    
    # APIに送信するデータの準備
    data = {
        "audio_duration": -1,
        "genre": genre,
        "infer_step": infer_step,
        "lyrics": lyrics,
        "guidance_scale": guidance_scale,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": omega_scale,
        "guidance_interval": 0.5,
        "guidance_interval_decay": 0.0,
        "min_guidance_scale": 3,
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0
    }
    
    print("Sending request to ACE-Step API...")
    response = requests.post(ace_url, data=data, timeout=60)
    
    # レスポンスが成功したかチェック
    if response.status_code != 200:
        print(f"音楽生成エラー: Status {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    # サーバからのContent-Dispositionヘッダーからファイル名を抽出
    cd = response.headers.get("Content-Disposition", "")
    match = re.search(r'filename="?([^"]+)"?', cd)
    filename = match.group(1) if match else "output.wav"
    
    # 音楽データを一時ファイルに保存
    temp_file = tempfile.NamedTemporaryFile(suffix=f".{filename.split('.')[-1]}", delete=False)
    temp_file.write(response.content)
    temp_file.close()
    
    print(f"音楽ファイルを保存しました: {temp_file.name}")
    return temp_file.name

def test_generate_song():
    print("=== Testing generate_song function ===")
    
    # テスト用のjson_songデータを作成
    test_lyrics_dict = {
        "verse": "春の風に誘われて\n桜の花びらがひらり\n新しい季節の始まり",
        "chorus": "歩いていこう この道を\n希望を胸に抱いて\n未来へと続く道を",
        "bridge": "時には立ち止まっても\nまた歩き出せばいい",
        "outro": "いつまでも歌い続けよう\nこの美しい日々を"
    }
    
    json_song = {
        "lyrics": test_lyrics_dict,
        "genre": "pop, ballad, emotional"
    }
    
    print("Test data:")
    print(f"lyrics: {test_lyrics_dict}")
    print(f"genre: {json_song['genre']}")
    
    # generate_song関数を呼び出し
    try:
        result = generate_song(
            jeson_song=json_song,
            infer_step=27,
            guidance_scale=15,
            omega_scale=10
        )
        
        if result:
            print(f"Success! Audio file saved at: {result}")
            # ファイルサイズを確認
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"File size: {file_size} bytes")
            else:
                print("Warning: File does not exist")
        else:
            print("Failed: generate_song returned None")
            
    except Exception as e:
        print(f"Error during generate_song: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generate_song()
