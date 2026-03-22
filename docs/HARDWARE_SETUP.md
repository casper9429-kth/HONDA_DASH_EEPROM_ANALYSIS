# Hardware Setup — CH341A → 93C76

Guide for wiring the CH341A USB programmer to the 93C76 EEPROM on a Honda Civic dashboard cluster.

> **Manufacturer note**: The datasheet in this repo is the **Seiko Instruments S-93C76A**. The pinout differs slightly from the **Microchip 93C76** — specifically Pin 6. See the Pin 6 note in the pinout table below.

---

## Programmer Kit — KeeYees S018 (model JK11-C1 / KYES61-KIT)

| Item | Qty | Used for 93C76? |
|------|:---:|-----------------|
| CH341A USB Programmer | 1 | Yes |
| SOP8 Test Clip (8-pin ribbon cable) | 1 | Yes — clips onto chip in-circuit |
| 8-Pin to 8-Pin Converter PCB | 1 | Yes — **after repinning** (see below) |
| SOP8 to DIP8 socket adapter | 2 | Yes — for desoldered chips |
| 2.54mm 4-Pin headers | 2 | Optional — spare parts |

---

## Chip Specifications (from S-93C76A datasheet)

| Parameter | Value |
|-----------|-------|
| Capacity | 8 Kbit — 512 × 16-bit words (1024 bytes) |
| Protocol | Microwire (3-wire serial) |
| Supply voltage (read) | 1.8V – 5.5V |
| Supply voltage (write) | 2.7V – 5.5V |
| Max clock frequency | 1.0 MHz @ 4.5–5.5V · 0.5 MHz @ 2.7–4.5V |
| Write time | 4 ms typical, 10 ms max |
| Endurance | 10⁶ write cycles/word @ 85°C · 5×10⁵ @ 105°C |
| Data retention | 100 years @ 25°C · 20 years @ 105°C |
| Operating temperature | −40°C to +105°C |
| Initial factory state | All `FFFFh` |

---

## CH341A Voltage — 5V Mod Required

Standard unmodified CH341A boards have a design flaw that matters for the 93C76:

| Pin | Unmodified output | Why |
|-----|------------------|-----|
| **VCC** (pin 8 of 25xx header) | **3.3V** | Onboard AMS1117-3.3 LDO regulator |
| **Logic signals** (CS, CLK, MOSI, MISO) | **5V** | Connected directly to the CH341A IC, which runs at 5V |

This mismatch is a problem. The target chip is powered at 3.3V but receives 5V logic signals. Per the S-93C76A datasheet (absolute maximum ratings):

> **Max input voltage: VCC + 0.3V**

At VCC = 3.3V → max input = **3.6V**. The 5V signals from the CH341A **exceed this limit** and can stress or damage the chip over time.

### The 5V mod

The fix for automotive Microwire EEPROMs like the 93C76: bridge the VCC output to 5V so the chip is powered at 5V and receives 5V signals. Everything runs at 5V, which is within the 93C76's full operating range (2.7V–5.5V write, abs max 7.0V).

**After the mod:**

| Pin | Output | 93C76 spec | Safe? |
|-----|--------|-----------|-------|
| VCC | 5V | 2.7V–5.5V | ✅ |
| Logic signals | 5V | VIH min = 2.0V @ 5V VCC | ✅ |
| Max input voltage limit | 5.3V | 5V signals < 5.3V | ✅ |

### How to do the mod

On most CH341A mini programmer boards the VCC output goes through the AMS1117-3.3 LDO. The mod bypasses it:

**Option A — Solder bridge (permanent):**
1. Locate the AMS1117-3.3 regulator — SOT-223 package, marked `1117 3.3` or `AMS1117`
2. Solder a short wire bridge between the **input pin** (5V side) and the **output pin** (3.3V side) of the regulator
3. This feeds 5V directly to the VCC header pin, bypassing the regulator

**Option B — Jumper (if your board has one):**
Some KeeYees / CH341A boards have a 3-pin voltage selection header marked `3.3V / 5V`. Move the jumper to the **5V** position. This switches both VCC output and (on boards with level shifting) the logic signals to 5V.

**Option C — Check first:**
Before modifying, measure the VCC header pin with a multimeter while the CH341A is plugged into USB. If it already reads 5V your board is already 5V output and no mod is needed.

