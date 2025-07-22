"""
GradioアプリのAPIと完全に互換性のあるFastAPIサーバー

ACE-Step: A Step Towards Music Generation Foundation Model
"""

import os
import uuid
import time
import asyncio
import threading
import gc
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn
import tempfile
import base64

from acestep.pipeline_ace_step import ACEStepPipeline
from acestep.data_sampler import DataSampler

app = FastAPI(title="ACE-Step Gradio Compatible API")

class RequestStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class QueuedRequest:
    request_id: str
    request: 'GenerateMusicRequest'  # Forward reference
    status: RequestStatus
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

# リクエストキューとステータス管理
request_queue = Queue()
request_status: Dict[str, QueuedRequest] = {}
request_lock = threading.Lock()

# ワーカースレッド用のExecutor
executor = ThreadPoolExecutor(max_workers=1)  # GPU使用のため1つのワーカー

# グローバル変数でパイプラインを管理
model_demo = None
data_sampler = None

# デフォルト値（Gradioアプリと同じ）
TAG_DEFAULT = "funk, pop, soul, rock, melodic, guitar, drums, bass, keyboard, percussion, 105 BPM, energetic, upbeat, groovy, vibrant, dynamic"
LYRIC_DEFAULT = """[verse]
Neon lights they flicker bright
City hums in dead of night
Rhythms pulse through concrete veins
Lost in echoes of refrains

[verse]
Bassline groovin' in my chest
Heartbeats match the city's zest
Electric whispers fill the air
Synthesized dreams everywhere

[chorus]
Turn it up and let it flow
Feel the fire let it grow
In this rhythm we belong
Hear the night sing out our song

[verse]
Guitar strings they start to weep
Wake the soul from silent sleep
Every note a story told
In this night we're bold and gold

[bridge]
Voices blend in harmony
Lost in pure cacophony
Timeless echoes timeless cries
Soulful shouts beneath the skies

[verse]
Keyboard dances on the keys
Melodies on evening breeze
Catch the tune and hold it tight
In this moment we take flight
"""

class GenerateMusicRequest(BaseModel):
    format: str = "wav"
    audio_duration: float = 60.0
    prompt: str = TAG_DEFAULT
    lyrics: str = LYRIC_DEFAULT
    infer_step: int = 60
    guidance_scale: float = 15.0
    scheduler_type: str = "euler"
    cfg_type: str = "apg"
    omega_scale: float = 10.0
    manual_seeds: Optional[str] = None
    guidance_interval: float = 0.5
    guidance_interval_decay: float = 0.0
    min_guidance_scale: float = 3.0
    use_erg_tag: bool = True
    use_erg_lyric: bool = False
    use_erg_diffusion: bool = True
    oss_steps: Optional[str] = None
    guidance_scale_text: float = 0.0
    guidance_scale_lyric: float = 0.0
    audio2audio_enable: bool = False
    ref_audio_strength: float = 0.5
    ref_audio_input: Optional[str] = None
    lora_name_or_path: str = "none"
    lora_weight: float = 1.0
    return_file_data: bool = False  # True の場合、ファイルデータを直接返す

class GenerateMusicResponse(BaseModel):
    success: bool
    audio_path: Optional[str] = None
    params_json: Optional[dict] = None
    error_message: Optional[str] = None

class GenerateMusicWithBase64Request(BaseModel):
    audio_base64: str
    format: str = "wav"
    audio_duration: float = 60.0
    prompt: str = TAG_DEFAULT
    lyrics: str = LYRIC_DEFAULT
    infer_step: int = 60
    guidance_scale: float = 15.0
    scheduler_type: str = "euler"
    cfg_type: str = "apg"
    omega_scale: float = 10.0
    manual_seeds: Optional[str] = None
    guidance_interval: float = 0.5
    guidance_interval_decay: float = 0.0
    min_guidance_scale: float = 3.0
    use_erg_tag: bool = True
    use_erg_lyric: bool = False
    use_erg_diffusion: bool = True
    oss_steps: Optional[str] = None
    guidance_scale_text: float = 0.0
    guidance_scale_lyric: float = 0.0
    ref_audio_strength: float = 0.5
    lora_name_or_path: str = "none"
    lora_weight: float = 1.0
    return_file_data: bool = False

def initialize_pipeline(
    checkpoint_path: str = "",
    device_id: int = 0,
    bf16: bool = True,
    torch_compile: bool = False,
    cpu_offload: bool = False,
    overlapped_decode: bool = False
):
    """Gradioアプリと同じ方法でパイプラインを初期化"""
    global model_demo, data_sampler
    
    os.environ["CUDA_VISIBLE_DEVICES"] = str(device_id)
    
    model_demo = ACEStepPipeline(
        checkpoint_dir=checkpoint_path,
        dtype="bfloat16" if bf16 else "float32",
        torch_compile=torch_compile,
        cpu_offload=cpu_offload,
        overlapped_decode=overlapped_decode,
        disable_progress_bar=True
    )
    data_sampler = DataSampler()
    
    return model_demo, data_sampler

