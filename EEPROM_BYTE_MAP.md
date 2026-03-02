# Honda 93c76 EEPROM — Complete Byte Map

> **Chip**: Microchip 93C76 — 8 Kbit (1024 bytes / 512 × 16-bit words) Serial EEPROM  
> **Vehicles**: Honda Civic 8th gen (FD/FK/FN) instrument clusters, 2006–2012  
> **Files analyzed**: 7 dumps with known mileages (88,108 – 369,475 km)

> [!WARNING]
> **8-Bit Reader / 16-Bit Chip**: The 93c76 stores data as **16-bit words** but the CH341A programmer reads in 8-bit mode, causing **every pair of bytes to be swapped** in the raw `.bin` files. All hex values in this document are presented in the chip's **native 16-bit word order** (i.e., byte-swapped from the raw dump). When reading or writing `.bin` files with your programmer, remember that each byte pair is reversed in the file compared to what's shown here.

> [!NOTE]
> **Proof of byte-swap**: In the raw `.bin` dump, the part number reads `8702S0BN`. After swapping each byte pair to native word order, it reads `7820 0S NB` → `78200SNB`, which matches Honda's OEM catalog format `78120-SNB-xxx`.

---

## File Groupings

The 7 dumps cluster into **3 vehicle groups** based on shared headers and part numbers:

| Group | Part Code | Honda OEM | Board Rev | Files | Header (native) |
|-------|----------|-----------|-----------|-------|------------------|
| **A** (Petrol) | **SNB** | 78120-**SNB**-xxx | `G2 11 1M` | `185000.bin`, `199954km.bin` | `FF 77` |
| **B** (Petrol) | **SNA** | 78120-**SNA**-xxx | `C1 14 1M` | `235...k.bin`, `373171km.bin` | `FF 77` |
| **C** (Diesel) | **SMJ** | 78120-**SMJ**-xxx | `G1 13 1M` | `183523km.bin`, `88108.bin`, `92054.bin` | `BA 65` |

- **SNA** = Honda Civic 8th gen (FD) sedan — base/standard trim
- **SNB** = Honda Civic 8th gen (FD) sedan — different trim or European market variant
- **SMJ** = Honda Civic 8th gen (FK/FN) — **diesel** variant (European i-CTDi/i-DTEC)

Groups A and B share the same first 2 bytes (`77 FF`) but differ in their part number suffix and header details. Group C (diesel) has a distinctly different header and much more data in the mid-range regions.

