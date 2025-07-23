#!/bin/bash

# MP3アップロード機能をcURLでテストするスクリプト

API_BASE_URL="http://localhost:8019"

echo "=== MP3 Upload API Test with cURL ==="

# ヘルスチェック
echo "1. Health Check..."
curl -X GET "$API_BASE_URL/health" | jq .

echo -e "\n"

# テスト用MP3ファイルのパス（存在するファイルに変更してください）
MP3_FILE="./data/test_track_001.mp3"

if [ ! -f "$MP3_FILE" ]; then
    MP3_FILE="./music.mp3"
fi

if [ ! -f "$MP3_FILE" ]; then
    echo "Error: No test MP3 file found. Please provide a valid MP3 file."
    echo "Available MP3 files in current directory:"
    find . -name "*.mp3" -type f
    exit 1
fi

echo "Using MP3 file: $MP3_FILE"

# 2. ファイルアップロード方式のテスト
echo -e "\n2. Testing File Upload..."
RESPONSE=$(curl -s -X POST "$API_BASE_URL/generate_music_with_audio" \
    -F "audio_file=@$MP3_FILE" \
    -F "format=wav" \
    -F "audio_duration=30.0" \
    -F "prompt=electronic, remix, upbeat, dance music" \
    -F "lyrics=[verse]
Dance to the beat
Feel the rhythm
[chorus]
Music flows through the night" \
    -F "infer_step=30" \
    -F "guidance_scale=12.0" \
    -F "ref_audio_strength=0.7" \
    -F "return_file_data=false")

echo "Upload response: $RESPONSE"

# リクエストIDを取得
REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id // empty')

if [ -n "$REQUEST_ID" ]; then
    echo "Request ID: $REQUEST_ID"
    
    # ステータスをチェック
    echo -e "\n3. Checking status..."
    while true; do
        STATUS_RESPONSE=$(curl -s -X GET "$API_BASE_URL/status/$REQUEST_ID")
        STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // empty')
        
        echo "Status: $STATUS"
        
        if [ "$STATUS" = "completed" ]; then
            echo "Processing completed!"
            echo "Status response: $STATUS_RESPONSE"
            
            # 結果をダウンロード
            echo -e "\n4. Downloading result..."
            OUTPUT_FILE="output_curl_test_$(date +%s).wav"
            curl -X GET "$API_BASE_URL/result/$REQUEST_ID" -o "$OUTPUT_FILE"
            
            if [ -f "$OUTPUT_FILE" ]; then
                echo "Result saved to: $OUTPUT_FILE"
                ls -la "$OUTPUT_FILE"
            fi
            break
        elif [ "$STATUS" = "failed" ]; then
            echo "Processing failed!"
            echo "Error response: $STATUS_RESPONSE"
            break
        elif [ "$STATUS" = "processing" ]; then
            echo "Still processing... waiting 5 seconds"
            sleep 5
        elif [ "$STATUS" = "pending" ]; then
            echo "Request is pending... waiting 5 seconds"
            sleep 5
        else
            echo "Unknown status: $STATUS"
            break
        fi
    done
else
    echo "Failed to get request ID from response"
fi

# 5. Base64アップロード方式のテスト
echo -e "\n5. Testing Base64 Upload..."

# MP3ファイルをBase64エンコード
AUDIO_BASE64=$(base64 -w 0 "$MP3_FILE")

# Base64データをPOST（データサイズが大きいので注意）
RESPONSE2=$(curl -s -X POST "$API_BASE_URL/generate_music_with_audio_base64" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "audio_base64=$AUDIO_BASE64" \
    --data-urlencode "format=wav" \
    --data-urlencode "audio_duration=30.0" \
    --data-urlencode "prompt=jazz, smooth, saxophone, piano" \
    --data-urlencode "lyrics=[verse]
Smooth jazz vibes
Soothing melodies
[chorus]
Relax and enjoy the sound" \
    --data-urlencode "infer_step=30" \
    --data-urlencode "guidance_scale=12.0" \
    --data-urlencode "ref_audio_strength=0.6" \
    --data-urlencode "return_file_data=false")

echo "Base64 upload response: $RESPONSE2"

# Base64アップロードのリクエストIDを取得
REQUEST_ID2=$(echo "$RESPONSE2" | jq -r '.request_id // empty')

if [ -n "$REQUEST_ID2" ]; then
    echo "Base64 Request ID: $REQUEST_ID2"
    
    # ステータスをチェック
    echo -e "\n6. Checking base64 upload status..."
    while true; do
        STATUS_RESPONSE2=$(curl -s -X GET "$API_BASE_URL/status/$REQUEST_ID2")
        STATUS2=$(echo "$STATUS_RESPONSE2" | jq -r '.status // empty')
        
        echo "Base64 Status: $STATUS2"
        
        if [ "$STATUS2" = "completed" ]; then
            echo "Base64 processing completed!"
            
            # 結果をダウンロード
            echo -e "\n7. Downloading base64 result..."
            OUTPUT_FILE2="output_base64_curl_test_$(date +%s).wav"
            curl -X GET "$API_BASE_URL/result/$REQUEST_ID2" -o "$OUTPUT_FILE2"
            
            if [ -f "$OUTPUT_FILE2" ]; then
                echo "Base64 result saved to: $OUTPUT_FILE2"
                ls -la "$OUTPUT_FILE2"
            fi
            break
        elif [ "$STATUS2" = "failed" ]; then
            echo "Base64 processing failed!"
            echo "Error response: $STATUS_RESPONSE2"
            break
        elif [ "$STATUS2" = "processing" ]; then
            echo "Still processing base64... waiting 5 seconds"
            sleep 5
        elif [ "$STATUS2" = "pending" ]; then
            echo "Base64 request is pending... waiting 5 seconds"
            sleep 5
        else
            echo "Unknown base64 status: $STATUS2"
            break
        fi
    done
else
    echo "Failed to get request ID from base64 response"
fi

# 8. JSON形式のBase64アップロード方式のテスト
echo -e "\n8. Testing JSON Base64 Upload..."

# JSON形式でBase64データをPOST
JSON_RESPONSE=$(curl -s -X POST "$API_BASE_URL/generate_music_with_audio_json" \
    -H "Content-Type: application/json" \
    -d "{
        \"audio_base64\": \"$AUDIO_BASE64\",
        \"format\": \"wav\",
        \"audio_duration\": 30.0,
        \"prompt\": \"ambient, chill, atmospheric, synth\",
        \"lyrics\": \"[verse]\\nFloating in space\\nDrifting away\\n[chorus]\\nPeaceful moments\",
        \"infer_step\": 30,
        \"guidance_scale\": 12.0,
        \"ref_audio_strength\": 0.5,
        \"return_file_data\": false
    }")

echo "JSON upload response: $JSON_RESPONSE"

# JSONアップロードのリクエストIDを取得
REQUEST_ID3=$(echo "$JSON_RESPONSE" | jq -r '.request_id // empty')

if [ -n "$REQUEST_ID3" ]; then
    echo "JSON Request ID: $REQUEST_ID3"
    
    # ステータスをチェック
    echo -e "\n9. Checking JSON upload status..."
    while true; do
        STATUS_RESPONSE3=$(curl -s -X GET "$API_BASE_URL/status/$REQUEST_ID3")
        STATUS3=$(echo "$STATUS_RESPONSE3" | jq -r '.status // empty')
        
        echo "JSON Status: $STATUS3"
        
        if [ "$STATUS3" = "completed" ]; then
            echo "JSON processing completed!"
            
            # 結果をダウンロード
            echo -e "\n10. Downloading JSON result..."
            OUTPUT_FILE3="output_json_curl_test_$(date +%s).wav"
            curl -X GET "$API_BASE_URL/result/$REQUEST_ID3" -o "$OUTPUT_FILE3"
            
            if [ -f "$OUTPUT_FILE3" ]; then
                echo "JSON result saved to: $OUTPUT_FILE3"
                ls -la "$OUTPUT_FILE3"
            fi
            break
        elif [ "$STATUS3" = "failed" ]; then
            echo "JSON processing failed!"
            echo "Error response: $STATUS_RESPONSE3"
            break
        elif [ "$STATUS3" = "processing" ]; then
            echo "Still processing JSON... waiting 5 seconds"
            sleep 5
        elif [ "$STATUS3" = "pending" ]; then
            echo "JSON request is pending... waiting 5 seconds"
            sleep 5
        else
            echo "Unknown JSON status: $STATUS3"
            break
        fi
    done
else
    echo "Failed to get request ID from JSON response"
fi

# 11. MP3形式で出力するテスト
echo -e "\n11. Testing MP3 Output..."
MP3_RESPONSE=$(curl -s -X POST "$API_BASE_URL/generate_music_with_audio_mp3" \
    -F "audio_file=@$MP3_FILE" \
    -F "audio_duration=30.0" \
    -F "prompt=electronic, remix, house music, bass" \
    -F "lyrics=[verse]
Drop the beat
Feel the bass
[chorus]
Dance all night" \
    -F "infer_step=30" \
    -F "guidance_scale=12.0" \
    -F "ref_audio_strength=0.8")

echo "MP3 output response: $MP3_RESPONSE"

REQUEST_ID_MP3=$(echo "$MP3_RESPONSE" | jq -r '.request_id // empty')

if [ -n "$REQUEST_ID_MP3" ]; then
    echo "MP3 Output Request ID: $REQUEST_ID_MP3"
    
    # ステータスをチェック
    echo -e "\n12. Checking MP3 output status..."
    while true; do
        STATUS_MP3=$(curl -s -X GET "$API_BASE_URL/status/$REQUEST_ID_MP3")
        STATUS_MP3_VALUE=$(echo "$STATUS_MP3" | jq -r '.status // empty')
        
        echo "MP3 Output Status: $STATUS_MP3_VALUE"
        
        if [ "$STATUS_MP3_VALUE" = "completed" ]; then
            echo "MP3 output processing completed!"
            
            # 結果をダウンロード
            echo -e "\n13. Downloading MP3 result..."
            OUTPUT_MP3="output_mp3_format_$(date +%s).mp3"
            curl -X GET "$API_BASE_URL/result/$REQUEST_ID_MP3" -o "$OUTPUT_MP3"
            
            if [ -f "$OUTPUT_MP3" ]; then
                echo "MP3 result saved to: $OUTPUT_MP3"
                ls -la "$OUTPUT_MP3"
            fi
            break
        elif [ "$STATUS_MP3_VALUE" = "failed" ]; then
            echo "MP3 output processing failed!"
            echo "Error response: $STATUS_MP3"
            break
        elif [ "$STATUS_MP3_VALUE" = "processing" ]; then
            echo "Still processing MP3... waiting 5 seconds"
            sleep 5
        elif [ "$STATUS_MP3_VALUE" = "pending" ]; then
            echo "MP3 request is pending... waiting 5 seconds"
            sleep 5
        else
            echo "Unknown MP3 status: $STATUS_MP3_VALUE"
            break
        fi
    done
else
    echo "Failed to get request ID from MP3 response"
fi

# 14. 直接MP3出力のテスト
echo -e "\n14. Testing Direct MP3 Output..."
echo "Note: This is a synchronous endpoint and may take a while..."

DIRECT_OUTPUT="output_direct_mp3_$(date +%s).mp3"
curl -X POST "$API_BASE_URL/generate_music_with_audio_direct_mp3" \
    -F "audio_file=@$MP3_FILE" \
    -F "audio_duration=30.0" \
    -F "prompt=trap, hip hop, heavy bass, 808" \
    -F "lyrics=[verse]
Bass drops hard
Trap beats flow
[chorus]
Feel the 808" \
    -F "infer_step=30" \
    -F "guidance_scale=12.0" \
    -F "ref_audio_strength=0.7" \
    -o "$DIRECT_OUTPUT"

if [ -f "$DIRECT_OUTPUT" ] && [ -s "$DIRECT_OUTPUT" ]; then
    echo "Direct MP3 output successful: $DIRECT_OUTPUT"
    ls -la "$DIRECT_OUTPUT"
else
    echo "Direct MP3 output failed or file is empty"
fi

# キューの状況を確認
echo -e "\n15. Queue Status..."
curl -X GET "$API_BASE_URL/queue/status" | jq .

echo -e "\n=== Test Completed ==="
