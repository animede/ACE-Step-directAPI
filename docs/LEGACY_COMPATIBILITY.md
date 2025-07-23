# ACE-Step Legacy Compatibility

This document explains how ACE-Step-directAPI maintains compatibility with existing ACE-Step samples and documentation.

## Overview

ACE-Step-directAPI is fully backward compatible with all existing ACE-Step APIs. This means:
- All existing sample code works without modification
- All existing documentation remains valid
- New Direct Mode features are additional, not replacement

## API Compatibility

### Existing Endpoints (Fully Compatible)
- `/generate_music` - Async music generation with file save
- `/status/{request_id}` - Check generation status
- `/result/{request_id}` - Download generated music
- `/upload_music` - Upload and process music files
- `/health` - Health check

### New Direct Mode Endpoints
- `/generate_music_direct` - Generate music directly in HTTP response
- `/upload_music_direct` - Upload and process music directly

## Sample Code Compatibility

### Original ACE-Step Samples (Still Valid)
All samples from the original ACE-Step repository work without changes:

1. **examples/example_async_simple.py** - Basic async API usage
2. **examples/examples_gradio_api.py** - Gradio API examples
3. **examples/simple_request.json** - Basic request format
4. **examples/test_request.json** - Test request format

### Test Scripts (Still Valid)
All test scripts from the original repository work:

1. **tests/test_gradio_compatible_api.py** - Comprehensive API tests
2. **tests/test_mp3_upload_api.py** - MP3 upload functionality tests
3. **tests/test_mp3_upload_curl.sh** - cURL-based upload tests

## Documentation Compatibility

### Legacy Documentation (docs/legacy/)
All original documentation remains valid:

1. **README_GRADIO_COMPATIBLE_API.md** - Gradio API documentation
2. **README_ASYNC_API.md** - Async API documentation
3. **README_MP3_UPLOAD_API.md** - MP3 upload API documentation
4. **QUICKSTART_GRADIO_API.md** - Quick start guide

## Migration Guide

### For Existing Users
No migration needed! Your existing code will continue to work.

### To Use Direct Mode
Simply change the endpoint from `/generate_music` to `/generate_music_direct`:

```python
# Old (still works)
response = requests.post('http://localhost:7860/generate_music', json=data)

# New Direct Mode
response = requests.post('http://localhost:7860/generate_music_direct', json=data)
# Audio data is directly in response.content
```

## Benefits of Direct Mode

1. **No File System Dependencies** - Audio generated in memory
2. **Faster Response** - No disk I/O overhead
3. **Better for Containers** - No persistent storage needed
4. **API-First Design** - Perfect for microservices

## Best Practices

### When to Use Async Mode (Original)
- Long duration music generation (>60 seconds)
- Batch processing
- When you need progress tracking

### When to Use Direct Mode
- Short to medium duration music (<60 seconds)
- Real-time applications
- Stateless services
- Container deployments

## Conclusion

ACE-Step-directAPI provides the best of both worlds:
- Complete backward compatibility with existing code
- New direct mode capabilities for modern use cases
- All original samples and documentation remain valid and useful
