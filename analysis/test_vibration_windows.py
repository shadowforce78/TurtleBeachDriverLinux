#!/usr/bin/env python3
"""
Test de vibration sur Windows pour la manette Turtle Beach.
Ce script permet de tester si on peut envoyer des commandes de vibration
via différentes méthodes (XInput, HID direct).

Requis:
    pip install pywinusb xinput-python hidapi
"""

import time
import sys

# Turtle Beach Controller IDs
VENDOR_ID = 0x10F5
PRODUCT_ID = 0x7018

def test_xinput():
    """Test via XInput (méthode standard Windows)."""
    print("\n=== Test XInput ===")
    try:
        import XInput as xinput
        
        controllers = xinput.get_connected()
        print(f"Manettes XInput connectées: {controllers}")
        
        if controllers:
            controller_id = controllers[0]
            print(f"Test vibration sur manette {controller_id}...")
            
            # Vibration: 0-65535 pour chaque moteur
            xinput.set_vibration(controller_id, 32767, 32767)
            print("  Vibration ON (50%)")
            time.sleep(1)
            
            xinput.set_vibration(controller_id, 65535, 65535)
            print("  Vibration ON (100%)")
            time.sleep(1)
            
            xinput.set_vibration(controller_id, 0, 0)
            print("  Vibration OFF")
            
            return True
        else:
            print("  Aucune manette XInput détectée")
            return False
            
    except ImportError:
        print("  XInput non disponible (pip install xinput-python)")
        return False
    except Exception as e:
        print(f"  Erreur XInput: {e}")
        return False

def test_hid_direct():
    """Test via HID direct avec hidapi."""
    print("\n=== Test HID Direct (hidapi) ===")
    try:
        import hid
        
        # Lister tous les périphériques HID
        print("Recherche de la manette Turtle Beach...")
        devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
        
        if not devices:
            print(f"  Manette non trouvée (VID:0x{VENDOR_ID:04X} PID:0x{PRODUCT_ID:04X})")
            print("  Périphériques HID disponibles:")
            for d in hid.enumerate():
                if d['vendor_id'] in [0x10F5, 0x045E]:  # Turtle Beach ou Microsoft
                    print(f"    - VID:0x{d['vendor_id']:04X} PID:0x{d['product_id']:04X} - {d['product_string']}")
            return False
        
        for dev_info in devices:
            print(f"  Trouvé: {dev_info['product_string']} (interface {dev_info['interface_number']})")
            
            try:
                device = hid.device()
                device.open_path(dev_info['path'])
                device.set_nonblocking(1)
                
                print(f"    Connecté! Manufacturer: {device.get_manufacturer_string()}")
                print(f"    Product: {device.get_product_string()}")
                
                # Essayer différents formats de commande de vibration
                # Format Xbox One standard
                vibration_commands = [
                    # Format 1: Xbox One standard
                    bytes([0x09, 0x00, 0x00, 0x09, 0x00, 0x0F, 0xFF, 0xFF, 0x00, 0x00]),
                    # Format 2: Simplifié
                    bytes([0x00, 0x01, 0x0F, 0xFF, 0xFF, 0x00, 0x00, 0x00]),
                    # Format 3: Autre variante
                    bytes([0x03, 0x0F, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00]),
                ]
                
                for i, cmd in enumerate(vibration_commands):
                    print(f"    Essai commande {i+1}: {cmd.hex()}")
                    try:
                        device.write(cmd)
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"      Erreur: {e}")
                
                # Arrêter vibration
                stop_cmd = bytes([0x09, 0x00, 0x00, 0x09, 0x00, 0x0F, 0x00, 0x00, 0x00, 0x00])
                device.write(stop_cmd)
                
                device.close()
                
            except Exception as e:
                print(f"    Erreur ouverture: {e}")
        
        return True
        
    except ImportError:
        print("  hidapi non disponible (pip install hidapi)")
        return False
    except Exception as e:
        print(f"  Erreur HID: {e}")
        return False

def test_pywinusb():
    """Test via pywinusb (Windows uniquement)."""
    print("\n=== Test pywinusb ===")
    try:
        import pywinusb.hid as hid
        
        # Chercher la manette
        devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()
        
        if not devices:
            print(f"  Manette non trouvée")
            return False
        
        for device in devices:
            print(f"  Trouvé: {device.product_name}")
            
            device.open()
            
            # Afficher les rapports disponibles
            print("  Rapports de sortie disponibles:")
            for report in device.find_output_reports():
                print(f"    Report ID: {report.report_id}, Taille: {len(report)}")
            
            device.close()
        
        return True
        
    except ImportError:
        print("  pywinusb non disponible (pip install pywinusb)")
        return False
    except Exception as e:
        print(f"  Erreur pywinusb: {e}")
        return False

def main():
    print("=" * 60)
    print("Test de vibration - Manette Turtle Beach Xbox")
    print(f"VID: 0x{VENDOR_ID:04X}, PID: 0x{PRODUCT_ID:04X}")
    print("=" * 60)
    
    # Tester les différentes méthodes
    xinput_ok = test_xinput()
    hid_ok = test_hid_direct()
    pywinusb_ok = test_pywinusb()
    
    print("\n" + "=" * 60)
    print("Résumé:")
    print(f"  XInput:   {'✓' if xinput_ok else '✗'}")
    print(f"  HID:      {'✓' if hid_ok else '✗'}")
    print(f"  pywinusb: {'✓' if pywinusb_ok else '✗'}")
    print("=" * 60)
    
    if xinput_ok:
        print("\n✓ XInput fonctionne! Les vibrations devraient marcher.")
        print("  Le problème sur Linux vient du driver/kernel.")

if __name__ == "__main__":
    main()
