# Protocole de Vibration Turtle Beach Xbox Controller

**VID**: `0x10F5` (Turtle Beach Corporation)  
**PID**: `0x7018`

## Format de la Commande de Vibration

La commande de vibration fait **13 bytes** et est envoyée via USB HID Output Report.

### Structure du Paquet

```
Offset:  0    1    2    3    4    5    6    7    8    9   10   11   12
       +----+----+----+----+----+----+----+----+----+----+----+----+----+
Bytes: | 09 | 00 | SQ | 09 | 00 | 0F | LT | RT |  L |  R | FF | 00 | EB |
       +----+----+----+----+----+----+----+----+----+----+----+----+----+
```

### Description des Bytes

| Offset | Valeur | Description |
|--------|--------|-------------|
| 0 | `0x09` | Report ID (fixe) |
| 1 | `0x00` | Réservé (toujours 0x00) |
| 2 | `0x00-0xFF` | Numéro de séquence (incrémenté à chaque commande) |
| 3 | `0x09` | Sub-command (fixe) |
| 4 | `0x00` | Réservé (toujours 0x00) |
| 5 | `0x0F` | Masque des moteurs (0x0F = tous actifs) |
| 6 | `0x00-0x64` | **Left Trigger** - Vibration gâchette gauche (0-100) |
| 7 | `0x00-0x64` | **Right Trigger** - Vibration gâchette droite (0-100) |
| 8 | `0x00-0x64` | **Left Motor** - Gros moteur, basses fréquences (0-100) |
| 9 | `0x00-0x64` | **Right Motor** - Petit moteur, hautes fréquences (0-100) |
| 10 | `0xFF` | Suffixe (fixe) |
| 11 | `0x00` | Suffixe (fixe) |
| 12 | `0xEB` | Suffixe (fixe) |

### Exemples

**Vibration moteur gauche à 50%:**
```
09 00 00 09 00 0F 00 00 32 00 FF 00 EB
                        ^^ Left=50
```

**Vibration des deux moteurs à 100%:**
```
09 00 01 09 00 0F 00 00 64 64 FF 00 EB
                        ^^ ^^ Left=100, Right=100
```

**Arrêt de la vibration:**
```
09 00 02 09 00 0F 00 00 00 00 FF 00 EB
                        ^^ ^^ Left=0, Right=0
```

## Masque des Moteurs (Byte 5)

Le byte 5 (`0x0F`) est un masque binaire:

| Bit | Moteur |
|-----|--------|
| 0 | Left Trigger |
| 1 | Right Trigger |
| 2 | Left Motor |
| 3 | Right Motor |

`0x0F` = `0b00001111` = tous les moteurs actifs

## Notes d'Implémentation

1. **Numéro de séquence**: Doit être incrémenté à chaque commande (0x00 → 0xFF puis retour à 0x00)

2. **Intensité**: Les valeurs vont de 0 à 100 (pas 0-255 comme sur d'autres manettes)

3. **HID Interface**: Utiliser l'interface 0 du périphérique HID

4. **Linux**: Nécessite des règles udev pour accéder au périphérique sans sudo

## Données Brutes Capturées

Exemples extraits de la capture Wireshark:

```
# Vibration progressive (test continu)
09001d09000f00000000ff00eb  L=0,   R=0
09001e09000f00000707ff00eb  L=7,   R=7
09001f09000f00000f0fff00eb  L=15,  R=15
09002009000f00001616ff00eb  L=22,  R=22
09002109000f00001e1eff00eb  L=30,  R=30
...
09002b09000f00006464ff00eb  L=100, R=100

# Test moteur gauche seul
09001109000f00003100ff00eb  L=49, R=0
09001309000f00006400ff00eb  L=100, R=0

# Test moteur droit seul
09001509000f00000031ff00eb  L=0, R=49
09001709000f00000064ff00eb  L=0, R=100
```

---
*Protocole découvert le 3 janvier 2026 par reverse engineering USB avec Wireshark/USBPcap*
