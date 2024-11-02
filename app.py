from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import os

# Download the VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')

# Initialize Flask app with templates and static folders set to current directory
app = Flask(__name__, template_folder='.', static_folder='.')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

sia = SentimentIntensityAnalyzer()

# Helper function to map sentiment to more diverse emojis
def get_emoji(text):
    sentiment = sia.polarity_scores(text)
    compound_score = sentiment['compound']

    # Mapping compound scores to a range of emojis
    if compound_score >= 0.8:
        return '😍'  # Very positive
    elif compound_score >= 0.5:
        return '😊'  # Positive
    elif compound_score >= 0.3:
        return '🙂'  # Mildly positive
    elif compound_score > 0.1:
        return '😌'  # Slightly happy
    elif -0.1 <= compound_score <= 0.1:
        return '😐'  # Neutral
    elif -0.3 >= compound_score > -0.1:
        return '😕'  # Slightly negative
    elif -0.5 >= compound_score > -0.3:
        return '😞'  # Negative
    elif -0.8 >= compound_score > -0.5:
        return '😢'  # Very negative
    else:
        return '😭'  # Extremely negative

# Route to serve index.html
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Route to serve static files (CSS and JS)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# SocketIO event handlers
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'msg': f"{username} has joined the room."}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', {'msg': f"{username} has left the room."}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    username = data['username']
    message = data['message']
    room = data['room']
    emoji = get_emoji(message)
    emit('receive_emoji', {'emoji': emoji, 'username': username}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
