"""
surveillance.py - Multi-stage security analysis system with AI-powered violence detection
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
from model_inference import ViolenceDetector
import numpy as np
from rich.console import Console
from rich.theme import Theme
from typing import Tuple, Optional, Dict, Any

load_dotenv()

# Initialize rich console with custom theme
console = Console(theme=Theme({
    "stage1": "cyan bold",
    "stage2": "yellow bold",
    "stage3": "red bold",
    "info": "blue",
    "alert": "red bold",
    "metric": "green"
}))

class SurveillanceSystem:
    """
    Multi-stage surveillance system with motion detection, AI analysis, and threat assessment.
    
    Features:
    - Motion detection with temporal analysis
    - AI-powered violence detection
    - Cloud-based object and activity recognition
    - Multi-stage threat assessment pipeline
    - Event recording and analysis
    """
    
    def __init__(self, 
                 credentials_path: str,
                 worker_url: str,
                 model_path: str,
                 save_dir: str = "detected_events",
                 motion_config: Optional[MotionConfig] = None):
        """
        Initialize surveillance system components.
        
        Args:
            credentials_path: Path to Google Cloud credentials
            worker_url: Cloudflare worker endpoint URL
            model_path: Path to fine-tuned ResNet model
            save_dir: Directory to save detected events
            motion_config: Optional motion detection configuration
        """
        console.print("\n[info]═══════════════════════════════════════")
        console.print("[info]    Surveillance System Initializing")
        console.print("[info]═══════════════════════════════════════")
        
        # Initialize with default or custom motion config
        self.motion_config = motion_config or MotionConfig(
            min_area=5000,
            learning_rate=0.5,
            detection_threshold=1200,
            temporal_window=1.5,
            accumulation_threshold=250000,
            decay_rate=0.95
        )
        
        # Initialize components
        self.motion_detector = MotionDetector(self.motion_config)
        self.cloud_analyzer = CloudVisionAnalyzer(credentials_path)
        self.violence_detector = ViolenceDetector(model_path)
        
        # System configuration
        self.worker_url = worker_url
        self.save_dir = save_dir
        self.frame_buffer = []
        self.buffer_size = 30  # ~1 second at 30fps
        self.session = None
        
        # Ensure save directory exists
        os.makedirs(save_dir, exist_ok=True)
        
    async def initialize(self):
        """Initialize network session and other async components."""
        self.session = aiohttp.ClientSession()
        console.print("[info]► Network session initialized")
        console.print("[info]═══════════════════════════════════════\n")

    async def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Process a single frame through all analysis stages.
        
        Args:
            frame: Input video frame
            
        Returns:
            Tuple of (processed_frame, is_suspicious)
        """
        # Update frame buffer for event recording
        self.frame_buffer.append(frame.copy())
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)

        # Stage 1: Motion Detection
        motion_event = self.motion_detector.detect(frame)
        if not motion_event:
            return frame, False
            
        if not motion_event.threshold_exceeded:
            return self.motion_detector.draw_debug(frame, motion_event), False

        # Stage 2: AI Analysis
        console.print(f"\n[stage2]╔════ STAGE 2: AI MODEL ANALYSIS ════╗")
        
        # Violence Detection
        is_violent, violence_prob = self.violence_detector.predict(frame)
        console.print(f"[stage2]║ Violence Probability: {violence_prob:.2f}")
        
        if is_violent:
            console.print(f"[alert]║ ⚠️  Violence Detected!")

        # Stage 3: Deep Analysis
        if violence_prob > 0.7:
            console.print(f"\n[stage3]╔════ STAGE 3: DEEP ANALYSIS REQUIRED ════╗")
            analysis = await self.cloud_analyzer.analyze_frame(frame)
            
            console.print(f"[stage3]║ Threat Level: {analysis.threat_level.name}")
            console.print(f"[stage3]║ Objects Detected: {', '.join(analysis.detected_objects)}")
            console.print(f"[stage3]║ Violence Likelihood: {analysis.violence_likelihood}")
            
            if analysis.threat_level != ThreatLevel.SAFE:
                await self._save_event(analysis, is_violent, violence_prob)
                console.print(f"[alert]║ ⚠️  Security Alert: Potential Threat Detected")
                console.print(f"[stage3]╚════ Event Recorded and Saved ════╝\n")
                return self._annotate_frame(frame, analysis, violence_prob), True
            
            console.print(f"[stage3]╚════ Deep Analysis Complete: No Threat ════╝\n")
                
        return self.motion_detector.draw_debug(frame, motion_event), False
        
    async def _analyze_with_worker(self, frame: np.ndarray, motion: MotionEvent) -> Dict[str, Any]:
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
            'center': motion.center,
            'accumulated_motion': motion.accumulated_motion
        }
        data.add_field('motion_data', 
                      json.dumps(motion_data),
                      content_type='application/json')
        
        async with self.session.post(self.worker_url, data=data) as response:
            return await response.json()
            
    async def _save_event(self, 
                         analysis: SecurityAnalysis,
                         is_violent: bool,
                         violence_prob: float):
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
                'ai_violence_detection': {
                    'is_violent': is_violent,
                    'confidence': violence_prob
                },
                'timestamp': timestamp
            }, f, indent=2)
            
    def _annotate_frame(self, 
                       frame: np.ndarray, 
                       analysis: SecurityAnalysis,
                       violence_prob: float) -> np.ndarray:
        """Add analysis visualization to frame."""
        annotated = frame.copy()
        
        # Add threat level indicator
        color = {
            ThreatLevel.SAFE: (0, 255, 0),
            ThreatLevel.SUSPICIOUS: (0, 255, 255),
            ThreatLevel.DANGEROUS: (0, 0, 255)
        }[analysis.threat_level]
        
        # Add threat information
        cv2.putText(
            annotated,
            f"Threat Level: {analysis.threat_level.name}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )
        
        cv2.putText(
            annotated,
            f"Violence Prob: {violence_prob:.2f}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255) if violence_prob > 0.7 else (0, 255, 0),
            2
        )
        
        # List detected objects
        y_pos = 100
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

    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()

async def main():
    """Main execution function."""
    # Load configuration
    config = {
        'credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        'worker_url': os.getenv('CLOUDFLARE_WORKER_URL'),
        'model_path': 'C:/Users/eyuma/OneDrive/Desktop/WatchDog/models/best_model.pth',
        'save_dir': os.getenv('SAVE_DIR', 'detected_events')
    }
    
    # Initialize system
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