from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

# Let's keep it simple: all files in the root folder
# Check for eventlet (recommended for production)
try:
    import eventlet
    async_mode = 'eventlet'
except ImportError:
    async_mode = 'threading'

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.config['SECRET_KEY'] = 'secret!'
# Production setup: use eventlet if available, otherwise fallback to threading
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=20000000, async_mode=async_mode)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('identify')
def handle_identify(role):
    print(f"Identified as {role}")
    if role == 'host':
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
    emit('host_status', False, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
