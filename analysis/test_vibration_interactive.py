#!/usr/bin/env python3
"""
Test interactif de vibration XInput - Version améliorée
"""

import time
import sys

try:
    import XInput
except ImportError:
    print("Installez XInput: pip install git+https://github.com/Zuzu-Typ/XInput-Python.git")
    sys.exit(1)

def main():
    print("=" * 60)
    print("TEST VIBRATION XINPUT - Turtle Beach")
    print("=" * 60)
    
    # Trouver les manettes connectées
    connected = XInput.get_connected()
    print(f"\nÉtat des slots: {connected}")
    print("  (True = manette connectée, False = vide)")
    
    # Trouver l'index de la manette connectée
    controller_index = None
    for i, is_connected in enumerate(connected):
        if is_connected:
            controller_index = i
            print(f"\n✓ Manette trouvée au slot {i}")
            break
    
    if controller_index is None:
        print("\n✗ Aucune manette détectée!")
        return
    
    # Récupérer l'état pour confirmer
    try:
        state = XInput.get_state(controller_index)
        print(f"  État récupéré: OK (packet #{state.dwPacketNumber})")
    except Exception as e:
        print(f"  Erreur état: {e}")
        return
    
    print("\n" + "=" * 60)
    print("TESTS DE VIBRATION")
    print("=" * 60)
    
    tests = [
        ("Moteur GAUCHE 50%", 32767, 0),
        ("Moteur GAUCHE 100%", 65535, 0),
        ("Moteur DROIT 50%", 0, 32767),
        ("Moteur DROIT 100%", 0, 65535),
        ("LES DEUX 50%", 32767, 32767),
        ("LES DEUX 100%", 65535, 65535),
    ]
    
    for name, left, right in tests:
        print(f"\n[TEST] {name}")
        print(f"       Left={left}, Right={right}")
        input("       Appuyez sur ENTRÉE pour tester...")
        
        try:
            XInput.set_vibration(controller_index, left, right)
            print("       Vibration envoyée! (attend 1 sec)")
            time.sleep(1)
            XInput.set_vibration(controller_index, 0, 0)
            print("       Vibration arrêtée")
        except Exception as e:
            print(f"       ERREUR: {e}")
        
        response = input("       As-tu senti la vibration? (o/n): ").lower()
        if response == 'o':
            print("       ✓ OK!")
        else:
            print("       ✗ Pas de vibration détectée")
    
    # Test continu
    print("\n" + "=" * 60)
    print("TEST CONTINU (Ctrl+C pour arrêter)")
    print("=" * 60)
    
    try:
        intensity = 0
        direction = 1
        while True:
            XInput.set_vibration(controller_index, intensity, intensity)
            print(f"\r  Intensité: {intensity:5d} / 65535  ", end="", flush=True)
            
            intensity += direction * 5000
            if intensity >= 65535:
                intensity = 65535
                direction = -1
            elif intensity <= 0:
                intensity = 0
                direction = 1
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        XInput.set_vibration(controller_index, 0, 0)
        print("\n\nArrêté.")

if __name__ == "__main__":
    main()
