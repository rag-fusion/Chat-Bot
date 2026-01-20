import sys
import subprocess

def check_whisper():
    print("Checking openai-whisper...")
    try:
        import whisper
        print("✅ openai-whisper is installed.")
    except ImportError:
        print("❌ openai-whisper is NOT installed.")
        return False
    return True

def check_ffmpeg():
    print("Checking ffmpeg...")
    try:
        # Try running ffmpeg -version
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("✅ ffmpeg is available in PATH.")
    except FileNotFoundError:
        print("❌ ffmpeg is NOT found in PATH. Whisper requires ffmpeg.")
        return False
    except Exception as e:
        print(f"❌ Error checking ffmpeg: {e}")
        return False
    return True

if __name__ == "__main__":
    w = check_whisper()
    f = check_ffmpeg()
    
    if w and f:
        print("\n🎉 All audio dependencies look good!")
    else:
        print("\n⚠️ Some dependencies are missing. Audio transcription might not work.")
