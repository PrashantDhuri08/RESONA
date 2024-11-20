from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ShazamAPI import Shazam


from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import librosa
import numpy as np
from pydub import AudioSegment
from datetime import datetime

app = Flask(__name__)

# First interface (online)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///song.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'prashant@123' 

db = SQLAlchemy(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login if not authenticated

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    

# Define the SongResult model
class SongResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    recognition_result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create the database and the tables
def create_tables():
    with app.app_context():
        db.create_all()

create_tables()  # Call the function to create tables

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('User already exists', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))  # Redirect to index
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    return render_template('Home.html')



@app.route('/upload', methods=['POST'])
@login_required
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
            # tag_id = result[1]['tagid']
            song_title =result[1]['track']['title'] if 'track' in result[1] else 'Unknown Title'
            artist_name = result[1]['track']['subtitle'] if 'track' in result[1] else 'Unknown Artist'
            # album_name = result['track']['album']['title'] if 'track' in result and 'album' in result['track'] else 'N/A'

            song_result = SongResult(
                filename=file.filename,
                recognition_result=f"{song_title} by {artist_name}"
            )
            db.session.add(song_result)
            db.session.commit()

            return jsonify(result)
        else:
            return jsonify({'error': 'No match found'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['GET'])
@login_required
def get_results():
    results = SongResult.query.order_by(SongResult.created_at.desc()).all()
    return render_template('res.html', results=results)

# Second Interface

# Custom Song recognition interface (Offline Mode)

# Initialize the Flask app and configure the database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# model to store recognition results
class SongRecognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    recognized_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_name = db.Column(db.String(100), nullable=False)
    folder_path = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Song '{self.song_name}' recognized from {self.file_name}>"


with app.app_context():
    db.create_all()

#  to convert audio file to WAV format
def convert_to_wav(file_path):
    sound = AudioSegment.from_file(file_path)
    wav_file_path = file_path + '.wav'
    sound.export(wav_file_path, format='wav')
    return wav_file_path

#  to extract features from audio files
def extract_features(file_path, clip_duration=15):
    audio, sr = librosa.load(file_path, duration=clip_duration)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
    roll_off = librosa.feature.spectral_rolloff(y=audio, sr=sr)
    features = np.concatenate((mfccs, spectral_centroid, bandwidth, roll_off), axis=0)
    return features

#  to create a fingerprint from features
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
@login_required
def ind():
    return render_template('ind.html')

@app.route('/record')
@login_required
def record():
    return render_template('recordog.html')

# About page route
@app.route('/about')
def about():
    return render_template('About.html')

# Route to render the song recognition page
@app.route('/recognize', methods=['POST'])
@login_required
def recognize():
    folder_path = request.form.get('folderPath')
    file = request.files['file']
    temp_fold_path= request.form.get('folderPath2')

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
@login_required
def display_songs():
    # Query all songs from the database
    all_songs = SongRecognition.query.all()

    # Render the template, passing the queried data
    return render_template('songs.html', songs=all_songs)

@app.route('/users')
@login_required  # Make sure only logged-in users can view this page
def display_users():
    users = User.query.all()  # Fetch all users from the database
    return render_template('users.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)
