from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import librosa
import numpy as np
from pydub import AudioSegment
from datetime import datetime

# Initialize the Flask app and configure the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# SongRecognition model to store recognition results
class SongRecognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    recognized_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_name = db.Column(db.String(100), nullable=False)
    folder_path = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Song '{self.song_name}' recognized from {self.file_name}>"

# Create the database tables (run this once to create the tables)
with app.app_context():
    db.create_all()

# Function to convert audio file to WAV format
def convert_to_wav(file_path):
    sound = AudioSegment.from_file(file_path)
    wav_file_path = file_path + '.wav'
    sound.export(wav_file_path, format='wav')
    return wav_file_path

# Function to extract features from audio files
def extract_features(file_path, clip_duration=15):
    audio, sr = librosa.load(file_path, duration=clip_duration)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
    roll_off = librosa.feature.spectral_rolloff(y=audio, sr=sr)
    features = np.concatenate((mfccs, spectral_centroid, bandwidth, roll_off), axis=0)
    return features

# Function to create a fingerprint from features
def create_fingerprint(features):
    fingerprint = np.mean(features, axis=1)
    return fingerprint

# Function to identify the closest matching song
def identify_song(unknown_fingerprint, song_fingerprints):
    distances = np.linalg.norm(unknown_fingerprint - song_fingerprints, axis=1)
    index = np.argmin(distances)
    return index

# Function to recognize the song
def recognize_song(folder_path, unknown_file_path):
    song_fingerprints = []
    song_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".wav") or file.endswith(".mp3"):
            file_path = os.path.join(folder_path, file)
            features = extract_features(file_path)
            fingerprint = create_fingerprint(features)
            song_fingerprints.append(fingerprint)
            song_files.append(file)

    unknown_file_path = convert_to_wav(unknown_file_path)
    unknown_features = extract_features(unknown_file_path)
    unknown_fingerprint = create_fingerprint(unknown_features)
    index = identify_song(unknown_fingerprint, song_fingerprints)
    return song_files[index]

# Home route to render the main page
@app.route('/ind')
def ind():
    return render_template('ind.html')

# About page route
@app.route('/about')
def about():
    return render_template('About.html')

# Route to render the song recognition page
@app.route('/recognize', methods=['POST'])
def recognize():
    folder_path = request.form.get('folderPath')
    file = request.files['file']

    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': 'Invalid folder path.'}), 400

    if file.filename == '':
        return jsonify({'error': 'No file uploaded.'}), 400

    # Save the uploaded file temporarily
    unknown_file_path = os.path.join(folder_path, file.filename)
    file.save(unknown_file_path)

    try:
        # Perform song recognition
        recognized_song = recognize_song(folder_path, unknown_file_path)
        result = f"Recognized song: {recognized_song}"

        # Store the result in the database
        song_entry = SongRecognition(
            song_name=recognized_song,
            file_name=file.filename,
            folder_path=folder_path
        )
        db.session.add(song_entry)
        db.session.commit()

    except Exception as e:
        result = f"Error during recognition: {str(e)}"
    finally:
        # Clean up the uploaded file
        os.remove(unknown_file_path)

    return jsonify({'result': result})


@app.route('/songs')
def display_songs():
    # Query all songs from the database
    all_songs = SongRecognition.query.all()

    # Render the template, passing the queried data
    return render_template('songs.html', songs=all_songs)



from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from ShazamAPI import Shazam
# app = Flask(__name__)



# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///song.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('Home2.html')

# Define the SongResult model
class SongResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    recognition_result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create the database and the tables
def create_tables():
    with app.app_context():  # Use the application context
        db.create_all()

create_tables()  # Call the function to create tables

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.mp3'):
        return jsonify({'error': 'Only MP3 files are allowed'}), 400

    try:
        mp3_data = file.read()
        shazam = Shazam(mp3_data)
        recognize_generator = shazam.recognizeSong()

        result = None
        for resp in recognize_generator:
            result = resp
            

        if result:
            song_title = result[1]['track']['share']['subject']

            # result[1].track.share.subject

            # Store the result in the database
            song_result = SongResult(filename=file.filename, recognition_result=str(song_title))
            db.session.add(song_result)
            db.session.commit()
            return jsonify(result)
        else:
            return jsonify({'error': 'No match found'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['GET'])
def get_results():
    results = SongResult.query.order_by(SongResult.created_at.desc()).all()
    return render_template('res.html', results=results)  # Render the results template




# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
