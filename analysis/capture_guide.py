"""
Script de capture USB avec monitoring en temps réel.
Utilise USBPcap pour capturer le trafic et l'analyser à la volée.

Ce script aide à identifier les commandes de vibration en temps réel
pendant que vous jouez à un jeu.
"""

import subprocess
import sys
import os
import re
from datetime import datetime

# Configuration
VENDOR_ID = 0x10F5  # Turtle Beach
PRODUCT_ID = 0x7018

def find_usbpcap():
    """Trouve l'exécutable USBPcap."""
    paths = [
        r"C:\Program Files\USBPcap\USBPcapCMD.exe",
        r"C:\Program Files (x86)\USBPcap\USBPcapCMD.exe",
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

def list_usb_devices():
    """Liste les périphériques USB disponibles."""
    usbpcap = find_usbpcap()
    
    if not usbpcap:
        print("[!] USBPcap non trouvé. Téléchargez-le depuis: https://desowin.org/usbpcap/")
        return None
    
    print("[*] Exécution de USBPcapCMD pour lister les périphériques...")
    
    try:
        # Lister les interfaces
        result = subprocess.run([usbpcap, "-h"], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    except Exception as e:
        print(f"[!] Erreur: {e}")

def generate_wireshark_filter():
    """Génère un filtre Wireshark pour la manette Turtle Beach."""
    
    filters = f"""
================================================================================
FILTRES WIRESHARK POUR CAPTURER LES VIBRATIONS
================================================================================

1. FILTRE DE BASE pour la manette Turtle Beach:
   usb.idVendor == 0x10f5 && usb.idProduct == 0x7018

2. FILTRE pour les paquets SORTANTS (Host -> Device) - C'est ça les vibrations:
   usb.transfer_type == 0x01 && usb.endpoint_address.direction == 0

3. FILTRE pour les Interrupt OUT (souvent utilisé pour vibration):
   usb.transfer_type == 0x01

4. FILTRE combiné (RECOMMANDÉ):
   (usb.idVendor == 0x10f5 || usb.src contains "10f5") && usb.transfer_type == 0x01

================================================================================
COMMENT CAPTURER:
================================================================================

1. Lancez Wireshark en ADMINISTRATEUR

2. Double-cliquez sur l'interface "USBPcap1" (ou celle où votre manette est connectée)

3. Dans la barre de filtre, entrez:
   usb.transfer_type == 0x01
   
4. Lancez un jeu qui fait vibrer la manette (ex: Forza, FIFA, The Crew)

5. Quand la manette vibre, vous verrez des paquets apparaître

6. IMPORTANT: Regardez les paquets avec:
   - Direction: host -> device (ou OUT)
   - Petite taille (8-32 bytes généralement)
   - Les bytes changent avec l'intensité de la vibration

7. Sauvegardez la capture: File -> Save As... (format .pcapng ou .pcap)

================================================================================
CE QU'IL FAUT CHERCHER:
================================================================================

Les commandes de vibration Xbox ressemblent généralement à:

Format Xbox One:
  09 00 00 09 00 0f [LeftTrig] [RightTrig] [LeftMotor] [RightMotor]

Où:
  - LeftTrig/RightTrig: Vibration des gâchettes (0x00-0xFF)
  - LeftMotor: Gros moteur, basses fréquences (0x00-0xFF)  
  - RightMotor: Petit moteur, hautes fréquences (0x00-0xFF)

MAIS Turtle Beach peut utiliser un format différent!
Cherchez des patterns qui changent quand l'intensité de vibration change.

================================================================================
"""
    return filters

def main():
    print("=" * 60)
    print("Guide de capture USB pour Turtle Beach Controller")
    print("=" * 60)
    
    print(generate_wireshark_filter())
    
    # Vérifier si USBPcap est installé
    usbpcap = find_usbpcap()
    if usbpcap:
        print(f"\n✓ USBPcap trouvé: {usbpcap}")
    else:
        print("\n✗ USBPcap NON INSTALLÉ!")
        print("  Téléchargez-le depuis: https://desowin.org/usbpcap/")
        print("  Puis redémarrez votre PC après l'installation.")
    
    # Créer un fichier de filtre pour import rapide
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\n[*] Pour lancer une capture rapide, utilisez cette commande PowerShell:")
    print(f'    & "{usbpcap}" -d "\\\\.\\USBPcap1" -o "capture_{timestamp}.pcap"')
    print("\n    (Remplacez USBPcap1 par le bon numéro d'interface)")

if __name__ == "__main__":
    main()
