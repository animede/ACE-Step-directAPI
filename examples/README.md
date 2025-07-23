# Examples and Tests

This directory contains examples and test scripts for ACE-Step-directAPI.

## Examples

### Direct Mode Examples
- **simple_usage.py** - Demonstrates both direct and async modes
- **async_mode_examples.py** - Comprehensive async mode examples

### Legacy Examples (From Original ACE-Step)
- **example_async_simple.py** - Basic async API usage
- **examples_gradio_api.py** - Gradio API examples
- **simple_request.json** - Basic request format
- **test_request.json** - Test request format

## Tests

### Direct Mode Tests
- **test_direct_mode_no_file_save.py** - Direct mode functionality tests
- **test_upload_direct_mode_no_file_save.py** - Upload direct mode tests
- **test_comprehensive_direct.py** - Comprehensive direct mode tests
- **test_direct_audio_response.py** - Audio response tests

### Legacy Tests (From Original ACE-Step)
- **test_gradio_compatible_api.py** - Comprehensive API tests
- **test_mp3_upload_api.py** - MP3 upload functionality tests
- **test_mp3_upload_curl.sh** - cURL-based upload tests

## Running Examples

### Start the API Server
```bash
python gradio_compatible_api.py --port 8019
```

### Run Direct Mode Example
```bash
python examples/simple_usage.py
```

### Run Legacy Examples
```bash
python examples/example_async_simple.py
python examples/examples_gradio_api.py
```

## Running Tests

### Direct Mode Tests
```bash
python tests/test_direct_mode_no_file_save.py
python tests/test_comprehensive_direct.py
```

### Legacy Tests
```bash
python tests/test_gradio_compatible_api.py
python tests/test_mp3_upload_api.py
bash tests/test_mp3_upload_curl.sh
```

## Configuration

All examples use the default configuration:
- **API Base URL**: http://localhost:8019
- **Format**: wav (direct mode), mp3 (async mode)
- **Audio Duration**: 30s (direct), 100s (async)

You can modify these settings in each example file.
