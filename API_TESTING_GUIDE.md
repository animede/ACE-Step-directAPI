# ACE-Step DirectAPI テストガイド

## 概要

このドキュメントでは、ACE-Step DirectAPIサーバーの包括的なテスト方法について説明します。自動テストスイートの使用方法から手動テストまで、API機能の検証手順を詳しく解説します。

## 🧪 テストスイート

### 1. 核心機能テスト

最も重要な機能の動作確認を行います：

```bash
cd /home/animede/ACE-Step
python core_functionality_test.py
```

**テスト内容:**
- Form-Dataエンドポイント (`/generate_music_form`)
- Direct APIエンドポイント (`/generate_music_direct`)
- music.py統合テスト

**期待される結果:**
```
ACE-Step Core Functionality Test
===================================
Form-Data Endpoint: ✓ PASS
Direct API Endpoint: ✓ PASS
music.py Integration: ✓ PASS

Overall: 3/3 tests passed
🎉 ALL TESTS PASSED!
```

### 2. 包括的テスト

全API機能の動作確認を行います：

```bash
cd /home/animede/ACE-Step
python comprehensive_test.py
```

**テスト内容:**
- レガシーフォームリクエスト
- 同期JSON APIリクエスト
- music.py統合
- 非同期APIワークフロー
- 直接バイナリAPI

### 3. レガシー互換性テスト

従来システムとの互換性を確認します：

```bash
cd /home/animede/ACE-Step-directAPI
python test_form_request.py
```

## 🔍 手動テスト

### 1. サーバヘルスチェック

```bash
curl -X GET http://localhost:8019/health
```

**期待されるレスポンス:**
```json
{
    "status": "healthy",
    "pipeline_loaded": true
}
```

### 2. Form-Dataエンドポイントテスト

```bash
curl -X POST http://localhost:8019/generate_music_form \
  -F "lyrics=君への想いを音楽に込めて" \
  -F "genre=pop ballad, piano" \
  -F "audio_duration=15" \
  -F "infer_step=5" \
  -F "guidance_scale=3.5" \
  -o test_output.wav
```

### 3. JSON APIエンドポイントテスト

```bash
curl -X POST http://localhost:8019/generate_music_direct \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": "君への想いを音楽に込めて",
    "prompt": "pop ballad, piano",
    "audio_duration": 15,
    "infer_step": 5,
    "guidance_scale": 3.5
  }' \
  -o test_direct.wav
```

### 4. 非同期APIテスト

```bash
# リクエスト送信
REQUEST_ID=$(curl -s -X POST http://localhost:8019/generate_music_async \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": "君への想いを音楽に込めて",
    "prompt": "pop ballad, piano",
    "audio_duration": 15,
    "return_file_data": true
  }' | jq -r '.request_id')

echo "Request ID: $REQUEST_ID"

# ステータス確認
curl -X GET "http://localhost:8019/status/$REQUEST_ID"

# 結果取得（完了後）
curl -X GET "http://localhost:8019/result/$REQUEST_ID?format=json"
```

## 📊 パフォーマンステスト

### 1. 生成時間測定

```python
import time
import requests

def measure_generation_time():
    data = {
        "lyrics": "君への想いを音楽に込めて",
        "prompt": "pop ballad, piano",
        "audio_duration": 30,
        "infer_step": 10
    }
    
    start_time = time.time()
    response = requests.post("http://localhost:8019/generate_music_direct", json=data)
    end_time = time.time()
    
    generation_time = end_time - start_time
    audio_size = len(response.content)
    
    print(f"Generation time: {generation_time:.2f} seconds")
    print(f"Audio size: {audio_size:,} bytes")
    print(f"Speed: {audio_size/generation_time/1024:.2f} KB/s")

measure_generation_time()
```

### 2. メモリ使用量監視

```bash
# GPU メモリ使用量監視
watch -n 1 nvidia-smi

# システムメモリ監視
watch -n 1 'free -h && ps aux | grep gradio_compatible_api | head -1'
```

### 3. 並行処理テスト

