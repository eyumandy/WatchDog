"""
surveillance.py - Multi-stage security analysis system
"""

import cv2
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from motion_detection import MotionDetector, MotionConfig, MotionEvent
from cloud_vision import CloudVisionAnalyzer, ThreatLevel, SecurityAnalysis
import numpy as np
from rich.console import Console
from rich.theme import Theme

load_dotenv()
# Initialize rich console
console = Console(theme=Theme({
    "stage1": "cyan bold",
    "stage2": "yellow bold",
    "stage3": "red bold",
    "info": "blue",
    "alert": "red bold"
}))

class SurveillanceSystem:
    def __init__(self, 
                 credentials_path: str,
                 worker_url: str,
                 save_dir: str = "detected_events",
                 motion_config: MotionConfig = None):
        """Initialize surveillance system components."""
        console.print("\n[info]═══════════════════════════════════════")
        console.print("[info]    Surveillance System Initializing")
        console.print("[info]═══════════════════════════════════════")
        
        # Initialize with default or custom motion config
        self.motion_config = motion_config or MotionConfig(
            min_area=5000,
            learning_rate=0.5,
            detection_threshold=1200,
            temporal_window=1.5,
            accumulation_threshold= 250000,
            decay_rate=0.95
        )
        
        self.motion_detector = MotionDetector(self.motion_config)
        self.cloud_analyzer = CloudVisionAnalyzer(credentials_path)
        self.worker_url = worker_url
        self.save_dir = save_dir
        self.frame_buffer = []
        self.buffer_size = 30
        self.session = None
        
    async def initialize(self):
        self.session = aiohttp.ClientSession()
        console.print("[info]► Network session initialized")
        console.print("[info]═══════════════════════════════════════\n")

    async def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, bool]:
        # Update frame buffer
        self.frame_buffer.append(frame.copy())
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)

        # Stage 1: Motion Detection
        motion_event = self.motion_detector.detect(frame)
        if not motion_event:
            return frame, False
            
        if not motion_event.threshold_exceeded:
            return self.motion_detector.draw_debug(frame, motion_event), False

        console.print(f"\n[stage2]╔════ STAGE 2: INITIATING CLOUDFLARE ANALYSIS ════╗")
        
        # Stage 2: Cloudflare Worker Analysis
        worker_result = await self._analyze_with_worker(frame, motion_event)
        threat_score = worker_result.get('threat_score', 0)
        
        console.print(f"[stage2]║ Threat Score: {threat_score:.2f}")
        if not worker_result.get('suspicious', False):
            console.print(f"[stage2]╚════ Analysis Complete: No Further Action ════╝\n")
            return self.motion_detector.draw_debug(frame, motion_event), False

        # Stage 3: Full Cloud Vision Analysis
        if threat_score > 0.7:
            console.print(f"\n[stage3]╔════ STAGE 3: DEEP ANALYSIS REQUIRED ════╗")
            analysis = await self.cloud_analyzer.analyze_frame(frame)
            
            console.print(f"[stage3]║ Threat Level: {analysis.threat_level.name}")
            console.print(f"[stage3]║ Objects Detected: {', '.join(analysis.detected_objects)}")
            console.print(f"[stage3]║ Violence Likelihood: {analysis.violence_likelihood}")
            
            if analysis.threat_level != ThreatLevel.SAFE:
                await self._save_event(analysis)
                console.print(f"[alert]║ ⚠️  Security Alert: Potential Threat Detected")
                console.print(f"[stage3]╚════ Event Recorded and Saved ════╝\n")
                return self._annotate_frame(frame, analysis), True
            
            console.print(f"[stage3]╚════ Deep Analysis Complete: No Threat ════╝\n")
                
        return self.motion_detector.draw_debug(frame, motion_event), False
        
    async def _analyze_with_worker(self, frame: np.ndarray, motion: MotionEvent) -> dict:
        """Send frame to Cloudflare worker for initial analysis."""
        success, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()
        
        data = aiohttp.FormData()
        data.add_field('image', 
                      image_bytes,
                      filename='frame.jpg',
                      content_type='image/jpeg')
        
        motion_data = {
            'area': motion.area,
            'center': motion.center
        }
        data.add_field('motion_data', 
                      json.dumps(motion_data),
                      content_type='application/json')
        
        async with self.session.post(self.worker_url, data=data) as response:
            return await response.json()
            
    async def _save_event(self, analysis: SecurityAnalysis):
        """Save event information and video clip."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Save video clip
        video_path = os.path.join(self.save_dir, f"event_{timestamp}.mp4")
        height, width = self.frame_buffer[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 30, (width, height))
        
        for frame in self.frame_buffer:
            out.write(frame)
        out.release()
        
        # Save analysis results
        analysis_path = os.path.join(self.save_dir, f"event_{timestamp}.json")
        with open(analysis_path, 'w') as f:
            json.dump({
                'threat_level': analysis.threat_level.name,
                'detected_objects': analysis.detected_objects,
                'violence_likelihood': analysis.violence_likelihood,
                'weapon_likelihood': analysis.weapon_likelihood,
                'timestamp': timestamp
            }, f, indent=2)
            
    def _annotate_frame(self, frame: np.ndarray, analysis: SecurityAnalysis) -> np.ndarray:
        """Add analysis visualization to frame."""
        annotated = frame.copy()
        
        # Add threat level indicator
        color = {
            ThreatLevel.SAFE: (0, 255, 0),
            ThreatLevel.SUSPICIOUS: (0, 255, 255),
            ThreatLevel.DANGEROUS: (0, 0, 255)
        }[analysis.threat_level]
        
        cv2.putText(
            annotated,
            f"Threat Level: {analysis.threat_level.name}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )
        
        # List detected objects
        y_pos = 70
        for obj in analysis.detected_objects[:5]:  # Show top 5 objects
            cv2.putText(
                annotated,
                f"Detected: {obj}",
                (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )
            y_pos += 25
            
        return annotated

async def main():
    """Main execution function."""
    # Load configuration
    config = {
        'credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        'worker_url': os.getenv('CLOUDFLARE_WORKER_URL'),
        'save_dir': os.getenv('SAVE_DIR', 'detected_events')
    }
    
    # Initialize system
    system = SurveillanceSystem(**config)
    await system.initialize()
    
    try:
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            processed_frame, suspicious = await system.process_frame(frame)
            cv2.imshow('WatchDog Surveillance', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        await system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())