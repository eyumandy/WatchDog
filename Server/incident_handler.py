"""
incident_handler.py - Handles incident recording, face saving, and uploads to R2
"""

import cv2
import os
import json
from datetime import datetime
import numpy as np
from collections import deque
import boto3
from botocore.config import Config
from typing import Optional, Dict, Any
from rich.console import Console

console = Console()

class IncidentHandler:
    def __init__(self, 
                 save_dir: str,
                 r2_endpoint: str,
                 access_key_id: str,
                 access_key_secret: str,
                 bucket_name: str,
                 fps: int = 30):
        """
        Initialize the IncidentHandler.
        Manages pre-incident and post-incident frame buffers, video saving, face detection,
        and uploads to R2.
        """
        self.bucket_name = bucket_name
        self.fps = fps
        self.pre_frames = 5 * fps  # 5 seconds of pre-incident frames
        self.post_frames = 10 * fps  # 10 seconds of post-incident frames
        self.save_dir = save_dir
        
        self.pre_buffer = deque(maxlen=self.pre_frames)
        self.post_buffer = []
        self.recording = False
        self.current_incident = None
        
        # Initialize S3 client
        self.s3_client = boto3.client('s3',
            endpoint_url=r2_endpoint,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key_secret,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        
        # Ensure the save directory exists
        os.makedirs(save_dir, exist_ok=True)
        console.print("[info]IncidentHandler initialized. Ready to handle incidents.")

    def add_frame(self, frame: np.ndarray) -> None:
        """
        Adds a frame to the pre/post buffer depending on recording status.

        Args:
            frame (np.ndarray): The current video frame.
        """
        if self.recording:
            if len(self.post_buffer) < self.post_frames:
                self.post_buffer.append(frame.copy())
                frames_remaining = self.post_frames - len(self.post_buffer)
                if frames_remaining % self.fps == 0:
                    console.print(f"[info]Recording: {frames_remaining // self.fps} seconds remaining")
                
                if len(self.post_buffer) >= self.post_frames:
                    console.print("\n[stage3]╔════ RECORDING COMPLETE ════╗")
                    console.print(f"[stage3]║ 15 Seconds Captured")
                    console.print(f"[stage3]║ Processing Video...")
                    console.print(f"[stage3]╚════════════════════════════╝\n")
                    self._finalize_recording()
        else:
            self.pre_buffer.append(frame.copy())

    async def start_incident(self, analysis_data: Dict[str, Any], violence_prob: float) -> Optional[str]:
        """
        Starts an incident recording and creates necessary metadata.

        Args:
            analysis_data (Dict[str, Any]): Analysis results for the incident.
            violence_prob (float): Probability of violence in the detected frame.

        Returns:
            Optional[str]: The incident ID if recording starts, else None.
        """
        if self.recording:
            console.print("[alert]Incident already recording. Ignoring new request.")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        incident_id = f"incident_{timestamp}"
        
        console.print(f"\n[stage3]╔════ STARTING INCIDENT RECORDING ════╗")
        console.print(f"[stage3]║ Incident ID: {incident_id}")
        console.print(f"[stage3]║ Recording 15 seconds total:")
        console.print(f"[stage3]║ • 5 seconds pre-incident")
        console.print(f"[stage3]║ • 10 seconds post-incident")
        console.print(f"[stage3]╚═══════════════════════════════════════╝\n")
        
        self.current_incident = {
            'incident_id': incident_id,
            'timestamp': timestamp,
            'violence_probability': violence_prob,
            'analysis': analysis_data
        }
        
        self.recording = True
        self.post_buffer = []

        # Create incident folder
        incident_path = os.path.join(self.save_dir, incident_id)
        os.makedirs(incident_path, exist_ok=True)
        os.makedirs(os.path.join(incident_path, "people"), exist_ok=True)
        
        # Save metadata
        metadata = {
            "incident_id": incident_id,
            "upload_date": datetime.now().isoformat(),
        }
        metadata_path = os.path.join(incident_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)
        console.print(f"[info]Metadata saved: {metadata_path}")
        
        return incident_id

    def _capture_faces(self, frame: np.ndarray, incident_id: str) -> None:
        """
        Detects faces in a frame and saves them to the 'people' folder for the incident.

        Args:
            frame (np.ndarray): The video frame.
            incident_id (str): The ID of the current incident.
        """
        incident_path = os.path.join(self.save_dir, incident_id, "people")
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        console.print(f"[info]► Detected {len(faces)} faces in frame for Incident ID: {incident_id}")

        for i, (x, y, w, h) in enumerate(faces, start=1):
            face_img = frame[y:y+h, x:x+w]
            face_filename = os.path.join(incident_path, f"person_{i}.jpg")
            cv2.imwrite(face_filename, face_img)
            console.print(f"[info]Face saved: {face_filename}")

    def _finalize_recording(self) -> None:
        """
        Finalizes recording, saves video, captures faces, and uploads to R2.
        """
        try:
            if not self.current_incident:
                console.print("[alert]No current incident to process")
                return
                
            # Prepare video frames
            console.print("[info]Step 1: Preparing frames for processing...")
            all_frames = list(self.pre_buffer) + self.post_buffer
            height, width = all_frames[0].shape[:2]
            
            incident_id = self.current_incident["incident_id"]
            incident_path = os.path.join(self.save_dir, incident_id)
            video_path = os.path.join(incident_path, "video.mp4")
            
            # Write video to file
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(video_path, fourcc, self.fps, (width, height))
            for frame in all_frames:
                writer.write(frame)
            writer.release()
            console.print(f"[info]Video saved: {video_path}")
            
            # Upload video to R2
            key = f'incidents/{incident_id}/video.mp4'
            console.print(f"[info]Uploading video to R2: {key}")
            self.s3_client.upload_file(video_path, self.bucket_name, key, ExtraArgs={'ContentType': 'video/mp4'})
            console.print("[info]Upload to R2 completed successfully!")
            
            self.recording = False
            self.current_incident = None
            self.post_buffer = []
        except Exception as e:
            console.print(f"[alert]Error during recording finalization: {e}")
            raise
