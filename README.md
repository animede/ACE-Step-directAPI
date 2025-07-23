# ACE-Step Direct API

A **Direct Mode** implementation for the ACE-Step music generation system that returns audio data directly via HTTP response without saving files to disk.

## 🎯 Overview

This project extends the original [ACE-Step](https://github.com/ace-step/ACE-Step) music generation system with direct API capabilities, enabling in-memory audio processing and HTTP streaming responses.

## ✨ Key Features

### 🚀 Direct Mode
- **Zero File I/O**: Generate music directly in memory without disk writes
- **HTTP Streaming**: Return audio data directly as HTTP response
- **Memory Efficient**: Optimized tensor-to-bytes conversion
- **Multiple Formats**: Support for WAV, MP3, and OGG output formats

### 🔄 Backward Compatible
- **Async Mode**: Original file-save functionality preserved
- **API Compatibility**: Existing clients work without modification
- **Gradual Migration**: Switch between modes as needed

### 📤 Upload Support
- **Audio Upload**: Direct audio file upload and processing
- **Base64 Support**: JSON-based audio data upload
- **Automatic Cleanup**: Temporary files are automatically cleaned up

## 🛠 Installation

```bash
git clone https://github.com/animede/ACE-Step-directAPI.git
cd ACE-Step-directAPI
pip install -r requirements.txt
pip install -e .
```

## 🚀 Quick Start

### Start the API Server

```bash
python gradio_compatible_api.py --port 8019 --host 0.0.0.0
```

### Direct Mode Examples

#### Text-to-Music (Direct)
```bash
curl -X POST "http://localhost:8019/generate_music_direct" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "wav",
    "audio_duration": 30.0,
    "prompt": "upbeat electronic music",
    "lyrics": "test lyrics",
    "infer_step": 20
  }' \
  --output generated_music.wav
```

#### Audio Upload + Generation (Direct)
```bash
curl -X POST "http://localhost:8019/generate_music_with_audio_direct_mp3" \
  -F "audio_file=@input.mp3" \
  -F "audio_duration=30.0" \
  -F "prompt=jazz fusion remix" \
  -F "infer_step=20" \
  --output remixed_music.mp3
```

### Async Mode Examples

#### Queue-based Processing
```bash
# 1. Submit request
curl -X POST "http://localhost:8019/generate_music" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "classical piano", "return_file_data": true}' \
  > response.json

# 2. Check status
REQUEST_ID=$(cat response.json | grep -o '"request_id":"[^"]*"' | cut -d'"' -f4)
curl "http://localhost:8019/status/$REQUEST_ID"

# 3. Download result
curl "http://localhost:8019/result/$REQUEST_ID" --output result.wav
```

## 📊 API Endpoints

### Direct Mode (No File Save)
| Endpoint | Method | Description | Input | Output |
|----------|--------|-------------|-------|--------|
| `/generate_music_direct` | POST | Text-to-music generation | JSON | Audio file (HTTP) |
| `/generate_music_with_audio_direct_mp3` | POST | Audio upload + generation | Multipart Form | MP3 file (HTTP) |

### Async Mode (File Save)
| Endpoint | Method | Description | Input | Output |
|----------|--------|-------------|-------|--------|
| `/generate_music` | POST | Queue music generation | JSON | request_id |
| `/generate_music_async` | POST | Async music generation | JSON | request_id |
| `/status/{request_id}` | GET | Check processing status | - | JSON status |
| `/result/{request_id}` | GET | Download result | - | Audio file or JSON |

### Utility
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/initialize` | POST | Initialize pipeline |
| `/queue/status` | GET | Queue status |

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test direct mode functionality
python test_direct_mode_no_file_save.py

# Test upload functionality
python test_upload_direct_mode_no_file_save.py

# Run all tests
python test_comprehensive_direct.py
```

## 🔄 Legacy Compatibility

**ACE-Step-directAPI is fully backward compatible with all original ACE-Step samples and documentation!**

### Using Original ACE-Step Samples

All samples from the original ACE-Step repository work without changes:

```bash
# Run original async examples
python examples/example_async_simple.py
python examples/examples_gradio_api.py

# Run original tests
python tests/test_gradio_compatible_api.py
python tests/test_mp3_upload_api.py
bash tests/test_mp3_upload_curl.sh
```

### Legacy Documentation

Original ACE-Step documentation is available in `docs/legacy/`:
- `README_GRADIO_COMPATIBLE_API.md` - Gradio API documentation
- `README_ASYNC_API.md` - Async API documentation  
- `README_MP3_UPLOAD_API.md` - MP3 upload API documentation
- `QUICKSTART_GRADIO_API.md` - Quick start guide

### Migration Guide

**No migration needed!** Your existing code will continue to work.

To use new Direct Mode features, simply change the endpoint:
```python
# Old (still works)
response = requests.post('http://localhost:8019/generate_music', json=data)

# New Direct Mode
response = requests.post('http://localhost:8019/generate_music_direct', json=data)
```

For more details, see `docs/LEGACY_COMPATIBILITY.md`.

## 📈 Performance Comparison

| Mode | Disk I/O | Memory Usage | Response Time | File Management |
|------|----------|--------------|---------------|-----------------|
| **Direct** | ❌ None | 📈 Temporary increase | ⚡ Faster | ✅ Automatic |
| **File-save** | ✅ Required | 📊 Standard | 📊 Standard | 🔧 Manual |

## 🔧 Configuration

### Environment Variables

```bash
export ACE_OUTPUT_DIR="./outputs"  # Output directory for file-save mode
export CUDA_VISIBLE_DEVICES="0"    # GPU device selection
```

### Pipeline Initialization Options

```python
initialize_pipeline(
    checkpoint_path="",      # Model checkpoint path
    device_id=0,            # CUDA device ID
    bf16=True,              # Use bfloat16 precision
    torch_compile=False,    # Enable torch compilation
    cpu_offload=False,      # Enable CPU offloading
    overlapped_decode=False # Enable overlapped decoding
)
```

## 📚 Documentation

- [**Implementation Details**](./docs/DIRECT_MODE_IMPLEMENTATION.md) - Technical implementation guide
- [**Work Summary**](./docs/WORK_SUMMARY.md) - Complete development summary
- [**Original ACE-Step**](https://github.com/ace-step/ACE-Step) - Base project

## 🎵 Examples

### Response Headers
Direct mode responses include proper audio headers:

```http
Content-Type: audio/wav
Content-Disposition: attachment; filename="generated_music_1642789123.wav"
Content-Length: 1141400
```

### Error Handling
```json
{
  "success": false,
  "error_message": "Pipeline not initialized. Call /initialize first."
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project extends the original ACE-Step project. Please refer to the original [ACE-Step license](https://github.com/ace-step/ACE-Step/blob/main/LICENSE) for licensing information.

## 🙏 Acknowledgments

- **ACE-Step Team**: Original music generation system
- **Stability AI**: Stable Audio Open Small sampler inspiration
- **Hugging Face**: Diffusers library integration

## 🔗 Links

- [Original ACE-Step Project](https://github.com/ace-step/ACE-Step)
- [ACE-Step Technical Report](https://arxiv.org/abs/2506.00045)
- [Hugging Face Space Demo](https://huggingface.co/spaces/ACE-Step/ACE-Step)

---

**🎼 Building the Stable Diffusion moment for music - with direct API capabilities! 🎼**