def process_music_generation(queued_request: QueuedRequest):
    """音楽生成の実際の処理（ブロッキング）"""
    try:
        queued_request.status = RequestStatus.PROCESSING
        queued_request.started_at = time.time()
        
        # return_file_dataがTrueの場合はreturn_audio_dataも使用
        use_return_audio_data = queued_request.request.return_file_data
        
        # 既存の音楽生成処理
        results = model_demo(
            format=queued_request.request.format,
            audio_duration=queued_request.request.audio_duration,
            prompt=queued_request.request.prompt,
            lyrics=queued_request.request.lyrics,
            infer_step=queued_request.request.infer_step,
            guidance_scale=queued_request.request.guidance_scale,
            scheduler_type=queued_request.request.scheduler_type,
            cfg_type=queued_request.request.cfg_type,
            omega_scale=queued_request.request.omega_scale,
            manual_seeds=queued_request.request.manual_seeds,
            guidance_interval=queued_request.request.guidance_interval,
            guidance_interval_decay=queued_request.request.guidance_interval_decay,
            min_guidance_scale=queued_request.request.min_guidance_scale,
            use_erg_tag=queued_request.request.use_erg_tag,
            use_erg_lyric=queued_request.request.use_erg_lyric,
            use_erg_diffusion=queued_request.request.use_erg_diffusion,
            oss_steps=queued_request.request.oss_steps,
            guidance_scale_text=queued_request.request.guidance_scale_text,
            guidance_scale_lyric=queued_request.request.guidance_scale_lyric,
            audio2audio_enable=queued_request.request.audio2audio_enable,
            ref_audio_strength=queued_request.request.ref_audio_strength,
            ref_audio_input=queued_request.request.ref_audio_input,
            lora_name_or_path=queued_request.request.lora_name_or_path,
            lora_weight=queued_request.request.lora_weight,
            return_audio_data=use_return_audio_data
        )
        
        # 一時ファイルのクリーンアップ（ref_audio_inputが一時ファイルの場合）
        if (queued_request.request.ref_audio_input and 
            queued_request.request.ref_audio_input.startswith(tempfile.gettempdir())):
            try:
                temp_audio_path = queued_request.request.ref_audio_input
                temp_dir = os.path.dirname(temp_audio_path)
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temporary audio file: {cleanup_error}")
        
        # ファイルデータを返す場合の処理
        if queued_request.request.return_file_data:
            if use_return_audio_data:
                # 新しい方式：音楽データを直接取得
                if isinstance(results, (list, tuple)) and len(results) > 0:
                    audio_data_dict = results[0]
                    params_json = audio_data_dict.get('input_params')
                else:
                    audio_data_dict = results
                    params_json = None
                
                # 音楽データをバイト形式に変換
                audio_tensor = audio_data_dict['audio']
                sample_rate = audio_data_dict['sample_rate']
                format_type = audio_data_dict['format']
                
                # PyTorchテンソルをバイト形式に変換
                import io
                import torchaudio
                
                buffer = io.BytesIO()
                backend = "soundfile"
                if format_type == "ogg":
                    backend = "sox"
                
                torchaudio.save(
                    buffer, 
                    audio_tensor, 
                    sample_rate=sample_rate, 
                    format=format_type, 
                    backend=backend
                )
                audio_bytes = buffer.getvalue()
                buffer.close()
                
                # Content-Typeを正しく設定
                content_type = "audio/wav"  # デフォルト
                if format_type.lower() == 'mp3':
                    content_type = "audio/mpeg"
                elif format_type.lower() == 'wav':
                    content_type = "audio/wav"
                
                queued_request.result = {
                    "success": True,
                    "audio_data": audio_bytes,
                    "params_json": params_json,
                    "content_type": content_type,
                    "format": format_type
                }
            else:
                # 旧方式：ファイルパスから読み込み（下位互換性のため残す）
                if isinstance(results, (list, tuple)) and len(results) > 0:
                    audio_path = results[0]
                    params_json = results[1] if len(results) > 1 else None
                else:
                    audio_path = results
                    params_json = None
                
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
                
                try:
                    os.remove(audio_path)
                    json_path = audio_path.replace(f".{queued_request.request.format}", "_input_params.json")
                    if os.path.exists(json_path):
                        os.remove(json_path)
                except:
                    pass
                
                # Content-Typeを正しく設定
                content_type = "audio/wav"  # デフォルト
                if queued_request.request.format.lower() == 'mp3':
                    content_type = "audio/mpeg"
                elif queued_request.request.format.lower() == 'wav':
                    content_type = "audio/wav"
                
                queued_request.result = {
                    "success": True,
                    "audio_data": audio_data,
                    "params_json": params_json,
                    "content_type": content_type,
                    "format": queued_request.request.format
                }
        else:
            # ファイルパスを返す場合
            if isinstance(results, (list, tuple)) and len(results) > 0:
                audio_path = results[0]
                params_json = results[1] if len(results) > 1 else None
            else:
                audio_path = results
                params_json = None
            
            queued_request.result = {
                "success": True,
                "audio_path": audio_path,
                "params_json": params_json
            }
        
        queued_request.status = RequestStatus.COMPLETED
        queued_request.completed_at = time.time()
        
    except Exception as e:
        # エラー時も一時ファイルをクリーンアップ
        if (hasattr(queued_request.request, 'ref_audio_input') and 
            queued_request.request.ref_audio_input and 
            queued_request.request.ref_audio_input.startswith(tempfile.gettempdir())):
            try:
                temp_audio_path = queued_request.request.ref_audio_input
                temp_dir = os.path.dirname(temp_audio_path)
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except:
                pass
        
        queued_request.status = RequestStatus.FAILED
        queued_request.error = str(e)
        queued_request.completed_at = time.time()

