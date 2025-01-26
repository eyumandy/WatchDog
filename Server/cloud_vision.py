"""
cloud_vision.py
Handles Google Cloud Vision API integration for advanced video analysis.
"""

from google.cloud import vision
from google.cloud import videointelligence
import os
from typing import Dict, Any, List
import cv2
import numpy as np
from dataclasses import dataclass
from enum import Enum

class ThreatLevel(Enum):
    SAFE = 0
    SUSPICIOUS = 1
    DANGEROUS = 2

@dataclass
class SecurityAnalysis:
    threat_level: ThreatLevel
    detected_objects: List[str]
    violence_likelihood: str
    weapon_likelihood: str
    suspicious_activity: bool

class CloudVisionAnalyzer:
    def __init__(self, credentials_path: str):
        """
        Initialize Cloud Vision clients.
        
        Args:
            credentials_path: Path to Google Cloud credentials JSON
        """
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.vision_client = vision.ImageAnnotatorClient()
        self.video_client = videointelligence.VideoIntelligenceServiceClient()
        
        # Common suspicious objects/activities
        self.suspicious_objects = {
            'weapon': ThreatLevel.DANGEROUS,
            'knife': ThreatLevel.DANGEROUS,
            'gun': ThreatLevel.DANGEROUS,
            'mask': ThreatLevel.SUSPICIOUS,
            'crowbar': ThreatLevel.SUSPICIOUS
        }

    async def analyze_frame(self, frame: np.ndarray) -> SecurityAnalysis:
        """
        Analyze a single frame for security threats.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            SecurityAnalysis containing threat assessment
        """
        # Convert frame to bytes
        success, buffer = cv2.imencode('.jpg', frame)
        content = buffer.tobytes()
        
        # Create image object
        image = vision.Image(content=content)
        
        # Request features
        features = [
            vision.Feature.Type.OBJECT_LOCALIZATION,
            vision.Feature.Type.SAFE_SEARCH_DETECTION,
            vision.Feature.Type.LABEL_DETECTION
        ]
        
        # Analyze image
        response = self.vision_client.annotate_image({
            'image': image,
            'features': features
        })
        
        # Process detected objects
        detected_objects = [obj.name.lower() for obj in response.localized_object_annotations]
        
        # Determine threat level
        threat_level = ThreatLevel.SAFE
        for obj in detected_objects:
            if obj in self.suspicious_objects:
                obj_threat = self.suspicious_objects[obj]
                threat_level = max(threat_level, obj_threat)
        
        # Check violence likelihood
        violence_likelihood = response.safe_search_annotation.violence.name
        if violence_likelihood in ['LIKELY', 'VERY_LIKELY']:
            threat_level = ThreatLevel.DANGEROUS
        
        return SecurityAnalysis(
            threat_level=threat_level,
            detected_objects=detected_objects,
            violence_likelihood=violence_likelihood,
            weapon_likelihood=response.safe_search_annotation.violence.name,
            suspicious_activity=threat_level != ThreatLevel.SAFE
        )

    async def analyze_video_segment(self, 
                                  video_path: str,
                                  start_time: float,
                                  end_time: float) -> Dict[str, Any]:
        """Analyze a video segment for detailed activity recognition."""
        with open(video_path, 'rb') as file:
            input_content = file.read()
            
        # Configure video analysis request
        features = [
            videointelligence.Feature.OBJECT_TRACKING,
            videointelligence.Feature.EXPLICIT_CONTENT_DETECTION,
            videointelligence.Feature.PERSON_DETECTION
        ]
        
        video_context = videointelligence.VideoContext(
            segments=[
                videointelligence.VideoSegment(
                    start_time_offset=videointelligence.Duration(seconds=int(start_time)),
                    end_time_offset=videointelligence.Duration(seconds=int(end_time))
                )
            ]
        )
        
        operation = self.video_client.annotate_video(
            request={
                "features": features,
                "input_content": input_content,
                "video_context": video_context
            }
        )
        
        result = operation.result(timeout=90)
        return self._parse_video_response(result)
        
    def _parse_video_response(self, result: Any) -> Dict[str, Any]:
        """Parse video intelligence API response."""
        analysis = {
            'objects': [],
            'activities': [],
            'explicit_content': []
        }
        
        # Parse object tracking results
        for obj in result.object_annotations:
            analysis['objects'].append({
                'entity': obj.entity.description,
                'confidence': obj.confidence,
                'frames': len(obj.frames)
            })
            
        # Parse explicit content results
        for frame in result.explicit_annotation.frames:
            if frame.pornography_likelihood >= videointelligence.Likelihood.LIKELY:
                analysis['explicit_content'].append({
                    'timestamp': frame.time_offset.seconds,
                    'likelihood': frame.pornography_likelihood.name
                })
                
        return analysis