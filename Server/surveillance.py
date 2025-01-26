"""
surveillance.py - Multi-stage security analysis system with AI-powered violence detection,
incident reporting, and enhanced face detection with metadata storage.
"""

import cv2
import asyncio
import aiohttp
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from motion_detection import MotionDetector, MotionConfig, MotionEvent
from model_inference import ViolenceDetector
from incident_handler import IncidentHandler
import numpy as np
from rich.console import Console
from rich.theme import Theme
from typing import Tuple, Optional

# Load environment variables
load_dotenv()

console = Console(theme=Theme({
    "stage1": "cyan bold",
    "stage2": "yellow bold",
    "stage3": "red bold",
    "info": "blue",
    "alert": "red bold",
    "metric": "green"
}))

class SurveillanceSystem:
    def __init__(self, 
                 worker_url: str,
                 model_path: str,
                 save_dir: str = "detected_events",
                 motion_config: Optional[MotionConfig] = None,
                 r2_config: Optional[dict] = None):
        console.print("\n[info]═══════════════════════════════════════")
        console.print("[info]    Surveillance System Initializing")
        console.print("[info]═══════════════════════════════════════")

        self.motion_config = motion_config or MotionConfig(
            min_area=5000,
            learning_rate=0.5,
            detection_threshold=1200,
            temporal_window=1.5,
            accumulation_threshold=250000,
            decay_rate=0.95
        )

        self.motion_detector = MotionDetector(self.motion_config)
        self.violence_detector = ViolenceDetector(model_path)
        self.worker_url = worker_url
        self.save_dir = save_dir
        self.session = None

        # Initialize incident handler with R2 config
        self.incident_handler = IncidentHandler(
            save_dir=save_dir,
            r2_endpoint=r2_config['endpoint'],
            access_key_id=r2_config['access_key_id'],
            access_key_secret=r2_config['access_key_secret'],
            bucket_name=r2_config['bucket_name']
        )

        os.makedirs(save_dir, exist_ok=True)

        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    async def initialize(self):
        self.session = aiohttp.ClientSession()
        console.print("[info]► Network session initialized")
        console.print("[info]═══════════════════════════════════════\n")

    async def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, bool]:
        # Add frame to incident handler buffer
        self.incident_handler.add_frame(frame)

        # If currently recording, just return the annotated frame
        if self.incident_handler.recording:
            return self._annotate_frame(frame, self.incident_handler.current_incident['violence_probability']), True

        # Stage 1: Motion Detection
        motion_event = self.motion_detector.detect(frame)
        if not motion_event or not motion_event.threshold_exceeded:
            return frame if not motion_event else self.motion_detector.draw_debug(frame, motion_event), False

        # Stage 2: AI Analysis
        console.print(f"\n[stage2]╔════ STAGE 2: AI MODEL ANALYSIS ════╗")
        is_violent, violence_prob = self.violence_detector.predict(frame)
        console.print(f"[stage2]║ Violence Probability: {violence_prob:.2f}")

        if not is_violent:
            console.print(f"[stage2]╚════ Analysis Complete: No Further Action ════╝\n")
            return self.motion_detector.draw_debug(frame, motion_event), False

        # Stage 3: Incident Recording
        if violence_prob > 0.7:
            incident_id = await self.incident_handler.start_incident(
                {
                    'detected_activity': 'Violent behavior',
                    'confidence': violence_prob,
                    'motion_data': {
                        'area': motion_event.area,
                        'center': motion_event.center,
                        'accumulated_motion': motion_event.accumulated_motion
                    }
                },
                violence_prob
            )

            # Capture face images
            self._capture_faces(frame, incident_id)
            return self._annotate_frame(frame, violence_prob), True

        return self.motion_detector.draw_debug(frame, motion_event), False
    
    def _annotate_frame(self, frame: np.ndarray, violence_prob: float) -> np.ndarray:
        """
        Annotate the frame with violence probability.
        """
        annotated = frame.copy()
        color = (0, 0, 255) if violence_prob > 0.7 else (0, 255, 255)

        cv2.putText(
            annotated,
            f"Violence Probability: {violence_prob:.2f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )

        return annotated
    
    def _capture_faces(self, frame: np.ndarray, incident_id: str) -> None:
        """
        Detect faces in the given frame and save them to the incident folder.
        """
        incident_path = os.path.join(self.save_dir, incident_id)
        faces_path = os.path.join(incident_path, 'faces')
        os.makedirs(faces_path, exist_ok=True)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        console.print(f"[info]► Detected {len(faces)} faces in incident frame.")

        for i, (x, y, w, h) in enumerate(faces):
            face_img = frame[y:y+h, x:x+w]
            face_filename = os.path.join(faces_path, f"face_{i + 1}.jpg")
            cv2.imwrite(face_filename, face_img)

    async def upload_to_r2(self, incident_id: str, video_path: str):
        """
        Upload video and metadata to R2 and store metadata in Cloudflare D1 SQL database.
        """
        try:
            # Metadata
            metadata = {
                "incident_id": incident_id,
                "upload_date": datetime.now().isoformat(),
                "video_path": video_path
            }

            # Save metadata locally
            metadata_path = os.path.join(self.save_dir, incident_id, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)

            # Upload to R2
            console.print("[info]Uploading video and metadata to R2...")
            await self.incident_handler.upload_video_and_metadata(video_path, metadata_path)

            # Insert metadata into Cloudflare D1
            await self.store_metadata_in_d1(metadata)

        except Exception as e:
            console.print(f"[alert]Error during upload: {str(e)}")

    async def store_metadata_in_d1(self, metadata: dict):
        """
        Store metadata in Cloudflare D1 SQL database.
        """
        try:
            query = """
            INSERT INTO incidents (incident_id, upload_date, video_path)
            VALUES (?, ?, ?);
            """
            payload = {
                "sql": query,
                "bindings": [
                    {"name": "incident_id", "value": metadata["incident_id"]},
                    {"name": "upload_date", "value": metadata["upload_date"]},
                    {"name": "video_path", "value": metadata["video_path"]}
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.worker_url,
                    json=payload,
                    headers={"Authorization": f"Bearer {os.getenv('Token')}"}
                ) as response:
                    if response.status == 200:
                        console.print("[info]Metadata successfully stored in D1 database.")
                    else:
                        console.print(f"[alert]Failed to store metadata in D1: {response.status}")
                        console.print(await response.text())

        except Exception as e:
            console.print(f"[alert]Error while storing metadata in D1: {str(e)}")



async def cleanup(self):
    if self.session:
        await self.session.close()
