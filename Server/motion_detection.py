"""
motion_detection.py
Implements motion detection with temporal accumulation to reduce false positives
and provide more robust detection of sustained movement.

Key Features:
- Temporal accumulation of motion intensity
- Sliding window analysis
- Configurable thresholds and window sizes
- Debug visualization
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional, List, Deque
from collections import deque
from datetime import datetime
import time

@dataclass
class MotionConfig:
    """Configuration parameters for motion detection.
    
    Attributes:
        min_area: Minimum contour area to be considered (pixels²)
        learning_rate: Background adaptation rate (0-1)
        detection_threshold: Pixel difference threshold
        temporal_window: Time window for motion accumulation (seconds)
        accumulation_threshold: Required accumulated motion to trigger
        decay_rate: Rate at which accumulated motion decays
    """
    min_area: int = 10000
    learning_rate: float = 0.5
    detection_threshold: int = 5000
    temporal_window: float = 1.0
    accumulation_threshold: float = 5000
    decay_rate: float = .90

@dataclass
class MotionEvent:
    """Data structure for motion detection events.
    
    Attributes:
        contours: List of detected motion contours
        mask: Binary mask showing motion regions
        area: Total area of detected motion
        center: (x,y) center of largest motion region
        accumulated_motion: Total accumulated motion over time window
        threshold_exceeded: Whether accumulation threshold was exceeded
    """
    contours: List[np.ndarray]
    mask: np.ndarray
    area: float
    center: Tuple[int, int]
    accumulated_motion: float
    threshold_exceeded: bool = False

class MotionDetector:
    """
    Motion detector with temporal accumulation for robust detection.
    
    The detector maintains a sliding window of motion intensity and only
    triggers when accumulated motion exceeds configured threshold.
    """
    
    def __init__(self, config: Optional[MotionConfig] = None):
        """
        Initialize motion detector with optional configuration.
        
        Args:
            config: MotionConfig object with detection parameters
        """
        self.config = config or MotionConfig()
        self.frame_count = 0
        self.last_log_time = time.time()
        
        # Initialize background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=100,
            varThreshold=self.config.detection_threshold,
            detectShadows=False
        )
        
        # Motion history
        self.motion_history: Deque[Tuple[float, float]] = deque()
        self.accumulated_motion = 0.0
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        
        # Log initialization
        print(f"\n{'='*50}")
        print("Motion Detector Initialization")
        print(f"{'='*50}")
        print(f"► Min Area: {self.config.min_area} px²")
        print(f"► Learning Rate: {self.config.learning_rate}")
        print(f"► Detection Threshold: {self.config.detection_threshold}")
        print(f"► Temporal Window: {self.config.temporal_window}s")
        print(f"► Accumulation Threshold: {self.config.accumulation_threshold}")
        print(f"► Decay Rate: {self.config.decay_rate}")
        print(f"{'='*50}\n")

    def detect(self, frame: np.ndarray) -> Optional[MotionEvent]:
        """
        Detect motion in frame with temporal accumulation.
        
        Args:
            frame: Input video frame
            
        Returns:
            MotionEvent if motion detected, None otherwise
        """
        current_time = time.time()
        self.frame_count += 1
        
        # Update motion history window
        self._update_motion_window(current_time)
        
        # Detect motion in current frame
        fg_mask = self._process_frame(frame)
        contours = self._find_contours(fg_mask)
        
        if not contours:
            return None
            
        # Calculate motion metrics
        total_area = sum(cv2.contourArea(cnt) for cnt in contours)
        center = self._calculate_center(max(contours, key=cv2.contourArea))
        
        # Update accumulated motion
        self.motion_history.append((current_time, total_area))
        self.accumulated_motion = self.accumulated_motion * self.config.decay_rate + total_area
        
        # Check if threshold exceeded
        threshold_exceeded = self.accumulated_motion > self.config.accumulation_threshold
        
        # Log detection if needed
        self._log_detection(total_area, center, threshold_exceeded)
        
        return MotionEvent(
            contours=contours,
            mask=fg_mask,
            area=total_area,
            center=center,
            accumulated_motion=self.accumulated_motion,
            threshold_exceeded=threshold_exceeded
        )
        
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Apply background subtraction and morphological operations."""
        fg_mask = self.bg_subtractor.apply(frame, learningRate=self.config.learning_rate)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        return cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        
    def _find_contours(self, mask: np.ndarray) -> List[np.ndarray]:
        """Find significant contours in mask."""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [cnt for cnt in contours if cv2.contourArea(cnt) > self.config.min_area]
        
    def _calculate_center(self, contour: np.ndarray) -> Tuple[int, int]:
        """Calculate center point of contour."""
        M = cv2.moments(contour)
        if M["m00"] == 0:
            return (0, 0)
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
    def _update_motion_window(self, current_time: float):
        """Remove old motion entries outside temporal window."""
        window_start = current_time - self.config.temporal_window
        while self.motion_history and self.motion_history[0][0] < window_start:
            self.motion_history.popleft()
            
    def _log_detection(self, area: float, center: Tuple[int, int], 
                      threshold_exceeded: bool):
        """Log detection details if significant or periodic."""
        if threshold_exceeded:
            print(f"\n[!] MOTION THRESHOLD EXCEEDED at {self._get_timestamp()}")
            print(f"  ├── Area: {area:.0f}px²")
            print(f"  ├── Accumulated: {self.accumulated_motion:.0f}")
            print(f"  ├── Center: ({center[0]}, {center[1]})")
            print(f"  └── Window Size: {len(self.motion_history)}\n")
        elif time.time() - self.last_log_time > 1.0:
            print(f"Motion detected at {self._get_timestamp()}")
            print(f"  ├── Area: {area:.0f}px²")
            print(f"  └── Accumulated: {self.accumulated_motion:.0f}")
            self.last_log_time = time.time()

    def draw_debug(self, frame: np.ndarray, event: MotionEvent) -> np.ndarray:
        """
        Draw debug visualization on frame.
        
        Args:
            frame: Input video frame
            event: Current motion event
            
        Returns:
            Frame with debug visualization
        """
        debug_frame = frame.copy()
        
        # Draw contours
        color = (0, 0, 255) if event.threshold_exceeded else (0, 255, 0)
        cv2.drawContours(debug_frame, event.contours, -1, color, 2)
        
        # Draw center point
        cx, cy = event.center
        cv2.circle(debug_frame, event.center, 5, color, -1)
        cv2.line(debug_frame, (cx-10, cy), (cx+10, cy), color, 1)
        cv2.line(debug_frame, (cx, cy-10), (cx, cy+10), color, 1)
        
        # Add metrics text
        metrics = [
            "THRESHOLD EXCEEDED" if event.threshold_exceeded else "Motion Detected",
            f"Area: {event.area:.0f}px²",
            f"Accumulated: {event.accumulated_motion:.0f}",
            f"Center: ({cx}, {cy})",
            f"Objects: {len(event.contours)}",
            self._get_timestamp()
        ]
        
        for i, text in enumerate(metrics):
            cv2.putText(
                debug_frame,
                text, 
                (10, 30 + i*30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )
        
        return debug_frame
        
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]