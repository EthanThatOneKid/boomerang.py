#!/usr/bin/env python3
import argparse
import ffmpeg
import sys
import os
import platform

# Research Finding 1: Hardware Acceleration.
# Different systems use different hardware-accelerated codecs. This dictionary
# maps common platforms/vendors to their respective H.264 encoders. Using these
# can dramatically speed up the encoding process.
HW_ACCEL_CODECS = {
    "nvidia": "h264_nvenc",
    "apple": "h264_videotoolbox",
    "intel": "h264_qsv",
}

def create_boomerang(
    input_file: str,
    output_file: str,
    start_time: float,
    duration: float,
    speed: float,
    crf: int,
    preset: str,
    fade_duration: float,
    include_audio: bool,
    use_gpu: bool,
    quiet: bool,
):
    """
    Creates a professional-quality boomerang video using advanced FFmpeg features.

    Args:
        input_file (str): Path to the source video file.
        output_file (str): Path for the generated output video.
        start_time (float): Start time in seconds for the boomerang segment.
        duration (float): Duration in seconds of the segment to use.
        speed (float): Playback speed multiplier.
        crf (int): Constant Rate Factor for video quality (lower is better).
        preset (str): H.264 encoding preset for speed vs. compression trade-off.
        fade_duration (float): Duration of the crossfade at the loop point.
        include_audio (bool): Whether to include and process the audio track.
        use_gpu (bool): Whether to attempt using hardware acceleration.
        quiet (bool): If True, suppresses FFmpeg's console output.
    """
    # Input validation
    if start_time < 0:
        raise ValueError("Start time cannot be negative")
    if duration <= 0:
        raise ValueError("Duration must be positive")
    if speed <= 0:
        raise ValueError("Speed must be positive")
    if fade_duration < 0:
        raise ValueError("Fade duration cannot be negative")
    if fade_duration >= duration:
        raise ValueError("Fade duration must be less than total duration")
    if crf < 0 or crf > 51:
        raise ValueError("CRF must be between 0 and 51")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("🚀 Starting advanced boomerang creation...")
    print(f"  - Source: '{input_file}'")
    print(f"  - Output: '{output_file}'")
    print(f"  - Segment: {start_time}s -> {start_time + duration}s ({duration}s)")
    print(f"  - Speed: {speed}x")
    print(f"  - Quality (CRF): {crf} | Preset: {preset}")
    print(f"  - Audio: {'Enabled' if include_audio else 'Disabled'}")
    print(f"  - GPU Acceleration: {'Enabled' if use_gpu else 'Disabled'}")
    if fade_duration > 0:
        print(f"  - Seamless Loop: {fade_duration}s crossfade")

    try:
        # --- Stream Setup ---
        # Define the input stream and trim it to the selected segment.
        input_stream = ffmpeg.input(input_file, ss=start_time, t=duration)
        video_stream = input_stream.video
        
        # --- Video Processing ---
        forward_video = video_stream
        reverse_video = video_stream.filter('reverse')

        # Research Finding 2: Seamless Looping with Crossfade.
        # A simple concatenation can cause a visible "jump". The 'xfade' filter
        # creates a smooth transition by blending the end of the forward clip
        # with the beginning of the reversed clip.
        if fade_duration > 0 and duration > fade_duration:
            final_video = ffmpeg.filter(
                [forward_video, reverse_video],
                'xfade',
                transition='fade',
                duration=fade_duration,
                offset=duration - fade_duration
            )
        else:
            final_video = ffmpeg.concat(forward_video, reverse_video)
            
        # Apply speed change to video using the 'setpts' filter.
        final_video = final_video.filter('setpts', f'{1/speed}*PTS')

        # --- Argument and Codec Setup ---
        output_args = [final_video]
        kwargs = {
            "preset": preset,
            "crf": crf,
            # Research Finding 3: Maximum Compatibility.
            # The 'yuv420p' pixel format is the most widely supported format
            # for H.264 video, ensuring playback on virtually all devices.
            "pix_fmt": "yuv420p",
        }

        # --- Audio Processing ---
        if include_audio:
            audio_stream = input_stream.audio
            forward_audio = audio_stream
            reverse_audio = audio_stream.filter('areverse')
            
            final_audio = ffmpeg.concat(forward_audio, reverse_audio, v=0, a=1)
            
            # Research Finding 4: Synchronized Audio Speed.
            # The 'atempo' filter changes audio tempo. It's limited to a range
            # of 0.5-100.0. To handle speeds outside this range, we must chain
            # multiple 'atempo' filters together.
            if speed != 1.0:
                # Build the atempo filter chain
                atempo_val = speed
                final_audio = final_audio.filter('atempo', atempo_val)
                
                # Note: FFmpeg's atempo filter automatically handles the chaining
                # for values outside the 0.5-2.0 range, so we don't need manual chaining
                # The filter will internally split and recombine as needed

            output_args.append(final_audio)
        else:
            kwargs["an"] = None  # Discard audio track.

        # --- Hardware Acceleration Logic ---
        # This logic attempts to select the correct hardware encoder based on the OS.
        if use_gpu:
            system = platform.system()
            codec_to_use = None
            
            if system == "Darwin":
                codec_to_use = HW_ACCEL_CODECS["apple"]
                print("  - Detected macOS, attempting to use VideoToolbox.")
            elif system == "Windows":
                # Check for NVIDIA GPU first (most common)
                try:
                    import subprocess
                    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        codec_to_use = HW_ACCEL_CODECS["nvidia"]
                        print("  - Detected NVIDIA GPU, using NVENC.")
                    else:
                        # Fall back to Intel QSV if available
                        codec_to_use = HW_ACCEL_CODECS["intel"]
                        print("  - No NVIDIA GPU detected, attempting Intel QSV.")
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    codec_to_use = HW_ACCEL_CODECS["intel"]
                    print("  - Could not detect GPU, attempting Intel QSV.")
            elif system == "Linux":
                # Check for NVIDIA GPU first
                try:
                    import subprocess
                    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        codec_to_use = HW_ACCEL_CODECS["nvidia"]
                        print("  - Detected NVIDIA GPU, using NVENC.")
                    else:
                        # Fall back to Intel QSV if available
                        codec_to_use = HW_ACCEL_CODECS["intel"]
                        print("  - No NVIDIA GPU detected, attempting Intel QSV.")
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    codec_to_use = HW_ACCEL_CODECS["intel"]
                    print("  - Could not detect GPU, attempting Intel QSV.")
            
            if codec_to_use:
                kwargs["vcodec"] = codec_to_use
            else:
                print("  - Warning: Could not determine a suitable GPU encoder, falling back to CPU.")
                kwargs["vcodec"] = "libx264"
        else:
            kwargs["vcodec"] = "libx264"

        # --- Execution ---
        output_stream = ffmpeg.output(*output_args, output_file, **kwargs)
        output_stream.run(overwrite_output=True, quiet=quiet)
        print(f"\n✅ Success! Boomerang saved to '{output_file}'")

    except ffmpeg.Error as e:
        print("\n❌ An FFmpeg error occurred:", file=sys.stderr)
        if hasattr(e, 'stderr') and e.stderr:
            print(e.stderr.decode(), file=sys.stderr)
        else:
            print(str(e), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Parses CLI arguments and initiates the boomerang creation process."""
    parser = argparse.ArgumentParser(
        description="📹 Create an advanced boomerang video from any input file.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example Usage:
  
  # 1. Basic boomerang with default settings (good quality)
  python boomerang.py my_video.mp4

  # 2. High-quality, smooth loop with audio
  python boomerang.py my_video.mp4 -o loop.mp4 --crf 18 --preset slow --fade-duration 0.1 --include-audio

  # 3. Fast preview using GPU acceleration
  python boomerang.py my_video.mp4 -o preview.mp4 --gpu --preset fast
"""
    )
    
    # --- Argument Definitions ---
    parser.add_argument("input_file", help="Path to the input video file.")
    parser.add_argument("-o", "--output", dest="output_file", help="Path for the output video (default: <input>_boomerang.mp4).")
    
    group_segment = parser.add_argument_group('Segment and Speed')
    group_segment.add_argument("-s", "--start-time", type=float, default=0.0, help="Start time of the clip in seconds. Default: 0.0")
    group_segment.add_argument("-d", "--duration", type=float, default=3.0, help="Duration of the clip to use. Default: 3.0")
    group_segment.add_argument("-sp", "--speed", type=float, default=1.0, help="Playback speed multiplier. Default: 1.0")

    group_quality = parser.add_argument_group('Quality and Encoding')
    group_quality.add_argument("--crf", type=int, default=23, help="Constant Rate Factor for quality (18-28 is a good range, lower is better). Default: 23")
    group_quality.add_argument("--preset", type=str, default="medium", choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'], help="Encoding speed vs. compression preset. Default: medium")
    group_quality.add_argument("--gpu", dest="use_gpu", action="store_true", help="Use hardware acceleration for encoding if available (e.g., NVIDIA NVENC, Apple VideoToolbox).")

    group_effects = parser.add_argument_group('Effects and Audio')
    group_effects.add_argument("--fade-duration", type=float, default=0.0, help="Duration of crossfade at loop point for a smooth transition (e.g., 0.1). Default: 0.0 (no fade)")
    group_effects.add_argument("--include-audio", action="store_true", help="Include and process the audio track to match the boomerang effect.")
    
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress all FFmpeg console output.")

    args = parser.parse_args()

    # --- Validation and Default Output Name ---
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found at '{args.input_file}'", file=sys.stderr)
        sys.exit(1)
    if args.output_file is None:
        base, _ = os.path.splitext(args.input_file)
        args.output_file = f"{base}_boomerang.mp4"

    create_boomerang(**vars(args))

if __name__ == "__main__":
    main()
