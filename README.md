# Honda Civic Dashboard EEPROM Analysis & Recovery

## Purpose
The purpose of this project is to read, analyze, and potentially re-flash the EEPROM from a Honda Civic dashboard. The primary goal is to recover a dashboard that is suspected to have corrupted EEPROM data.

## Hardware & Tools
- **Dashboard**: Honda Civic instrument cluster
- **Programmer**: KeeYees S018 SOP8 Test Clip with CH341A Programmer (USB)
- **Host OS**: Windows 11 (ARM edition, running on Apple Silicon via VMware Fusion Pro)

## Project Plan

### Phase 1: Environment Setup
1. **Install Programmer Drivers**: The CH341A programmer requires specific drivers. Since the host OS is Windows 11 ARM via VMware Fusion Pro, ensure the USB device is properly passed through to the VM, and compatible drivers are recognized.
2. **Setup Programming Software**: Install compatible software to read/write the EEPROM. 
   - **NeoProgrammer**: Generally considered more user-friendly with visual guides showing exactly how to orient the chip, and it immediately displays read data in a hex/binary viewer. Often preferred by beginners for these exact reasons.
   - **AsProgrammer**: The open-source original that NeoProgrammer was based on. It is actively maintained and some users report it being slightly faster and more stable, though it lacks the visual pin-out guides.
   *Ensure whichever you choose runs correctly under Windows 11 ARM emulation.*

### Phase 2: Reading the Existing EEPROM
1. **Locate the EEPROM**: Identify the **93c76** EEPROM chip on the Honda Civic dashboard circuit board.
2. **Connect the SOP8 Clip**: Ensure the board is powered off and isolated. Connect the SOP8 test clip to the **93c76** chip, ensuring correct pin orientation (Pin 1 to Pin 1).
   *Note: As per community feedback, check if the chip can be read in-circuit. Some boards require 3.3V to be injected or the chip to be desoldered if surrounding components interfere with the reading process.*
3. **Read and Verify**: 
   - Read the chip contents at least 3 separate times.
   - Save each read as a `.bin` file.
   - Compare the checksums or file contents of the 3 reads. **Do not proceed to flashing unless all 3 reads are 100% identical.** This ensures a good connection and prevents catastrophic data loss.
4. **Backup**: Safely store the validated original dump.

### Phase 3: Analysis
1. **Analyze Corrupt Data**: Compare the corrupted dump from the target dashboard against known good dumps (the reference `.bin` files previously extracted).
2. **Identify Key Regions**: Identify specific data blocks such as mileage (odometer readings), VIN numbers, and immobilization data (if applicable to this specific EEPROM sector).
3. **Prepare New Image**: Repair the corrupted dump or modify a known-good dump to match the required parameters (like matching the correct mileage) for the target vehicle.

### Phase 4: Flashing the Repaired EEPROM
1. **Erase (If Required)**: Depending on the chip and software, explicitly erase the EEPROM.
2. **Write Data**: Flash the repaired or modified `.bin` file back to the EEPROM using the CH341A programmer.
3. **Verify Write**: Read the chip one final time to verify that the flashed contents exactly match the intended `.bin` file.

### Phase 5: Testing
1. **Reassembly**: Disconnect the programmer and reassemble the dashboard.
2. **In-Car Test**: Install the dashboard back into the vehicle and turn on the ignition to verify functionality (gauges, LCD, warning lights, and correct mileage display).
