from flask import Flask, request, jsonify, render_template
from ShazamAPI import Shazam

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Home2.html')


@app.route('/about')
def about():
    return render_template('About.html')


@app.route('/record')
def record():
    return render_template('recordog.html')


@app.route('/upload', methods=['POST'])
def upload():

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Read the file and pass it to Shazam API
    mp3_data = file.read()
    shazam = Shazam(mp3_data)
    recognize_generator = shazam.recognizeSong()

    # Collect responses
    result = None
    for resp in recognize_generator:
        result = resp

    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'No match found'})
    


from flask import Flask, request, render_template, jsonify
import os
import librosa
import numpy as np

# app = Flask(__name__)

# Set a fixed folder path for audio files
AUDIO_FOLDER_PATH = './songs/Wav'  # Update this with the actual path to your audio files

# Function to extract features from audio files
def extract_features(file_path, clip_duration=15):
    audio, sr = librosa.load(file_path, duration=clip_duration)
    
    # Extract MFCCs and spectral features
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
    roll_off = librosa.feature.spectral_rolloff(y=audio, sr=sr)
    
    # Ensure all arrays have the same number of dimensions for concatenation
    features = np.concatenate((mfccs, spectral_centroid, bandwidth, roll_off), axis=0)
    
    return features

# Function to create a fingerprint from features
def create_fingerprint(features):
    fingerprint = np.mean(features, axis=1)
    return fingerprint

# Function to identify the closest matching song based on Euclidean distance
def identify_song(unknown_fingerprint, song_fingerprints):
    distances = [np.linalg.norm(unknown_fingerprint - fingerprint) for fingerprint in song_fingerprints]
    index = np.argmin(distances)
    return index

# Function to recognize the song
def recognize_song(unknown_file_path):
    song_fingerprints = []
    song_files = []
    
    for file in os.listdir(AUDIO_FOLDER_PATH):
        if file.endswith(".wav") or file.endswith(".mp3"):
            file_path = os.path.join(AUDIO_FOLDER_PATH, file)
            features = extract_features(file_path)
            fingerprint = create_fingerprint(features)
            song_fingerprints.append(fingerprint)
            song_files.append(file)
    
    unknown_features = extract_features(unknown_file_path)
    unknown_fingerprint = create_fingerprint(unknown_features)
    
    index = identify_song(unknown_fingerprint, song_fingerprints)
    return song_files[index]

# Route to render the HTML form
@app.route('/identify')
def identify():
    return render_template('identify.html')

# Route to handle the song recognition request
@app.route('/recognize', methods=['POST'])
def recognize():
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file uploaded.'}), 400

    # Save the uploaded file temporarily
    unknown_file_path = os.path.join(AUDIO_FOLDER_PATH, file.filename)
    file.save(unknown_file_path)

    try:
        # Perform song recognition
        recognized_song = recognize_song(unknown_file_path)
        result = f"Recognized song: {recognized_song}"
    except Exception as e:
        result = f"Error during recognition: {str(e)}"
    finally:
        # Clean up the uploaded file
        os.remove(unknown_file_path)

    return jsonify({'result': result})




if __name__ == '__main__':
    app.run(debug=True)
