# ACE-Step Gradio互換APIサーバー 使用ガイド

## 概要

`gradio_compatible_api.py` は、ACE-StepのGradioアプリケーションと完全に互換性のあるFastAPIベースのサーバーです。GradioのWebインターフェースを使わずに、HTTP APIとして音楽生成機能を利用できます。

## 特徴

- 🎵 **Gradio完全互換**: GradioアプリのUI機能をAPI経由で利用可能
- 🚀 **高性能**: FastAPIベースで高速レスポンス
- 🔧 **カスタマイズ可能**: 詳細なパラメータ設定が可能
- 📝 **OpenAPI対応**: Swagger UIでAPIドキュメント確認可能
- 🔍 **ヘルスチェック**: サーバー状態の監視機能
- 📊 **リクエスト検証**: Pydanticによる入力データ検証

## 前提条件

### システム要件
- Python 3.8+
- CUDA対応GPU（推奨）
- 最低8GB RAM、推奨16GB以上

### 依存パッケージ
```bash
pip install fastapi uvicorn pydantic
pip install torch torchaudio  # PyTorchとtorchaudio
# その他のACE-Step依存パッケージ
```

## インストールと起動

### 1. 基本的な起動方法

```bash
python gradio_compatible_api.py
```

**デフォルト設定:**
- ホスト: `0.0.0.0`
- ポート: `8019`
- GPU: `cuda:0`
- データタイプ: `bfloat16`

### 2. カスタムパラメータでの起動

```bash
python gradio_compatible_api.py \
    --port 8020 \
    --host localhost \
    --device_id 1 \
    --checkpoint_path /path/to/checkpoints \
    --cpu_offload \
    --torch_compile
```

### 3. 起動オプション一覧

| オプション | デフォルト値 | 説明 |
|-----------|-------------|------|
| `--port` | 8019 | サーバーポート番号 |
| `--host` | 0.0.0.0 | バインドホストアドレス |
| `--checkpoint_path` | "" | チェックポイントディレクトリパス |
| `--device_id` | 0 | 使用するCUDAデバイスID |
| `--bf16` | True | bfloat16データタイプを使用 |
| `--torch_compile` | False | torch.compileを有効化 |
| `--cpu_offload` | False | CPUオフロードを有効化 |
| `--overlapped_decode` | False | オーバーラップデコードを有効化 |

## API エンドポイント

### 基本情報

- **ベースURL**: `http://localhost:8019`
- **OpenAPI仕様**: `http://localhost:8019/docs`
- **ReDoc**: `http://localhost:8019/redoc`

### エンドポイント一覧

#### 1. ヘルスチェック `GET /health`

サーバーの稼働状況を確認します。

**レスポンス例:**
```json
{
  "status": "healthy",
  "pipeline_loaded": true
}
```

#### 2. パイプライン初期化 `POST /initialize`

AIモデルパイプラインを初期化または再初期化します。

**リクエストパラメータ:**
```json
{
  "checkpoint_path": "",
  "device_id": 0,
  "bf16": true,
  "torch_compile": false,
  "cpu_offload": false,
  "overlapped_decode": false
}
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "Pipeline initialized successfully"
}
```

#### 3. 音楽生成 `POST /generate_music`

メインの音楽生成API。Gradioアプリと同じパラメータを使用できます。

**リクエストパラメータ:**
```json
{
  "format": "wav",
  "audio_duration": 30.0,
  "prompt": "acoustic guitar, calm, peaceful",
  "lyrics": "",
  "infer_step": 60,
  "guidance_scale": 15.0,
  "scheduler_type": "euler",
  "cfg_type": "apg",
  "omega_scale": 10.0,
  "manual_seeds": null,
  "guidance_interval": 0.5,
  "guidance_interval_decay": 0.0,
  "min_guidance_scale": 3.0,
  "use_erg_tag": true,
  "use_erg_lyric": false,
  "use_erg_diffusion": true,
  "oss_steps": null,
  "guidance_scale_text": 0.0,
  "guidance_scale_lyric": 0.0,
  "audio2audio_enable": false,
  "ref_audio_strength": 0.5,
  "ref_audio_input": null,
  "lora_name_or_path": "none",
  "lora_weight": 1.0
}
```

**レスポンス例:**
```json
{
  "success": true,
  "audio_path": "./outputs/output_20250721120000_0.wav",
  "params_json": {...}
}
```

#### 4. サンプルデータ取得 `GET /sample_data`

サンプルプロンプトや設定値を取得します。

**レスポンス例:**
```json
{
  "success": true,
  "sample": {
    "prompt": "funk, pop, soul, rock...",
    "lyrics": "[verse]\\nNeon lights they flicker..."
  }
}
```

## 使用例

### Python クライアント例

```python
import requests
import json

# 基本設定
BASE_URL = "http://localhost:8019"

# 1. ヘルスチェック
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 2. 音楽生成
music_request = {
    "prompt": "jazz piano, smooth, relaxing",
    "audio_duration": 15.0,
    "infer_step": 30,
    "guidance_scale": 15.0
}

response = requests.post(
    f"{BASE_URL}/generate_music",
    json=music_request,
    timeout=300
)

if response.status_code == 200:
    result = response.json()
    if result["success"]:
        print(f"Generated: {result['audio_path']}")
    else:
        print(f"Error: {result['error_message']}")
```

