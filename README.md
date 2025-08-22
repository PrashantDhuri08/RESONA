
# Resona: Song recognition app

A Flask-based web application that enables users to identify songs by uploading audio files. This project combines the Shazam API for quick recognition and a custom audio fingerprinting algorithm using libraries like librosa and pydub.


# Overview


This is a Flask-based web application that allows users to register, log in, and recognize songs using two different interfaces: one using the Shazam API and another using Librosa, a Python library for audio signal processing.

# Features
User registration and login using Flask-Login
Song recognition using the Shazam API
Song recognition using Librosa and audio signal processing techniques
Storage of recognition results in a SQLite database
Routes to display recognition results and user information
Requirements
Python 3.x
Flask
Flask-SQLAlchemy
Flask-Login
Shazam API key
Librosa
SQLite database

# Librosa Feature Extraction
### The Librosa interface uses the following feature extraction process:

 Audio File Conversion: The uploaded audio file is converted to WAV format using PyDub.

Feature Extraction: The following features are extracted from the audio file using Librosa:
Mel-Frequency Cepstral Coefficients (MFCCs)
Spectral Centroid
Spectral Bandwidth
Spectral Roll-Off
Fingerprint Creation: The extracted features are used to create a fingerprint for the audio file.
Song Recognition: The fingerprint is compared to a database of known song fingerprints to identify the recognized song.
Note
This is a basic implementation, and you may want to consider improving the application by adding error handling, caching mechanisms, and more robust security features.
## Installation

Clone the repository:


```bash
  git clone https://github.com/your-username/your-repo-name.git
```


### Step 1: Navigate to your project directory
```bash
  cd path/to/your/project
```

### Step 2: Create the virtual environment
```bash
python -m venv venv   # or `virtualenv venv`
```

### Step 3: Activate the virtual environment
#### Windows
```bash
venv\Scripts\activate
```

### macOS/Linux
```bash
source venv/bin/activate
```

### Step 4: Install required packages
```bash
pip install -r requirements.txt   # or install packages individually
```


### Run the application:
```bash
   python app.py
```

### Step 5: Deactivate the virtual environment
```bash
deactivate
```


    
