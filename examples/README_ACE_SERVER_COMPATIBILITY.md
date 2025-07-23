# ACE-Server.py Compatibility Guide

This guide shows how to use ACE-Step-directAPI as a drop-in replacement for the original `ace_server.py` `/generate` endpoint.

## Files in this directory

- **ace_server_compatibility.py** - Complete compatibility client
- **music_py_compatibility.py** - Drop-in replacement functions for music.py
- **README_ACE_SERVER_COMPATIBILITY.md** - This guide

## Original vs New API Comparison

### Original ace_server.py
```python
@app.post('/generate')
async def generate(
    audio_duration: float = Form(-1),
    genre: str = Form(...),
    infer_step: int = Form(50),
    lyrics: str = Form(...),
    guidance_scale: float = Form(15),
    # ... other parameters
):
    # Returns audio as bytes with Content-Disposition header
```

### ACE-Step-directAPI Equivalent

**Legacy Mode (Async with file save):**
```python
POST /generate_music
{
    "format": "mp3",
    "audio_duration": -1,
    "prompt": "genre_text",  # genre -> prompt
    "lyrics": "lyrics_text",
    "infer_step": 50,
    "guidance_scale": 15,
    "return_file_data": true
}
```

**Direct Mode (No file save):**
```python
POST /generate_music_direct
{
    "format": "mp3",
    "audio_duration": -1,
    "prompt": "genre_text",
    "lyrics": "lyrics_text",
    "infer_step": 50,
    "guidance_scale": 15
}
```

## Migration Guide

### Option 1: Using the Compatibility Client

```python
from ace_server_compatibility import ACEStepLegacyClient

client = ACEStepLegacyClient("http://127.0.0.1:8019")

# Same parameters as original ace_server.py
audio_content = client.generate_legacy(
    audio_duration=-1,
    genre="upbeat electronic music",
    lyrics="[verse]\nHello world\n[chorus]\nMusic time",
    infer_step=27,
    guidance_scale=15,
    omega_scale=10
)

# Or use direct mode for faster response
audio_content = client.generate_direct(
    # ... same parameters
)
```

### Option 2: Modify Your Existing music.py

Replace your `generate_song` function:

```python
# OLD (using ace_server.py)
def generate_song(jeson_song: dict, infer_step: int = 27, guidance_scale: float = 15, omega_scale: float = 10):
    # ... original code using requests.post(ace_url, data=data)

# NEW (using ACE-Step-directAPI) 
from music_py_compatibility import generate_song_new

def generate_song(jeson_song: dict, infer_step: int = 27, guidance_scale: float = 15, omega_scale: float = 10):
    return generate_song_new(jeson_song, infer_step, guidance_scale, omega_scale, use_direct=True)
```

### Option 3: Change URL Only (Quick Fix)

For a quick fix, just change the URL in your existing code:

```python
# OLD
ace_url = "http://127.0.0.1:64756/generate"

# NEW - Legacy mode (async)
ace_url = "http://127.0.0.1:8019/generate_music"

# NEW - Direct mode (faster)
ace_url = "http://127.0.0.1:8019/generate_music_direct"
```

**Note:** You'll need to change from `requests.post(url, data=data)` to `requests.post(url, json=data)` for the new API.

## Parameter Mapping

| Original ace_server.py | ACE-Step-directAPI | Notes |
|------------------------|-------------------|-------|
| `genre` | `prompt` | Renamed field |
| `audio_duration` | `audio_duration` | Same |
| `lyrics` | `lyrics` | Same |
| `infer_step` | `infer_step` | Same |
| `guidance_scale` | `guidance_scale` | Same |
| `scheduler_type` | `scheduler_type` | Same |
| `cfg_type` | `cfg_type` | Same |
| `omega_scale` | `omega_scale` | Same |
| All other params | Same | All parameters supported |

## Key Differences

### Input Format
- **Original:** Form data (`application/x-www-form-urlencoded`)
- **New:** JSON data (`application/json`)

### Output Format
- **Both:** Raw audio bytes with proper headers
- **New Direct Mode:** Immediate response
- **New Legacy Mode:** Async processing (like original)

### Response Headers
Both APIs return the same headers:
```
Content-Type: audio/mpeg
Content-Disposition: attachment; filename="generated_music.mp3"
```

## Performance Comparison

| Mode | Processing | File Save | Response Time | Use Case |
|------|------------|-----------|---------------|----------|
| Original ace_server.py | Sync | Yes | Medium | Original compatibility |
| ACE-Step Legacy Mode | Async | Yes | Medium | Drop-in replacement |
| ACE-Step Direct Mode | Sync | No | Fast | New applications |

## Example: Complete Migration

### Before (music.py with ace_server.py)
```python
ace_url = "http://127.0.0.1:64756/generate"

def generate_song(jeson_song: dict, infer_step: int = 27, guidance_scale: float = 15, omega_scale: float = 10):
    lyrics_dic = jeson_song['lyrics']
    lyrics = convert_lyrics_dict_to_text(lyrics_dic)
    genre = jeson_song['genre']
    
    data = {
        "audio_duration": -1,
        "genre": genre,
        "infer_step": infer_step,
        "lyrics": lyrics,
        "guidance_scale": guidance_scale,
        "scheduler_type": "euler",
        "cfg_type": "apg",
        "omega_scale": omega_scale,
        # ... other params
    }
    response = requests.post(ace_url, data=data)  # Form data
    return response.content
```

### After (music.py with ACE-Step-directAPI)
```python
from music_py_compatibility import generate_song_new

def generate_song(jeson_song: dict, infer_step: int = 27, guidance_scale: float = 15, omega_scale: float = 10):
    # Use new function - same interface, better performance
    return generate_song_new(jeson_song, infer_step, guidance_scale, omega_scale, use_direct=True)
```

## Testing

Run the compatibility tests:

```bash
# Test the compatibility client
python examples/ace_server_compatibility.py

# Test the music.py replacement functions
python examples/music_py_compatibility.py
```

Both tests will generate sample music files to verify compatibility.

## Conclusion

ACE-Step-directAPI provides complete backward compatibility with ace_server.py while offering:

- ✅ Same input/output interface
- ✅ Same parameter support  
- ✅ Improved performance with Direct Mode
- ✅ Async processing option
- ✅ No file system dependencies (Direct Mode)
- ✅ Drop-in replacement capability

Choose the migration approach that works best for your project!
