"""
setup.py - Dataset preprocessing for ResNet-50 fine-tuning
"""

import os
import subprocess
import json
import time
from pathlib import Path
import cv2
from tqdm import tqdm
import numpy as np
from sklearn.model_selection import train_test_split
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
import shutil

# --------------------------------------------------------------------------------
# DatasetSetup class is responsible for:
#  1. Extracting frames from violence and non-violence videos at a defined sample rate.
#  2. Creating train, validation, and test splits from the extracted frames.
#  3. Logging all the relevant information and storing splits in a JSON file.
# --------------------------------------------------------------------------------

console = Console()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('setup.log'), logging.StreamHandler()])

class DatasetSetup:
    def __init__(self):
        # Base paths for input videos and output frames/models
        self.base_path = Path("Real Life Violence Dataset")
        self.frames_path = Path("frames")
        self.models_path = Path("models")
        self.logger = logging.getLogger(__name__)

    def extract_frames(self, sample_rate=5):
        """
        Extract frames from videos at a specified sample_rate.
        For each video in 'Violence' or 'NonViolence' folder, 
        frames are saved every 'sample_rate' frames.
        """
        self.logger.info("Starting frame extraction...")
        os.makedirs(self.frames_path, exist_ok=True)

        total_processed = 0
        start_time = time.time()

        try:
            # Loop through the two classes in the dataset
            for class_name in ['Violence', 'NonViolence']:
                video_path = self.base_path / class_name
                # Ensuring our directories match later usage ('violence' or 'nonviolence')
                frames_class_path = self.frames_path / (
                    'violence' if class_name == 'Violence' else 'nonviolence'
                )
                os.makedirs(frames_class_path, exist_ok=True)

                videos = list(video_path.glob('*.mp4'))
                self.logger.info(f"Processing {len(videos)} {class_name} videos...")

                # Use rich progress to visually track progress in the console
                with Progress(SpinnerColumn(),
                              *Progress.get_default_columns(),
                              TimeElapsedColumn(),
                              console=console) as progress:
                    task = progress.add_task(
                        f"[cyan]Processing {class_name} videos...",
                        total=len(videos)
                    )

                    # Process each video file
                    for video_file in videos:
                        frames_extracted = self._process_video(
                            video_file,
                            frames_class_path,
                            sample_rate
                        )
                        total_processed += frames_extracted
                        progress.advance(task)

            elapsed = time.time() - start_time
            self.logger.info(f"Frame extraction complete: {total_processed} frames in {elapsed:.2f}s")

        except Exception as e:
            self.logger.error(f"Frame extraction failed: {str(e)}")
            raise

    def _process_video(self, video_file: Path, output_path: Path, sample_rate: int) -> int:
        """
        Internal helper method to read a video file frame by frame,
        resize each frame, and save it every 'sample_rate' frames.
        """
        frames_extracted = 0
        cap = cv2.VideoCapture(str(video_file))
        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % sample_rate == 0:
                    # Resize frame to 224x224 as per standard ResNet input size
                    frame = cv2.resize(frame, (224, 224))
                    save_path = output_path / f"{video_file.stem}_{frame_count}.jpg"
                    cv2.imwrite(str(save_path), frame)
                    frames_extracted += 1

                frame_count += 1
        finally:
            cap.release()

        return frames_extracted

    def create_dataset_splits(self):
        """
        Create train, validation, and test splits from the extracted frames.
        Splits are stored in models/splits.json for downstream usage.
        """
        self.logger.info("Creating dataset splits...")

        try:
            data = []
            labels = []

            # --------------------------------------------------------------------------------
            # IMPORTANT FIX:
            # Ensure the class names here match the frame directory names created above.
            # We changed 'non-violence' to 'nonviolence' for consistency.
            # --------------------------------------------------------------------------------
            for class_id, class_name in enumerate(['violence', 'nonviolence']):
                frame_paths = list((self.frames_path / class_name).glob('*.jpg'))
                self.logger.info(f"Found {len(frame_paths)} frames for {class_name}")
                data.extend(frame_paths)
                labels.extend([class_id] * len(frame_paths))

            # Split 30% off for validation/test, then split that half-and-half for val/test
            X_train, X_temp, y_train, y_temp = train_test_split(
                data, labels, test_size=0.3, random_state=42
            )
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=0.5, random_state=42
            )

            splits = {
                'train': list(zip(X_train, y_train)),
                'val': list(zip(X_val, y_val)),
                'test': list(zip(X_test, y_test))
            }

            os.makedirs(self.models_path, exist_ok=True)
            with open(self.models_path / 'splits.json', 'w') as f:
                # Convert Paths to strings before dumping to JSON
                json.dump({
                    k: [(str(x), y) for x, y in v]
                    for k, v in splits.items()
                }, f)

            self.logger.info(
                f"Splits created: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}"
            )

        except Exception as e:
            self.logger.error(f"Failed to create dataset splits: {str(e)}")
            raise

    def setup(self):
        """
        Orchestrates the entire setup process:
         1. Extract frames from violence and non-violence videos.
         2. Create training, validation, and test splits.
        """
        console.print("\n[bold cyan]═══ Starting Dataset Setup Process ═══")

        try:
            for func, description in [
                (self.extract_frames, "Extracting Frames"),
                (self.create_dataset_splits, "Creating Data Splits")
            ]:
                console.print(f"[bold green]{description}...")
                func()

            console.print("[bold green]Setup completed successfully!")

        except Exception as e:
            console.print(f"[bold red]Setup failed: {str(e)}")
            raise

if __name__ == "__main__":
    setup = DatasetSetup()
    setup.setup()
