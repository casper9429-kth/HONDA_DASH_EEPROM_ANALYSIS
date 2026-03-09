# Honda Civic Dashboard EEPROM Analysis

Reverse-engineering project for the **93C76** EEPROM found in Honda Civic 8th gen (2006–2012) instrument clusters. The goal is to read, analyze, and repair/modify dashboard EEPROM data — primarily odometer values.

> **Chip manufacturer note**: The 93C76 is made by multiple manufacturers. The datasheet in this repo is the **Seiko Instruments S-93C76A**. The more common reference is the **Microchip 93C76**. They are functionally identical in storage (512 × 16-bit words) but differ on Pin 6 — see [HARDWARE_SETUP.md](HARDWARE_SETUP.md).

---

## Hardware

| Component | Details |
|-----------|---------|
| **Dashboard** | Honda Civic 8th gen (FD/FK/FN), 2006–2012 |
| **EEPROM** | 93C76 — 8 Kbit, 512 × 16-bit words (1024 bytes). Variants: Seiko S-93C76A or Microchip 93C76 |
| **Programmer** | KeeYees S018 kit (model JK11-C1) — CH341A USB Programmer + SOP8 Test Clip + adapters |
| **Host OS** | Windows 11 ARM via VMware Fusion Pro on Apple Silicon — Windows required for NeoProgrammer (macOS ch341eeprom lacks Microwire CS support for 93C76) |

---

## Critical: Byte Swap

The CH341A reads in **8-bit mode**, but the 93C76 is a **16-bit word chip**. Every pair of bytes is swapped in the raw `.bin` file vs. the chip's native word order.

```
Chip stores:  AB CD  →  .bin file contains:  CD AB
```

All hex values in the documentation use **native word order** (byte-swapped from the raw file). When writing back, the programmer handles the swap automatically.

---

## Cluster Variants

Three firmware variants were analyzed across 7 dumps:

| Group | Part Code | Honda OEM | Type | Mileage Samples |
|-------|-----------|-----------|------|----------------|
| **A** | SNB | 78120-SNB-xxx | Petrol (European trim) | 185k, 200k km |
| **B** | SNA | 78120-SNA-xxx | Petrol (DX/EX/LX) | 235k, 369k km |
| **C** | SMJ | 78120-SMJ-xxx | **Diesel** (i-CTDi/i-DTEC) | 88k, 92k, 184k km |

Groups A and B share the same header byte (`FF 77`). Group C (diesel) is distinctly different (`BA 65`).

---

## Key Findings

| Finding | Detail |
|---------|--------|
| **Odometer location** | `0x180–0x1BF` — 16 × 4-byte rolling entries |
| **Odometer formula** | `km = BE16 × 31` (diesel) · `km ≈ BE16 × 32` (petrol) |
| **Integrity check** | Per-entry word complement only — no global CRC |
| **No global checksum** | Bytes at `0x398`, `0x3EA`, `0x3F2` are config values, not checksums |
| **No VIN/immobilizer** | These are stored on the ECU/BCM, not in this chip |
| **Unused space** | ~60% of the EEPROM is `0xFF` (erased/unused) |
| **Part number** | At `0x386` in ASCII: `78020S` + `NB`/`NA`/`MJ` |

---

## Repository Structure

```
Files/
├── A_Petrol_SNB/       Honda Civic petrol SNB variant dumps
├── B_Petrol_SNA/       Honda Civic petrol SNA variant dumps
├── C_Diesel_SMJ/       Honda Civic diesel SMJ variant dumps
├── corrupted/          Corrupted EEPROM dumps (reference)
└── my_car_corrupted/   Personal car's corrupted dumps

HARDWARE_SETUP.md       Wiring guide, adapter build, software setup
EEPROM_MEMORY_MAP.md    Full reference of all memory regions (0x000–0x3FF)
ODOMETER_GUIDE.md       Odometer encoding, formulas, modification guide
```

---

## Quick Start: Modifying the Odometer

1. Pick a donor `.bin` file matching your cluster variant (A/B/C)
2. Calculate the odometer word: `value = target_km ÷ 31` (diesel) or `÷ 32` (petrol)
3. Write all 16 × 4-byte slots at `0x180–0x1BF` with `[HI] [LO] [~HI] [~LO]`
4. No other bytes need updating — there is no global checksum

See [ODOMETER_GUIDE.md](ODOMETER_GUIDE.md) for the full procedure with examples.
