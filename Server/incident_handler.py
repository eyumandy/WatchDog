"""
incident_handler.py - Handles incident recording and direct R2 uploads
"""

import cv2
import os
import numpy as np
from collections import deque
import boto3
from botocore.config import Config
from typing import Optional, Dict, Any
from datetime import datetime
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
        self.bucket_name = bucket_name
        self.fps = fps
        self.pre_frames = 5 * fps
        self.post_frames = 10 * fps
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
        
        os.makedirs(save_dir, exist_ok=True)
        
    def add_frame(self, frame: np.ndarray) -> None:
        if self.recording:
            if len(self.post_buffer) < self.post_frames:
                self.post_buffer.append(frame.copy())
                frames_remaining = self.post_frames - len(self.post_buffer)
                if frames_remaining % self.fps == 0:
                    console.print(f"[info]Recording: {frames_remaining//self.fps} seconds remaining")
                
                if len(self.post_buffer) >= self.post_frames:
                    console.print("\n[stage3]╔════ RECORDING COMPLETE ════╗")
                    console.print(f"[stage3]║ 15 Seconds Captured")
                    console.print(f"[stage3]║ Processing Video...")
                    console.print(f"[stage3]╚════════════════════════════╝\n")
                    self._finalize_recording()
        else:
            self.pre_buffer.append(frame.copy())
    
    async def start_incident(self, analysis_data: Dict[str, Any], violence_prob: float) -> Optional[str]:
        if self.recording:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        incident_id = f"incident_{timestamp}"
        
        console.print(f"\n[stage3]╔════ STARTING INCIDENT RECORDING ════╗")
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
        return incident_id

    def _finalize_recording(self) -> None:
        """Compile video and upload directly to R2."""
        try:
            if not self.current_incident:
                console.print("[alert]No current incident to process")
                return
                
            # Process frames
            console.print("[info]Step 1: Preparing frames for processing...")
            all_frames = list(self.pre_buffer) + self.post_buffer
            height, width = all_frames[0].shape[:2]
            
            # Create video file
            temp_path = os.path.join(self.save_dir, 'temp.mp4')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(temp_path, fourcc, self.fps, (width, height))
            
            for i, frame in enumerate(all_frames, start=1):
                writer.write(frame)
                if i % 30 == 0:
                    console.print(f"[info]Processed {i}/{len(all_frames)} frames")
            writer.release()
            
            # Upload to R2
            incident_id = self.current_incident["incident_id"]
            key = f'incidents/{incident_id}.mp4'
            
            console.print("[info]Uploading to R2...")
            self.s3_client.upload_file(
                temp_path,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            
            # Cleanup
            os.remove(temp_path)
            self.recording = False
            self.current_incident = None
            self.post_buffer = []
            console.print("[info]Recording process completed successfully!\n")
            
        except Exception as e:
            console.print(f"[alert]Error during recording finalization: {str(e)}")
            import traceback
            console.print(f"[alert]{traceback.format_exc()}")
            raise