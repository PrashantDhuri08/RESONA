from flask import Flask, request, jsonify, render_template
import os
import librosa
import numpy as np
from scipy.spatial.distance import euclidean

app = Flask(__name__)

# Function to extract MFCC features from an audio file
def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return np.mean(mfccs.T, axis=0)
    except Exception as e:
        raise RuntimeError(f"Error extracting features from {file_path}: {str(e)}")

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
    # finally:
    #     os.remove(file_path)  # Clean up the temporary file

    # Compare the uploaded file with all songs in the folder
    distances = {}
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".mp3"):
                song_path = os.path.join(folder_path, filename)
                features_song = extract_features(song_path)
                distance = euclidean(features_song_to_compare, features_song)
                distances[song_path] = distance
    except Exception as e:
        return jsonify({'error': f'Error during comparison: {str(e)}'}), 500

    if distances:
        most_similar_song = min(distances, key=distances.get)
        result = f"The song most similar to the uploaded file is: {most_similar_song}"
    else:
        result = "No songs found in the selected folder."

    return jsonify({'result': result, 'distances': distances})

if __name__ == '__main__':
    app.run(debug=True)
