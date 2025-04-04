from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import uuid
import json
from datetime import datetime

# Importer nos fonctions de génération de QR code
from qr_generator import generate_styled_qr

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
QR_FOLDER = 'static/qrcodes'
IMAGES_FOLDER = 'static/images'  # Nouveau dossier pour les images de contenu
DATA_FILE = 'data/qr_data.json'

# Créer les dossiers nécessaires s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)  # Création du dossier d'images
os.makedirs('data', exist_ok=True)

# Initialiser le fichier de données s'il n'existe pas
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_qr_data():
    """Charger les données des QR codes depuis le fichier JSON"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_qr_data(data):
    """Sauvegarder les données des QR codes dans le fichier JSON"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    """Page d'accueil - Formulaire de création de QR code"""
    return render_template('index.html')

@app.route('/create_qr', methods=['POST'])
def create_qr():
    """Endpoint pour créer un QR code"""
    # Récupérer les données du formulaire
    title = request.form.get('title', 'Sans titre')
    description = request.form.get('description', '')
    content_type = request.form.get('content_type', 'text')  # Nouveau champ pour le type de contenu
    
    # Options de style
    fill_color = request.form.get('fill_color', 'black')
    back_color = request.form.get('back_color', 'white')
    box_size = int(request.form.get('box_size', 10))
    border = int(request.form.get('border', 4))
    
    # Gérer le contenu selon le type
    content = ''
    image_filename = None
    
    if content_type == 'text':
        content = request.form.get('content', '')
    elif content_type == 'image' and 'content_image' in request.files:
        content_image = request.files['content_image']
        if content_image.filename:
            image_ext = os.path.splitext(content_image.filename)[1]
            image_filename = f"content_{uuid.uuid4().hex}{image_ext}"
            image_path = os.path.join(IMAGES_FOLDER, image_filename)
            content_image.save(image_path)
    
    # Gérer le logo s'il est fourni
    logo_path = None
    if 'logo' in request.files and request.files['logo'].filename:
        logo = request.files['logo']
        logo_ext = os.path.splitext(logo.filename)[1]
        logo_filename = f"logo_{uuid.uuid4().hex}{logo_ext}"
        logo_path = os.path.join(UPLOAD_FOLDER, logo_filename)
        logo.save(logo_path)
    
    # Générer un ID unique pour ce QR code
    qr_id = uuid.uuid4().hex
    
    # Construire l'URL de destination
    qr_url = url_for('qr_destination', qr_id=qr_id, _external=True)
    
    # Nom du fichier QR code
    qr_filename = f"qr_{qr_id}.png"
    qr_path = os.path.join(QR_FOLDER, qr_filename)
    
    # Options de style pour la génération du QR code
    style_options = {
        'logo_path': logo_path,
        'box_size': box_size,
        'border': border,
        'fill_color': fill_color,
        'back_color': back_color
    }
    
    # Générer le QR code
    generate_styled_qr(qr_url, qr_path, **style_options)
    
    # Enregistrer les données du QR code
    qr_data = load_qr_data()
    qr_data[qr_id] = {
        'title': title,
        'description': description,
        'content_type': content_type,
        'content': content,
        'image_filename': image_filename,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'qr_file': qr_filename
    }
    save_qr_data(qr_data)
    
    # Rediriger vers la page de visualisation du QR code
    return redirect(url_for('view_qr', qr_id=qr_id))

@app.route('/view/<qr_id>')
def view_qr(qr_id):
    """Page pour visualiser et télécharger un QR code généré"""
    qr_data = load_qr_data()
    
    if qr_id not in qr_data:
        return "QR code non trouvé", 404
    
    qr_info = qr_data[qr_id]
    qr_file = qr_info['qr_file']
    
    return render_template('view_qr.html', 
                           qr_id=qr_id, 
                           qr_info=qr_info, 
                           qr_file=qr_file,
                           qr_destination_url=url_for('qr_destination', qr_id=qr_id, _external=True))

@app.route('/qr/<qr_id>')
def qr_destination(qr_id):
    """Page de destination lorsqu'un QR code est scanné"""
    qr_data = load_qr_data()
    
    if qr_id not in qr_data:
        return "Contenu non trouvé", 404
    
    qr_info = qr_data[qr_id]
    
    return render_template('destination.html', 
                           title=qr_info['title'],
                           description=qr_info['description'],
                           content=qr_info.get('content', ''),
                           content_type=qr_info.get('content_type', 'text'),
                           image_filename=qr_info.get('image_filename'))

@app.route('/download/<qr_id>')
def download_qr(qr_id):
    """Télécharger le QR code généré"""
    qr_data = load_qr_data()
    
    if qr_id not in qr_data:
        return "QR code non trouvé", 404
    
    qr_file = qr_data[qr_id]['qr_file']
    
    return send_from_directory(QR_FOLDER, qr_file, as_attachment=True)

@app.route('/list')
def list_qr_codes():
    """Liste tous les QR codes générés"""
    qr_data = load_qr_data()
    return render_template('list.html', qr_codes=qr_data)

if __name__ == '__main__':
    app.run(debug=True)