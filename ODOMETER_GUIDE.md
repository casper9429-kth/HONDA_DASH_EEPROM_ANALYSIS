# Odometer Guide — Reading, Understanding & Modifying

This guide covers everything needed to read, interpret, and modify the odometer value in a Honda Civic 8th gen (2006–2012) EEPROM dump.

---

## Where the Odometer Is Stored

**Address range**: `0x180 – 0x1BF` (64 bytes)

This block contains **16 × 4-byte entries** in a rolling ring. The dashboard writes a new entry each time the odometer updates, cycling through all 16 slots.

---

## Entry Structure

Each 4-byte entry holds a 16-bit value and its bitwise complement as an integrity check.

**Native word order (as on the chip):**
```
[HI] [LO] [~HI] [~LO]
```

**Raw `.bin` file order (byte-swapped by programmer):**
```
[LO] [HI] [~LO] [~HI]
```

**Integrity rule**: `Word0 XOR Word1 = 0xFFFF`

If a slot's two words don't XOR to `0xFFFF`, it is the **active write slot** (write in progress — see Rolling Write Pointer below).

---

## Odometer Formula

Read the first two bytes of a valid entry as a big-endian 16-bit integer (BE16), then multiply:

| Variant | Formula | Accuracy |
|---------|---------|---------|
| **Diesel (SMJ)** | `km = BE16 × 31` | ~0.03–0.08% error |
| **Petrol (SNA/SNB)** | `km = BE16 × 32` | <1% error |

### Verified Examples

| File | Known km | Entry (native) | BE16 | × 31 | × 32 |
|------|----------|---------------|------|------|------|
| 88108.bin | 88,108 | `0B 1B F4 E4` | 2,843 | 88,133 ✓ | 90,976 |
| 92054.bin | 92,054 | `0B 9C F4 63` | 2,972 | 92,132 ✓ | 95,104 |
| 183523km.bin | 183,523 | `17 1C E8 E3` | 5,916 | 183,396 ✓ | 189,312 |
| 185000.bin | 185,000 | `16 C9 E9 36` | 5,833 | — | 186,656 ✓ |
| 235...k.bin | 235,000 | `1C CE E3 31` | 7,374 | — | 235,968 ✓ |
| 373171km.bin | 369,475 | `2D 82 D2 7D` | 11,650 | — | 372,800 ✓ |

---

## Rolling Write Pointer

The 16 slots are not all identical. The dashboard marks its current write position by deliberately **breaking the complement** in one slot:

1. Move to the next slot in the ring
2. Write new `HI` and `LO` bytes (the value)
3. Write `~HI` but leave the old `~LO` → this breaks the XOR check (`Word0 XOR Word1 ≠ 0xFFFF`)
4. On the next update, `~LO` is corrected and the pointer moves forward

**Reading the correct mileage**: Find the most common (dominant) pattern across all 16 slots — that is the last fully-committed odometer value. The slot with the broken complement is the in-progress entry (may be slightly off).

---

## How to Modify the Odometer

### Step 1: Choose a Donor File

Pick a `.bin` file matching your cluster's model group:
- **Petrol (SNA/SNB)**: use any file from `Files/A_Petrol_SNB/` or `Files/B_Petrol_SNA/`
- **Diesel (SMJ)**: use any file from `Files/C_Diesel_SMJ/`

### Step 2: Calculate the Entry Bytes

```
Diesel:  value = target_km ÷ 31   (round to nearest integer)
Petrol:  value = target_km ÷ 32   (round to nearest integer)

HI  = (value >> 8) & 0xFF
LO  =  value & 0xFF
~HI =  HI ^ 0xFF
~LO =  LO ^ 0xFF

Native entry (chip word order):  HI  LO  ~HI  ~LO
Raw .bin entry (file byte order): LO  HI  ~LO  ~HI
```

### Example: 150,000 km on a petrol cluster

```
value = 150000 ÷ 32 = 4687 = 0x124F

HI  = 0x12    LO  = 0x4F
~HI = 0xED    ~LO = 0xB0

Native entry:   12 4F ED B0
Raw .bin entry: 4F 12 B0 ED   ← write this to the file
```

### Step 3: Write All 16 Slots

Fill every 4-byte slot at `0x180–0x1BF` with the same entry. This creates a clean odometer state with no rolling write pointer active.

The 16 slots occupy bytes `0x180` to `0x1BF` (64 bytes total):
```
0x180: [entry] [entry] [entry] [entry]
0x190: [entry] [entry] [entry] [entry]
0x1A0: [entry] [entry] [entry] [entry]
0x1B0: [entry] [entry] [entry] [entry]
```

### Step 4: No Other Changes Needed

The EEPROM has **no global checksum**. Only the per-entry word complement matters. After updating `0x180–0x1BF`, the file is ready to flash.

---

## What Is Safe to Modify

| Region | Address | Safe? | Notes |
|--------|---------|-------|-------|
| Odometer block | `0x180–0x1BF` | Yes | Must maintain complement pairs |
| Trip / service counters | `0x1E8–0x1F3` | Yes | Zeroing resets trip meters |
| DTC codes | `0x150–0x177` | Yes | Zero out to clear fault codes |
| Gauge last-position values | `0x1C0–0x1E7` | Caution | Keep gauge XOR parity = 0x00 |
| Config header | `0x000–0x04F` | No | Model-specific calibration |
| Part number | `0x386–0x399` | No | Hardware identifier |
| Config footer | `0x3F2–0x3FB` | No | Unknown function |
| Tail status | `0x3EA–0x3EB` | No | Accumulated state value |

---

## Integrity Mechanisms (Summary)

| Mechanism | Where | What It Does |
|-----------|-------|-------------|
| Word complement | Each odometer entry | Word0 XOR Word1 must = 0xFFFF |
| Gauge XOR parity | `0x1C0–0x1E7` | All gauge value bytes XOR to 0x00 |
| No global CRC | — | None exists — confirmed by exhaustive testing |
