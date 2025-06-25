from flask import Flask, request, jsonify, send_file,render_template
from pymongo import MongoClient
import gridfs
import os
from io import BytesIO
from flask_cors import CORS
import webbrowser
import threading


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Connetti a MongoDB
try:
    client = MongoClient('mongodb://mongodb:27017')
except:
    client = MongoClient('mongodb://127.0.0.1:27017')
#stampare i database presenti
print(client.list_database_names())
db = client['CatalogoFantasyForge']
fs = gridfs.GridFS(db)

# Configurazione per paginazione
ITEMS_PER_PAGE = 9
ITEMS_PER_IFRAME = 6

@app.route("/get_number_of_pages", methods=['GET'])
def get_number_of_pages():
    if request.args.get('iframe'):
        video_files = list(fs.find({'filename': {'$regex': r'\.mp4$'}}))
        return jsonify({'number_of_pages': (len(video_files) + ITEMS_PER_IFRAME - 1) // ITEMS_PER_IFRAME})
    else:
        video_files = list(fs.find({'filename': {'$regex': r'\.mp4$'}}))
        return jsonify({'number_of_pages': (len(video_files) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE})

@app.route('/videos', methods=['GET'])
def list_videos():
    if request.args.get('iframe'):
        page = int(request.args.get('page', 1))
        skip = (page - 1) * ITEMS_PER_IFRAME
        video_files = fs.find({'filename': {'$regex': r'\.mp4$'}}).skip(skip).limit(ITEMS_PER_IFRAME)
    
    else:
        page = int(request.args.get('page', 1))
        skip = (page - 1) * ITEMS_PER_PAGE
        video_files = fs.find({'filename': {'$regex': r'\.mp4$'}}).skip(skip).limit(ITEMS_PER_PAGE)
    
    videos = []
    for video_file in video_files:
        videos.append({
            'filename': video_file.filename,
            'file_id': str(video_file._id)
        })

    return jsonify({
        'page': page,
        'videos': videos,
    })

@app.route('/video', methods=['GET'])
def get_video():
    try:
        file_name = request.args.get('file_name')
        file_data = fs.get_last_version(filename=file_name)
        return send_file(BytesIO(file_data.read()), mimetype='video/mp4', as_attachment=True, download_name=file_name)
    except gridfs.errors.NoFile:
        return jsonify({'error': 'File not found'}), 404

@app.route('/')
def home():
    #se ci sta il parametro iframe ritorna pagina_aiframe.html
    if request.args.get('iframe'):
        return render_template('pagina_aiframe.html')
    return render_template('pagina_full.html')

# creare una route per prelevare i file stl dal database
@app.route('/stl', methods=['GET'])
def get_stl():
    try:
        file_name = request.args.get('file_name')
        file_name = file_name.split("_video.mp4")[0] + ".stl"
        file_data = fs.get_last_version(filename=file_name)
        return send_file(BytesIO(file_data.read()), mimetype='application/octet-stream', as_attachment=True, download_name=file_name)
    except gridfs.errors.NoFile:
        return jsonify({'error': 'File not found'}), 404

def open_browser():
    # L'indirizzo del server Flask
    url = 'http://127.0.0.1:5000/'
    # Attendi qualche secondo per assicurarti che il server sia avviato
    threading.Timer(1, lambda: webbrowser.open(url)).start()

#creare una route per aprire la pagina html preferiti.html
@app.route('/preferiti')
def preferiti():
    return render_template('preferiti.html')

@app.route("/check_video", methods=['POST'])
def check_video():
    file_name = request.json['filename']
    file_data = fs.get_last_version(filename=file_name)
    return jsonify({'exists': file_data is not None})

#creare una route per aggiungere un video al database
@app.route('/add_file', methods=['POST'])
def add_video():
    file = request.files['file']
    filename = request.form.get('filename', file.filename)
    file_id = fs.put(file, filename=filename)
    return jsonify({'file_id': str(file_id)})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

    
