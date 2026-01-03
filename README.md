# Turtle Beach Xbox Controller - Linux Vibration Driver

## 🎮 Objectif
Driver de vibration pour la manette Turtle Beach Xbox One (VID: 10F5, PID: 7018) sur Linux.

**✅ Protocole découvert par reverse engineering USB !**

## 📋 Protocole de Vibration

Format: `09 00 [SEQ] 09 00 0F [LT] [RT] [LEFT] [RIGHT] FF 00 EB` (13 bytes)

| Byte | Description | Valeurs |
|------|-------------|---------|
| 0-1 | Header | `09 00` |
| 2 | Séquence | `00-FF` |
| 3-5 | Config | `09 00 0F` |
| 6 | Gâchette gauche | `0-100` |
| 7 | Gâchette droite | `0-100` |
| 8 | **Moteur gauche** (gros) | `0-100` |
| 9 | **Moteur droit** (petit) | `0-100` |
| 10-12 | Suffixe | `FF 00 EB` |

Voir [docs/PROTOCOL.md](docs/PROTOCOL.md) pour les détails complets.

## 🔧 Installation (Linux)

```bash
# 1. Installer hidapi
pip install hidapi

# 2. Configurer les permissions udev
sudo cp linux_driver/udev/99-turtlebeach.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

# 3. Débrancher/rebrancher la manette
```

## 🚀 Utilisation

### En ligne de commande

```bash
cd linux_driver

# Démo interactive
python vibration.py --demo

# Vibration personnalisée
python vibration.py --left 50 --right 50 --duration 2

# Pulse
python vibration.py --pulse 3 --left 80
```

### En Python

```python
from vibration import TurtleBeachController

controller = TurtleBeachController()
controller.connect()

# Vibration simple
controller.vibrate(left=50, right=50)

# Avec gâchettes
controller.vibrate(left=80, right=40, left_trigger=30, right_trigger=30)

# Pulse
controller.pulse(intensity=80, duration_ms=200, count=3)

# Arrêt
controller.stop_vibration()
controller.disconnect()
```

## 📁 Structure du projet

```
├── captures/                    # Fichiers Wireshark
│   └── capture_vibration.pcapng
├── analysis/                    # Scripts d'analyse Windows
│   ├── analyze_capture.py
│   ├── capture_guide.py
│   ├── test_vibration_windows.py
│   └── test_vibration_interactive.py
├── linux_driver/                # Driver Linux
│   ├── vibration.py             # ← Script principal
│   └── udev/
│       └── 99-turtlebeach.rules
├── docs/
│   └── PROTOCOL.md              # Documentation du protocole
└── README.md
```

## 🔬 Informations techniques

| Propriété | Valeur |
|-----------|--------|
| Vendor ID | `0x10F5` (Turtle Beach) |
| Product ID | `0x7018` |
| Type | Xbox Controller (XInput) |
| Intensité max | 100 (pas 255!) |



<!-- Test linux -->
# 1. Installer hidapi
pip install hidapi

# 2. Permissions
sudo cp udev/99-turtlebeach.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
# Débrancher/rebrancher la manette

# 3. Tester
python vibration.py --demo