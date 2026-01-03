#!/usr/bin/env python3
"""
Analyse des captures Wireshark USB pour identifier les commandes de vibration
de la manette Turtle Beach Xbox One.

Usage:
    python analyze_capture.py <capture.pcap>
"""

import sys
try:
    from scapy.all import rdpcap, USB
except ImportError:
    print("Installez scapy: pip install scapy")
    sys.exit(1)

# IDs de la manette Turtle Beach
VENDOR_ID = 0x10F5
PRODUCT_ID = 0x7018

def analyze_pcap(filename):
    """Analyse un fichier pcap pour extraire les commandes USB pertinentes."""
    print(f"[*] Chargement de {filename}...")
    
    try:
        packets = rdpcap(filename)
    except Exception as e:
        print(f"[!] Erreur lors du chargement: {e}")
        return
    
    print(f"[*] {len(packets)} paquets chargés")
    print("[*] Recherche des paquets de sortie (vibration)...\n")
    
    vibration_candidates = []
    
    for i, pkt in enumerate(packets):
        # Les paquets USB ont généralement ces caractéristiques
        if hasattr(pkt, 'load'):
            data = bytes(pkt.load)
            
            # Les commandes de vibration Xbox sont typiquement:
            # - Direction: Host -> Device (OUT)
            # - Endpoint: souvent 0x01 ou 0x02
            # - Taille: généralement 8-32 bytes
            
            if len(data) >= 4 and len(data) <= 64:
                # Afficher les paquets potentiellement intéressants
                hex_data = data.hex()
                print(f"Paquet #{i}: {hex_data}")
                
                # Pattern commun pour vibration Xbox: commence par 0x00 0x01 ou 0x03
                if data[0] in [0x00, 0x03, 0x09]:
                    vibration_candidates.append({
                        'index': i,
                        'data': data,
                        'hex': hex_data
                    })
    
    print(f"\n[*] {len(vibration_candidates)} candidats potentiels pour vibration")
    
    if vibration_candidates:
        print("\n=== Candidats de vibration ===")
        for c in vibration_candidates:
            print(f"  #{c['index']}: {c['hex']}")
            # Tenter de décoder
            decode_vibration_packet(c['data'])

def decode_vibration_packet(data):
    """Tente de décoder un paquet de vibration Xbox."""
    if len(data) < 4:
        return
    
    # Format Xbox One standard (pas forcément celui de Turtle Beach):
    # Byte 0: Report ID (0x09 pour vibration)
    # Byte 1: Sub-command
    # Byte 2: Left trigger motor
    # Byte 3: Right trigger motor  
    # Byte 4: Left motor (gros moteur)
    # Byte 5: Right motor (petit moteur)
    
    print(f"    Possible décodage:")
    print(f"      Report ID: 0x{data[0]:02X}")
    if len(data) > 1:
        print(f"      Byte 1: 0x{data[1]:02X}")
    if len(data) > 4:
        print(f"      Moteur gauche?: 0x{data[4]:02X} ({data[4]})")
    if len(data) > 5:
        print(f"      Moteur droit?: 0x{data[5]:02X} ({data[5]})")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nPour capturer avec Wireshark:")
        print("1. Lancez un jeu avec vibrations (ex: Forza, The Crew)")
        print("2. Capturez l'interface USBPcap")
        print("3. Filtrez par: usb.addr == \"X.Y.Z\" (adresse de votre manette)")
        print("4. Sauvegardez en .pcap")
        return
    
    analyze_pcap(sys.argv[1])

if __name__ == "__main__":
    main()