async def background_worker():
    """バックグラウンドでキューを処理"""
    while True:
        try:
            if not request_queue.empty():
                queued_request = request_queue.get()
                
                # ThreadPoolExecutorで実行
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(executor, process_music_generation, queued_request)
                
            await asyncio.sleep(0.1)  # CPU使用率を下げる
        except Exception as e:
            print(f"Background worker error: {e}")
            await asyncio.sleep(1)

@app.post("/generate_music")
async def generate_music(request: GenerateMusicRequest):
    """
    Gradioアプリのtext2music APIと完全に同じ処理を実行
    return_file_data=True の場合、音楽データを直接レスポンスとして返す
    """
    try:
        if model_demo is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized. Call /initialize first.")
        
        # 出力ディレクトリの設定
        output_file_dir = os.environ.get("ACE_OUTPUT_DIR", "./outputs")
        if not os.path.isdir(output_file_dir):
            os.makedirs(output_file_dir, exist_ok=True)
        
        # リクエストをキューに追加
        request_id = str(uuid.uuid4())
        queued_request = QueuedRequest(
            request_id=request_id,
            request=request,
            status=RequestStatus.PENDING,
            created_at=time.time()
        )
        
        with request_lock:
            request_queue.put(queued_request)
            request_status[request_id] = queued_request
        
        return {"success": True, "request_id": request_id}
    
    except Exception as e:
        return {"success": False, "error_message": str(e)}

@app.post("/generate_music_direct")
async def generate_music_direct(request: GenerateMusicRequest):
    """
    音楽を生成してMP3/WAVデータを直接レスポンスとして返す
    ファイルは作成されず、メモリ内でバイナリデータを直接処理します
    """
    try:
        if model_demo is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized. Call /initialize first.")
        
        # 直接音楽生成を実行（ファイル保存なし）
        results = model_demo(
            format=request.format,
            audio_duration=request.audio_duration,
            prompt=request.prompt,
            lyrics=request.lyrics,
            infer_step=request.infer_step,
            guidance_scale=request.guidance_scale,
            scheduler_type=request.scheduler_type,
            cfg_type=request.cfg_type,
            omega_scale=request.omega_scale,
            manual_seeds=request.manual_seeds,
            guidance_interval=request.guidance_interval,
            guidance_interval_decay=request.guidance_interval_decay,
            min_guidance_scale=request.min_guidance_scale,
            use_erg_tag=request.use_erg_tag,
            use_erg_lyric=request.use_erg_lyric,
            use_erg_diffusion=request.use_erg_diffusion,
            oss_steps=request.oss_steps,
            guidance_scale_text=request.guidance_scale_text,
            guidance_scale_lyric=request.guidance_scale_lyric,
            audio2audio_enable=request.audio2audio_enable,
            ref_audio_strength=request.ref_audio_strength,
            ref_audio_input=request.ref_audio_input,
            lora_name_or_path=request.lora_name_or_path,
            lora_weight=request.lora_weight,
            return_audio_data=True  # 音楽データを直接返す
        )
        
        # 一時ファイルのクリーンアップ（ref_audio_inputが一時ファイルの場合）
        if (request.ref_audio_input and 
            request.ref_audio_input.startswith(tempfile.gettempdir())):
            try:
                temp_audio_path = request.ref_audio_input
                temp_dir = os.path.dirname(temp_audio_path)
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temporary audio file: {cleanup_error}")
        
        # resultsから音楽データを取得
        if isinstance(results, (list, tuple)) and len(results) > 0:
            audio_data_dict = results[0]  # 最初の音楽データを取得
        else:
            audio_data_dict = results
        
        # 音楽データをバイト形式に変換
        audio_tensor = audio_data_dict['audio']
        sample_rate = audio_data_dict['sample_rate']
        format_type = audio_data_dict['format']
        
        # PyTorchテンソルをバイト形式に変換
        import io
        import torchaudio
        
        buffer = io.BytesIO()
        backend = "soundfile"
        if format_type == "ogg":
            backend = "sox"
        
        torchaudio.save(
            buffer, 
            audio_tensor, 
            sample_rate=sample_rate, 
            format=format_type, 
            backend=backend
        )
        audio_bytes = buffer.getvalue()
        buffer.close()
        
        # Content-Typeを設定
        content_type = "audio/wav"  # デフォルト
        if format_type.lower() == 'mp3':
            content_type = "audio/mpeg"
        elif format_type.lower() == 'wav':
            content_type = "audio/wav"
        
        # ファイル名の生成
        filename = f"generated_music_{int(time.time())}.{format_type}"
        
        return Response(
            content=audio_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(audio_bytes))
            }
        )
            
    except Exception as e:
        # エラー時もref_audio_inputの一時ファイルをクリーンアップ
        if (hasattr(request, 'ref_audio_input') and 
            request.ref_audio_input and 
            request.ref_audio_input.startswith(tempfile.gettempdir())):
            try:
                temp_audio_path = request.ref_audio_input
                temp_dir = os.path.dirname(temp_audio_path)
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_music_async")
async def generate_music_async(request: GenerateMusicRequest):
    """非同期音楽生成エンドポイント"""
    try:
        if model_demo is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized.")
        
        # リクエストIDを生成
        request_id = str(uuid.uuid4())
        
        # キューに追加
        queued_request = QueuedRequest(
            request_id=request_id,
            request=request,
            status=RequestStatus.PENDING,
            created_at=time.time()
        )
        
        with request_lock:
            request_status[request_id] = queued_request
            request_queue.put(queued_request)
        
        return {
            "request_id": request_id,
            "status": "queued",
            "message": "Request has been queued for processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{request_id}")
