# EEPROM Memory Map — Honda 93C76

Full reference for the 93C76 EEPROM (1024 bytes / 512 × 16-bit words) as used in Honda Civic 8th gen (2006–2012) instrument clusters.

> **Chip**: The datasheet in this repo is the **Seiko Instruments S-93C76A** (automotive grade, −40°C to +105°C). The Microchip 93C76 is a functionally compatible alternative. Both store data as 512 × 16-bit words. Initial factory state of all addresses is `FFFFh`.

> All addresses and hex values are in **native chip word order** (byte-swapped from the raw `.bin` file). See README for the byte-swap explanation.

---

## Memory Map Overview

| Address Range | Size | Region | Notes |
|--------------|------|--------|-------|
| `0x000–0x04F` | 80 B | Vehicle Configuration Header | Model-specific calibration |
| `0x050–0x05F` | 16 B | Static Configuration | Mostly fixed constants |
| `0x060–0x095` | 54 B | Operational Counters | Running sensor data |
| `0x096–0x0AB` | 22 B | Zero-Padded Region | All `0x00` |
| `0x0AC–0x0E5` | 58 B | Extended Data | Zeros in A/B; active in Diesel |
| `0x0E6–0x0EF` | 10 B | Padding | All `0xFF` |
| `0x0F0–0x10F` | 32 B | Boundary Markers | Fixed pattern `00…00 F0 FF FF F0 00…00` |
| `0x110–0x11F` | 16 B | Zero Block | All `0x00` |
| `0x120–0x12F` | 16 B | FF/00 Marker Block | Fixed pattern |
| `0x130–0x13F` | 16 B | Fuel/Sensor Calibration | Contains magic number `5A 88 E4 F6` |
| `0x140–0x14F` | 16 B | FF Block | All `0xFF` |
| `0x150–0x177` | 40 B | DTC / Diagnostic Codes | Active in Group B; zeroed in A & C |
| `0x178–0x17F` | 8 B | FF Boundary | All `0xFF` — marks start of odometer |
| **`0x180–0x1BF`** | **64 B** | **Odometer Block** | **16 × 4-byte rolling entries** |
| `0x1C0–0x1E7` | 40 B | Gauge Calibration / Trip | Last gauge positions before power-off |
| `0x1E8–0x1F3` | 12 B | Running Counters | Trip, service, ignition counters |
| `0x1F4–0x1FF` | 12 B | Status / Flags | Model flags and boundary marker |
| `0x200–0x20F` | 16 B | System Configuration | Model/version flags |
| `0x210–0x24F` | 64 B | Extended Config | All `0xFF` in A/B; active in Diesel |
| `0x250–0x27F` | 48 B | Sensor Calibration Tables | Fuel, temperature, speed sensor cal |
| `0x280–0x29F` | 32 B | Calibration / Flags | Mixed calibration data |
| `0x2A0–0x2BF` | 32 B | Service / Maintenance Data | Service interval tracking |
| `0x2C0–0x30F` | 80 B | Extended Data | All `0xFF` in A/B; active in Diesel |
| `0x310–0x385` | 118 B | Unused / Reserved | All `0xFF` |
| **`0x386–0x397`** | **18 B** | **Part Number / Serial** | ASCII part number + board revision |
| `0x398–0x399` | 2 B | Part Number Metadata | Per-model config bytes (not a checksum) |
| `0x39A–0x3DF` | 70 B | Reserved | `0x00` and `0xFF` padding |
| `0x3E0–0x3E9` | 10 B | FF Padding | All `0xFF` |
| `0x3EA–0x3EB` | 2 B | Tail Status Value | Accumulated state (not a checksum) |
| `0x3EC–0x3F1` | 6 B | FF Padding | All `0xFF` |
| **`0x3F2–0x3FB`** | **10 B** | **Configuration Footer** | Small numeric config values |
| `0x3FC–0x3FF` | 4 B | FF Terminator | All `0xFF` |

---

## Region Details

### Vehicle Configuration Header — `0x000–0x04F`

The first 2 bytes identify the cluster variant:

| Value (native) | Variant |
|----------------|---------|
| `FF 77` | Petrol (Groups A and B) |
| `BA 65` | Diesel (Group C) |

Selected constants found at fixed offsets within this region:

