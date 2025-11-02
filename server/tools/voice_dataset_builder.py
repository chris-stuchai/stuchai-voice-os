"""
Voice Dataset Builder Tool.

Provides script to record or upload voice samples and format dataset for Coqui TTS.
Includes future auto-train pipeline stub.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional
import zipfile
import json

from shared.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceDatasetBuilder:
    """
    Voice dataset builder for Coqui TTS training.
    
    Handles:
    - Recording voice samples
    - Uploading existing audio files
    - Formatting dataset structure
    - Preparing for training
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize dataset builder.
        
        Args:
            output_dir: Output directory for dataset
        """
        self.output_dir = Path(output_dir or settings.VOICE_DATASET_PATH)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.samples_dir = self.output_dir / "samples"
        self.samples_dir.mkdir(exist_ok=True)
    
    def record_samples(self, voice_name: str, count: int = 10) -> None:
        """
        Record voice samples interactively.
        
        Args:
            voice_name: Name of the voice
            count: Number of samples to record
        """
        logger.info(f"Recording {count} samples for voice: {voice_name}")
        
        voice_dir = self.samples_dir / voice_name
        voice_dir.mkdir(exist_ok=True)
        
        try:
            import pyaudio
            import wave
            
            # Audio recording settings
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 22050
            RECORD_SECONDS = 5
            
            audio = pyaudio.PyAudio()
            
            for i in range(count):
                print(f"\nRecording sample {i+1}/{count}")
                print("Press Enter to start recording...")
                input()
                
                stream = audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                )
                
                print(f"Recording for {RECORD_SECONDS} seconds...")
                frames = []
                
                for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    frames.append(data)
                
                stream.stop_stream()
                stream.close()
                
                # Save audio file
                output_file = voice_dir / f"sample_{i+1:03d}.wav"
                wf = wave.open(str(output_file), 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                print(f"Saved: {output_file}")
            
            audio.terminate()
            logger.info(f"Recording complete. Samples saved to {voice_dir}")
        
        except ImportError:
            logger.error("pyaudio not installed. Install with: pip install pyaudio")
            logger.info("Falling back to file upload mode")
    
    def upload_samples(self, voice_name: str, audio_files: List[str]) -> None:
        """
        Upload existing audio files.
        
        Args:
            voice_name: Name of the voice
            audio_files: List of audio file paths
        """
        logger.info(f"Uploading {len(audio_files)} samples for voice: {voice_name}")
        
        voice_dir = self.samples_dir / voice_name
        voice_dir.mkdir(exist_ok=True)
        
        for i, file_path in enumerate(audio_files):
            source = Path(file_path)
            if not source.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            dest = voice_dir / f"sample_{i+1:03d}{source.suffix}"
            
            # Copy file
            import shutil
            shutil.copy2(source, dest)
            logger.info(f"Copied: {source} -> {dest}")
        
        logger.info(f"Upload complete. Samples saved to {voice_dir}")
    
    def format_dataset(self, voice_name: str) -> dict:
        """
        Format dataset for Coqui TTS training.
        
        Creates metadata.json with transcriptions and file mappings.
        
        Args:
            voice_name: Name of the voice
            
        Returns:
            dict: Dataset metadata
        """
        voice_dir = self.samples_dir / voice_name
        if not voice_dir.exists():
            raise ValueError(f"Voice directory not found: {voice_dir}")
        
        # Find all audio files
        audio_files = sorted(list(voice_dir.glob("*.wav")) + list(voice_dir.glob("*.mp3")))
        
        if not audio_files:
            raise ValueError(f"No audio files found in {voice_dir}")
        
        # Create metadata structure
        metadata = {
            "voice_name": voice_name,
            "samples": [],
            "total_duration": 0,
            "sample_rate": 22050,
            "format": "wav"
        }
        
        logger.info(f"Formatting {len(audio_files)} samples...")
        
        # For each file, create entry (user will need to add transcriptions)
        for audio_file in audio_files:
            entry = {
                "file": str(audio_file.name),
                "text": "",  # User needs to add transcription
                "duration": 0  # Will be calculated
            }
            metadata["samples"].append(entry)
        
        # Save metadata
        metadata_file = voice_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Dataset formatted. Metadata saved to {metadata_file}")
        logger.info("Please add transcriptions to metadata.json before training")
        
        return metadata
    
    def prepare_training(self, voice_name: str) -> dict:
        """
        Prepare dataset for training (stub for future auto-train pipeline).
        
        Args:
            voice_name: Name of the voice
            
        Returns:
            dict: Training configuration
        """
        voice_dir = self.samples_dir / voice_name
        metadata_file = voice_dir / "metadata.json"
        
        if not metadata_file.exists():
            raise ValueError(f"Metadata not found. Run format_dataset first.")
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Validate transcriptions
        missing_transcriptions = [
            s["file"] for s in metadata["samples"]
            if not s.get("text") or len(s["text"].strip()) == 0
        ]
        
        if missing_transcriptions:
            raise ValueError(
                f"Missing transcriptions for: {', '.join(missing_transcriptions)}"
            )
        
        # Create training config
        training_config = {
            "voice_name": voice_name,
            "dataset_path": str(voice_dir),
            "output_path": str(self.output_dir / "models" / voice_name),
            "config": {
                "epochs": 100,
                "batch_size": 16,
                "learning_rate": 0.001
            }
        }
        
        # Save training config
        config_file = voice_dir / "training_config.json"
        with open(config_file, 'w') as f:
            json.dump(training_config, f, indent=2)
        
        logger.info(f"Training configuration saved to {config_file}")
        logger.info("Ready for training (auto-train pipeline coming soon)")
        
        return training_config


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Voice Dataset Builder for Coqui TTS"
    )
    parser.add_argument(
        "command",
        choices=["record", "upload", "format", "prepare"],
        help="Command to execute"
    )
    parser.add_argument(
        "--voice-name",
        required=True,
        help="Name of the voice"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of samples to record (for record command)"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Audio files to upload (for upload command)"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for dataset"
    )
    
    args = parser.parse_args()
    
    builder = VoiceDatasetBuilder(output_dir=args.output_dir)
    
    if args.command == "record":
        builder.record_samples(args.voice_name, args.count)
    elif args.command == "upload":
        if not args.files:
            logger.error("--files required for upload command")
            sys.exit(1)
        builder.upload_samples(args.voice_name, args.files)
    elif args.command == "format":
        builder.format_dataset(args.voice_name)
    elif args.command == "prepare":
        builder.prepare_training(args.voice_name)


if __name__ == "__main__":
    main()