async def get_request_status(request_id: str):
    """リクエストのステータスを取得"""
    with request_lock:
        if request_id not in request_status:
            raise HTTPException(status_code=404, detail="Request not found")
        
        queued_request = request_status[request_id]
        
        response = {
            "request_id": request_id,
            "status": queued_request.status.value,
            "created_at": queued_request.created_at,
            "started_at": queued_request.started_at,
            "completed_at": queued_request.completed_at
        }
        
        if queued_request.status == RequestStatus.COMPLETED:
            # レスポンスにresultを含める際、audio_dataは除外
            result_for_response = queued_request.result.copy() if queued_request.result else None
            if result_for_response and "audio_data" in result_for_response:
                # audio_dataは除外し、代わりにファイル情報のみを含める
                result_for_response = {
                    "success": result_for_response.get("success", True),
                    "content_type": result_for_response.get("content_type"),
                    "format": result_for_response.get("format"),
                    "audio_size_bytes": len(result_for_response["audio_data"]) if "audio_data" in result_for_response else 0,
                    "params_json": result_for_response.get("params_json"),
                    "message": "Audio data ready for download. Use /result/{request_id} to download."
                }
            response["result"] = result_for_response
        elif queued_request.status == RequestStatus.FAILED:
            response["error"] = queued_request.error
        
        return response

@app.get("/result/{request_id}")
async def get_request_result(request_id: str):
    """完了したリクエストの結果を取得"""
    with request_lock:
        if request_id not in request_status:
            raise HTTPException(status_code=404, detail="Request not found")
        
        queued_request = request_status[request_id]
        
        if queued_request.status != RequestStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Request is {queued_request.status.value}, not completed"
            )
        
        result = queued_request.result
        
        # ファイルデータを返す場合
        if "audio_data" in result:
            # ファイル名の拡張子を正しく設定
            file_format = result.get("format", queued_request.request.format)
            filename = f"generated_music_{int(time.time())}.{file_format}"
            
            return Response(
                content=result["audio_data"],
                media_type=result["content_type"],
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Content-Length": str(len(result["audio_data"]))
                }
            )
        else:
            return result

@app.get("/queue/status")
async def get_queue_status():
    """キューの状況を取得"""
    with request_lock:
        queue_size = request_queue.qsize()
        
        status_counts = {
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0
        }
        
        for queued_request in request_status.values():
            status_counts[queued_request.status.value] += 1
        
        return {
            "queue_size": queue_size,
            "status_counts": status_counts,
            "total_requests": len(request_status)
        }

@app.delete("/request/{request_id}")
async def cancel_request(request_id: str):
    """リクエストをキャンセル（ペンディング状態のみ）"""
    with request_lock:
        if request_id not in request_status:
            raise HTTPException(status_code=404, detail="Request not found")
        
        queued_request = request_status[request_id]
        
        if queued_request.status == RequestStatus.PENDING:
            # キューから削除は難しいので、ステータスを変更
            queued_request.status = RequestStatus.FAILED
            queued_request.error = "Cancelled by user"
            queued_request.completed_at = time.time()
            return {"message": "Request cancelled"}
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel request in {queued_request.status.value} status"
            )