| Offset | Value | Notes |
|--------|-------|-------|
| `0x002` | `FE` | Always identical across all dumps |
| `0x007` | `7B` | Always identical |
| `0x00E` | `FF` | Always identical |
| `0x010` | `57` (= 87 dec) | Protocol/version marker |
| `0x017` | `D7` | Always identical |
| `0x01B` | `FB` | Always identical |
| `0x01F` | `01` | Always identical |
| `0x022–0x025` | `0A 19 5F FF` | Always identical |
| `0x028–0x029` | `07 D0` (= 2000) | Clock base constant |
| `0x00C` | Varies | Feature flags: `0x9F` (A), `0xAF` (B), `0x7F`/`0xBF` (C) |
| `0x012` | Varies | Trim-level features: `0x96` (A), `0x26` (B), `0x31`/`0xF1` (C) |

The remaining bytes contain RPM/speed/fuel gauge scaling factors specific to each model.

---

### Odometer Block — `0x180–0x1BF`

See [ODOMETER_GUIDE.md](ODOMETER_GUIDE.md) for full details. Summary:

- **16 × 4-byte entries** in a rolling ring
- Each entry: `[HI] [LO] [~HI] [~LO]` where `Word0 XOR Word1 = 0xFFFF`
- `km = BE16 × 31` (diesel) or `km ≈ BE16 × 32` (petrol)
- The slot with a broken complement is the active write position

---

### Part Number / Serial — `0x386–0x399`

In native word order, this reads as clean ASCII:

| Offset | Contents | Description |
|--------|----------|-------------|
| `0x386–0x38B` | `78020S` | Honda instrument cluster prefix (identical in all dumps) |
| `0x38C–0x38D` | `NB` / `NA` / `MJ` | Model code identifying the variant |
| `0x38E–0x38F` | Version bytes | `b`+`07` (SNB), `a`+`07` (SNA), `i`+`87` (SMJ) |
| `0x390–0x395` | ASCII | Board revision: `G2 11 1M` (A), `C1 14 1M` (B), `G1 13 1M` (C) |
| `0x396–0x397` | `FF FF` | Padding |
| `0x398–0x399` | Config bytes | `2E 09` (A), `2F 0B` (B), `2A 08` (C) — not a checksum |

Decoded Honda OEM part numbers:
- Group A → **78120-SNB-xxx**
- Group B → **78120-SNA-xxx**
- Group C → **78120-SMJ-xxx**

---

### Fuel / Sensor Calibration — `0x130–0x13F`

```
Native: 00 00 00 00 00 00  5A 88 E4 F6  FF FF  [xx xx]  00 C0
```

| Offset | Value | Notes |
|--------|-------|-------|
| `0x136–0x139` | `5A 88 E4 F6` | Fixed magic number — identical across ALL 7 dumps |
| `0x13C–0x13D` | `28 28` (petrol) / `14 14` (diesel) | Fuel gauge scaling (40 vs 20) |

---

### DTC / Diagnostic Codes — `0x150–0x177`

- **Groups A and C**: All `0x00` — no stored codes
- **Group B** (both files): Contains active fault code data

```
Native (Group B):
0x154: A4 D3 28 3A 03 65 73 C4 28 4F 0B D0
0x160: 47 C5 28 0F 00 A5 20 6D 28 2F 0B 4A
0x16C: 47 C5 28 0F 00 A5
```

Safe to zero out to clear stored DTCs.

---

### Gauge Calibration / Trip Data — `0x1C0–0x1E7`

Stores the last gauge needle positions before power-off as paired values:

```
Format per gauge: [VALUE] [STATUS_FLAGS]
```

Status flag byte meanings: `0x00` = idle, `0x02` = last reading while driving, `0xE0` = service snapshot, `0xE2` = full operational snapshot.

| Offset | Description | Example (185000.bin, native) |
|--------|-------------|------------------------------|
| `0x1C0–0x1C3` | Gauge needle #1 | `00 5D 02 5D` |
| `0x1C8–0x1CB` | Gauge needle #3 | `00 32 02 32` (= 50) |
| `0x1CC–0x1CF` | Gauge needle #4 | `00 31 02 31` (= 49) |
| `0x1D0–0x1D3` | Speed gauge | `00 52 E2 52` (= 82) |
| `0x1D4–0x1D7` | Temperature gauge | `00 44 E0 44` (= 68) |
| `0x1D8–0x1DB` | RPM gauge | `00 48 E0 48` (= 72) |
| `0x1DC–0x1DF` | Fuel gauge | `00 01 E2 01` |
| `0x1E0–0x1E3` | Trip A | `00 1D E0 1D` (= 29) |
| `0x1E4–0x1E7` | Trip B | `00 32 E2 32` (= 50) |

