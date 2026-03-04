from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__, static_folder='public', static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
# Set max_http_buffer_size to allow larger image payloads
# Production setup: use eventlet for WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=10000000, async_mode='eventlet')

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@socketio.on('identify')
def handle_identify(role):
    print(f"Identified as {role}")
    # In a real app, you'd track sessions better
    if role == 'host':
        # Notify clients that host is online
        emit('host_status', True, broadcast=True)

@socketio.on('screen_frame')
def handle_screen_frame(data):
    # Relay base64 image from host to all clients
    emit('screen_frame', data, broadcast=True, include_self=False)

@socketio.on('control_event')
def handle_control_event(data):
    # Relay control events (mouse/key) to the host
    emit('control_event', data, broadcast=True, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    # If the host disconnects, notify clients
    # Note: This is a simplification
    emit('host_status', False, broadcast=True)

if __name__ == '__main__':
    # Use 'eventlet' or 'gevent' for production-like behavior locally
    socketio.run(app, debug=True, port=3000)
