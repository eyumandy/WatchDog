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

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type"]}})

# Global variables
frame_queue = Queue(maxsize=3)
surveillance_system = None
incident_lock = threading.Lock()  # Lock for concurrent incident handling

# Initialize S3 client for R2
s3_client = boto3.client('s3',
    endpoint_url=os.getenv('R2_ENDPOINT'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_ACCESS_KEY_SECRET'),
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def init_surveillance():
    """Initialize SurveillanceSystem."""
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

def process_camera():
    """Run the camera and process frames asynchronously."""
    global surveillance_system
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    async def async_process_frame(frame):
        """Asynchronously process a single frame."""
        return await surveillance_system.process_frame(frame)

    loop = asyncio.new_event_loop()  # Create a new event loop for async tasks
    asyncio.set_event_loop(loop)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Asynchronously process the frame
            task = loop.create_task(async_process_frame(frame))
            processed_frame, suspicious = loop.run_until_complete(task)

            if not frame_queue.full():
                frame_queue.put(processed_frame)

    finally:
        cap.release()
        loop.close()


def generate_frames():
    """Generate frames for video feed."""
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video feed route."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


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
@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up SurveillanceSystem."""
    global surveillance_system
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(surveillance_system.cleanup())
        loop.close()
        return jsonify({'status': 'Surveillance system cleaned up'})
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
