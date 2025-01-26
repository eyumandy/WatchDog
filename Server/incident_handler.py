"""
incident_handler.py - Handles incident recording and worker-based uploading
"""

import cv2
import os
import numpy as np
from collections import deque
import asyncio
import aiohttp
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
        self.presign_url_endpoint = f"{r2_endpoint}/get-presigned-url"
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.bucket_name = bucket_name
        self.fps = fps
        
        self.pre_frames = 5 * fps  # 5 seconds pre-incident
        self.post_frames = 10 * fps  # 10 seconds post-incident
        
        self.pre_buffer = deque(maxlen=self.pre_frames)
        self.post_buffer = []
        self.recording = False
        self.current_incident = None
        
    def add_frame(self, frame: np.ndarray) -> None:
        if self.recording:
            if len(self.post_buffer) < self.post_frames:
                self.post_buffer.append(frame.copy())
                frames_remaining = self.post_frames - len(self.post_buffer)
                if frames_remaining % self.fps == 0:  # Log every second
                    console.print(f"[info]Recording: {frames_remaining//self.fps} seconds remaining")
                
                if len(self.post_buffer) >= self.post_frames:
                    console.print("\n[stage3]╔════ RECORDING COMPLETE ════╗")
                    console.print(f"[stage3]║ 15 Seconds Captured")
                    console.print(f"[stage3]║ Processing Video...")
                    console.print(f"[stage3]╚════════════════════════════╝\n")
                    asyncio.create_task(self._finalize_recording())
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

    async def _finalize_recording(self) -> None:
        """Compile video and upload via presigned URL."""
        try:
            if not self.current_incident:
                console.print("[alert]No current incident to process")
                return
                
            console.print("[info]Step 1: Preparing frames for processing...")
            all_frames = list(self.pre_buffer) + self.post_buffer
            height, width = all_frames[0].shape[:2]
            console.print(f"[info]Total frames to process: {len(all_frames)}")
            
            # STEP 2: Initialize video writer
            console.print("[info]Step 2: Initializing video writer...")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter('temp.mp4', fourcc, self.fps, (width, height))
            
            console.print("[info]Step 3: Writing frames to video file...")
            for i, frame in enumerate(all_frames, start=1):
                writer.write(frame)
                if i % 30 == 0:  # Log every second worth of frames
                    console.print(f"[info]Processed {i}/{len(all_frames)} frames")
            writer.release()
            console.print(f"[info]Video writer released after writing {len(all_frames)} frames")
            
            # STEP 4: Read video file into memory
            console.print("[info]Step 4: Reading video file into memory...")
            with open('temp.mp4', 'rb') as f:
                video_bytes = f.read()
            file_size_mb = len(video_bytes) / (1024 * 1024)
            console.print(f"[info]Video file size: {file_size_mb:.2f} MB")
            
            # Cleanup local file
            console.print("[info]Step 5: Cleaning up temporary file...")
            os.remove('temp.mp4')
            
            # STEP 6: Request a presigned URL from the Worker
            console.print("[info]Step 6: Requesting presigned URL...")
            incident_id = self.current_incident["incident_id"]
            async with aiohttp.ClientSession() as session:
                # Post JSON to /get-presigned-url
                response = await session.post(
                    self.presign_url_endpoint,
                    json={"incidentId": incident_id}
                )
                if response.status != 200:
                    console.print(f"[alert]Failed to retrieve presigned URL; status={response.status}")
                    console.print(f"[alert]Response: {await response.text()}")
                    return
                
                presign_data = await response.json()
                upload_url = presign_data["uploadUrl"]
                console.print(f"[info]Got presigned URL. Key = {presign_data['key']}")
            
            # STEP 7: PUT the video bytes directly to R2 using the presigned URL
            console.print("[info]Step 7: Uploading file via presigned URL...")
            async with aiohttp.ClientSession() as session:
                put_headers = {
                    "Content-Type": "video/mp4"
                }
                put_resp = await session.put(upload_url, data=video_bytes, headers=put_headers)
                if put_resp.status != 200 and put_resp.status != 201:
                    console.print(f"[alert]Presigned PUT failed; status={put_resp.status}")
                    console.print(f"[alert]Response: {await put_resp.text()}")
                else:
                    console.print("[info]Upload successful via presigned URL!")
            
            # STEP 8: Cleanup
            console.print("[info]Step 8: Final cleanup and state reset...")
            self.recording = False
            self.current_incident = None
            self.post_buffer = []
            console.print("[info]Recording process completed successfully!\n")
            
        except Exception as e:
            console.print(f"[alert]Error during recording finalization: {str(e)}")
            import traceback
            console.print(f"[alert]{traceback.format_exc()}")
            raise