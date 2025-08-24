# 🪃 Boomerang.py - Advanced Video Boomerang Creator

A professional-grade Python script that creates seamless boomerang videos using advanced FFmpeg features. Perfect for content creators, social media managers, and video enthusiasts who want to create high-quality looping videos with smooth transitions.

## ✨ Features

- **Seamless Looping**: Advanced crossfade transitions for smooth video loops
- **Hardware Acceleration**: GPU encoding support (NVIDIA NVENC, Apple VideoToolbox, Intel QSV)
- **Professional Quality**: Configurable CRF and encoding presets
- **Audio Processing**: Synchronized audio boomerang effects with tempo matching
- **Flexible Timing**: Custom start time, duration, and playback speed
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

1. **Python 3.6+** installed on your system
2. **FFmpeg** installed and accessible in your PATH
3. **Python dependencies** (see Installation section)

### Installation

1. **Clone or download** the script:
   ```bash
   git clone <repository-url>
   cd boomerang.py
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install ffmpeg-python
   ```

3. **Install FFmpeg**:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`
   - **macOS**: Use [Homebrew](https://brew.sh/): `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

4. **Verify installation**:
   ```bash
   python boomerang.py --help
   ```

## 📖 Usage

### Basic Commands

```bash
# Simple boomerang with default settings
python boomerang.py input_video.mp4

# Custom output filename
python boomerang.py input_video.mp4 -o my_boomerang.mp4

# High-quality output with smooth loop
python boomerang.py input_video.mp4 --crf 18 --preset slow --fade-duration 0.1

# Fast preview using GPU acceleration
python boomerang.py input_video.mp4 --gpu --preset fast
```

### Advanced Examples

```bash
# Extract segment from 10s to 15s, create smooth loop
python boomerang.py video.mp4 -s 10 -d 5 --fade-duration 0.2 --include-audio

# Slow-motion boomerang (0.5x speed)
python boomerang.py video.mp4 --speed 0.5 --crf 20

# Ultra-fast encoding for testing
python boomerang.py video.mp4 --preset ultrafast --crf 28

# High-quality with audio processing
python boomerang.py video.mp4 --crf 18 --preset slow --include-audio --fade-duration 0.15
```

## 🔧 Command Line Options

### Input/Output
- `input_file`: Path to the source video file (required)
- `-o, --output`: Output filename (default: `<input>_boomerang.mp4`)

### Segment and Speed
- `-s, --start-time`: Start time in seconds (default: 0.0)
- `-d, --duration`: Duration of clip to use (default: 3.0)
- `-sp, --speed`: Playback speed multiplier (default: 1.0)

### Quality and Encoding
- `--crf`: Constant Rate Factor for quality (18-28 recommended, lower is better, default: 23)
- `--preset`: Encoding speed vs. compression (ultrafast to veryslow, default: medium)
- `--gpu`: Enable hardware acceleration if available

### Effects and Audio
- `--fade-duration`: Crossfade duration for smooth loops (default: 0.0)
- `--include-audio`: Process audio track to match video effect
- `-q, --quiet`: Suppress FFmpeg console output

## 🎯 Quality Settings Guide

### CRF Values
- **18-20**: Visually lossless, high quality (larger files)
- **21-23**: High quality, good balance (recommended)
- **24-26**: Good quality, smaller files
- **27-28**: Acceptable quality, very small files

### Encoding Presets
- **ultrafast**: Fastest encoding, largest files
- **superfast/veryfast**: Quick encoding, good for testing
- **fast/medium**: Balanced speed and compression (recommended)
- **slow/slower/veryslow**: Best compression, slowest encoding

## 🖥️ Hardware Acceleration

The script automatically detects your system and attempts to use the best available hardware encoder:

- **NVIDIA**: Uses NVENC encoder (Windows/Linux)
- **Apple**: Uses VideoToolbox (macOS)
- **Intel**: Uses Quick Sync Video (if available)

Enable with `--gpu` flag for significantly faster encoding.

## 🔍 Troubleshooting

### Common Issues

1. **"FFmpeg not found"**
   - Ensure FFmpeg is installed and in your system PATH
   - Restart your terminal after installation

2. **"Permission denied"**
   - Check file permissions on input/output directories
   - Ensure you have write access to the output location

3. **Poor video quality**
   - Lower the CRF value (try 18-20)
   - Use a slower preset (slow, slower, veryslow)
   - Ensure input video has sufficient quality

4. **Slow encoding**
   - Enable GPU acceleration with `--gpu`
   - Use faster presets (fast, veryfast, ultrafast)
   - Reduce input video resolution if possible

5. **Audio sync issues**
   - Use `--include-audio` flag for proper audio processing
   - Avoid extreme speed values (stick to 0.5-2.0 range)

### Performance Tips

- **For testing**: Use `--preset ultrafast --crf 28`
- **For production**: Use `--preset slow --crf 18-20`
- **For speed**: Always use `--gpu` if available
- **For smooth loops**: Use `--fade-duration 0.1-0.2`

## 🧪 Testing

Test the script with a short video first:

```bash
# Quick test with low quality
python boomerang.py test_video.mp4 --preset ultrafast --crf 28 --duration 2

# Test GPU acceleration
python boomerang.py test_video.mp4 --gpu --preset fast
```

## 📁 Supported Formats

### Input Formats
- MP4, MOV, AVI, MKV, WebM
- Any format supported by FFmpeg

### Output Format
- MP4 with H.264 video codec
- YUV420p pixel format for maximum compatibility
- AAC audio (if included)

## 🔄 Maintenance

### Updating Dependencies
```bash
pip install --upgrade ffmpeg-python
```

### Checking FFmpeg Version
```bash
ffmpeg -version
```

### Verifying Hardware Support
```bash
# Check available encoders
ffmpeg -encoders | grep -E "(nvenc|videotoolbox|qsv)"
```

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script.

## 📄 License

This project is open source. Please check the repository for specific license information.

## 🙏 Acknowledgments

- Built with [FFmpeg](https://ffmpeg.org/) - the powerful multimedia framework
- Uses [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) for Python integration
- Inspired by the need for high-quality social media content

---

**Happy Boomeranging! 🪃✨**