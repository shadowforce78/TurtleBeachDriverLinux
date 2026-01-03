#!/usr/bin/env python3
"""
Turtle Beach Xbox Controller - Linux Vibration Driver
PROTOCOLE DÉCOUVERT PAR REVERSE ENGINEERING USB

Format de commande de vibration (13 bytes):
    09 00 [SEQ] 09 00 0F [LT] [RT] [LEFT] [RIGHT] FF 00 EB

Où:
    - SEQ: Numéro de séquence (0x00-0xFF, incrémenté à chaque commande)
    - LT: Left Trigger motor (0-100)
    - RT: Right Trigger motor (0-100)  
    - LEFT: Left motor - gros moteur basses fréquences (0-100)
    - RIGHT: Right motor - petit moteur hautes fréquences (0-100)

Usage:
    python vibration.py --demo
    
    # Ou en import:
    from vibration import TurtleBeachController
    controller = TurtleBeachController()
    controller.connect()
    controller.vibrate(left=50, right=50)
    controller.disconnect()
"""

import time
import sys
import argparse
from typing import Optional

try:
    import hid
except ImportError:
    print("Erreur: hidapi non installé. Exécutez: pip install hidapi")
    sys.exit(1)

# IDs de la manette Turtle Beach
VENDOR_ID = 0x10F5
PRODUCT_ID = 0x7018


class TurtleBeachController:
    """Contrôleur de vibration pour manette Turtle Beach Xbox."""
    
    # Constantes du protocole (découvertes par reverse engineering)
    REPORT_ID = 0x09
    MOTOR_MASK = 0x0F  # Active tous les moteurs
    PACKET_SUFFIX = bytes([0xFF, 0x00, 0xEB])
    MAX_INTENSITY = 100  # Intensité max acceptée par la manette
    
    def __init__(self, vendor_id: int = VENDOR_ID, product_id: int = PRODUCT_ID):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device: Optional[hid.device] = None
        self.sequence = 0  # Compteur de séquence
        
    def connect(self) -> bool:
        """
        Connecte à la manette.
        
        Returns:
            True si connexion réussie, False sinon.
        """
        try:
            devices = hid.enumerate(self.vendor_id, self.product_id)
            
            if not devices:
                print(f"[!] Manette Turtle Beach non trouvée")
                print(f"    VID:0x{self.vendor_id:04X} PID:0x{self.product_id:04X}")
                self._list_available_devices()
                return False
            
            # Chercher l'interface appropriée
            target_device = None
            for dev in devices:
                print(f"[*] Interface {dev['interface_number']}: "
                      f"usage_page=0x{dev.get('usage_page', 0):04X}")
                # Généralement interface 0 pour les commandes
                if dev['interface_number'] == 0:
                    target_device = dev
            
            if not target_device:
                target_device = devices[0]
            
            self.device = hid.device()
            self.device.open_path(target_device['path'])
            self.device.set_nonblocking(1)
            
            print(f"[✓] Connecté: {self.device.get_product_string()}")
            self.sequence = 0
            return True
            
        except Exception as e:
            print(f"[!] Erreur de connexion: {e}")
            self._print_permission_help()
            return False
    
    def disconnect(self):
        """Déconnecte proprement."""
        if self.device:
            self.stop_vibration()
            self.device.close()
            self.device = None
            print("[✓] Déconnecté")
    
    def _build_vibration_command(self, left: int, right: int, 
                                  left_trigger: int = 0, right_trigger: int = 0) -> bytes:
        """
        Construit la commande de vibration selon le protocole découvert.
        
        Format: 09 00 [SEQ] 09 00 0F [LT] [RT] [L] [R] FF 00 EB
        """
        # Clamp les valeurs entre 0 et MAX_INTENSITY
        left = max(0, min(self.MAX_INTENSITY, left))
        right = max(0, min(self.MAX_INTENSITY, right))
        left_trigger = max(0, min(self.MAX_INTENSITY, left_trigger))
        right_trigger = max(0, min(self.MAX_INTENSITY, right_trigger))
        
        command = bytes([
            self.REPORT_ID,    # 0x09 - Report ID
            0x00,              # Toujours 0x00
            self.sequence,     # Numéro de séquence
            0x09,              # Toujours 0x09
            0x00,              # Toujours 0x00
            self.MOTOR_MASK,   # 0x0F - Masque moteurs (tous activés)
            left_trigger,      # Moteur gâchette gauche
            right_trigger,     # Moteur gâchette droite
            left,              # Moteur gauche (gros, basses fréquences)
            right,             # Moteur droit (petit, hautes fréquences)
        ]) + self.PACKET_SUFFIX  # FF 00 EB
        
        # Incrémenter la séquence (wrap à 256)
        self.sequence = (self.sequence + 1) & 0xFF
        
        return command
    
    def vibrate(self, left: int = 0, right: int = 0,
                left_trigger: int = 0, right_trigger: int = 0) -> bool:
        """
        Active la vibration.
        
        Args:
            left: Intensité moteur gauche (0-100)
            right: Intensité moteur droit (0-100)
            left_trigger: Intensité gâchette gauche (0-100)
            right_trigger: Intensité gâchette droite (0-100)
            
        Returns:
            True si commande envoyée avec succès.
        """
        if not self.device:
            print("[!] Non connecté")
            return False
        
        command = self._build_vibration_command(left, right, left_trigger, right_trigger)
        
        try:
            # Note: Sur certains systèmes, il faut ajouter 0x00 au début
            result = self.device.write(command)
            if result < 0:
                # Essayer avec un byte supplémentaire au début
                result = self.device.write(bytes([0x00]) + command)
            return result >= 0
        except Exception as e:
            print(f"[!] Erreur d'envoi: {e}")
            return False
    
    def stop_vibration(self) -> bool:
        """Arrête toute vibration."""
        return self.vibrate(0, 0, 0, 0)
    
    def pulse(self, intensity: int = 80, duration_ms: int = 200, 
              count: int = 1, motor: str = 'both'):
        """
        Fait pulser la vibration.
        
        Args:
            intensity: Force (0-100)
            duration_ms: Durée par pulse en ms
            count: Nombre de pulses
            motor: 'left', 'right', ou 'both'
        """
        for i in range(count):
            if motor == 'left':
                self.vibrate(left=intensity)
            elif motor == 'right':
                self.vibrate(right=intensity)
            else:
                self.vibrate(left=intensity, right=intensity)
            
            time.sleep(duration_ms / 1000)
            self.stop_vibration()
            
            if i < count - 1:
                time.sleep(duration_ms / 1000)
    
    def _list_available_devices(self):
        """Liste les périphériques HID disponibles."""
        print("\n[*] Périphériques HID disponibles:")
        for d in hid.enumerate():
            if d['vendor_id'] in [0x10F5, 0x045E]:
                print(f"    VID:0x{d['vendor_id']:04X} PID:0x{d['product_id']:04X} - "
                      f"{d.get('product_string', 'Unknown')}")
    
    def _print_permission_help(self):
        """Affiche l'aide pour les permissions Linux."""
        print("\n[?] Sur Linux, ajoutez les règles udev:")
        print("    sudo cp udev/99-turtlebeach.rules /etc/udev/rules.d/")
        print("    sudo udevadm control --reload-rules")
        print("    sudo udevadm trigger")
        print("    # Puis débranchez/rebranchez la manette")


