# ACE-Step DirectAPI Server

## 🎯 概要

ACE-Step DirectAPIは、レガシーシステムとの完全な互換性を保ちながら、高性能な音楽生成機能を提供するFastAPIベースのサーバーです。従来の`music.py`、`music_server.py`などのクライアントと100%互換性を維持し、新しい機能も追加しています。

## ✨ 主要機能

### 🔄 レガシー互換性
- **完全な後方互換性**: 既存の`music.py`クライアントが変更なしで動作
- **自動パイプライン初期化**: レガシーリクエスト時に自動的にACE-Stepパイプラインを初期化
- **フォームデータサポート**: 従来のフォーム形式リクエストを完全サポート

### 🚀 高性能
- **メモリ最適化**: CPUオフロードによる低GPU メモリ使用量
- **CUDA メモリ管理**: 自動的なメモリクリアとガベージコレクション
- **効率的な音楽生成**: 15秒の音楽を数秒で生成

### 🔧 柔軟なAPI設計
- **複数のエンドポイント**: 同期・非同期・直接バイナリレスポンス
- **多様な出力形式**: WAV、MP3対応
- **詳細なエラーログ**: デバッグとトラブルシューティングの支援

## 📋 APIエンドポイント

### 1. レガシー互換エンドポイント

#### `POST /generate_music_form`
従来の`music.py`クライアントと完全互換のフォームデータエンドポイント

**リクエスト例:**
```python
import requests

data = {
    'lyrics': '君への想いを音楽に込めて',
    'genre': 'pop ballad, piano, emotional, japanese',
    'audio_duration': '30',
    'guidance_scale': '15.0',
    'infer_step': '10'
}

response = requests.post("http://localhost:8019/generate_music_form", data=data)
with open("output.wav", "wb") as f:
    f.write(response.content)
```

### 2. 直接APIエンドポイント

#### `POST /generate_music_direct`
JSON形式のリクエストでWAVファイルを直接返すエンドポイント

**リクエスト例:**
```python
import requests

data = {
    "lyrics": "君への想いを音楽に込めて",
    "prompt": "pop ballad, piano, emotional, japanese",
    "audio_duration": 30,
    "guidance_scale": 15.0,
    "infer_step": 10
}

response = requests.post("http://localhost:8019/generate_music_direct", json=data)
with open("output.wav", "wb") as f:
    f.write(response.content)
```

### 3. 非同期APIエンドポイント

#### `POST /generate_music_async`
非同期処理でリクエストIDを返し、後で結果を取得

**リクエスト例:**
```python
import requests
import time

# リクエスト送信
data = {
    "lyrics": "君への想いを音楽に込めて",
    "prompt": "pop ballad, piano, emotional, japanese",
    "audio_duration": 30,
    "return_file_data": True
}

response = requests.post("http://localhost:8019/generate_music_async", json=data)
request_id = response.json()["request_id"]

# ステータス確認
while True:
    status_response = requests.get(f"http://localhost:8019/status/{request_id}")
    status = status_response.json()["status"]
    if status == "completed":
        break
    time.sleep(2)

# 結果取得
result_response = requests.get(f"http://localhost:8019/result/{request_id}?format=json")
result_data = result_response.json()
audio_data = base64.b64decode(result_data["audio"])
```

### 4. ヘルスチェックエンドポイント

#### `GET /health`
サーバとパイプラインの状態を確認

**レスポンス例:**
```json
{
    "status": "healthy",
    "pipeline_loaded": true
}
```

## 🔧 インストールと起動

### 1. 環境セットアップ
```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 依存関係インストール
pip install -r requirements.txt
```

### 2. サーバ起動
```bash
# 基本起動
python gradio_compatible_api.py

# 高性能設定での起動
python gradio_compatible_api.py --host 0.0.0.0 --port 8019

# バックグラウンド起動
nohup python gradio_compatible_api.py > server.log 2>&1 &
```

### 3. Docker起動
```bash
# Docker Compose使用
docker-compose up -d

# 直接Docker実行
docker run -p 8019:8019 -v $(pwd):/app ace-step-directapi
```

## 📊 パフォーマンス

### ベンチマーク結果
- **15秒の音楽生成**: 約3-5秒（5ステップ、低精度モード）
- **30秒の音楽生成**: 約10-15秒（標準設定）
- **メモリ使用量**: 4-8GB GPU VRAM（CPUオフロード使用時）

### 最適化設定
```python
# メモリ不足環境向け設定
data = {
    "audio_duration": 15,     # 短い音楽生成
    "infer_step": 5,          # 少ないステップ数
    "guidance_scale": 3.5,    # 低い案内スケール
}
```

## 🧪 テストとバリデーション

### 自動テストスイート
```bash
# 核心機能テスト
python core_functionality_test.py

# 包括的テスト
python comprehensive_test.py

# レガシー互換性テスト
python test_form_request.py
```

### テスト結果例
```
ACE-Step Core Functionality Test
===================================
Form-Data Endpoint: ✓ PASS
Direct API Endpoint: ✓ PASS  
music.py Integration: ✓ PASS

Overall: 3/3 tests passed
🎉 ALL TESTS PASSED!
```

## 🔍 トラブルシューティング

### よくある問題と解決方法

#### 1. CUDA メモリ不足
```bash
# CPUオフロードを有効化
export CUDA_VISIBLE_DEVICES=0
python gradio_compatible_api.py --cpu_offload
```

#### 2. パイプライン初期化エラー
```bash
# 手動初期化
curl -X POST http://localhost:8019/initialize \
  -H "Content-Type: application/json" \
  -d '{"cpu_offload": true}'
```

#### 3. 音楽生成の品質向上
```python
# 高品質設定
data = {
    "audio_duration": 60,
    "infer_step": 50,          # より多いステップ
    "guidance_scale": 15.0,    # 高い案内スケール
    "scheduler_type": "euler"
}
```

## 📝 設定ファイル

### サーバ設定 (`config.json`)
```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 8019,
        "workers": 1
    },
    "pipeline": {
        "checkpoint_path": "",
        "device_id": 0,
        "bf16": true,
        "cpu_offload": true,
        "torch_compile": false
    },
    "generation": {
        "default_duration": 60,
        "default_steps": 50,
        "max_duration": 240
    }
}
```

## 🤝 貢献

### 開発への参加
1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/new-feature`)
3. 変更をコミット (`git commit -am 'Add new feature'`)
4. ブランチをプッシュ (`git push origin feature/new-feature`)
5. プルリクエストを作成

### バグレポート
GitHubのIssuesでバグレポートや機能要求を送信してください。

## 📄 ライセンス

このプロジェクトはApache License 2.0の下でライセンスされています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

- **ACE-Step Team**: 元のACE-Stepモデルとアーキテクチャ
- **StepFun**: 研究開発サポート
- **Hugging Face**: モデルホスティングとSpaceデモ
- **コミュニティ**: フィードバックと貢献

---

**作成日**: 2025年7月23日  
**最終更新**: 2025年7月23日  
**バージョン**: 1.0.0
