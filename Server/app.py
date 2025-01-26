"""
app.py
Flask server implementation for WatchDog surveillance system.
Handles video streaming, threat detection, incident reporting, and R2 storage.
"""

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
import asyncio
import threading
from queue import Queue
import numpy as np
from surveillance import SurveillanceSystem
import os
from dotenv import load_dotenv
import boto3
from botocore.config import Config
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type"]}})

# Global variables
frame_queue = Queue(maxsize=10)
latest_analysis = None
surveillance_system = None

# Initialize S3 client for R2
s3_client = boto3.client('s3',
    endpoint_url=os.getenv('R2_ENDPOINT'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_ACCESS_KEY_SECRET'),
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def init_surveillance():
    """Initialize surveillance system with configuration."""
    global surveillance_system
    
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
    
    surveillance_system = SurveillanceSystem(**config)
    return asyncio.run(surveillance_system.initialize())

# Separate queues for raw feed and analysis
frame_queue = Queue(maxsize=3)  # Smaller queue for lower latency
analysis_queue = Queue(maxsize=10)

def process_camera():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    # Set camera thread priority
    try:
        import psutil
        process = psutil.Process()
        process.nice(10)  # Higher priority
    except:
        pass

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Fast path for video feed
        if not frame_queue.full():
            # Optimize frame for streaming
            small_frame = cv2.resize(frame, (854, 480))
            frame_queue.put(small_frame)
            
            
        
    cap.release()

def generate_frames():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            
            # Aggressive JPEG compression for faster streaming
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            if ret:
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + 
                      buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')               

@app.route('/get_presigned_url', methods=['POST'])
def get_presigned_url():
    """Generate presigned URL for R2 upload."""
    try:
        data = request.get_json()
        incident_id = data.get('incident_id')
        
        if not incident_id:
            return jsonify({'error': 'Missing incident_id'}), 400
            
        # Generate presigned URL valid for 10 minutes
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': os.getenv('R2_BUCKET_NAME'),
                'Key': f'incidents/{incident_id}.mp4',
                'ContentType': 'video/mp4'
            },
            ExpiresIn=600
        )
        
        return jsonify({
            'uploadUrl': presigned_url,
            'key': f'incidents/{incident_id}.mp4'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/incidents', methods=['GET'])
def list_incidents():
    """List all recorded incidents."""
    try:
        response = s3_client.list_objects_v2(
            Bucket=os.getenv('R2_BUCKET_NAME'),
            Prefix='incidents/'
        )
        
        incidents = []
        for obj in response.get('Contents', []):
            # Generate presigned GET URL for each incident
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': os.getenv('R2_BUCKET_NAME'),
                    'Key': obj['Key']
                },
                ExpiresIn=3600  # URL valid for 1 hour
            )
            
            incidents.append({
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat(),
                'download_url': presigned_url
            })
            
        return jsonify({'incidents': incidents})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/incident/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Get details and download URL for specific incident."""
    try:
        key = f'incidents/{incident_id}.mp4'
        
        # Check if object exists
        s3_client.head_object(
            Bucket=os.getenv('R2_BUCKET_NAME'),
            Key=key
        )
        
        # Generate presigned download URL
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': os.getenv('R2_BUCKET_NAME'),
                'Key': key
            },
            ExpiresIn=3600
        )
        
        return jsonify({
            'incident_id': incident_id,
            'download_url': download_url
        })
        
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return jsonify({'error': 'Incident not found'}), 404
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize surveillance system
    init_surveillance()
    
    # Start camera processing in background thread
    camera_thread = threading.Thread(target=process_camera, daemon=True)
    camera_thread.start()
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, threaded=True, processes=1)