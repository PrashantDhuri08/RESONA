from flask import Flask, request, jsonify, render_template
from ShazamAPI import Shazam

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Home2.html')

@app.route('/about')
def about():
    return render_template('About.html')


@app.route('/upload', methods=['POST'])
def upload():

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # If the user does not select a file, the browser also submits an empty part without filename
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

if __name__ == '__main__':
    app.run(debug=True)