@app.post("/initialize")
async def initialize(
    checkpoint_path: str = "",
    device_id: int = 0,
    bf16: bool = True,
    torch_compile: bool = False,
    cpu_offload: bool = False,
    overlapped_decode: bool = False
):
    """パイプラインを初期化"""
    try:
        initialize_pipeline(
            checkpoint_path=checkpoint_path,
            device_id=device_id,
            bf16=bf16,
            torch_compile=torch_compile,
            cpu_offload=cpu_offload,
            overlapped_decode=overlapped_decode
        )
        return {"success": True, "message": "Pipeline initialized successfully"}
    except Exception as e:
        return {"success": False, "error_message": str(e)}

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "pipeline_loaded": model_demo is not None
    }

@app.get("/sample_data")
async def sample_data():
    """サンプルデータを取得（Gradioアプリのsample機能と同等）"""
    try:
        if data_sampler is None:
            raise HTTPException(status_code=500, detail="Data sampler not initialized")
        
        sample = data_sampler.sample()
        return {"success": True, "sample": sample}
    except Exception as e:
        return {"success": False, "error_message": str(e)}

@app.on_event("startup")
async def startup_event():
    """サーバー起動時にバックグラウンドワーカーを開始"""
    asyncio.create_task(background_worker())

@app.post("/generate_music_with_audio")
async def generate_music_with_audio(
    audio_file: UploadFile = File(..., description="MP3 audio file"),
    format: str = Form("wav"),
    audio_duration: float = Form(60.0),
    prompt: str = Form(TAG_DEFAULT),
    lyrics: str = Form(LYRIC_DEFAULT),
    infer_step: int = Form(60),
    guidance_scale: float = Form(15.0),
    scheduler_type: str = Form("euler"),
    cfg_type: str = Form("apg"),
    omega_scale: float = Form(10.0),
    manual_seeds: Optional[str] = Form(None),
    guidance_interval: float = Form(0.5),
    guidance_interval_decay: float = Form(0.0),
    min_guidance_scale: float = Form(3.0),
    use_erg_tag: bool = Form(True),
    use_erg_lyric: bool = Form(False),
    use_erg_diffusion: bool = Form(True),
    oss_steps: Optional[str] = Form(None),
    guidance_scale_text: float = Form(0.0),
    guidance_scale_lyric: float = Form(0.0),
    ref_audio_strength: float = Form(0.5),
    lora_name_or_path: str = Form("none"),
    lora_weight: float = Form(1.0),
    return_file_data: bool = Form(False)
):
    """
    MP3ファイルをアップロードして音楽生成を行う
    アップロードされたMP3ファイルをref_audio_inputとして使用します
    """
    try:
        if model_demo is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized. Call /initialize first.")
        
        # ファイルタイプのチェック
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Uploaded file must be an audio file")
        
        # 一時ファイルとしてMP3を保存
        temp_dir = tempfile.mkdtemp()
        temp_audio_path = os.path.join(temp_dir, f"uploaded_audio_{uuid.uuid4().hex}.mp3")
        
        try:
            # アップロードされたファイルを保存
            with open(temp_audio_path, "wb") as buffer:
                content = await audio_file.read()
                buffer.write(content)
            
            # GenerateMusicRequestオブジェクトを作成
            request = GenerateMusicRequest(
                format=format,
                audio_duration=audio_duration,
                prompt=prompt,
                lyrics=lyrics,
                infer_step=infer_step,
                guidance_scale=guidance_scale,
                scheduler_type=scheduler_type,
                cfg_type=cfg_type,
                omega_scale=omega_scale,
                manual_seeds=manual_seeds,
                guidance_interval=guidance_interval,
                guidance_interval_decay=guidance_interval_decay,
                min_guidance_scale=min_guidance_scale,
                use_erg_tag=use_erg_tag,
                use_erg_lyric=use_erg_lyric,
                use_erg_diffusion=use_erg_diffusion,
                oss_steps=oss_steps,
                guidance_scale_text=guidance_scale_text,
                guidance_scale_lyric=guidance_scale_lyric,
                audio2audio_enable=True,  # MP3アップロード時は強制的にaudio2audioを有効化
                ref_audio_strength=ref_audio_strength,
                ref_audio_input=temp_audio_path,  # アップロードされたファイルパスを設定
                lora_name_or_path=lora_name_or_path,
                lora_weight=lora_weight,
                return_file_data=return_file_data
            )
            
            # リクエストをキューに追加
            request_id = str(uuid.uuid4())
            queued_request = QueuedRequest(
                request_id=request_id,
                request=request,
                status=RequestStatus.PENDING,
                created_at=time.time()
            )
            
            with request_lock:
                request_queue.put(queued_request)
                request_status[request_id] = queued_request
            
            return {
                "success": True, 
                "request_id": request_id,
                "message": f"Audio file uploaded and queued for processing. Original filename: {audio_file.filename}"
            }
            
        except Exception as e:
            # エラー時は一時ファイルをクリーンアップ
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                os.rmdir(temp_dir)
            except:
                pass
            raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_music_with_audio_base64")
