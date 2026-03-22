# How to Read a Honda Civic Dashboard EEPROM

Step-by-step guide. Honda Civic 8th gen (2006–2012), 93C76 EEPROM chip.

---

## Shopping List

| What | Where | Notes |
|------|-------|-------|
| CH341A Mini Programmer kit | [Amazon](https://www.amazon.com/KeeYees-SOIC8-EEPROM-CH341A-Programmer/dp/B07SHSL9X9) | Must include SOP8 test clip |
| Replacement chip (optional) | [DigiKey: S-93C76ADFJ-TB-U](https://www.digikey.com/en/products/detail/ablic-inc/S-93C76ADFJ-TB-U/6122914) | Seiko/ABLIC, verified working. See chip guide below |
| Soldering iron + flux + solder wick | Any | For desoldering the chip and doing the 5V mod |
| Multimeter | Any | To verify the 5V mod |
| x86 Windows PC | — | **Windows ARM does not work** (no CH341A driver support) |

---

## Replacement Chip Guide

The Honda dashboard uses the 93C76 in **16-bit mode** (512 words × 16 bits = 1024 bytes). If you need a replacement, you must buy the right variant.

**Best choice — Seiko/ABLIC S-93C76A:**
- Always 16-bit. No configuration needed. Pin 6 (TEST) can be left unconnected.
- [DigiKey: S-93C76ADFJ-TB-U](https://www.digikey.com/en/products/detail/ablic-inc/S-93C76ADFJ-TB-U/6122914) — SOP-8 package, confirmed working.

**Microchip 93C76 — watch the variant letter:**

| Variant | Mode | Pin 6 | Works? |
|---------|------|-------|--------|
| 93C76**A** | 8-bit only | — | **NO** |
| 93C76**B** | 16-bit only | — | **YES** |
| 93C76**C** | Selectable | ORG pin | **YES** — Pin 6 must be tied to VCC |

The **A variant is 8-bit and will not work**. If buying Microchip, get the **B** or **C**.

---

## Step 1 — 5V Mod on the CH341A

The CH341A has a voltage mismatch out of the box. The logic signals run at 5V but the VCC output is only 3.3V. The 93C76 datasheet says max input voltage is VCC + 0.3V — so at 3.3V VCC, the 5V signals exceed the 3.6V limit and can damage the chip.

The fix is to make VCC output 5V as well. The 93C76 is rated for 2.7V–5.5V so 5V is within spec. Google how to fix it.


---

## Step 2 — Desolder the Chip

**In-circuit reading does not work.** The CH341A cannot supply enough current to power the 93C76 while it is on the dashboard PCB.

1. Remove the instrument cluster from the car
2. Open it up — remove the clear cover and needle caps
3. Find the 93C76 — small 8-pin SOIC near the main MCU
4. Desolder with hot air or soldering iron + flux + solder wick

---

## Step 3 — Rewire the SOP8 Clip

The SOP8 clip that comes with the kit is wired for 25xx SPI chips. The 93C76 uses a different pinout (Microwire). You need to rearrange the wires in the connector.

**The red wire on the clip = Pin 1 (CS).**

### 93C76 pinout

```
     ┌──────────┐
CS 1 ┤●         ├ 8 VCC
SK 2 ┤          ├ 7 NC
DI 3 ┤          ├ 6 TEST/ORG
DO 4 ┤          ├ 5 GND
     └──────────┘
```

### Wiring map (93C76 → CH341A header)

| Clip pin | 93C76 signal | → CH341A slot | CH341A signal |
|:--------:|-------------|:-------------:|--------------|
| 1 | CS | 1 | CS |
| 2 | SK (clock) | 6 | CLK |
| 3 | DI (data in) | 5 | MOSI |
| 4 | DO (data out) | 2 | MISO |
| 5 | GND | 4 | GND |
| 6 | TEST/ORG | 8 | VCC (tie high) |
| 7 | NC | 7 | (no change) |
| 8 | VCC | 8 | VCC |

### How to repin the connector

Each wire snaps into its slot with a tiny plastic tab. Use a toothpick or SIM eject pin to press the tab and pull the wire out, then push it into the correct slot.

1. Remove wires 2, 3, 4, 5, 6 from the housing (leave 1, 7, 8)
2. Insert wire 4 (DO) → slot 2
3. Insert wire 5 (GND) → slot 4
4. Insert wire 3 (DI) → slot 5
5. Insert wire 2 (SK) → slot 6
6. Slot 3 stays **empty**
7. Wire 6 (TEST/ORG): twist together with wire 8 (VCC) into slot 8, or just leave it disconnected if your chip is a Seiko (TEST pin can float)

### Verify with a multimeter (continuity mode)

| Clip pin | Should connect to CH341A slot |
|:--------:|:----------------------------:|
| 1 (CS) | 1 (CS) |
| 2 (SK) | 6 (CLK) |
| 3 (DI) | 5 (MOSI) |
| 4 (DO) | 2 (MISO) |
| 5 (GND) | 4 (GND) |
| 8 (VCC) | 8 (VCC) |

---

## Step 4 — Read the Chip

1. Put the desoldered chip into a **SOP8-to-DIP8 socket adapter** (included in the kit). Match Pin 1 dot to the socket marker.
2. Connect the rewired clip or use Dupont wires following the wiring map above.
3. Double-check VCC and GND — a reversed connection destroys the chip.
4. Plug the CH341A into your **x86 Windows PC**.

### Software: NeoProgrammer

Download NeoProgrammer V2.2.0.10. It is available from the [YTEC-info CH341A-Softwares GitHub repo](https://github.com/YTEC-info/CH341A-Softwares) and other sources — search for "NeoProgrammer V2.2.0.10".

Install the CH341A driver from `Drivers/CH341A/SETUP.EXE` inside the NeoProgrammer folder.

### Reading

1. Open NeoProgrammer
2. **Select IC** → search `93C76` → select it (under Microwire)
3. Click **Read** → save as `dump.bin`
4. Please, if it is working firmware, upload it to digital kaos!

### Writing

1. **Open** → load your modified `.bin` file
2. Click **Program**
3. **Read** again and compare to verify the write

---

## Step 5 — Reinstall

1. Solder the chip back onto the dashboard PCB (Pin 1 dot matches the footprint marker)
2. Use flux and check for solder bridges
3. Reassemble and test in the car

---

## Byte Swap

The CH341A byte-swaps every pair of bytes when reading. The `.bin` file has reversed pairs compared to what the chip actually stores:

```
Chip: AB CD  →  File: CD AB
```

All the web tools in this project handle this automatically.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| CH341A not detected | Install driver from NeoProgrammer `Drivers/CH341A/SETUP.EXE` |
| CH341A not detected (ARM Windows) | **Not supported.** Use a regular x86 Windows PC |
| "No EEPROM found" | Check CS and CLK wiring |
| Reads all `0xFF` | VCC not reaching chip — do the 5V mod |
| Reads all `0x00` | GND not connected, or wrong chip selected in NeoProgrammer |
| Two reads don't match | Bad contact — clean chip pins, reseat adapter |
| Garbage data | Wrong chip variant — 93C76**A** is 8-bit, won't work |
| Write fails | 5V mod needed — stock VCC is too low for reliable writes |
