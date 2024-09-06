from flask import Flask, request, jsonify, render_template
import os
import librosa
import numpy as np
from scipy.spatial.distance import euclidean
from mutagen.easyid3 import EasyID3
from scipy.ndimage import maximum_filter

app = Flask(__name__)

# Function to extract MFCC features and spectrogram peaks from an audio file
def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)

        # MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfccs_mean = np.mean(mfccs.T, axis=0)

        # Spectrogram Peaks
        S = np.abs(librosa.stft(y))  # Short-time Fourier Transform
        peaks = get_spectrogram_peaks(S)

        # Combine MFCCs and Spectrogram Peaks into one feature vector
        features = np.concatenate((mfccs_mean, peaks))
        return features
    except Exception as e:
        raise RuntimeError(f"Error extracting features from {file_path}: {str(e)}")

# Function to extract peaks from a spectrogram
def get_spectrogram_peaks(S, size=5):
    # Identify local maxima in the spectrogram
    local_max = maximum_filter(S, size=size) == S
    peaks = np.sum(local_max, axis=1)  # Sum across frequency bins
    return peaks[:13]  # Use the first 13 peaks to keep feature size consistent

# Function to get metadata of the song
def get_song_metadata(file_path):
    try:
        audio = EasyID3(file_path)
        metadata = {
            "title": audio.get("title", ["Unknown Title"])[0],
            "artist": audio.get("artist", ["Unknown Artist"])[0],
            "album": audio.get("album", ["Unknown Album"])[0],
        }
        return metadata
    except Exception as e:
        return {"title": "Unknown Title", "artist": "Unknown Artist", "album": "Unknown Album"}

@app.route('/')
def index():
    return render_template('inde.html')

@app.route('/compare', methods=['POST'])
def compare_songs():
    folder_path = request.form.get('folderPath')
    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': 'Invalid folder path.'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    # Save the uploaded file temporarily to extract features
    file_path = os.path.join(folder_path, file.filename)
    try:
        file.save(file_path)
        features_song_to_compare = extract_features(file_path)
    except Exception as e:
        return jsonify({'error': f'Failed to save or process file: {str(e)}'}), 500
    finally:
        os.remove(file_path)  # Clean up the temporary file

    # Compare the uploaded file with all songs in the folder
    distances = {}
    metadata_dict = {}
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".mp3"):
                song_path = os.path.join(folder_path, filename)
                features_song = extract_features(song_path)
                distance = euclidean(features_song_to_compare, features_song)
                distances[song_path] = distance
                metadata_dict[song_path] = get_song_metadata(song_path)
    except Exception as e:
        return jsonify({'error': f'Error during comparison: {str(e)}'}), 500

    if distances:
        most_similar_song = min(distances, key=distances.get)
        metadata = metadata_dict[most_similar_song]
        
        result = f"The song most similar to the uploaded file is: {metadata['title']} by {metadata['artist']} from the album {metadata['album']}."
    else:
        result = "No songs found in the selected folder."

    return jsonify({'result': result, 'distances': distances})

if __name__ == '__main__':
    app.run(debug=True)
