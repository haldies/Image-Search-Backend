import numpy as np
from PIL import Image
from feature_extractor import FeatureExtractor
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, url_for
from pathlib import Path
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
IMG_FOLDER = 'img'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMG_FOLDER, exist_ok=True)

fe = FeatureExtractor()
features = []
img_paths = []
for feature_path in Path("./feature").glob("*.npy"):
    features.append(np.load(feature_path))
    img_paths.append(Path("./img") / (feature_path.stem + ".jpg"))
features = np.array(features)

@app.route('/uploads/<filename>')
def uploads_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/img/<filename>')
def image_file(filename):
    return send_from_directory(IMG_FOLDER, filename)

@app.route('/', methods=['POST'])
def index(): 
    if request.method == 'POST':
        file = request.files['query_img']
        if file:
           
            img = Image.open(file.stream) 
            uploaded_img_path = os.path.join(UPLOAD_FOLDER, datetime.now().isoformat().replace(":", ".") + "_" + file.filename)
            img.save(uploaded_img_path)

           
            query = fe.extract(img)
            dists = np.linalg.norm(features - query, axis=1)  
            ids = np.argsort(dists)[:30]  

           
            scores = []
            for id in ids:
                score = {
                    'id': int(id),
                    'distance': float(dists[id]),
                    'imageUrl': "https://rjk80hjv-5000.asse.devtunnels.ms/" + ('/') + url_for('image_file', filename=os.path.basename(str(img_paths[id])))
                }
                scores.append(score)

            response = {
                'query_image': "https://rjk80hjv-5000.asse.devtunnels.ms/" + ('/') + url_for('uploads_file', filename=os.path.basename(uploaded_img_path)),
                'results': scores
            }


            return jsonify(response)

        else:
            return jsonify({'error': 'No file uploaded'}), 400

    else:
        return jsonify({'error': 'Method not allowed'}), 405

if __name__ == "__main__":
    app.run("0.0.0.0")