```python
import concurrent.futures
import requests
import time

def generate_music(test_id):
    data = {
        "lyrics": f"Test lyrics {test_id}",
        "prompt": "pop ballad",
        "audio_duration": 15,
        "infer_step": 5
    }
    
    start_time = time.time()
    response = requests.post("http://localhost:8019/generate_music_direct", json=data)
    end_time = time.time()
    
    return {
        "test_id": test_id,
        "status_code": response.status_code,
        "time": end_time - start_time,
        "size": len(response.content) if response.status_code == 200 else 0
    }

# 並行テスト実行
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(generate_music, i) for i in range(3)]
    results = [future.result() for future in futures]

for result in results:
    print(f"Test {result['test_id']}: {result['status_code']} - {result['time']:.2f}s - {result['size']:,} bytes")
```

## 🚨 エラーテスト

### 1. 不正なパラメータテスト

```python
import requests

# 不正なaudio_duration
response = requests.post("http://localhost:8019/generate_music_direct", json={
    "audio_duration": -1,  # 負の値
    "lyrics": "test"
})
print(f"Negative duration: {response.status_code}")

# 不正なinfer_step
response = requests.post("http://localhost:8019/generate_music_direct", json={
    "infer_step": 0,  # ゼロ
    "lyrics": "test"
})
print(f"Zero steps: {response.status_code}")

# 空の歌詞
response = requests.post("http://localhost:8019/generate_music_direct", json={
    "lyrics": "",  # 空文字
    "prompt": "pop"
})
print(f"Empty lyrics: {response.status_code}")
```

### 2. サーバ負荷テスト

```python
import requests
import threading
import time

def stress_test():
    results = {"success": 0, "error": 0}
    
    def make_request():
        try:
            response = requests.post("http://localhost:8019/generate_music_direct", 
                json={
                    "lyrics": "stress test",
                    "prompt": "pop",
                    "audio_duration": 10,
                    "infer_step": 3
                }, timeout=60)
            
            if response.status_code == 200:
                results["success"] += 1
            else:
                results["error"] += 1
        except Exception:
            results["error"] += 1
    
    # 10個の並行リクエスト
    threads = []
    start_time = time.time()
    
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    print(f"Stress test results:")
    print(f"Success: {results['success']}")
    print(f"Error: {results['error']}")
    print(f"Total time: {end_time - start_time:.2f} seconds")

stress_test()
```

## 📋 テストチェックリスト

### 機能テスト

- [ ] サーバ起動確認
- [ ] ヘルスチェック応答
- [ ] パイプライン初期化
- [ ] Form-Dataリクエスト処理
- [ ] JSON リクエスト処理
- [ ] 非同期処理ワークフロー
- [ ] エラーハンドリング

### レガシー互換性

- [ ] music.py統合動作
- [ ] 従来パラメータ形式対応
- [ ] レスポンス形式互換性
- [ ] エラーレスポンス形式

### パフォーマンス

- [ ] 生成時間測定
- [ ] メモリ使用量確認
- [ ] GPU使用率確認
- [ ] 並行処理性能

### 安定性

- [ ] 長時間稼働テスト
- [ ] メモリリーク確認
- [ ] エラー後の復旧
- [ ] 負荷テスト

## 🐛 デバッグ

### ログレベル設定

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 詳細なリクエスト/レスポンスログ

```python
import requests
import logging

# HTTPリクエストの詳細ログ有効化
logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
```

### サーバサイドデバッグ

```python
# gradio_compatible_api.py に追加
import traceback

try:
    # 音楽生成処理
    results = model_demo(...)
except Exception as e:
    print(f"DEBUG: Exception occurred: {e}")
    traceback.print_exc()
    raise
```

## 📈 継続的テスト

### 自動化テストスクリプト

```bash
#!/bin/bash
# automated_test.sh

echo "Starting ACE-Step DirectAPI tests..."

# サーバ起動チェック
if ! curl -s http://localhost:8019/health > /dev/null; then
    echo "ERROR: Server is not running"
    exit 1
fi

# 核心機能テスト
python core_functionality_test.py
if [ $? -ne 0 ]; then
    echo "ERROR: Core functionality tests failed"
    exit 1
fi

# レガシー互換性テスト
python test_form_request.py
if [ $? -ne 0 ]; then
    echo "ERROR: Legacy compatibility tests failed"
    exit 1
fi

echo "All tests passed successfully!"
```

### CI/CD統合

```yaml
# .github/workflows/test.yml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start API server
        run: python gradio_compatible_api.py &
      - name: Wait for server
        run: sleep 30
      - name: Run tests
        run: python core_functionality_test.py
```

---

**最終更新**: 2025年7月23日  
**バージョン**: 1.0.0  
**対応API**: ACE-Step DirectAPI v1.x
