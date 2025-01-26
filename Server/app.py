from flask import Flask, Response, jsonify, request, send_file, make_response
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
import mimetypes
import re

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

@app.route('/static/<path:incident_id>/<path:filename>')
def serve_incident_file(incident_id, filename):
    """
    Serve static files (videos, images) from incident folders with proper streaming support.
    """
    incidents_dir = os.getenv('SAVE_DIR', 'detected_events')
    file_path = os.path.join(incidents_dir, incident_id, filename)
    
    # Debug logging
    print(f"Accessing file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {'error': 'File not found'}, 404

    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size} bytes")

        # Handle range request
        range_header = request.headers.get('Range', None)
        print(f"Range header: {range_header}")

        if range_header:
            # Parse range header
            byte1, byte2 = 0, None
            match = re.search(r'(\d+)-(\d*)', range_header)
            groups = match.groups()

            if groups[0]: byte1 = int(groups[0])
            if groups[1]: byte2 = int(groups[1])

            if byte2 is None:
                byte2 = file_size - 1

            length = byte2 - byte1 + 1

            def generate():
                with open(file_path, 'rb') as f:
                    f.seek(byte1)
                    remaining = length
                    while remaining:
                        chunk_size = min(8192, remaining)  # Read in 8KB chunks
                        data = f.read(chunk_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data

            response = Response(
                generate(),
                206,
                mimetype='video/mp4',
                direct_passthrough=True
            )
            response.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{file_size}')
            response.headers.add('Accept-Ranges', 'bytes')
            response.headers.add('Content-Length', str(length))
        else:
            # Full file response
            def generate():
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)  # Read in 8KB chunks
                        if not chunk:
                            break
                        yield chunk

            response = Response(
                generate(),
                200,
                mimetype='video/mp4',
                direct_passthrough=True
            )
            response.headers.add('Content-Length', str(file_size))

        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Range, Content-Type')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
        
        print("Response headers:", dict(response.headers))
        return response

    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/incident/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    """
    Fetch metadata and resources for a specific incident.
    """
    incidents_dir = os.getenv('SAVE_DIR', 'detected_events')
    incident_path = os.path.join(incidents_dir, incident_id)

    # Debug print the paths
    console.print(f"[info]Checking incident path: {incident_path}")

    # Ensure the requested incident directory exists
    if not os.path.isdir(incident_path):
        console.print(f"[alert]Incident directory not found: {incident_path}")
        return jsonify({'error': 'Incident not found'}), 404

    try:
        # Read metadata from metadata.json
        metadata_path = os.path.join(incident_path, 'metadata.json')
        if not os.path.exists(metadata_path):
            console.print(f"[alert]Metadata file not found: {metadata_path}")
            return jsonify({'error': 'Metadata not found'}), 404

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Construct URLs for video and face images
        base_url = f"/static/{incident_id}"
        faces_dir = os.path.join(incident_path, 'faces')  # Changed from 'people' to 'faces'
        faces = []
        
        # Debug print
        console.print(f"[info]Checking faces directory: {faces_dir}")
        
        if os.path.exists(faces_dir):
            # Get list of face images
            face_images = [f for f in os.listdir(faces_dir) 
                         if f.endswith(('.jpg', '.png'))]
            console.print(f"[info]Found face images: {face_images}")
            
            faces = [f"{base_url}/faces/{face}" for face in face_images]  # Changed path to use 'faces'

        response_data = {
            'incident_id': metadata['incident_id'],
            'upload_date': metadata['upload_date'],
            'video_path': f"{base_url}/video.mp4",
            'faces': faces
        }
        
        # Debug print the response
        console.print(f"[info]Sending response: {response_data}")
        
        return jsonify(response_data)

    except Exception as e:
        console.print(f"[alert]Error processing incident: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
