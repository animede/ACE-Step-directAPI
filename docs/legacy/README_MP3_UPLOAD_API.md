# MP3アップロード機能 API仕様書

## 概要

`gradio_compatible_api.py`にMP3ファイルをアップロードして音楽生成を行う機能を追加しました。この機能により、既存の音楽ファイルを参照音声として使用し、それをベースにした新しい音楽を生成できます。

## 新しいエンドポイント

## 新しいエンドポイント

### 1. `/generate_music_with_audio` (POST)

ファイルアップロード形式でMP3ファイルを受け取り、音楽生成を行います。

### 2. `/generate_music_with_audio_base64` (POST)

Form形式でBase64エンコードされたMP3データを受け取り、音楽生成を行います。

### 3. `/generate_music_with_audio_json` (POST)

JSON形式でBase64エンコードされたMP3データを受け取り、音楽生成を行います。

### 4. `/generate_music_with_audio_mp3` (POST)

MP3ファイルをアップロードして音楽生成を行い、**MP3形式で結果を返します**。

### 5. `/generate_music_with_audio_json_mp3` (POST)

JSON形式でBase64エンコードされたMP3データを受け取り、**MP3形式で結果を返します**。

## エンドポイント詳細

### 1. `/generate_music_with_audio` (POST)

ファイルアップロード形式でMP3ファイルを受け取り、音楽生成を行います。

#### リクエスト形式

```
Content-Type: multipart/form-data
```

#### パラメータ

| パラメータ名 | 型 | 必須 | デフォルト値 | 説明 |
|-------------|-----|------|-------------|------|
| `audio_file` | File | ✓ | - | アップロードするMP3ファイル |
| `format` | string | - | "wav" | 出力音声フォーマット |
| `audio_duration` | float | - | 60.0 | 生成する音楽の長さ（秒） |
| `prompt` | string | - | デフォルトタグ | 音楽スタイルのプロンプト |
| `lyrics` | string | - | デフォルト歌詞 | 歌詞テキスト |
| `infer_step` | int | - | 60 | 推論ステップ数 |
| `guidance_scale` | float | - | 15.0 | ガイダンススケール |
| `scheduler_type` | string | - | "euler" | スケジューラータイプ |
| `cfg_type` | string | - | "apg" | CFGタイプ |
| `omega_scale` | float | - | 10.0 | オメガスケール |
| `manual_seeds` | string | - | null | 手動シード |
| `guidance_interval` | float | - | 0.5 | ガイダンス間隔 |
| `guidance_interval_decay` | float | - | 0.0 | ガイダンス間隔の減衰 |
| `min_guidance_scale` | float | - | 3.0 | 最小ガイダンススケール |
| `use_erg_tag` | bool | - | true | ERGタグの使用 |
| `use_erg_lyric` | bool | - | false | ERG歌詞の使用 |
| `use_erg_diffusion` | bool | - | true | ERG拡散の使用 |
| `oss_steps` | string | - | null | OSSステップ |
| `guidance_scale_text` | float | - | 0.0 | テキストガイダンススケール |
| `guidance_scale_lyric` | float | - | 0.0 | 歌詞ガイダンススケール |
| `ref_audio_strength` | float | - | 0.5 | 参照音声の強度 |
| `lora_name_or_path` | string | - | "none" | LoRAの名前またはパス |
| `lora_weight` | float | - | 1.0 | LoRAの重み |
| `return_file_data` | bool | - | false | ファイルデータを直接返すかどうか |

#### レスポンス

```json
{
  "success": true,
  "request_id": "uuid-string",
  "message": "Audio file uploaded and queued for processing. Original filename: example.mp3"
}
```

#### cURLサンプル

```bash
curl -X POST "http://localhost:8019/generate_music_with_audio" \
  -F "audio_file=@/path/to/your/music.mp3" \
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
  -F "ref_audio_strength=0.7"
```

### 2. `/generate_music_with_audio_base64` (POST)

Base64エンコードされたMP3データで音楽生成を行います。

#### リクエスト形式

```
Content-Type: application/x-www-form-urlencoded
```

#### パラメータ

基本的なパラメータは上記と同じですが、以下が追加されます：