### cURL例

```bash
# ヘルスチェック
curl -X GET "http://localhost:8019/health"

# 音楽生成
curl -X POST "http://localhost:8019/generate_music" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "acoustic guitar, peaceful",
    "audio_duration": 10.0,
    "infer_step": 20
  }'
```

## パラメータ詳細説明

### 音楽生成パラメータ

#### 基本パラメータ
- **`format`**: 出力音声形式（`"wav"`, `"mp3"`など）
- **`audio_duration`**: 音楽の長さ（秒）
- **`prompt`**: 音楽のスタイルや特徴を表すテキスト
- **`lyrics`**: 歌詞（オプション）

#### AI生成パラメータ
- **`infer_step`**: 推論ステップ数（高いほど品質向上、処理時間増加）
- **`guidance_scale`**: ガイダンススケール（プロンプトへの従順度）
- **`scheduler_type`**: スケジューラータイプ（`"euler"`, `"dpm_solver_multistep"`, `"ddim"`）
- **`cfg_type`**: CFGタイプ（`"apg"`推奨）

#### 高度なパラメータ
- **`omega_scale`**: オメガスケール値
- **`guidance_interval`**: ガイダンス適用区間
- **`guidance_interval_decay`**: ガイダンス減衰率
- **`min_guidance_scale`**: 最小ガイダンススケール

#### LoRAパラメータ
- **`lora_name_or_path`**: LoRAモデルのパス（`"none"`で無効）
- **`lora_weight`**: LoRAの重み（0.0-2.0）

## 出力ファイル

### 保存場所
- デフォルト: `./outputs/`
- 環境変数 `ACE_OUTPUT_DIR` で変更可能

### ファイル名形式
```
output_YYYYMMDDHHMMSS_0.wav
```

例: `output_20250721120530_0.wav`

## トラブルシューティング

### よくある問題と解決法

#### 1. サーバーが起動しない
```bash
# ポートが使用中の場合
python gradio_compatible_api.py --port 8020

# 権限エラーの場合
sudo python gradio_compatible_api.py --host 127.0.0.1
```

#### 2. メモリ不足エラー
```bash
# CPU オフロードを有効化
python gradio_compatible_api.py --cpu_offload

# より小さなGPUデバイスを使用
python gradio_compatible_api.py --device_id 1
```

#### 3. 音楽生成が遅い
```bash
# torch.compileを有効化（初回は遅いが、その後高速化）
python gradio_compatible_api.py --torch_compile

# 推論ステップを減らす（品質は下がる）
# リクエストで "infer_step": 20 などに設定
```

#### 4. 品質が低い
- `infer_step` を増やす（60-100推奨）
- `guidance_scale` を調整（10-20推奨）
- より具体的な `prompt` を使用

### ログとデバッグ

#### ログレベル設定
```bash
export LOG_LEVEL=DEBUG
python gradio_compatible_api.py
```

#### エラー詳細の確認
- Swagger UI (`/docs`) でAPIテスト
- レスポンスの `error_message` フィールドを確認
- サーバーコンソール出力を確認

## パフォーマンス最適化

### 推奨設定

#### 高品質・低速設定
```bash
python gradio_compatible_api.py --torch_compile
```
```json
{
  "infer_step": 100,
  "guidance_scale": 15.0,
  "scheduler_type": "euler"
}
```

#### 高速・標準品質設定
```bash
python gradio_compatible_api.py --cpu_offload --overlapped_decode
```
```json
{
  "infer_step": 30,
  "guidance_scale": 10.0,
  "scheduler_type": "euler"
}
```

#### リソース節約設定
```bash
python gradio_compatible_api.py --cpu_offload --bf16
```

### 並列処理

複数のリクエストを同時に処理する場合：

```bash
# uvicornで複数ワーカーを起動
uvicorn gradio_compatible_api:app --host 0.0.0.0 --port 8019 --workers 4
```

## セキュリティ考慮事項

### 本番環境での注意点

1. **アクセス制限**
   ```bash
   # 特定IPからのみアクセス許可
   python gradio_compatible_api.py --host 127.0.0.1
   ```

2. **リバースプロキシ使用**
   ```nginx
   # nginx設定例
   location /api/ {
       proxy_pass http://localhost:8019/;
   }
   ```

3. **認証の追加**
   - API キー認証の実装を推奨
   - JWTトークン認証の検討

## API変更履歴

### v1.0.0 (2025-07-21)
- 初回リリース
- Gradio完全互換API実装
- ヘルスチェック機能追加
- OpenAPI仕様対応

## サポート

### 関連ファイル
- `test_gradio_compatible_api.py`: APIテストスイート
- `test_config.json`: テスト設定ファイル
- `README_TEST_GRADIO_API.md`: テストガイド

### よくある質問

**Q: Gradioアプリとの違いは？**
A: 機能は同じですが、WebUIの代わりにHTTP APIとして利用できます。

**Q: 同時に複数の音楽を生成できますか？**
A: 現在のバージョンではシーケンシャル処理です。並列処理は複数のサーバーインスタンスで対応してください。

**Q: カスタムLoRAモデルは使用できますか？**
A: はい、`lora_name_or_path` パラメータでLoRAモデルのパスを指定できます。

---

📧 **お問い合わせ**: GitHub Issues または ACE-Step プロジェクトページまで