def demo():
    """Démonstration interactive."""
    print("=" * 60)
    print("Turtle Beach Controller - Demo Vibration")
    print("Protocole: 09 00 [SEQ] 09 00 0F [LT] [RT] [L] [R] FF 00 EB")
    print("=" * 60)
    
    controller = TurtleBeachController()
    
    if not controller.connect():
        return 1
    
    try:
        tests = [
            ("Moteur GAUCHE (gros)", 80, 0, 0, 0),
            ("Moteur DROIT (petit)", 0, 80, 0, 0),
            ("Les DEUX moteurs", 60, 60, 0, 0),
            ("Gâchette GAUCHE", 0, 0, 80, 0),
            ("Gâchette DROITE", 0, 0, 0, 80),
            ("TOUT", 50, 50, 50, 50),
        ]
        
        for name, left, right, lt, rt in tests:
            print(f"\n[TEST] {name}")
            print(f"       L={left}, R={right}, LT={lt}, RT={rt}")
            
            controller.vibrate(left, right, lt, rt)
            time.sleep(0.7)
            controller.stop_vibration()
            time.sleep(0.3)
        
        print("\n[TEST] Pulse x3")
        controller.pulse(intensity=80, duration_ms=150, count=3)
        
        print("\n[✓] Demo terminée!")
        return 0
        
    except KeyboardInterrupt:
        print("\n[!] Interrompu")
        return 1
    finally:
        controller.disconnect()


def main():
    parser = argparse.ArgumentParser(description='Turtle Beach Controller Vibration')
    parser.add_argument('--demo', action='store_true', help='Lancer la démo')
    parser.add_argument('--left', '-l', type=int, default=0, help='Intensité moteur gauche (0-100)')
    parser.add_argument('--right', '-r', type=int, default=0, help='Intensité moteur droit (0-100)')
    parser.add_argument('--duration', '-d', type=float, default=1.0, help='Durée en secondes')
    parser.add_argument('--pulse', '-p', type=int, default=0, help='Nombre de pulses')
    
    args = parser.parse_args()
    
    if args.demo:
        return demo()
    
    if args.left == 0 and args.right == 0 and args.pulse == 0:
        parser.print_help()
        print("\nExemples:")
        print("  python vibration.py --demo")
        print("  python vibration.py --left 50 --right 50 --duration 2")
        print("  python vibration.py --pulse 3 --left 80")
        return 0
    
    controller = TurtleBeachController()
    if not controller.connect():
        return 1
    
    try:
        if args.pulse > 0:
            controller.pulse(
                intensity=max(args.left, args.right) or 80,
                count=args.pulse
            )
        else:
            controller.vibrate(args.left, args.right)
            time.sleep(args.duration)
            controller.stop_vibration()
    finally:
        controller.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