| パラメータ名 | 型 | 必須 | デフォルト値 | 説明 |
|-------------|-----|------|-------------|------|
| `audio_base64` | string | ✓ | - | Base64エンコードされたMP3データ |

#### レスポンス

```json
{
  "success": true,
  "request_id": "uuid-string",
  "message": "Base64 audio data uploaded and queued for processing"
}
```

#### cURLサンプル

```bash
# MP3ファイルをBase64エンコード
AUDIO_BASE64=$(base64 -w 0 /path/to/your/music.mp3)

curl -X POST "http://localhost:8019/generate_music_with_audio_base64" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "audio_base64=$AUDIO_BASE64" \
  --data-urlencode "format=wav" \
  --data-urlencode "audio_duration=30.0" \
  --data-urlencode "prompt=jazz, smooth, saxophone, piano" \
  --data-urlencode "ref_audio_strength=0.6"
```

### 3. `/generate_music_with_audio_json` (POST)

JSON形式でBase64エンコードされたMP3データを受け取り、音楽生成を行います。

#### リクエスト形式

```http
Content-Type: application/json
```

#### パラメータ

| パラメータ名 | 型 | 必須 | デフォルト値 | 説明 |
|-------------|-----|------|-------------|------|
| `audio_base64` | string | ✓ | - | Base64エンコードされたMP3データ |
| その他のパラメータ | - | - | - | 上記と同じ |

#### リクエストサンプル

```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10...",
  "format": "wav",
  "audio_duration": 30.0,
  "prompt": "ambient, chill, atmospheric",
  "lyrics": "[verse]\nFloating in space\n[chorus]\nPeaceful moments",
  "infer_step": 30,
  "guidance_scale": 12.0,
  "ref_audio_strength": 0.5
}
```

#### レスポンス

```json
{
  "success": true,
  "request_id": "uuid-string",
  "message": "Base64 audio data uploaded and queued for processing"
}
```

#### cURLサンプル

```bash
# MP3ファイルをBase64エンコード
AUDIO_BASE64=$(base64 -w 0 /path/to/your/music.mp3)

curl -X POST "http://localhost:8019/generate_music_with_audio_json" \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_base64\": \"$AUDIO_BASE64\",
    \"format\": \"wav\",
    \"audio_duration\": 30.0,
    \"prompt\": \"ambient, chill, atmospheric\",
    \"ref_audio_strength\": 0.5
  }"
```

### 4. `/generate_music_with_audio_mp3` (POST)

MP3ファイルをアップロードして音楽生成を行い、**MP3形式で結果を返します**。

#### 特徴
- 入力: MP3ファイル
- 出力: MP3形式（自動設定）
- `return_file_data`が自動的に`true`に設定される

### 5. `/generate_music_with_audio_json_mp3` (POST)

JSON形式でBase64エンコードされたMP3データを受け取り、**MP3形式で結果を返します**。

#### 特徴
- 入力: JSON + Base64 MP3データ
- 出力: MP3形式（自動設定）
- `return_file_data`が自動的に`true`に設定される

## 出力形式の対応

| エンドポイント | 出力形式 | Content-Type | ファイル拡張子 |
|---------------|----------|--------------|----------------|
| `/generate_music_with_audio` | WAV (デフォルト) または MP3 | audio/wav または audio/mpeg | .wav または .mp3 |
| `/generate_music_with_audio_base64` | WAV (デフォルト) または MP3 | audio/wav または audio/mpeg | .wav または .mp3 |
| `/generate_music_with_audio_json` | WAV (デフォルト) または MP3 | audio/wav または audio/mpeg | .wav または .mp3 |
| `/generate_music_with_audio_mp3` | MP3 (固定) | audio/mpeg | .mp3 |
| `/generate_music_with_audio_json_mp3` | MP3 (固定) | audio/mpeg | .mp3 |

## MP3出力の使用例

### cURLでMP3出力

```bash
# ファイルアップロード形式でMP3出力
curl -X POST "http://localhost:8019/generate_music_with_audio_mp3" \
  -F "audio_file=@music.mp3" \
  -F "prompt=electronic, remix" \
  -F "audio_duration=30"

# JSON形式でMP3出力
curl -X POST "http://localhost:8019/generate_music_with_audio_json_mp3" \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_base64\": \"$(base64 -w 0 music.mp3)\",
    \"prompt\": \"electronic, remix\",
    \"audio_duration\": 30
  }"
```