The board revision codes (`2G111M`, `1C141M`, `1G131M`) identify the physical PCB: the leading digit is the hardware **revision**, the letter (**G**/**C**) is the **board layout variant**, the 3-digit number is the **board version**, and trailing **M** is common to all.

---

## Complete Memory Map (0x000 – 0x3FF)

### Overview Table

| Offset Range | Size | Region | Varies? | Description |
|-------------|------|--------|---------|-------------|
| `0x000–0x04F` | 80 B | **Vehicle Configuration / Calibration Header** | Partially | Firmware config, model-specific calibration |
| `0x050–0x05F` | 16 B | **Static Configuration** | Mostly same | Fixed constants, partially identical across all files |
| `0x060–0x095` | 54 B | **Operational Data / Counters** | Yes | Running counters, sensor data, operational metrics |
| `0x096–0x0AB` | 22 B | **Zero-Padded Region 1** | Same | All `0x00` across all files |
| `0x0AC–0x0E5` | 58 B | **Extended Data (Model-Dep.)** | Varies | All `0x00`/`0xFF` in Groups A/B; active data in Group C |
| `0x0E6–0x0EF` | 10 B | **Padding** | Same | All `0xFF` |
| `0x0F0–0x10F` | 32 B | **Boundary Markers** | Same | `00...00 F0 FF FF F0 00...00` — fixed pattern |
| `0x110–0x11F` | 16 B | **Zero Block** | Same | All `0x00` |
| `0x120–0x12F` | 16 B | **FF/00 Marker Block** | Same | `00 00 FF FF FF FF 00 00 00 FF FF 00 00 00 00 00` |
| `0x130–0x13F` | 16 B | **Fuel / Sensor Calibration** | Partially | Contains `88 5A F6 E4` constant + model-specific bytes |
| `0x140–0x14F` | 16 B | **FF Block** | Same | All `0xFF` |
| `0x150–0x17F` | 48 B | **DTC / Diagnostic Codes** | Varies | Active in Group B; zeroed in A & C |
| `0x178–0x17F` | 8 B | **Boundary (FF)** | Same | All `0xFF` — marks start of odometer block |
| `0x180–0x1BF` | 64 B | **⭐ ODOMETER BLOCK** | **Yes** | 16 × 4-byte entries; main mileage storage |
| `0x1C0–0x1E7` | 40 B | **Gauge Calibration / Trip Data** | Yes | Paired values for gauge needles / trip counters |
| `0x1E8–0x1F3` | 12 B | **Running Counters** | Yes | Trip or service counters |
| `0x1F4–0x1FF` | 12 B | **Status / Flags** | Partially | Flags, status bits, and model identifiers |
| `0x200–0x20F` | 16 B | **System Configuration** | Partially | Model/version flags (differs between groups) |
| `0x210–0x24F` | 64 B | **Extended Config (Model-Dep.)** | Varies | All `0xFF` in A/B; active config in Group C |
| `0x250–0x27F` | 48 B | **Sensor Calibration Tables** | Partially | Fuel gauge, temperature tables — partially shared |
| `0x280–0x29F` | 32 B | **Calibration / Flags** | Partially | Mixed calibration data |
| `0x2A0–0x2BF` | 32 B | **Service / Maintenance Data** | Varies | Service history counters |
| `0x2C0–0x30F` | 80 B | **Extended Data (Model-Dep.)** | Varies | All `0xFF` in A/B; active in Group C |
| `0x310–0x385` | 118 B | **Unused / Reserved** | Same | All `0xFF` |
| `0x386–0x397` | 18 B | **⭐ PART NUMBER / SERIAL** | Varies by model | ASCII part number + version |
| `0x398–0x399` | 2 B | **Part Number Metadata** | Per-model | Version/metadata bytes (NOT a checksum) |
| `0x39A–0x3DF` | 70 B | **Reserved / FF Block** | Mostly same | `0x00` and `0xFF` padding |
| `0x3E0–0x3E9` | 10 B | **FF Padding** | Same | All `0xFF` |
| `0x3EA–0x3EB` | 2 B | **Configuration / Status** | Varies | Accumulated state value (NOT a checksum) |
| `0x3EC–0x3F1` | 6 B | **FF Padding** | Same | All `0xFF` |
| `0x3F2–0x3FB` | 10 B | **⭐ Configuration Footer** | Varies | Small numeric config values |
| `0x3FC–0x3FF` | 4 B | **FF Terminator** | Same | All `0xFF` |

---

## Region Deep Dives

### 🔑 Odometer Block (0x180 – 0x1BF)

This is the most critical region — **64 bytes** organized as **16 repeating 4-byte entries**.

#### Structure

Each 4-byte entry consists of **two 16-bit words**: a value word and its complement.

In **native word order** (as on the chip): `[HI] [LO] [~HI] [~LO]`

**Rule**: Word0 ⊕ Word1 = 0xFFFF (the second word is the bitwise inverse of the first)

```
Native entry:    [HI] [LO] [~HI] [~LO]
Raw dump order:  [LO] [HI] [~LO] [~HI]   (byte-swapped by 8-bit programmer)
```

#### Odometer Encoding

The mileage value is stored as a **big-endian 16-bit** value (BE16) in native word order. Read the first two bytes of the entry as a standard BE16 integer, then multiply:

**`km = BE16 × multiplier`**

| File | Known KM | Native Pattern | BE16 | × 31 | × 31 err | × 32 | × 32 err |
|------|---------|----------------|------|------|----------|------|----------|
| 88108.bin | 88,108 | `0B 1B F4 E4` | 2,843 | 88,133 | **0.03%** | 90,976 | 3.3% |
| 92054.bin | 92,054 | `0B 9C F4 63` | 2,972 | 92,132 | **0.08%** | 95,104 | 3.3% |
| 183523km.bin | 183,523 | `17 1C E8 E3` | 5,916 | 183,396 | **0.07%** | 189,312 | 3.2% |
| 185000.bin | 185,000 | `16 C9 E9 36` | 5,833 | — | 2.3% | 186,656 | 0.9% |
| 199954km.bin | 199,954 | `18 AA E7 55` | 6,314 | — | 2.1% | 202,048 | 1.0% |
| 235...k.bin | 235,000 | `1C CE E3 31` | 7,374 | — | 2.7% | 235,968 | 0.4% |
| 373171km.bin | 369,475 | `2D 82 D2 7D` | 11,650 | — | 2.3% | 372,800 | 0.9% |

> [!IMPORTANT]
> **Two distinct multipliers exist**:
> - **Group C (Diesel / SMJ)**: **`km = BE16 × 31`** — yields 0.03–0.08% error (essentially exact)
> - **Groups A/B (Petrol / SNB/SNA)**: **`km ≈ BE16 × 32`** — gives <1% error; the exact multiplier is ~31.7
>
> The diesel firmware uses a clean `km = BE16 × 31` formula. The petrol firmware likely uses `BE16 × 32` with the residual error being due to approximate mileage values in filenames.
>
> **For synthesis**: Use **×31** for diesel (SMJ) and **×32** for petrol (SNA/SNB).

#### Rolling Write Pointer (Write-in-Progress Marker)

The 16 entries are NOT all identical — the dashboard uses a **rolling write pointer** with a deliberate broken complement to mark the active write position. The write sequence is:

1. Move to the next slot in the 16-entry ring
2. Write the new B0 and B1 (value bytes)
3. Write B2 (complement of new B0) but leave B3 as the **old complement** → this **breaks the complement check** (`B1 ⊕ B3 ≠ 0xFF`)
4. The broken entry marks the "write in progress" position
5. On the next update cycle, B3 is corrected and the pointer moves forward

**Evidence from dumps** (native word order):

| File | Active Slot | Native Entry | Word XOR | BE16 |
|------|------------|--------------|----------|------|
| 185000.bin | `[1]` | `16 CE E9 36` | `0xFFFF` but stale value ⚠ | 5838 (+5 from dominant) |
| 199954km.bin | `[1]` | `18 AD E7 55` | partial mismatch ⚠ | 6317 (+3 from dominant) |
| 373171km.bin | `[9]` | `2D 82 D2 7A` | `0xFFF8` ≠ `0xFFFF` ⚠ | 11650 |

The entry with a **broken word complement** (Word0 ⊕ Word1 ≠ 0xFFFF) is the current write position. The dominant (most common) pattern across the 16 slots is the last fully-committed odometer value.

---

### 🔑 Part Number / Serial Region (0x386 – 0x399)

In native word order, the part number reads as clean ASCII:

| Offset | Native Contents | Description |
|--------|----------------|-------------|
| `0x386–0x38B` | `73 02 0S` → `7802 0S` | **"78020S"** — Honda instrument cluster prefix, identical across all files |
| `0x38C–0x38D` | `NB` / `NA` / `MJ` | **Model code**: SNB (Group A), SNA (Group B), SMJ (Group C) |
| `0x38E–0x38F` | 2 bytes | Variant + version: `b`+`07` (A), `a`+`07` (B), `i`+`87` (C) |
| `0x390–0x395` | 6 chars ASCII | **Board revision**: `G2 11 1M` (A), `C1 14 1M` (B), `G1 13 1M` (C) |
| `0x396–0x397` | `FF FF` | Padding |
| `0x398–0x399` | 2 bytes | **Part number metadata** — NOT a checksum. `2E 09` (A), `2F 0B` (B), `2A 08` (C) |

Mapped to Honda OEM part numbers:
- **Group A**: **78120-SNB-xxx** → 2006-2011 Honda Civic sedan (European/trim variant)
- **Group B**: **78120-SNA-xxx** → 2006-2011 Honda Civic sedan (DX/EX/LX)
- **Group C**: **78120-SMJ-xxx** → 2006-2012 Honda Civic diesel (European i-CTDi/i-DTEC)

---

### Vehicle Configuration Header (0x000 – 0x04F)

This 80-byte region contains model-specific calibration data.

| Offset | Size | Description | Notes |
|--------|------|-------------|-------|
| `0x000–0x001` | 2 B | **Model identifier** | `FF 77` = petrol, `BA 65` = diesel (native) |
| `0x002` | 1 B | **Constant** | Always `FE` |
| `0x003–0x006` | 4 B | Config flags | Varies per model |
| `0x007` | 1 B | **Constant** | Always `7B` |
| `0x008–0x00B` | 4 B | Calibration data | Model-specific |
| `0x00C` | 1 B | **Feature flags** | Bit-field: A=`0x9F`, B=`0xAF`, C=`0x7F`/`0xBF`. Only bits 5-6 differ — hardware revision within group |
| `0x00D` | 1 B | Calibration data | Model-specific |
| `0x00E` | 1 B | **Constant** | Always `0xFF` |
| `0x010` | 1 B | **Constant** | Always `0x57` = 87 — protocol/version marker |
| `0x012` | 1 B | **Feature flags** | Bit-field: A=`0x96`, B=`0x26`, C=`0x31`/`0xF1`. Encodes trim-level feature differences |
| `0x017` | 1 B | **Constant** | Always `D7` |
| `0x01B` | 1 B | **Constant** | Always `FB` |
| `0x01F` | 1 B | **Constant** | Always `01` |
| `0x022–0x025` | 4 B | **Constant** | Always `0A 19 5F FF` (native) |
| `0x028–0x029` | 2 B | **Constant** | Always `07 D0` = 2000 in BE16 — clock base? |
| `0x03C–0x03D` | 2 B | **Constant** | Always `07 D0` (repeated) |
| `0x026–0x04F` | ~41 B | Calibration tables | RPM/speed/fuel gauge scaling factors |

Groups A & B share identical headers within each group. Group C has a completely different header, consistent with a different instrument cluster variant (diesel vs petrol).

---

### Static Configuration (0x050 – 0x05F)

```
Native: 05 14 B3 00 FF FF FF FF 04 A2 FF [xx] FF FF 00 [xx]
```

| Offset | Native Value | Description |
|--------|-------------|-------------|
| `0x050–0x053` | `05 14 B3 00` | Fixed calibration constants |
| `0x054–0x057` | `FF FF FF FF` | Reserved (all 0xFF) |
| `0x058–0x05A` | `04 A2 FF` | Hardware identifier |
| `0x05B` | Varies | Group-dependent: `9B` (A/B) or `5B` (C) |
| `0x05C–0x05D` | `FF FF` | Reserved |
| `0x05E–0x05F` | Varies | Status bytes |

---

### Operational Data / Counters (0x060 – 0x095)

This region contains running operational counters and sensor-related data. Several bytes in Group C **correlate with mileage** (increase or decrease monotonically with km), suggesting they track accumulated operational state.

> [!NOTE]
> **Diesel mileage-correlated bytes**: Offsets `0x0060`, `0x0063`, `0x0088`, `0x008A`, `0x00B7`, `0x00BC`, `0x00D8`, `0x00DB` all show monotonic correlation with mileage in Group C. These are likely accumulated sensor readings (e.g., total fuel injected, turbo hours, DPF regeneration count) rather than primary odometer values.

| Offset | Size | Description |
|--------|------|-------------|
| `0x060–0x061` | 2 B | Operational flags (differs A/B vs C) |
| `0x062–0x063` | 2 B | Running counter (partially varies) |
| `0x064–0x067` | 4 B | **Fixed**: `03 E8 0B B8` (native) — 1000 and 3000 in BE16, timer/clock constants |
| `0x068–0x077` | 16 B | Sensor readings / accumulated values |
| `0x078–0x07A` | 3 B | **Fixed**: `30 30 18` — clock/timer config |
| `0x07B–0x07C` | 2 B | Model-dependent flags |
| `0x07D` | 1 B | **Fixed**: `0x00` |
| `0x07E–0x08B` | 14 B | Hardware/firmware specific values |
| `0x08C–0x08D` | 2 B | **Fixed**: `32 64` (native) — dec 50 and 100 |
| `0x08E–0x095` | 8 B | Additional counters / ID bytes |

---

### Extended Data Region (0x0AC – 0x0E5)

This is where Groups A/B and Group C diverge most significantly:

- **Groups A & B**: Entirely `0x00` and `0xFF` (unused)
- **Group C (Diesel)**: Contains active data including what appears to be:

| C Offset | Description |
|----------|-------------|
| `0x0B4–0x0B6` | Configuration flags (e.g., `03 89` or `05 88`) |
| `0x0B7` | Monotonically ↑ with km (86→88→89) — likely DPF regeneration counter |
| `0x0B8–0x0CB` | Diesel-specific sensor calibration (DPF, EGR, turbo) |
| `0x0CC–0x0D9` | Additional diagnostic data (0xD8 and 0xDB correlate ↓ with km) |
| `0x0DA–0x0E1` | Error/fault counters |
| `0x2CB–0x2DA` | Per-vehicle DPF/EGR calibration (small variations: 93–95, 10–26) |

---

### Fuel / Sensor Calibration (0x130 – 0x13F)

```
Native: 00 00 00 00 00 00  5A 88 E4 F6  FF FF  [xx xx]  00 C0
```

| Offset | Native Value | Description |
|--------|-------------|-------------|
| `0x130–0x135` | `00 00 00 00 00 00` | Padding |
| `0x136–0x139` | `5A 88 E4 F6` | **Fixed across ALL files** — fuel sensor calibration magic number |
| `0x13A–0x13B` | `FF FF` | Reserved |
| `0x13C–0x13D` | Model-dep. | `28 28` for A/B, `14 14` for C — **fuel gauge scaling** (40 vs 20) |
| `0x13E–0x13F` | `00 C0` | Fixed footer |

> [!TIP]
> The values `0x28 = 40` and `0x14 = 20` at 0x13C-0x13D likely relate to fuel gauge calibration differences between petrol and diesel models.

---

### DTC / Diagnostic Codes (0x150 – 0x177)

- **Groups A & C**: All `0x00` (no stored codes)
- **Group B** (235k and 373k files): Contains active DTC data:

```
Native:
0x154: A4 D3 28 3A 03 65 73 C4 28 4F 0B D0
0x160: 47 C5 28 0F 00 A5 20 6D 28 2F 0B 4A
0x16C: 47 C5 28 0F 00 A5
```

These appear to be stored diagnostic trouble codes with their status bytes and freeze-frame data.

---

### Gauge Calibration / Trip Data (0x1C0 – 0x1E7)

This region stores gauge needle positions and trip meter data as paired values:

```
Format: [VALUE] [00/E0/E2/02]
```

The second byte of each pair encodes status flags:
- `0x00` = normal/idle
- `0x02` = flag A set (last reading taken while driving)
- `0xE0` = flags B+C set (service-related snapshot)
- `0xE2` = flags A+B+C set (full operational snapshot)

> [!NOTE]
> **Gauge values self-calibrate on boot** from live sensor data. These bytes store the last needle positions before power-off. For synthesis, any reasonable values work — the cluster recalibrates within seconds of engine start. Setting all to `0x00` is safe.

| Offset | Description | Native Example (185000.bin) |
|--------|-------------|----------------------------|
| `0x1C0–0x1C3` | Gauge needle #1 position + copy | `00 5D 02 5D` |
| `0x1C4–0x1C7` | Gauge needle #2 position | `00 00 00 00` |
| `0x1C8–0x1CB` | Gauge needle #3 position | `00 32 02 32` (dec 50) |
| `0x1CC–0x1CF` | Gauge needle #4 position | `00 31 02 31` (dec 49) |
| `0x1D0–0x1D3` | Speed gauge calibration | `00 52 E2 52` (dec 82) |
| `0x1D4–0x1D7` | Temperature gauge | `00 44 E0 44` (dec 68) |
| `0x1D8–0x1DB` | RPM gauge calibration | `00 48 E0 48` (dec 72) |
| `0x1DC–0x1DF` | Fuel gauge | `00 01 E2 01` |
| `0x1E0–0x1E3` | Trip A value | `00 1D E0 1D` (dec 29) |
| `0x1E4–0x1E7` | Trip B value | `00 32 E2 32` (dec 50) |

Each gauge value appears twice — the first is the raw value, the second is a flagged copy (with status bits in the low byte). Values change between files as they reflect different driving/calibration states.

> [!TIP]
> **Integrity**: The first bytes of all gauge value pairs (the VALUE bytes at even offsets) consistently **XOR to 0x00** across every file. This suggests the gauge block uses an internal parity check.

---

### Running Counters (0x1E8 – 0x1F3)

These bytes change across all files and appear to be rolling counters:

| Offset | Description |
|--------|-------------|
| `0x1E8–0x1EB` | Counter set A (4 bytes) — trip distance accumulator |
| `0x1EC–0x1EF` | Counter set B (4 bytes) — fuel consumption counter |
| `0x1F0–0x1F3` | Counter set C (4 bytes) — service interval counter |

> [!NOTE]
> These counters show no direct linear correlation with the main odometer value. They likely track trip distances, fuel consumption, or service intervals independentlyfrom the main odometer. **For synthesis, zeroing these bytes is safe** — it simply resets trip/service counters.

---

### Status / Flags (0x1F4 – 0x1FF)

```
Native:
Groups A/B: 00 00 00 00 00 00 FF FF 00 00 00 07
Group C:    00 00 00 00 00 00 FF FF [0E 10] 00 00
```

| Offset | Description |
|--------|-------------|
| `0x1F4–0x1F9` | Zero padding |
| `0x1FA–0x1FB` | `FF FF` — boundary marker |
| `0x1FC–0x1FD` | Model flags: `00 00` (A/B) or `10 0E` (C) |
| `0x1FE–0x1FF` | Config: `07 00` (A/B) or `00 00` (C) |

---

### System Configuration (0x200 – 0x20F)

```
Native:
Groups A/B: BF FF 05 32 32 02 FF FF 39 47 FF FF FF FF FF FF
Group C:    7F FF 05 00 32 02 FF FF 31 B5 32 32 05 0A FF FD
```

| Offset | Description |
|--------|-------------|
| `0x200–0x201` | System flags (differ between groups) |
| `0x202–0x205` | Configuration parameters |
| `0x206–0x207` | `FF FF` reserved |
| `0x208–0x209` | Hardware revision code |
| `0x20A–0x20F` | Model-specific extended config |

---

### Sensor Calibration Tables (0x250 – 0x27F)

Largely identical across all files:

```
Native:
0x250: FF FF 78 04 FF FF FF FF 08 7C FF FF FF FF FF FF
0x260: FF FF FF FF [65/67] A1 00 FF FF FF FF FF [02/03] [3B/39] FF FF
0x270: FF FF FF FF FF FF FF FF 09 [99/00] 0B 3C 64 FF FF FF
```

| Offset | Native Value | Description |
|--------|-------------|-------------|
| `0x252–0x253` | `78 04` = 0x7804 | Calibration constant (possibly fuel level sensor) |
| `0x258–0x259` | `08 7C` = 0x087C = 2172 | Calibration constant |
| `0x264–0x265` | `65/67 A1` | Temperature sensor calibration (65=petrol, 67=diesel) |
| `0x26C–0x26D` | `02/03 3B/39` | Fuel gauge cal (model-specific) |
| `0x278–0x279` | `09 99/00` | Speed sensor cal (model-specific) |
| `0x27A–0x27B` | `0B 3C` = 0x0B3C = 2876 | Fixed constant |
| `0x27C–0x27D` | `64 FF` | Fixed constant (0x64 = 100 decimal) |

---

### Service / Maintenance Data (0x2A0 – 0x2BF)

| Same Across | Values |
|-------------|--------|
| All files | `0x2A0: FF 7F` |
| A/B only | `0x2A8: 80 01 50 00 82 01 C5 03 49 06 5A 84 C9 06 04 03 25 03 FF FF EE 28` |
| Group C | Mostly `0x00` — service counters not populated |

Groups A/B contain service interval tracking data. Group C has this region cleared.

---

### Tail Status Value (0x3EA – 0x3EB)

| Group | Native Value | BE16 Decimal |
|-------|-------------|-------|
| A | `55 56` | 0x5556 = 21846 |
| B | `1F 10` | 0x1F10 = 7952 |
| C (88k/92k) | `DD B0` | 0xDDB0 = 56752 |
| C (183k) | `6E EC` | 0x6EEC = 28396 |

> [!NOTE]
> **Not a checksum.** Does NOT correlate linearly with mileage (km/tail ratios range from 1.5 to 46). Consistent within Group A (both files = 0x5556) and Group B (both = 0x1F10). Likely tracks **total ignition cycles** or **accumulated operating hours**. For synthesis, copy from donor — this value doesn't affect cluster operation.

---

### Configuration Footer (0x3F2 – 0x3FB)

```
Native:
Group A: 00 03 00 01 00 02 00 01 01 04
Group B: 03 0F 00 01 00 01 00 01 01 06
Group C: [02/03] [6D/82] 00 00 01 07 00 07 05 04
```

| Offset | Description |
|--------|-------------|
| `0x3F2–0x3F3` | Config value A (model-specific) |
| `0x3F4–0x3F5` | Config value B |
| `0x3F6–0x3F7` | Config value C |
| `0x3F8–0x3F9` | Config value D |
| `0x3FA–0x3FB` | Config value E |

These are small configuration parameters that encode display settings and warning thresholds:
- **Word 0** (`0x3F2`): Varies between model sub-variants. Group A=`0x0003`, Group B=`0x030F`. Diesel 183k=`0x0382`, diesel 88k/92k=`0x026D` — likely encodes service history or cluster feature flags.
- **Words 1–4**: Encode unit display (km/mph), warning thresholds, and regional market options. For synthesis, copy from donor.

> [!NOTE]
> **No VIN or immobilizer data** exists in this EEPROM. Exhaustive ASCII search (both raw and native byte order) found no 17-character VIN patterns. Honda stores VIN and immobilizer keys in separate chips on the ECU and body control module, not in the instrument cluster EEPROM.

---

## Unused / Reserved Regions

Approximately **60%** of the EEPROM is filled with `0xFF` (erased/unused). Key unused ranges:

| Range | Size | Contents |
|-------|------|----------|
| `0x0C0–0x0EF` (A/B) | 48 B | All `0xFF` |
| `0x140–0x14F` | 16 B | All `0xFF` |
| `0x2C0–0x30F` (A/B) | 80 B | All `0xFF` |
| `0x310–0x385` | 118 B | All `0xFF` |
| `0x39A–0x3DF` | ~70 B | Mostly `0xFF`/`0x00` |
| `0x3C0–0x3E0` | 32 B | All `0xFF` |

---

## Integrity Mechanisms

The Honda 93c76 EEPROM has **no global checksum**. Integrity is maintained through localized mechanisms:

### 1. Odometer Word Complement
Each 4-byte odometer entry is two 16-bit words where Word1 = ~Word0 (bitwise NOT). In native order: `[HI] [LO] [~HI] [~LO]`. This is the **primary data integrity check**.

### 2. Odometer Rolling Write Pointer
The dashboard deliberately **breaks the word complement** on the active write slot to mark "write in progress". A broken complement entry = current write position. See the [Odometer Block](#-odometer-block-0x180--0x1bf) section for details.

### 3. Gauge Value Parity
The gauge calibration values at `0x1C0–0x1E7` consistently XOR to `0x00`, providing internal parity verification.

### 4. No Global CRC
Exhaustive testing against all standard checksum algorithms found **no global checksum**. The bytes at `0x398-0x399`, `0x3EA-0x3EB`, and `0x3F2-0x3F3` are **configuration/metadata values**, not checksums.

> [!IMPORTANT]
> **Practical implication**: To modify the odometer, you only need to write the 16 × 4-byte entries at `0x180–0x1BF` with correct word complements. No other bytes need updating.

---

## Synthesis Guide

To create a new EEPROM file from scratch or modify an existing one:

### Step 1: Choose a Base File
Pick a donor file matching your target cluster's model group:
- **Petrol sedan (SNA/SNB)**: Use `185000.bin`, `199954km.bin`, `235...k.bin`, or `373171km.bin`
- **Diesel (SMJ)**: Use `183523km.bin`, `88108.bin`, or `92054.bin`

### Step 2: Compute Odometer Words

```
For DIESEL (SMJ):    value = target_km / 31
For PETROL (SNA/SNB): value = target_km / 32

Word0 (BE16):  HI = (value >> 8) & 0xFF,  LO = value & 0xFF
Word1:         ~HI = HI ^ 0xFF,           ~LO = LO ^ 0xFF

Native entry:     [HI] [LO] [~HI] [~LO]
Raw dump entry:   [LO] [HI] [~LO] [~HI]   (as written to .bin file)
```

**Example**: 150,000 km on a petrol cluster:
```
value = 150000 / 32 = 4687 = 0x124F
HI = 0x12, LO = 0x4F
~HI = 0xED, ~LO = 0xB0

Native entry: 12 4F ED B0
Raw .bin:     4F 12 B0 ED   (byte-swapped for 8-bit programmer)
```

### Step 3: Write Odometer Block (0x180–0x1BF)
Fill all 16 × 4-byte slots with the same entry. This creates a clean odometer state with no rolling pointer.

### Step 4: Leave Everything Else Unchanged
- **No global checksum** needs updating
- **Part number** (0x386) identifies the hardware — do NOT change unless swapping cluster models
- **Gauge calibration** (0x1C0–0x1E7) should match the donor file
- **Header** (0x000–0x04F) is model-specific — do NOT change

### Regions Safe to Modify
| Region | Safe? | Notes |
|--------|-------|-------|
| Odometer (0x180–0x1BF) | ✅ | Must maintain complement pairs |
| Trip counters (0x1E8–0x1F3) | ✅ | Can zero out |
| DTC codes (0x150–0x177) | ✅ | Can zero out to clear codes |
| Gauge values (0x1C0–0x1E7) | ⚠️ | Keep gauge XOR parity = 0x00 |
| Header (0x000–0x04F) | ❌ | Model-specific, do not touch |
| Part number (0x386–0x399) | ❌ | Hardware identifier |
| Config footer (0x3F2–0x3FB) | ❌ | Unknown function |
| Tail status (0x3EA–0x3EB) | ❌ | Unknown accumulated value |

---

## Key Takeaways

1. **Odometer** at `0x180–0x1BF`: 16 word-complemented entries. **`BE16 × 31 = km` (diesel, 0.03% error)** or **`BE16 × 32 ≈ km` (petrol, <1% error)**
2. **8-bit reader / 16-bit chip**: the CH341A swaps bytes within each 16-bit word. Raw `.bin` files have every pair reversed vs native chip order
3. **No global checksum** — only per-entry word complements and gauge XOR parity
4. **Part number** at `0x386` reads `78020S` + `NB`/`NA`/`MJ` in native order → Honda OEM `78120-SNA/SNB/SMJ`
5. The **rolling write pointer** uses a broken word complement to mark the active odometer slot
6. Diesel (SMJ) and petrol (SNA/SNB) variants use the same base layout but differ in header, calibration, fuel config, and odometer multiplier (×31 vs ×32)
7. **~60% of the EEPROM is unused** (`0xFF`-filled)
8. `0x136–0x139` is a universal magic number (`5A 88 E4 F6` native) across all files