> **Note on the "3.3V mod"**: You may also see a "3.3V mod" for CH341A, which does the opposite — makes logic signals also 3.3V. That mod is for programming modern 3.3V-only SPI flash chips (25xx series). Do NOT apply it for the 93C76.

---

## Warnings

> **Do NOT plug the clip directly into the CH341A.** The ribbon cable is wired straight-through (clip pin 1→CH341A pin 1, etc.), which is the correct layout for 25xx SPI chips — but wrong for the 93C76. You must repin the connector first (instructions below).

> **Voltage**: Do the 5V mod before use — see section above. Unmodified boards power the chip at 3.3V while driving signals at 5V, which exceeds the chip's absolute maximum input ratings.

---

## Chip Pinout: 93C76 (8-pin SOIC)

View from top — dot/notch = Pin 1, top-left:

```
       ┌──────────┐
CS  1 ─┤●         ├─ 8  VCC
SK  2 ─┤          ├─ 7  NC
DI  3 ─┤          ├─ 6  TEST (Seiko) / ORG (Microchip)
DO  4 ─┤          ├─ 5  GND
       └──────────┘
```

| Pin | Name | Function |
|-----|------|----------|
| 1 | CS | Chip Select (active high) |
| 2 | SK | Serial Clock |
| 3 | DI | Data In (MOSI) |
| 4 | DO | Data Out (MISO) |
| 5 | GND | Ground |
| 6 | TEST / ORG | See note below |
| 7 | NC | No connect |
| 8 | VCC | Power (min 2.7V writes, 1.8V reads; max 5.5V) |

> **Pin 6 — manufacturer difference**:
> - **Seiko S-93C76A**: Pin 6 is **TEST**. Always 16-bit — no mode selection. Can be left floating, or tied to VCC or GND.
> - **Microchip 93C76**: Pin 6 is **ORG**. Must be tied to VCC for 16-bit mode. Honda dashboards use 16-bit mode.
>
> Tying Pin 6 to VCC is safe for both variants and is the default in these instructions.

---

## CH341A 25xx Header Pinout

```
       ┌─────────────┐
CS   1 ─┤●            ├─ 8  VCC (3.3V)
MISO 2 ─┤             ├─ 7  HOLD#
WP#  3 ─┤             ├─ 6  CLK
GND  4 ─┤             ├─ 5  MOSI
       └─────────────┘
```

Pin 1 is marked with a dot or square pad — usually closest to the USB connector.

---

## Repinning the Clip Connector

The SOP8 clip's ribbon cable ends in an **8-pin DuPont female housing**. Currently, the clip is wired straight-through: clip pin 1 → housing slot 1, clip pin 2 → housing slot 2, and so on. This is correct for 25xx chips but wrong for the 93C76.

You need to pull the individual metal pins out of the housing and reinsert them in the correct slots. No soldering required — just a toothpick or a fine pin.

### How to repin a DuPont connector

Each slot has a small plastic retention tab that locks the metal crimp pin. To remove a pin:

1. Insert a toothpick, SIM-card pin, or thin flathead screwdriver into the slot from the **opening side** (not the wire side)
2. Gently press the retention tab inward while pulling the wire from the back — the pin slides out
3. To reinsert: push the pin in from the wire side until it clicks

### Before and after — housing slot positions

The table shows what clip wire (= 93C76 chip pin) should end up in each CH341A header slot:

| Housing slot | CH341A signal | Default (wrong) | After repinning (correct) |
|:---:|---|---|---|
| 1 | CS | Clip wire 1 — CS | Clip wire 1 — CS ✅ no change |
| 2 | MISO | Clip wire 2 — SK | Clip wire 4 — DO ✅ moved in |
| 3 | WP# | Clip wire 3 — DI | **empty** — remove wire |
| 4 | GND | Clip wire 4 — DO | Clip wire 5 — GND ✅ moved in |
| 5 | MOSI | Clip wire 5 — GND | Clip wire 3 — DI ✅ moved in |
| 6 | CLK | Clip wire 6 — TEST/ORG | Clip wire 2 — SK ✅ moved in |
| 7 | HOLD# | Clip wire 7 — NC | Clip wire 7 — NC (no change, harmless) |
| 8 | VCC | Clip wire 8 — VCC | Clip wire 8 — VCC ✅ no change |

Clip wire 6 (TEST/ORG) is **removed from the housing** and bridged to VCC separately — see step below.

### Step-by-step

