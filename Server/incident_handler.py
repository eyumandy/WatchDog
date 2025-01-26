"""
incident_handler.py - Handles incident reporting and video caching for security events.
"""

import cv2
import os
import json
import asyncio
from datetime import datetime
from collections import deque
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class IncidentReport:
    incident_id: str
    timestamp: str
    threat_level: str
    violence_probability: float
    detected_objects: List[str]
    video_path: str
    analysis_data: Dict[str, Any]

class IncidentHandler:
    def __init__(self, 
                 save_dir: str,
                 pre_incident_frames: int = 150,  # 5 seconds at 30fps
                 post_incident_frames: int = 300,  # 10 seconds at 30fps
                 cooldown_frames: int = 450):     # 15 seconds at 30fps
        self.save_dir = save_dir
        self.pre_incident_frames = pre_incident_frames
        self.post_incident_frames = post_incident_frames
        self.cooldown_frames = cooldown_frames
        
        # Frame buffer and state
        self.frame_buffer = deque(maxlen=pre_incident_frames)
        self.post_incident_buffer = []
        self.recording = False
        self.frames_since_incident = 0
        self.current_incident = None
        
        # Ensure directories exist
        self.video_dir = os.path.join(save_dir, "incidents")
        os.makedirs(self.video_dir, exist_ok=True)
        
    def add_frame(self, frame: np.ndarray) -> None:
        """Add frame to buffer."""
        self.frame_buffer.append(frame.copy())
        
        if self.recording:
            self.post_incident_buffer.append(frame.copy())
            if len(self.post_incident_buffer) >= self.post_incident_frames:
                self._finalize_incident()
                
    async def start_incident(self, 
                           analysis_data: Dict[str, Any],
                           violence_prob: float) -> Optional[str]:
        """Start recording an incident if not in cooldown."""
        if self.recording or self.frames_since_incident < self.cooldown_frames:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        incident_id = f"incident_{timestamp}"
        
        self.current_incident = IncidentReport(
            incident_id=incident_id,
            timestamp=timestamp,
            threat_level=analysis_data.get('threat_level', 'UNKNOWN'),
            violence_probability=violence_prob,
            detected_objects=analysis_data.get('detected_objects', []),
            video_path=os.path.join(self.video_dir, f"{incident_id}.mp4"),
            analysis_data=analysis_data
        )
        
        self.recording = True
        self.post_incident_buffer = []
        return incident_id
        
    def _finalize_incident(self) -> None:
        """Save incident video and data."""
        if not self.current_incident:
            return
            
        # Combine pre and post incident frames
        all_frames = list(self.frame_buffer) + self.post_incident_buffer
        
        # Save video
        if all_frames:
            height, width = all_frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                self.current_incident.video_path, 
                fourcc, 
                30, 
                (width, height)
            )
            
            for frame in all_frames:
                out.write(frame)
            out.release()
            
        # Save metadata
        meta_path = os.path.join(
            self.save_dir, 
            f"{self.current_incident.incident_id}.json"
        )
        with open(meta_path, 'w') as f:
            json.dump({
                'incident_id': self.current_incident.incident_id,
                'timestamp': self.current_incident.timestamp,
                'threat_level': self.current_incident.threat_level,
                'violence_probability': self.current_incident.violence_probability,
                'detected_objects': self.current_incident.detected_objects,
                'video_path': self.current_incident.video_path,
                'analysis_data': self.current_incident.analysis_data
            }, f, indent=2)
            
        # Reset state
        self.recording = False
        self.frames_since_incident = 0
        self.current_incident = None
        self.post_incident_buffer = []