### Pythonでの使用例

```python
import requests
import base64

# MP3ファイルをアップロード
with open('input.mp3', 'rb') as f:
    files = {'audio_file': f}
    data = {'prompt': 'electronic, remix', 'audio_duration': 30}
    response = requests.post('http://localhost:8019/generate_music_with_audio_mp3', 
                           files=files, data=data)

request_id = response.json()['request_id']

# 結果をMP3として取得
result_response = requests.get(f'http://localhost:8019/result/{request_id}')
with open('output.mp3', 'wb') as f:
    f.write(result_response.content)
```

## エンドポイント比較

| エンドポイント | 形式 | 利点 | 用途 |
|---------------|------|------|------|
| `/generate_music_with_audio` | ファイルアップロード | 簡単、直接的 | Webフォーム、ブラウザから |
| `/generate_music_with_audio_base64` | Form + Base64 | 軽量 | シンプルなAPIクライアント |
| `/generate_music_with_audio_json` | JSON + Base64 | 構造化、型安全 | 本格的なAPIクライアント |
| `/generate_music_with_audio_mp3` | MP3 (固定) | MP3形式での簡単な結果取得 | MP3ファイルを直接扱う場合 |
| `/generate_music_with_audio_json_mp3` | MP3 (固定) | MP3形式での簡単な結果取得 | MP3ファイルを直接扱う場合 |

## 既存エンドポイント

これらの新しいエンドポイントは、既存の以下のエンドポイントと連携します：

### ステータス確認

- `GET /status/{request_id}` - リクエストの処理状況を確認
- `GET /result/{request_id}` - 完了したリクエストの結果を取得
- `GET /queue/status` - キューの状況を確認

### その他

- `POST /initialize` - パイプラインの初期化
- `GET /health` - ヘルスチェック
- `DELETE /request/{request_id}` - リクエストのキャンセル

## 使用手順

### 1. サーバーの起動

```bash
python gradio_compatible_api.py --port 8019 --checkpoint_path /path/to/checkpoint
```

### 2. ヘルスチェック

```bash
curl -X GET "http://localhost:8019/health"
```

### 3. MP3ファイルのアップロード

```bash
curl -X POST "http://localhost:8019/generate_music_with_audio" \
  -F "audio_file=@your_music.mp3" \
  -F "prompt=your style description"
```

### 4. ステータス確認

```bash
curl -X GET "http://localhost:8019/status/{request_id}"
```

### 5. 結果の取得

```bash
curl -X GET "http://localhost:8019/result/{request_id}" -o output.wav
```

## テストスクリプト

以下のテストスクリプトが用意されています：

### Python版テストスクリプト

```bash
python test_mp3_upload_api.py
```

### cURL版テストスクリプト

```bash
./test_mp3_upload_curl.sh
```

## 特徴

1. **ファイルアップロード対応**: 一般的なHTTPファイルアップロード形式に対応
2. **Base64エンコード対応**: APIクライアントによってはBase64形式が便利
3. **自動クリーンアップ**: 一時ファイルは処理完了後に自動削除
4. **エラーハンドリング**: アップロードエラーや処理エラーに対する適切な対応
5. **非同期処理**: 大きなファイルでもサーバーをブロックしない
6. **互換性**: 既存のGradio APIとの完全な互換性を維持

## 注意事項

1. **ファイルサイズ制限**: 大きなMP3ファイルはアップロード時間が長くなる可能性があります
2. **一時ファイル**: アップロードされたファイルは処理中のみ一時保存されます
3. **Audio2Audio**: MP3アップロード時は自動的にaudio2audio機能が有効になります
4. **メモリ使用量**: Base64形式は元ファイルより約33%大きくなります

## エラーレスポンス

一般的なエラーレスポンス：

```json
{
  "detail": "Pipeline not initialized. Call /initialize first."
}
```

ファイルタイプエラー：

```json
{
  "detail": "Uploaded file must be an audio file"
}
```

Base64デコードエラー：

```json
{
  "detail": "Invalid base64 audio data: Invalid base64-encoded string"
}
```
