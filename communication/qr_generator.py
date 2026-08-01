import os
import sys
from pathlib import Path

# Add project root to python path so we can resolve package imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

import qrcode
from config.robot_identity import robot_identity

def generate_qr_code() -> str:
    """
    Generates a QR code linking to the permanent robot domain (http://campusguiderobot.local:8000).
    Prints a scannable ASCII QR code in the console terminal on startup and saves 
    a PNG copy to static/assets/qr_code.png.
    
    Returns:
        The permanent URL address.
    """
    url = robot_identity.permanent_url
    fallback_url = robot_identity.fallback_url
    
    print("\n" + "=" * 60)
    print("               ROBOT IDENTITY LAYER INITIALIZED")
    print("=" * 60)
    print(f"🤖 Robot Name : {robot_identity.robot_name}")
    print(f"🔗 Permanent URL : {url}  (Printed on Robot QR Code)")
    print(f"🛠️  Fallback Debug IP: {fallback_url} (If network blocks mDNS)")
    print("\nScan the QR code below to connect your mobile client:")
    print("-" * 60)
    
    # 1. Initialize QR Code generator locked to the permanent domain
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=2
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # 2. Print ASCII QR Code directly into the terminal
    try:
        # Invert=True makes it correctly scannable in standard dark-background shells
        qr.print_ascii(out=sys.stdout, invert=True)
    except Exception as e:
        print(f"[WARNING] Could not print ASCII QR Code to terminal: {e}")
        
    print("-" * 60)
    print("============================================================\n")
    
    # 3. Export PNG image to static assets (used by web app / display dashboards)
    try:
        # Resolve path relative to project root
        base_dir = Path(__file__).resolve().parent.parent
        assets_dir = base_dir / "static" / "assets"
        os.makedirs(assets_dir, exist_ok=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(assets_dir / "qr_code.png")
        print(f"[INFO] Permanent QR Code image written to: static/assets/qr_code.png")
        
    except Exception as e:
        print(f"[ERROR] Failed to save QR Code image: {e}")
        
    return url

if __name__ == "__main__":
    generate_qr_code()
