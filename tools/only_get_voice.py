import os
from pydub import AudioSegment

def extract_audio(video_dir):
    """
    Extract audio from all video files in the specified directory
    Save as MP3 with the same name as the video file, removing last 4 seconds
    """
    # Get all files in the directory
    files = os.listdir(video_dir)
    
    # Process each video file
    for file in files:
        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):  # Add more video formats if needed
            try:
                video_path = os.path.join(video_dir, file)
                # Get filename without extension
                filename = os.path.splitext(file)[0]
                # Output audio path
                audio_path = os.path.join(video_dir, f"{filename}.mp3")
                
                # Extract audio
                audio = AudioSegment.from_file(video_path)
                # # Remove last 4 seconds (4000 milliseconds)
                # audio = audio[:-4000]
                audio.export(audio_path, format="mp3")
                
                print(f"Successfully extracted audio from: {file}")
                
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")

if __name__ == "__main__":
    video_directory = r"E:\git_repo\xiaozhi-self-deploy\video"
    extract_audio(video_directory)