async def generate_music_with_audio_base64(
    audio_base64: str = Form(..., description="Base64 encoded MP3 audio data"),
    format: str = Form("wav"),
    audio_duration: float = Form(60.0),
    prompt: str = Form(TAG_DEFAULT),
    lyrics: str = Form(LYRIC_DEFAULT),
    infer_step: int = Form(60),
    guidance_scale: float = Form(15.0),
    scheduler_type: str = Form("euler"),
    cfg_type: str = Form("apg"),
    omega_scale: float = Form(10.0),
    manual_seeds: Optional[str] = Form(None),
    guidance_interval: float = Form(0.5),
    guidance_interval_decay: float = Form(0.0),
    min_guidance_scale: float = Form(3.0),
    use_erg_tag: bool = Form(True),
    use_erg_lyric: bool = Form(False),
    use_erg_diffusion: bool = Form(True),
    oss_steps: Optional[str] = Form(None),
    guidance_scale_text: float = Form(0.0),
    guidance_scale_lyric: float = Form(0.0),
    ref_audio_strength: float = Form(0.5),
    lora_name_or_path: str = Form("none"),
    lora_weight: float = Form(1.0),
    return_file_data: bool = Form(False)
):
    """
    Base64エンコードされたMP3データで音楽生成を行う
    """
    try:
        if model_demo is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized. Call /initialize first.")
        
        # Base64デコード
        try:
            audio_data = base64.b64decode(audio_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")
        
        # 一時ファイルとしてMP3を保存
        temp_dir = tempfile.mkdtemp()
        temp_audio_path = os.path.join(temp_dir, f"uploaded_audio_{uuid.uuid4().hex}.mp3")
        
        try:
            with open(temp_audio_path, "wb") as f:
                f.write(audio_data)
            
            # GenerateMusicRequestオブジェクトを作成
            request = GenerateMusicRequest(
                format=format,
                audio_duration=audio_duration,
                prompt=prompt,
                lyrics=lyrics,
                infer_step=infer_step,
                guidance_scale=guidance_scale,
                scheduler_type=scheduler_type,
                cfg_type=cfg_type,
                omega_scale=omega_scale,
                manual_seeds=manual_seeds,
                guidance_interval=guidance_interval,
                guidance_interval_decay=guidance_interval_decay,
                min_guidance_scale=min_guidance_scale,
                use_erg_tag=use_erg_tag,
                use_erg_lyric=use_erg_lyric,
                use_erg_diffusion=use_erg_diffusion,
                oss_steps=oss_steps,
                guidance_scale_text=guidance_scale_text,
                guidance_scale_lyric=guidance_scale_lyric,
                audio2audio_enable=True,  # MP3アップロード時は強制的にaudio2audioを有効化
                ref_audio_strength=ref_audio_strength,
                ref_audio_input=temp_audio_path,  # アップロードされたファイルパスを設定
                lora_name_or_path=lora_name_or_path,
                lora_weight=lora_weight,
                return_file_data=return_file_data
            )
            
            # リクエストをキューに追加
            request_id = str(uuid.uuid4())
            queued_request = QueuedRequest(
                request_id=request_id,
                request=request,
                status=RequestStatus.PENDING,
                created_at=time.time()
            )
            
            with request_lock:
                request_queue.put(queued_request)
                request_status[request_id] = queued_request
            
            return {
                "success": True, 
                "request_id": request_id,
                "message": "Base64 audio data uploaded and queued for processing"
            }
            
        except Exception as e:
            # エラー時は一時ファイルをクリーンアップ
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                os.rmdir(temp_dir)
            except:
                pass
            raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_music_with_audio_json")
async def generate_music_with_audio_json(request: GenerateMusicWithBase64Request):
    """
    JSON形式でBase64エンコードされたMP3データを受け取って音楽生成を行う
    """
    try:
        if model_demo is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized. Call /initialize first.")
        
        # Base64デコード
        try:
            audio_data = base64.b64decode(request.audio_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")
        
        # 一時ファイルとしてMP3を保存
        temp_dir = tempfile.mkdtemp()
        temp_audio_path = os.path.join(temp_dir, f"uploaded_audio_{uuid.uuid4().hex}.mp3")
        
        try:
            with open(temp_audio_path, "wb") as f:
                f.write(audio_data)
            
            # GenerateMusicRequestオブジェクトを作成
            music_request = GenerateMusicRequest(
                format=request.format,
                audio_duration=request.audio_duration,
                prompt=request.prompt,
                lyrics=request.lyrics,
                infer_step=request.infer_step,
                guidance_scale=request.guidance_scale,
                scheduler_type=request.scheduler_type,
                cfg_type=request.cfg_type,
                omega_scale=request.omega_scale,
                manual_seeds=request.manual_seeds,
                guidance_interval=request.guidance_interval,
                guidance_interval_decay=request.guidance_interval_decay,
                min_guidance_scale=request.min_guidance_scale,
                use_erg_tag=request.use_erg_tag,
                use_erg_lyric=request.use_erg_lyric,
                use_erg_diffusion=request.use_erg_diffusion,
                oss_steps=request.oss_steps,
                guidance_scale_text=request.guidance_scale_text,
                guidance_scale_lyric=request.guidance_scale_lyric,
                audio2audio_enable=True,  # MP3アップロード時は強制的にaudio2audioを有効化
                ref_audio_strength=request.ref_audio_strength,
                ref_audio_input=temp_audio_path,  # アップロードされたファイルパスを設定
                lora_name_or_path=request.lora_name_or_path,
                lora_weight=request.lora_weight,
                return_file_data=request.return_file_data
            )
            
            # リクエストをキューに追加
            request_id = str(uuid.uuid4())
            queued_request = QueuedRequest(
                request_id=request_id,
                request=music_request,
                status=RequestStatus.PENDING,
                created_at=time.time()
            )
            
            with request_lock:
                request_queue.put(queued_request)
                request_status[request_id] = queued_request
            
            return {
                "success": True, 
                "request_id": request_id,
                "message": "Base64 audio data uploaded and queued for processing"
            }
            
        except Exception as e:
            # エラー時は一時ファイルをクリーンアップ
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                os.rmdir(temp_dir)
            except:
                pass
            raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_music_with_audio_mp3")
async def generate_music_with_audio_mp3(
    audio_file: UploadFile = File(..., description="MP3 audio file"),
    audio_duration: float = Form(60.0),
    prompt: str = Form(TAG_DEFAULT),
    lyrics: str = Form(LYRIC_DEFAULT),
    infer_step: int = Form(60),
    guidance_scale: float = Form(15.0),
    scheduler_type: str = Form("euler"),
    cfg_type: str = Form("apg"),
    omega_scale: float = Form(10.0),
    manual_seeds: Optional[str] = Form(None),
    guidance_interval: float = Form(0.5),
    guidance_interval_decay: float = Form(0.0),
    min_guidance_scale: float = Form(3.0),
    use_erg_tag: bool = Form(True),
    use_erg_lyric: bool = Form(False),
    use_erg_diffusion: bool = Form(True),
    oss_steps: Optional[str] = Form(None),
    guidance_scale_text: float = Form(0.0),
    guidance_scale_lyric: float = Form(0.0),
    ref_audio_strength: float = Form(0.5),
    lora_name_or_path: str = Form("none"),
    lora_weight: float = Form(1.0)
):
    """
    MP3ファイルをアップロードして音楽生成を行い、MP3形式で結果を返す
    注意: このエンドポイントは /result/{request_id} で結果を取得する必要があります
    """
    # formatを強制的にmp3に設定し、return_file_dataをTrueに設定
    result = await generate_music_with_audio(
        audio_file=audio_file,
        format="mp3",
        audio_duration=audio_duration,
        prompt=prompt,
        lyrics=lyrics,
        infer_step=infer_step,
        guidance_scale=guidance_scale,
        scheduler_type=scheduler_type,
        cfg_type=cfg_type,
        omega_scale=omega_scale,
        manual_seeds=manual_seeds,
        guidance_interval=guidance_interval,
        guidance_interval_decay=guidance_interval_decay,
        min_guidance_scale=min_guidance_scale,
        use_erg_tag=use_erg_tag,
        use_erg_lyric=use_erg_lyric,
        use_erg_diffusion=use_erg_diffusion,
        oss_steps=oss_steps,
        guidance_scale_text=guidance_scale_text,
        guidance_scale_lyric=guidance_scale_lyric,
        ref_audio_strength=ref_audio_strength,
        lora_name_or_path=lora_name_or_path,
        lora_weight=lora_weight,
        return_file_data=True
    )
    
    # MP3専用エンドポイントの場合、メッセージを追加
    if result.get("success"):
        result["message"] = f"{result.get('message', '')} MP3 format will be available at /result/{{request_id}}"
    
    return result

@app.post("/generate_music_with_audio_json_mp3")
async def generate_music_with_audio_json_mp3(request: GenerateMusicWithBase64Request):
    """
    JSON形式でBase64エンコードされたMP3データを受け取って音楽生成を行い、MP3形式で結果を返す
    注意: このエンドポイントは /result/{request_id} で結果を取得する必要があります
    """
    # formatを強制的にmp3に設定し、return_file_dataをTrueに設定
    request.format = "mp3"
    request.return_file_data = True
    
    result = await generate_music_with_audio_json(request)
    
    # MP3専用エンドポイントの場合、メッセージを追加
    if result.get("success"):
        result["message"] = f"{result.get('message', '')} MP3 format will be available at /result/{{request_id}}"
    
    return result

@app.post("/generate_music_with_audio_direct_mp3")
async def generate_music_with_audio_direct_mp3(
    audio_file: UploadFile = File(..., description="MP3 audio file"),
    audio_duration: float = Form(60.0),
    prompt: str = Form(TAG_DEFAULT),
    lyrics: str = Form(LYRIC_DEFAULT),
    infer_step: int = Form(60),
    guidance_scale: float = Form(15.0),
    scheduler_type: str = Form("euler"),
    cfg_type: str = Form("apg"),
    omega_scale: float = Form(10.0),
    manual_seeds: Optional[str] = Form(None),
    guidance_interval: float = Form(0.5),
    guidance_interval_decay: float = Form(0.0),
    min_guidance_scale: float = Form(3.0),
    use_erg_tag: bool = Form(True),
    use_erg_lyric: bool = Form(False),
    use_erg_diffusion: bool = Form(True),
    oss_steps: Optional[str] = Form(None),
    guidance_scale_text: float = Form(0.0),
    guidance_scale_lyric: float = Form(0.0),
    ref_audio_strength: float = Form(0.5),
    lora_name_or_path: str = Form("none"),
    lora_weight: float = Form(1.0)
):
    """
    MP3ファイルをアップロードして音楽生成を行い、MP3ファイルを直接レスポンスとして返す
    注意: このエンドポイントは同期的に処理され、完了まで待機します
    """
    try:
        if model_demo is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized. Call /initialize first.")
        
        # ファイルタイプのチェック
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Uploaded file must be an audio file")
        
        # 一時ファイルとしてMP3を保存
        temp_dir = tempfile.mkdtemp()
        temp_audio_path = os.path.join(temp_dir, f"uploaded_audio_{uuid.uuid4().hex}.mp3")
        
        try:
            # アップロードされたファイルを保存
            with open(temp_audio_path, "wb") as buffer:
                content = await audio_file.read()
                buffer.write(content)
            
            # 直接音楽生成を実行（ファイル保存なし）
            results = model_demo(
                format="mp3",
                audio_duration=audio_duration,
                prompt=prompt,
                lyrics=lyrics,
                infer_step=infer_step,
                guidance_scale=guidance_scale,
                scheduler_type=scheduler_type,
                cfg_type=cfg_type,
                omega_scale=omega_scale,
                manual_seeds=manual_seeds,
                guidance_interval=guidance_interval,
                guidance_interval_decay=guidance_interval_decay,
                min_guidance_scale=min_guidance_scale,
                use_erg_tag=use_erg_tag,
                use_erg_lyric=use_erg_lyric,
                use_erg_diffusion=use_erg_diffusion,
                oss_steps=oss_steps,
                guidance_scale_text=guidance_scale_text,
                guidance_scale_lyric=guidance_scale_lyric,
                audio2audio_enable=True,
                ref_audio_strength=ref_audio_strength,
                ref_audio_input=temp_audio_path,
                lora_name_or_path=lora_name_or_path,
                lora_weight=lora_weight,
                return_audio_data=True  # 音楽データを直接返す
            )
            
            # 一時ファイルをクリーンアップ
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temporary audio file: {cleanup_error}")
            
            # resultsから音楽データを取得
            if isinstance(results, (list, tuple)) and len(results) > 0:
                audio_data_dict = results[0]  # 最初の音楽データを取得
            else:
                audio_data_dict = results
            
            # 音楽データをバイト形式に変換
            audio_tensor = audio_data_dict['audio']
            sample_rate = audio_data_dict['sample_rate']
            format_type = audio_data_dict['format']
            
            # PyTorchテンソルをバイト形式に変換
            import io
            import torchaudio
            
            buffer = io.BytesIO()
            backend = "soundfile"
            if format_type == "ogg":
                backend = "sox"
            
            torchaudio.save(
                buffer, 
                audio_tensor, 
                sample_rate=sample_rate, 
                format=format_type, 
                backend=backend
            )
            audio_bytes = buffer.getvalue()
            buffer.close()
            
            # MP3ファイルとして直接返す
            filename = f"generated_music_{int(time.time())}.mp3"
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Content-Length": str(len(audio_bytes))
                }
            )
            
        except Exception as e:
            # エラー時は一時ファイルをクリーンアップ
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                os.rmdir(temp_dir)
            except:
                pass
            raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ACE-Step Gradio Compatible API Server")
    parser.add_argument("--port", type=int, default=8019, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--checkpoint_path", type=str, default="", help="Path to checkpoint")
    parser.add_argument("--device_id", type=int, default=0, help="CUDA device ID")
    parser.add_argument("--bf16", action="store_true", default=True, help="Use bfloat16")
    parser.add_argument("--torch_compile", action="store_true", default=False, help="Use torch.compile")
    parser.add_argument("--cpu_offload", action="store_true", default=False, help="Use CPU offloading")
    parser.add_argument("--overlapped_decode", action="store_true", default=False, help="Use overlapped decoding")
    
    args = parser.parse_args()
    
    # 起動時にパイプラインを初期化
    print("Initializing pipeline...")
    initialize_pipeline(
        checkpoint_path=args.checkpoint_path,
        device_id=args.device_id,
        bf16=args.bf16,
        torch_compile=args.torch_compile,
        cpu_offload=args.cpu_offload,
        overlapped_decode=args.overlapped_decode
    )
    print("Pipeline initialized successfully!")
    
    # サーバー起動
    uvicorn.run(app, host=args.host, port=args.port)
