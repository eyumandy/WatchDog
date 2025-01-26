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
from rich.console import Console
import json
from flask import send_from_directory

# Load environment variables
load_dotenv()
console = Console()

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

@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Serve static files such as videos and images from the detected_events directory.
    """
    incidents_dir = os.getenv('SAVE_DIR', 'detected_events')
    file_path = os.path.join(incidents_dir, filename)

    # Debugging log
    console.print(f"[info] Static file requested: {file_path}")
    console.print(f"[info] Checking file existence at: {file_path}")
    if not os.path.exists(file_path):
        console.print(f"[alert] File not found: {file_path}")
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(incidents_dir, filename)

@app.route('/incident/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    """
    Fetch metadata and resources (video, detected faces) for a specific incident.
    """
    incidents_dir = os.getenv('SAVE_DIR', 'detected_events')
    incident_path = os.path.join(incidents_dir, incident_id)

    # Ensure the requested incident directory exists
    if not os.path.isdir(incident_path):
        console.print(f"[alert] Incident directory not found: {incident_path}")
        return jsonify({'error': 'Incident not found'}), 404

    # Read metadata from metadata.json
    metadata_path = os.path.join(incident_path, 'metadata.json')
    if not os.path.exists(metadata_path):
        console.print(f"[alert] Metadata file not found: {metadata_path}")
        return jsonify({'error': 'Metadata not found'}), 404

    # Load metadata into a Python dictionary
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Construct URLs for video and detected faces
    base_url = request.host_url.rstrip('/')  # Get the base URL (e.g., http://localhost:5000)
    video_path = f"{base_url}/static/{incident_id}/video.mp4"
    faces_path = os.path.join(incident_path, 'people')
    faces = [
        f"{base_url}/static/{incident_id}/people/{face}"
        for face in os.listdir(faces_path)
        if face.endswith(('.jpg', '.png'))
    ] if os.path.exists(faces_path) else []

    return jsonify({
        'incident_id': metadata['incident_id'],
        'upload_date': metadata['upload_date'],
        'video_path': video_path,
        'faces': faces
    })

@app.route('/incidents', methods=['GET'])
def get_incidents():
    """
    Retrieve a list of incidents from the `detected_events` folder.
    Each incident includes its metadata, video path, and detected faces.
    """
    incidents_dir = os.getenv('SAVE_DIR', 'detected_events')
    incidents = []

    try:
        # Loop through each incident folder
        for incident_id in os.listdir(incidents_dir):
            incident_path = os.path.join(incidents_dir, incident_id)

            # Skip non-directories
            if not os.path.isdir(incident_path):
                continue

            # Read metadata.json
            metadata_path = os.path.join(incident_path, 'metadata.json')
            if not os.path.exists(metadata_path):
                continue

            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            # Get video path
            video_path = os.path.join(incident_path, 'video.mp4')

            # Get detected faces
            faces_path = os.path.join(incident_path, 'people')
            faces = []
            if os.path.exists(faces_path):
                faces = [
                    os.path.join(faces_path, face)
                    for face in os.listdir(faces_path) if face.endswith(('.jpg', '.png'))
                ]

            # Append incident data
            incidents.append({
                'incident_id': metadata['incident_id'],
                'upload_date': metadata['upload_date'],
                'video_path': f"/static/{incident_id}/video.mp4",
                'faces': [f"/static/{incident_id}/people/{os.path.basename(face)}" for face in faces]
            })

        return jsonify({'incidents': incidents})
    except Exception as e:
        console.print(f"[alert]Error fetching incidents: {str(e)}")
        return jsonify({'error': 'Failed to retrieve incidents'}), 500
    
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
