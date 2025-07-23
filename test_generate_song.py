#!/usr/bin/env python3
"""
music.pyのgenerate_song関数を直接テストする
"""
import sys
sys.path.append('/home/animede/momo_song2_yutub')

from music import generate_song
import json

# テスト用のデータ
test_data = {
    'lyrics': {
        'verse_1': 'Test verse lyrics',
        'chorus': 'Test chorus lyrics'
    },
    'genre': 'pop rock'
}

try:
    print("Testing generate_song function...")
    result = generate_song(test_data, infer_step=10)
    print(f'Result type: {type(result)}')
    
    if result is None:
        print('Error: Function returned None')
    elif isinstance(result, bytes):
        print(f'Success: Returns {len(result)} bytes')
        
        # Base64エンコードのテスト
        import base64
        try:
            audio_base64 = 'data:audio/mp3;base64,' + base64.b64encode(result).decode()
            print(f'Base64 encoding successful, length: {len(audio_base64)}')
        except Exception as b64_error:
            print(f'Base64 encoding failed: {b64_error}')
    else:
        print(f'Unexpected result type: {type(result)}')
        print(f'Result content: {result}')
        
except Exception as e:
    print(f'Error testing generate_song: {e}')
    import traceback
    print(f'Full traceback: {traceback.format_exc()}')
