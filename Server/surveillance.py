"""
surveillance.py - Multi-stage security analysis system with AI-powered violence detection
and incident reporting.
"""

import cv2
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from datetime import datetime
from motion_detection import MotionDetector, MotionConfig, MotionEvent
from model_inference import ViolenceDetector
from incident_handler import IncidentHandler
import numpy as np
from rich.console import Console
from rich.theme import Theme
from typing import Tuple, Optional

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
            
            return self._annotate_frame(frame, violence_prob), True
            
        return self.motion_detector.draw_debug(frame, motion_event), False
        
    def _annotate_frame(self, frame: np.ndarray, violence_prob: float) -> np.ndarray:
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

    async def cleanup(self):
        if self.session:
            await self.session.close()

async def main():
    config = {
        'worker_url': os.getenv('CLOUDFLARE_WORKER_URL'),
        'model_path': os.path.join(os.path.dirname(__file__), '../models/best_model.pth'),
        'save_dir': os.getenv('SAVE_DIR', 'detected_events'),
        'r2_config': {
            'endpoint': os.getenv('R2_ENDPOINT'),
            'access_key_id': os.getenv('R2_ACCESS_KEY_ID'),
            'access_key_secret': os.getenv('R2_ACCESS_KEY_SECRET'),
            'bucket_name': os.getenv('R2_BUCKET_NAME')
        }
    }
    
    system = SurveillanceSystem(**config)
    await system.initialize()
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Failed to open camera")
            
        console.print("[info]Camera initialized successfully")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                console.print("[alert]Failed to read frame")
                break
                
            processed_frame, suspicious = await system.process_frame(frame)
            cv2.imshow('WatchDog Surveillance', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        console.print(f"[alert]Error: {str(e)}")
        
    finally:
        cap.release()
        cv2.destroyAllWindows()
        await system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())