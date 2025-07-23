#!/usr/bin/env python3
"""
music.pyのgenerate_song関数をテストする
"""
import sys
import os

# music.pyのパスを追加
sys.path.append('/home/animede/momo_song2_yutub')

# music.pyから必要な関数をインポート
from music import generate_song, convert_lyrics_dict_to_text

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
