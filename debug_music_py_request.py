#!/usr/bin/env python3
"""
music.pyが送信するリクエストをデバッグするスクリプト
"""
import requests
import json

# music.pyと同じデータ構造でテスト
def test_music_py_format():
    print("=== Testing music.py format ===")
    
    # music.pyのgenerate_song関数と同じデータ構造
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
            processed_key = key.strip()
            processed_value = value
            result += f"[{processed_key}]\n{processed_value}\n"
        return result
    
    lyrics_text = convert_lyrics_dict_to_text(test_lyrics_dict)
    print("Converted lyrics:")
    print(repr(lyrics_text))
    
    # music.pyと同じデータ構造
    data = {
        "audio_duration": -1,
        "genre": "pop, ballad, emotional",
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
    
    print("\nSending data:")
    for key, value in data.items():
        print(f"  {key}: {repr(value)}")
    
    # /generate_music エンドポイントにformデータとして送信
    try:
        print(f"\n=== Testing POST to http://localhost:8019/generate_music (form data) ===")
        response = requests.post("http://localhost:8019/generate_music", data=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 422:
            try:
                error_detail = response.json()
                print(f"Error Detail: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error Text: {response.text}")
        else:
            print(f"Response length: {len(response.content)} bytes")
            
    except Exception as e:
        print(f"Request failed: {e}")
    
    # JSONとしても試す
    try:
        print(f"\n=== Testing POST to http://localhost:8019/generate_music (JSON) ===")
        response = requests.post(
            "http://localhost:8019/generate_music", 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 422:
            try:
                error_detail = response.json()
                print(f"Error Detail: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error Text: {response.text}")
        else:
            print(f"Response length: {len(response.content)} bytes")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_music_py_format()
