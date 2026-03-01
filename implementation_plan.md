# Hex Heatmap Visualizer

## Goal Description
The objective is to create a visual tool that reads multiple `.bin` EEPROM dump files (specifically for the Honda Civic 93c76 chip) and compares them hex-by-hex. The tool will generate a "heatmap" to highlight which bytes are identical across all files, which are similar, and which are completely different. This visualization will help identify the specific memory regions that store the odometer (mileage) data, as these regions will vary continuously across different dumps, while static data (like VIN or fixed configuration) will remain identical.

## Proposed Changes

### Visualizer Script
I will create a Python script that accomplishes the following:
#### [NEW] `heatmap_visualizer.py`(file:///Users/casper/repos/HONDA_DASH_EEPROM_ANALYSIS/heatmap_visualizer.py)
- **Data Loading**: Read all `.bin` files from the `Files` directory.
- **Data Alignment**: Ensure all files are the same size (1024 bytes for a 93c76 EEPROM).
- **Comparison Logic**: Compare each byte position (0x000 to 0x3FF) across all loaded files.
- **Scoring**: Assign a "variance score" to each byte position based on how many different values exist at that location across the dataset.
  - 0 variance (Static): Byte is identical in all files (e.g., color: Dark Blue).
  - Low variance: Byte has a few different values (e.g., color: Light Blue or Yellow - possible checksums or small counters).
  - High variance: Byte has many different values (e.g., color: Red - likely the mileage data we are looking for).
- **Visualization Output**: Use `matplotlib` and `seaborn` to generate a 2D grid heatmap (e.g., 32 columns x 32 rows = 1024 bytes) visualizing the variance scores. The x-axis will represent the column offset (0x00-0x1F), and the y-axis will represent the row offset (0x000-0x3E0).
- **Interactive Output**: Save the plot as an image (`heatmap.png`) or display it interactively if the environment allows. It will also print out the specific hex addresses that showed the highest variance.

## Verification Plan

### Automated Tests
- Run the script against the unpacked `.bin` files in the `Files` directory.
```bash
python3 heatmap_visualizer.py
```
- Verify that `heatmap.png` is successfully generated and visually highlights the regions of change.
- Verify that the terminal output lists the memory addresses of the highest variance bytes, which should correlate with known Honda Civic 93c76 odometer locations based on community knowledge.
