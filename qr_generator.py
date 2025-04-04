import qrcode
from PIL import Image
import os

def generate_qr(data, output_filename="qrcode.png", 
               box_size=10, border=4, fill_color="black", back_color="white"):
    """
    Génère un QR code simple
    
    Args:
        data (str): Données à encoder dans le QR code
        output_filename (str): Nom du fichier pour sauvegarder le QR code
        box_size (int): Taille de chaque boîte du QR code
        border (int): Taille de la bordure
        fill_color (str): Couleur des modules QR
        back_color (str): Couleur de fond
    
    Returns:
        PIL.Image: Image du QR code généré
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color)
    qr_img.save(output_filename)
    
    return qr_img

def generate_qr_with_logo(data, logo_path=None, output_filename="qrcode_with_logo.png", 
                          box_size=10, border=4, fill_color="black", back_color="white"):
    """
    Génère un QR code avec un logo au centre
    
    Args:
        data (str): Données à encoder dans le QR code
        logo_path (str): Chemin vers l'image du logo
        output_filename (str): Nom du fichier pour sauvegarder le QR code
        box_size (int): Taille de chaque boîte du QR code
        border (int): Taille de la bordure
        fill_color (str): Couleur des modules QR
        back_color (str): Couleur de fond
    
    Returns:
        PIL.Image: Image du QR code généré avec logo
    """
    # Générer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGBA')
    
    # Si un logo est spécifié, l'ajouter au centre du QR code
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert('RGBA')
        
        # Redimensionner le logo (ne pas dépasser 30% de la taille du QR code)
        qr_size = qr_img.size[0]
        logo_size = int(qr_size * 0.25)  # 25% de la taille du QR code
        logo = logo.resize((logo_size, logo_size))
        
        # Calculer la position pour centrer le logo
        pos = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
        
        # Coller le logo sur le QR code
        qr_img.paste(logo, pos, logo)
    
    # Sauvegarder l'image finale
    qr_img.save(output_filename)
    
    return qr_img

def generate_styled_qr(data, filename="styled_qr.png", **style_options):
    """
    Génère un QR code avec différentes options de style
    
    Args:
        data (str): Données à encoder dans le QR code
        filename (str): Nom du fichier pour sauvegarder le QR code
        style_options (dict): Options de style (logo_path, box_size, border, fill_color, back_color)
    
    Returns:
        PIL.Image: Image du QR code généré
    """
    # Extraire les options de style
    logo_path = style_options.get('logo_path')
    box_size = style_options.get('box_size', 10)
    border = style_options.get('border', 4)
    fill_color = style_options.get('fill_color', 'black')
    back_color = style_options.get('back_color', 'white')
    
    # Générer le QR code avec ou sans logo
    if logo_path:
        return generate_qr_with_logo(
            data, logo_path, filename, box_size, border, fill_color, back_color
        )
    else:
        return generate_qr(
            data, filename, box_size, border, fill_color, back_color
        )

# Exemple d'utilisation
if __name__ == "__main__":
    # URL vers laquelle le QR code pointera
    url = "https://example.com"
    
    # Générer un QR code simple
    generate_qr(url, "qr_simple.png")
    
    # Générer un QR code avec des couleurs personnalisées
    generate_qr(url, "qr_colored.png", fill_color="blue", back_color="yellow")
    
    # Générer un QR code avec un logo (remplacez 'path/to/your/logo.png' par le chemin réel)
    # logo_path = "path/to/your/logo.png"  # Décommenter et ajuster le chemin
    # generate_qr_with_logo(url, logo_path, "qr_with_logo.png")
    
    # Générer un QR code stylisé avec plusieurs options
    style_options = {
        # 'logo_path': logo_path,  # Décommenter si vous avez un logo
        'box_size': 12,
        'border': 2,
        'fill_color': 'darkgreen',
        'back_color': 'lightgreen'
    }
    generate_styled_qr(url, "qr_styled.png", **style_options)
    
    print("QR codes générés avec succès!")