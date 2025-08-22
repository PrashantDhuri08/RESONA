from flask import Flask, request, jsonify, render_template
from ShazamAPI import Shazam

from flask import Flask, request, render_template, jsonify
import os
import librosa
import numpy as np
from pydub import AudioSegment

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
    


# from flask import Flask, request, render_template, jsonify
# import os
# import librosa
# import numpy as np
# from pydub import AudioSegment

# app = Flask(__name__)

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

# Route to render the HTML form
@app.route('/ind')
def indbro():
    return render_template('ind.html')

# Route to handle the song recognition request
@app.route('/recognize', methods=['POST'])
def recognize():
    folder_path = request.form.get('folderPath')
    file = request.files['file']

    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': 'Invalid folder path.'}), 400

    if file.filename == '':
        return jsonify({'error': 'No file uploaded.'}), 400

    # Save the uploaded file temporarily
    temp_fold_path ='./songs/temp'
    unknown_file_path = os.path.join(temp_fold_path, file.filename)
    file.save(unknown_file_path)

    try:
        # Perform song recognition
        recognized_song = recognize_song(folder_path, unknown_file_path)
        result = f"Recognized song: {recognized_song}"
    except Exception as e:
        result = f"Error during recognition: {str(e)}"
    finally:
        # Clean up the uploaded file
        try:
            os.remove(unknown_file_path)
        except Exception as e:
            print(f"Error deleting file: {str(e)}")  

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
    