> **Parity**: The VALUE bytes (even offsets) across the entire gauge block XOR to `0x00`. Maintain this when editing.
>
> **Self-calibration**: The cluster re-calibrates gauges from live sensor data within seconds of engine start. Setting all values to `0x00` is safe.

---

### Running Counters — `0x1E8–0x1F3`

Six 16-bit words that track operational state. None scale linearly with mileage — they wrap, plateau, and reset independently.

| Offset | Description |
|--------|-------------|
| `0x1E8–0x1E9` | Rolling counter (fuel injection events — wraps at 65535) |
| `0x1EA–0x1EB` | Trip distance counter (resets between trips) |
| `0x1EC–0x1ED` | Service interval counter (resets periodically) |
| `0x1EE–0x1EF` | Accumulated operating time / engine hours |
| `0x1F0–0x1F1` | Ignition cycle counter |
| `0x1F2–0x1F3` | DPF regen counter or fuel average |

Safe to zero out — resets trip/service counters without affecting odometer.

---

### System Configuration — `0x200–0x20F`

```
Petrol (A/B): BF FF 05 32 32 02 FF FF 39 47 FF FF FF FF FF FF
Diesel (C):   7F FF 05 00 32 02 FF FF 31 B5 32 32 05 0A FF FD
```

---

### Sensor Calibration Tables — `0x250–0x27F`

| Offset | Value | Description |
|--------|-------|-------------|
| `0x252–0x253` | `78 04` | Fuel level sensor calibration |
| `0x258–0x259` | `08 7C` (= 2172) | Calibration constant |
| `0x264–0x265` | `65` (petrol) / `67` (diesel) + `A1` | Temperature sensor calibration |
| `0x26C–0x26D` | `02`/`03` + `3B`/`39` | Fuel gauge calibration (model-specific) |
| `0x27A–0x27B` | `0B 3C` (= 2876) | Fixed constant |
| `0x27C–0x27D` | `64 FF` | Fixed constant (0x64 = 100) |

---

### Tail Status Value — `0x3EA–0x3EB`

| Group | Native Value | Decimal |
|-------|-------------|---------|
| A (both files) | `55 56` | 21,846 |
| B (both files) | `1F 10` | 7,952 |
| C (88k/92k km) | `DD B0` | 56,752 |
| C (183k km) | `6E EC` | 28,396 |

Not a checksum. Likely tracks total ignition cycles or operating hours. Consistent within each group. Copy from donor when synthesizing a new image.

---

### Configuration Footer — `0x3F2–0x3FB`

10 bytes encoding display settings and warning thresholds:

| Group | Native bytes |
|-------|-------------|
| A | `00 03 00 01 00 02 00 01 01 04` |
| B | `03 0F 00 01 00 01 00 01 01 06` |
| C (183k) | `03 82 00 00 01 07 00 07 05 04` |
| C (88k/92k) | `02 6D 00 00 01 07 00 07 05 04` |

Copy from donor — unknown function, do not modify.

---

## Diesel vs. Petrol Differences

| Feature | Petrol (SNA/SNB) | Diesel (SMJ) |
|---------|-----------------|-------------|
| Header ID | `FF 77` | `BA 65` |
| Odometer multiplier | × 32 | × 31 |
| `0x0AC–0x0E5` | Unused (`0x00`/`0xFF`) | Active diesel data (DPF, EGR, turbo) |
| `0x210–0x24F` | All `0xFF` | Active config |
| `0x2C0–0x30F` | All `0xFF` | Active data |
| Fuel gauge scaling | `28 28` (= 40) | `14 14` (= 20) |
| Service data `0x2A8` | Active | Cleared |
| Static config byte `0x05B` | `9B` | `5B` |

---

## Unused Regions

Approximately 60% of the EEPROM is `0xFF` (erased/unused):

| Range | Size |
|-------|------|
| `0x0C0–0x0EF` (A/B only) | 48 B |
| `0x140–0x14F` | 16 B |
| `0x2C0–0x30F` (A/B only) | 80 B |
| `0x310–0x385` | 118 B |
| `0x39A–0x3DF` | ~70 B |
| `0x3C0–0x3E0` | 32 B |
