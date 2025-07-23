# ACE-Step 非同期API機能

## 概要

ACE-Step Gradio互換APIに非同期処理機能を追加しました。これにより、複数のリクエストを同時に処理し、長時間の音楽生成処理を効率的に管理できます。

## 新機能

### 1. 非同期音楽生成
- `/generate_music_async` - 非同期で音楽生成リクエストを送信
- キューベースの処理システム
- リクエストID による進捗管理

### 2. ステータス管理
- `/status/{request_id}` - リクエストの進捗状況を確認
- `/result/{request_id}` - 完了したリクエストの結果取得
- `/queue/status` - キュー全体の状況確認

### 3. リクエスト管理
- `/request/{request_id}` (DELETE) - ペンディング中のリクエストをキャンセル
- 自動的なメモリクリーンアップ
- エラーハンドリング

## 使用方法

### 基本的な非同期生成

```python
import requests
import time

# 1. 非同期リクエスト送信
response = requests.post("http://localhost:8019/generate_music_async", json={
    "format": "mp3",
    "audio_duration": 15.0,
    "prompt": "jazz piano, smooth",
    "infer_step": 20
})

request_id = response.json()["request_id"]

# 2. ステータス監視
while True:
    status = requests.get(f"http://localhost:8019/status/{request_id}").json()
    if status["status"] == "completed":
        break
    time.sleep(2)

# 3. 結果取得
result = requests.get(f"http://localhost:8019/result/{request_id}")
with open("music.mp3", "wb") as f:
    f.write(result.content)
```

### 複数リクエストの同時処理

```python
# 複数のリクエストを送信
request_ids = []
for i in range(3):
    response = requests.post("http://localhost:8019/generate_music_async", json={
        "prompt": f"music style {i+1}",
        "audio_duration": 10.0
    })
    request_ids.append(response.json()["request_id"])

# 全完了を待機
for request_id in request_ids:
    while True:
        status = requests.get(f"http://localhost:8019/status/{request_id}").json()
        if status["status"] in ["completed", "failed"]:
            break
        time.sleep(1)
```

## APIエンドポイント詳細

### POST /generate_music_async
非同期音楽生成リクエストを送信

**レスポンス:**
```json
{
    "request_id": "uuid-string",
    "status": "queued",
    "message": "Request has been queued for processing"
}
```

### GET /status/{request_id}
リクエストのステータスを取得

**レスポンス:**
```json
{
    "request_id": "uuid-string",
    "status": "completed",  // pending, processing, completed, failed
    "created_at": 1234567890.0,
    "started_at": 1234567891.0,
    "completed_at": 1234567920.0,
    "result": { ... }  // 完了時のみ
}
```

### GET /result/{request_id}
完了したリクエストの結果を取得
- 音楽ファイルまたはJSONレスポンス

### GET /queue/status
キューの状況を確認

**レスポンス:**
```json
{
    "queue_size": 2,
    "status_counts": {
        "pending": 1,
        "processing": 1,
        "completed": 5,
        "failed": 0
    },
    "total_requests": 7
}
```

### DELETE /request/{request_id}
ペンディング中のリクエストをキャンセル

## 既存のエンドポイント

### 同期処理（既存）
- `/generate_music` - 従来の同期音楽生成
- `/generate_music_direct` - 音楽データを直接返す

### 音楽データ直接取得
- `return_file_data=True` で音楽データを直接レスポンス
- ファイルI/Oを削減し、効率的な配信

## テスト

```bash
# 非同期API機能のテスト
python test_async_api.py

# 既存の同期API機能のテスト
python test_gradio_compatible_api.py

# 音楽データ直接取得のテスト
python test_direct_audio_response.py
```

## 使い分け

### 同期処理を使う場合
- 単発のテスト生成
- リアルタイム性が重要
- シンプルな実装

### 非同期処理を使う場合
- 複数の音楽を同時生成
- 長時間の処理
- Webアプリケーションとの統合
- バッチ処理

## パフォーマンス

- **同期処理**: 1リクエストずつ順次処理
- **非同期処理**: キューイング + バックグラウンド処理
- **スループット**: 複数リクエストの効率的な管理
- **レスポンス性**: 即座にリクエストIDを返却

## 注意事項

1. **GPU制限**: 現在はGPU使用のため1つのワーカーのみ
2. **メモリ管理**: 長時間の運用では定期的な再起動を推奨
3. **ファイル管理**: 一時ファイルは自動削除されます
4. **タイムアウト**: 長時間処理はタイムアウトする可能性があります

## 設定可能なパラメータ

```python
# ワーカー数（GPUのリソースに応じて調整）
executor = ThreadPoolExecutor(max_workers=1)

# ポーリング間隔（CPU使用率調整）
await asyncio.sleep(0.1)  # バックグラウンドワーカー

# リクエスト管理
request_queue = Queue()  # キューサイズは無制限
```

## 今後の拡張

- **マルチGPU対応**: 複数のワーカーで並列処理
- **優先度キュー**: 重要なリクエストを優先処理
- **進捗通知**: WebSocketによるリアルタイム進捗通知
- **リクエスト永続化**: Redis等での状態管理
- **負荷分散**: 複数サーバー間での負荷分散
