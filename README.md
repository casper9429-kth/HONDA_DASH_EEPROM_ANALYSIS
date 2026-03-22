# Honda Civic 8th Gen EEPROM Tools

Reverse-engineering the **93C76 EEPROM** in Honda Civic 8th gen (2006–2012) instrument clusters.

Read, analyze, compare, and repair dashboard EEPROM data.

## Tools

Open any `.html` file in a browser. No install needed.

| Tool | File | What it does |
|------|------|-------------|
| **Mileage Editor** | [tools/mileage.html](tools/mileage.html) | Load a dump, see current km, change it, export |
| **Inspector** | [tools/inspector.html](tools/inspector.html) | Inspect one or compare multiple EEPROM dumps |
| **Repair Tool** | [tools/repair.html](tools/repair.html) | Detect corruption, fix known issues, toggle features |

## Quick Reference

| | Diesel (SMJ) | Petrol (SNA/SNB) |
|---|---|---|
| Header | `BA 65` | `FF 77` |
| Odometer formula | km = value x 31 | km = value x 32 |
| Odometer location | `0x180–0x1BF` | `0x180–0x1BF` |

**No global checksum.** Only per-entry word complements. See [docs/](docs/) for full details.

## Byte Swap

The CH341A reads the 93C76 in byte-swapped order. Every pair of bytes in the `.bin` file is reversed vs. native chip order:

```
Chip: AB CD  →  File: CD AB
```

All tools handle this automatically.

## Hardware

- **EEPROM**: 93C76 — 1024 bytes. Use Seiko S-93C76ADFJ-TB-U or Microchip 93C76**B** (not A!)
- **Programmer**: CH341A Mini Programmer + SOP8 clip (5V mod required, adapter rewiring required)
- **Computer**: x86 Windows PC (ARM Windows does not work with CH341A drivers)
- **Software**: [NeoProgrammer](https://github.com/YTEC-info/CH341A-Softwares) V2.2.0.10

See [docs/HARDWARE_SETUP.md](docs/HARDWARE_SETUP.md) for the complete step-by-step guide.

## Docs

- [EEPROM_MEMORY_MAP.md](docs/EEPROM_MEMORY_MAP.md) — Full 1024-byte memory map
- [ODOMETER_GUIDE.md](docs/ODOMETER_GUIDE.md) — Odometer encoding and modification
- [HARDWARE_SETUP.md](docs/HARDWARE_SETUP.md) — CH341A wiring, 5V mod, software
- [S93C76A.PDF](docs/S93C76A.PDF) — Seiko datasheet

## EEPROM Dumps

```
Files/
├── A_Petrol_SNB/     Petrol European trim
├── B_Petrol_SNA/     Petrol DX/EX/LX
├── C_Diesel_SMJ/     Diesel i-CTDi/i-DTEC
└── MY_CAR_Diesel/    Personal car dumps
```
