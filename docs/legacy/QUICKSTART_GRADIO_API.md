# ACE-Step Gradio互換API クイックスタートガイド

## 🚀 5分で始める音楽生成API

### ステップ1: サーバー起動

```bash
# 基本起動
python gradio_compatible_api.py

# カスタムポートで起動
python gradio_compatible_api.py --port 8020
```

起動成功時の出力例:
```
Initializing pipeline...
Pipeline initialized successfully!
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8019
```

### ステップ2: 動作確認

ブラウザで以下にアクセス:
- **API ドキュメント**: http://localhost:8019/docs
- **ヘルスチェック**: http://localhost:8019/health

### ステップ3: 最初の音楽生成

#### Python を使用

```python
import requests

# 音楽生成リクエスト
response = requests.post("http://localhost:8019/generate_music", json={
    "prompt": "acoustic guitar, peaceful",
    "audio_duration": 10.0,
    "infer_step": 20
})

result = response.json()
if result["success"]:
    print(f"🎵 音楽ファイル生成: {result['audio_path']}")
else:
    print(f"❌ エラー: {result['error_message']}")
```

#### cURL を使用

```bash
curl -X POST "http://localhost:8019/generate_music" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "jazz piano, relaxing",
    "audio_duration": 15.0,
    "infer_step": 30
  }'
```

### ステップ4: 生成された音楽の確認

音楽ファイルは `./outputs/` ディレクトリに保存されます:

```bash
ls outputs/
# output_20250721120000_0.wav
```

## 📋 よく使うパラメータ

### 高品質・長時間の音楽

```json
{
  "prompt": "classical orchestra, dramatic, epic",
  "audio_duration": 60.0,
  "infer_step": 80,
  "guidance_scale": 15.0
}
```

### 高速生成・短時間

```json
{
  "prompt": "electronic beat, upbeat",
  "audio_duration": 10.0,
  "infer_step": 20,
  "guidance_scale": 10.0
}
```

### 歌詞付き音楽

```json
{
  "prompt": "pop song, cheerful, 120 BPM",
  "lyrics": "[verse]\\nHello world\\nThis is a test\\n[chorus]\\nSinging with AI",
  "audio_duration": 30.0,
  "use_erg_lyric": true
}
```

## 🛠️ トラブルシューティング

### エラー: "Pipeline not initialized"

```bash
# パイプラインを手動で初期化
curl -X POST "http://localhost:8019/initialize"
```

### エラー: メモリ不足

```bash
# CPU オフロードを有効化して再起動
python gradio_compatible_api.py --cpu_offload
```

### エラー: ポートが使用中

```bash
# 別のポートを使用
python gradio_compatible_api.py --port 8020
```

## 📖 詳細情報

完全なドキュメントは [README_GRADIO_COMPATIBLE_API.md](README_GRADIO_COMPATIBLE_API.md) を参照してください。

## 🧪 テスト実行

APIの動作確認には専用のテストスイートを使用:

```bash
# 基本テスト
python test_gradio_compatible_api.py

# 拡張テスト
python test_gradio_compatible_api.py --extended
```

---

💡 **ヒント**: `http://localhost:8019/docs` のSwagger UIを使って、ブラウザから直接APIをテストできます！