1. Lay out the ribbon cable with the clip end away from you and the 8-pin housing facing you. Slot 1 is on the left (same side as the clip's Pin 1 marker).

2. **Remove clip wire 6** (TEST/ORG) from slot 6 — pull it out and set aside.

3. **Remove clip wire 3** (DI) from slot 3.

4. **Remove clip wire 4** (DO) from slot 4.

5. **Remove clip wire 5** (GND) from slot 5.

6. **Remove clip wire 2** (SK) from slot 2.

   At this point only wires 1, 7, and 8 remain in the housing.

7. **Insert clip wire 4** (DO) into slot 2.

8. **Insert clip wire 5** (GND) into slot 4.

9. **Insert clip wire 3** (DI) into slot 5.

10. **Insert clip wire 2** (SK) into slot 6.

11. Slot 3 stays **empty**.

12. **Bridge clip wire 6 (TEST/ORG) to VCC**: the easiest way is to twist it together with clip wire 8 (VCC) and use a female Dupont socket over both, or solder them together. Alternatively, leave clip wire 6 disconnected if your chip is a Seiko S-93C76A (TEST can float).

### Final connector layout (after repinning)

```
Slot:   1     2     3      4     5     6     7      8
       CS    DO   empty   GND   DI    SK    NC    VCC (+TEST/ORG)
        ↓     ↓            ↓     ↓     ↓     ↓     ↓
CH341A: CS   MISO  (WP#)  GND  MOSI  CLK  (HOLD#) VCC
```

### Verify before connecting

Check each slot visually — confirm the wire colours/positions match the table, then use a multimeter in continuity mode to confirm:
- Clip Pin 1 (CS) → CH341A Pin 1 (CS)
- Clip Pin 2 (SK) → CH341A Pin 6 (CLK)
- Clip Pin 3 (DI) → CH341A Pin 5 (MOSI)
- Clip Pin 4 (DO) → CH341A Pin 2 (MISO)
- Clip Pin 5 (GND) → CH341A Pin 4 (GND)
- Clip Pin 6 (TEST/ORG) → CH341A Pin 8 (VCC)
- Clip Pin 8 (VCC) → CH341A Pin 8 (VCC)

---

## Out-of-Circuit Reading (Desoldered Chip)

Use one of the included **SOP8-to-DIP8 socket adapters**:

1. Place the 93C76 into the socket — match the chip's Pin 1 dot to the socket's Pin 1 marker
2. The socket presents the chip as a DIP8 — use individual Dupont wires from the DIP8 pins to the CH341A 25xx header per the wiring table above
3. DIP8 and SOP8 pin numbers are identical (Pin 1 top-left, Pin 8 top-right when viewed from top)

> The SOP8-to-DIP8 adapters map straight through, so the same pin remapping applies — do not use the 8-pin converter PCB, use Dupont wires.

---

## Reading Procedure

### Step 1: Prepare the Chip

**In-circuit** (chip still on dashboard PCB):
- Remove the instrument cluster from the car
- Locate the 93C76 — small 8-pin SOIC near the main MCU
- Attach the SOP8 clip: open the jaws, align the Pin 1 arrow on the clip with the dot on the chip, press until it clicks on both sides
- Plug the repinned connector into the CH341A 25xx header (Pin 1 of housing → Pin 1 of header)

**Out-of-circuit** (chip desoldered):
- Place the chip into a SOP8-to-DIP8 socket adapter
- Wire from socket pins to CH341A 25xx header with individual Dupont wires per the wiring table

### Step 2: Double-check

1. Do not plug in USB yet
2. Verify every connection once more — especially VCC/GND (a short can destroy the chip)

### Step 3: Read

See the Software Setup section below for step-by-step instructions per OS and tool.

> **Always read twice.** Read the chip, save the file, then read again and compare the two dumps byte-for-byte. If they differ, the connection is unreliable — clean the chip pins with contact spray, reseat the clip, and retry before proceeding.

---

## Software Setup

### Windows — NeoProgrammer (primary)

NeoProgrammer is the recommended GUI tool for Windows. It supports Microwire chips including the 93C76 natively and includes visual chip orientation guides.

#### 1. USB passthrough (VMware Fusion Pro)

The CH341A must be passed through from macOS to the Windows 11 VM:

1. Plug in the CH341A
2. In VMware Fusion menu: **Virtual Machine → USB & Bluetooth → Connect CH341 USB Programmer** (or similar name)
3. Verify it appears as a USB device inside Windows (Device Manager → Ports or Unknown Device)

#### 2. Install the CH341A driver

NeoProgrammer includes the driver in its package. If Windows doesn't recognise the CH341A automatically:

1. Open **Device Manager** — look for an unknown device or `USB-SERIAL CH340`
2. Right-click → Update driver → Browse my computer → navigate to the NeoProgrammer `driver/` folder
3. Alternatively, download **CH341PAR.exe** from the WCH website and run it

> **Windows 11 ARM note**: WCH's signed driver supports ARM64 from version 3.6 onwards. If the driver install fails, check you have the latest version from the WCH website.

#### 3. Read with NeoProgrammer

1. Open NeoProgrammer
2. Click **Select IC** → search for `93C76` → select it (listed under Microwire / Serial EEPROM)
3. Click **Read** — NeoProgrammer auto-detects the CH341A
4. When the read completes, click **Save** → save as `dump.bin`
5. Click **Read** again → save as `dump_verify.bin`
6. Compare: **File → Compare** or diff the two files — they must be identical

#### 4. Write with NeoProgrammer

1. Click **Open** → load your modified `.bin` file
2. Click **Program** (this erases and writes in one operation)
3. Click **Read** when done → compare against the file you wrote to verify

> **Chip orientation prompt**: NeoProgrammer shows a visual diagram of the chip. Confirm your physical chip's Pin 1 dot matches the diagram before clicking Read/Write.

---

### macOS — Not reliably supported for 93C76

> **Known limitation**: The macOS `ch341eeprom` tool uses `libusb` for direct USB access but does not correctly drive the **CS (Chip Select) line** for Microwire 93xx chips. CS on the 93C76 is active-high and must be toggled precisely per-transaction — without this, the chip never responds and reads return all `0xFF` or garbage. This is a driver-level limitation, not a wiring issue.

`flashrom` also does NOT support the 93C76 — it only handles SPI flash (25xx series).

**Use Windows + NeoProgrammer** (see above). Since the host machine runs macOS with Windows 11 in VMware Fusion Pro, this is the correct approach for this project. NeoProgrammer on Windows has full Microwire CS support and has been tested with 93xx automotive EEPROMs.

If a macOS-native solution is ever needed, consider **SNANDer** (in the `SNANDer/` folder in this repo) which has broader Microwire support than `ch341eeprom`, though its 93C76 CS handling should still be verified before trusting results.

---

### Byte ordering note

The CH341A reads the 93C76's 16-bit words in byte-swapped order. Both NeoProgrammer and ch341eeprom save the raw bytes as the hardware delivers them — so `.bin` files from either tool are **byte-swapped** relative to native chip word order.

This means the byte swap behaviour documented throughout this project applies equally to both tools. All hex values in [EEPROM_MEMORY_MAP.md](EEPROM_MEMORY_MAP.md) are in native word order; raw `.bin` files have every byte pair reversed.

> **To verify**: open a known good dump in a hex editor and check offset `0x386`. In the raw file you should see `87 02` (byte-swapped). In native order this reads `78 02` → ASCII `78020S...` (Honda part number prefix). If you see `78 02` directly, your tool is outputting in native order — treat all byte-swap notes in the documentation as inverted.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No EEPROM found" | Check CS and CLK — most common cause of this error |
| Reads all `0xFF` | VCC not reaching chip — check Pin 8 and the 5V mod |
| Reads all `0x00` | GND not connected, or wrong chip type specified |
| Two reads differ | Bad clip contact — clean chip pins, reseat clip firmly |
| Clip slips off | 93C76 is a small SOIC; press clip from both sides simultaneously |
| NeoProgrammer: CH341A not detected | Install/reinstall CH341A driver; check USB passthrough in VMware |
| NeoProgrammer: driver fails on ARM | Download latest CH341PAR (v3.6+) from WCH — older versions lack ARM64 support |
| NeoProgrammer: chip not in list | Search `93C76` — it may be listed as `93LC76` or under Microwire category |
| macOS reads all `0xFF` | CS line not driven — macOS ch341eeprom lacks Microwire CS support; use Windows + NeoProgrammer |
| USB not detected | Try a different USB port; avoid USB hubs |
| Write errors / verify fails | 5V mod likely needed — unmodified board VCC is 3.3V, signals are 5V |
