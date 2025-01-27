Watchdog - AI-Powered Security Surveillance System

Overview
Watchdog is an advanced security surveillance system that combines real-time video analysis, AI-powered violence detection, and automated incident reporting. The system uses a multi-stage detection approach to identify and document security incidents while minimizing false positives.
Key Features

Real-time motion detection with temporal accumulation
AI-powered violence detection using fine-tuned ResNet50
Automatic face detection and capture during incidents
Incident video recording with pre/post-event buffering
Cloud storage integration with Cloudflare R2
Web-based dashboard for incident review
Secure metadata storage in Cloudflare D1 database

System Architecture
Components

Motion Detection (motion_detection.py)

Implements background subtraction with temporal accumulation
Configurable thresholds and detection windows
Robust against environmental noise


Violence Detection (model_inference.py)

Fine-tuned ResNet50 model
Real-time frame analysis
Configurable confidence thresholds


Incident Handler (incident_handler.py)

Manages pre/post incident frame buffers
Automated video capture and face detection
Cloud storage integration


Web Dashboard (React Components)

Real-time incident monitoring
Historical incident review
Face detection visualization
Video playback capabilities

Data Flow
CopyVideo Input → Motion Detection → Violence Detection → Incident Recording → Cloud Storage
                                                                      ↓
                                                              Web Dashboard