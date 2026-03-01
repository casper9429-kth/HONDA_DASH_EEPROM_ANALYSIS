import os
import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLabel, QComboBox, QHeaderView, QCheckBox, 
                             QGroupBox, QScrollArea, QGridLayout, QSplitter,
                             QListWidget, QListWidgetItem, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPalette, QFontDatabase


# ─── Data Loading ───────────────────────────────────────────────────────────

def load_bin_files(directory):
    bin_files = []
    data_arrays = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".bin"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "rb") as f:
                data = f.read()
            if len(data) == 1024:
                bin_files.append(filename)
                data_arrays.append(list(data))
    return bin_files, data_arrays


# ─── Bit Operation Helpers ──────────────────────────────────────────────────

def bit_invert(val):
    return val ^ 0xFF

def nibble_swap(val):
    return ((val >> 4) & 0x0F) | ((val & 0x0F) << 4)

def bit_reverse(val):
    result = 0
    for _ in range(8):
        result = (result << 1) | (val & 1)
        val >>= 1
    return result

def bcd_decode_bytes(byte_list):
    """Decode a list of bytes as BCD. Returns None if any nibble > 9."""
    digits = []
    for b in byte_list:
        hi = (b >> 4) & 0x0F
        lo = b & 0x0F
        if hi > 9 or lo > 9:
            return None
        digits.append(str(hi))
        digits.append(str(lo))
    return "".join(digits)

def format_binary(val, bits=8):
    s = format(val, f'0{bits}b')
    # Group in 4-bit nibbles
    return " ".join(s[i:i+4] for i in range(0, len(s), 4))


# ─── Main Window ────────────────────────────────────────────────────────────

class HexHeatmapViewer(QMainWindow):
    def __init__(self, bin_files, data_arrays):
        super().__init__()
        self.setWindowTitle("Honda 93c76 EEPROM Inspector")
        self.resize(1500, 900)

        self.all_bin_files = bin_files
        self.all_data_arrays = data_arrays
        self.num_bytes = 1024
        self.active_file_indices = list(range(len(self.all_bin_files)))
        self.selected_byte_idx = None

        self._build_ui()
        self.recalculate_variance()
        self.update_table()

    # ── UI Construction ─────────────────────────────────────────────────

    def _build_ui(self):
        # Force light palette
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        pal.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        pal.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        pal.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        QApplication.instance().setPalette(pal)

        # Monospace font
        self.mono_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.mono_font.setPointSize(11)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # ── Panel 1: File Sidebar ───────────────────────────────────────
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(6, 6, 6, 6)

        sidebar_layout.addWidget(QLabel("<b>Files for Comparison</b>"))

        self.file_list = QListWidget()
        for i, fname in enumerate(self.all_bin_files):
            item = QListWidgetItem(fname)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.file_list.addItem(item)
        self.file_list.itemChanged.connect(self.on_file_toggled)
        sidebar_layout.addWidget(self.file_list)

        sidebar_layout.addWidget(QLabel("<b>Display File</b>"))
        self.file_combo = QComboBox()
        self.file_combo.addItems(self.all_bin_files)
        self.file_combo.currentIndexChanged.connect(self.update_table)
        sidebar_layout.addWidget(self.file_combo)

        # Active low toggle
        self.invert_cb = QCheckBox("Active Low (Invert)")
        self.invert_cb.stateChanged.connect(self._on_mode_changed)
        sidebar_layout.addWidget(self.invert_cb)

        # Byte swap toggle (swap every pair of bytes — 16-bit word endian flip)
        self.byteswap_cb = QCheckBox("Byte Swap (High↔Low)")
        self.byteswap_cb.stateChanged.connect(self._on_mode_changed)
        sidebar_layout.addWidget(self.byteswap_cb)

        # Legend
        legend = QLabel(
            "<small>"
            "<span style='background:#fff; border:1px solid #ccc; padding:2px'>&nbsp;&nbsp;</span> Identical&nbsp;&nbsp;"
            "<span style='background:#ffff00; padding:2px'>&nbsp;&nbsp;</span> Low var&nbsp;&nbsp;"
            "<span style='background:#ff4400; color:#fff; padding:2px'>&nbsp;&nbsp;</span> High var"
            "</small>"
        )
        sidebar_layout.addWidget(legend)
        sidebar_layout.addStretch()

        sidebar.setMaximumWidth(300)
        splitter.addWidget(sidebar)

        # ── Panel 2: Hex Grid ───────────────────────────────────────────
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(2, 2, 2, 2)

        self.table = QTableWidget()
        self.table.setColumnCount(17)  # 16 hex + 1 ASCII
        self.table.setRowCount(self.num_bytes // 16)

        col_headers = [f"+{i:X}" for i in range(16)] + ["ASCII"]
        self.table.setHorizontalHeaderLabels(col_headers)
        row_headers = [f"{i*16:04X}" for i in range(self.num_bytes // 16)]
        self.table.setVerticalHeaderLabels(row_headers)

        self.table.setFont(self.mono_font)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #ffffff; color: #000000; gridline-color: #d0d0d0; }
            QTableWidget::item:selected { background-color: #0078d7; color: #ffffff; }
        """)

        for i in range(16):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(16, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellClicked.connect(self.on_cell_clicked)

        center_layout.addWidget(self.table)
        splitter.addWidget(center)

        # ── Panel 3: Inspector ──────────────────────────────────────────
        inspector = QWidget()
        inspector_layout = QVBoxLayout(inspector)
        inspector_layout.setContentsMargins(8, 8, 8, 8)

        inspector_layout.addWidget(QLabel("<b>Inspector</b>"))

        self.inspector_text = QLabel("Click a byte in the hex grid.")
        self.inspector_text.setFont(self.mono_font)
        self.inspector_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.inspector_text.setWordWrap(True)
        self.inspector_text.setStyleSheet(
            "background-color: #ffffff; color: #000000; padding: 10px; border: 1px solid #ccc;"
        )
        self.inspector_text.setMinimumWidth(280)

        scroll = QScrollArea()
        scroll.setWidget(self.inspector_text)
        scroll.setWidgetResizable(True)
        inspector_layout.addWidget(scroll)

        inspector.setMaximumWidth(340)
        splitter.addWidget(inspector)

        # Set initial splitter proportions
        splitter.setSizes([220, 800, 320])

    # ── Event Handlers ──────────────────────────────────────────────────

    def on_file_toggled(self, item):
        self.active_file_indices = []
        for i in range(self.file_list.count()):
            if self.file_list.item(i).checkState() == Qt.CheckState.Checked:
                self.active_file_indices.append(i)
        self.recalculate_variance()
        self.update_table()
        # Re-render inspector if a byte was selected
        if self.selected_byte_idx is not None:
            self._update_inspector(self.selected_byte_idx)

    def _on_mode_changed(self):
        self.recalculate_variance()
        self.update_table()
        if self.selected_byte_idx is not None:
            self._update_inspector(self.selected_byte_idx)

    def on_cell_clicked(self, row, col):
        if col == 16:
            # ASCII column clicked — show per-file ASCII for this row
            self._update_ascii_inspector(row)
            return
        byte_idx = row * 16 + col
        if byte_idx >= self.num_bytes:
            return
        self.selected_byte_idx = byte_idx
        self._update_inspector(byte_idx)

    def _update_ascii_inspector(self, row):
        """Show the full 16-byte ASCII string per active file for the given row."""
        start = row * 16
        addr = f"0x{start:04X}"

        lines = []
        lines.append(f"<h3>ASCII Row {addr}–0x{start+15:04X}</h3>")
        lines.append("<table width='100%' style='border-collapse:collapse;'>")
        lines.append("<tr><th align='left'>File</th><th align='left'>ASCII (16 bytes)</th></tr>")

        for f_idx in self.active_file_indices:
            fname = self.all_bin_files[f_idx]
            data = self._apply_transforms(self.all_data_arrays[f_idx])
            chars = []
            for i in range(16):
                v = data[start + i]
                chars.append(chr(v) if 32 <= v <= 126 else '.')
            ascii_str = "".join(chars)
            short_name = fname[:25] + "…" if len(fname) > 25 else fname
            lines.append(
                f"<tr>"
                f"<td style='padding:2px 4px; border-top:1px solid #ccc;'>{short_name}</td>"
                f"<td style='padding:2px 4px; border-top:1px solid #ccc; font-family:monospace;'><b>{ascii_str}</b></td>"
                f"</tr>"
            )
        lines.append("</table>")
        self.inspector_text.setText("<br>".join(lines))
        self.inspector_text.repaint()

    # ── Variance ────────────────────────────────────────────────────────

    def recalculate_variance(self):
        self.variance_scores = np.zeros(self.num_bytes)
        if len(self.active_file_indices) <= 1:
            self.max_variance = 1
            return
        # Apply current transforms so heatmap matches what's displayed
        transformed = [self._apply_transforms(self.all_data_arrays[i]) for i in self.active_file_indices]
        for byte_idx in range(self.num_bytes):
            values = set(t[byte_idx] for t in transformed)
            self.variance_scores[byte_idx] = len(values) - 1
        self.max_variance = max(np.max(self.variance_scores), 1)

    def get_heatmap_color(self, variance):
        if variance == 0 or len(self.active_file_indices) <= 1:
            return QColor(255, 255, 255)
        intensity = variance / self.max_variance
        return QColor(255, int(255 * (1 - intensity)), 0)

    # ── Table Update ────────────────────────────────────────────────────

    def _apply_transforms(self, data):
        """Return a transformed copy of the data based on current toggle states."""
        out = list(data)
        if self.byteswap_cb.isChecked():
            # Swap every pair of bytes (16-bit word endian flip)
            for i in range(0, len(out) - 1, 2):
                out[i], out[i+1] = out[i+1], out[i]
        if self.invert_cb.isChecked():
            out = [v ^ 0xFF for v in out]
        return out

    def update_table(self):
        file_idx = self.file_combo.currentIndex()
        if file_idx < 0:
            return
        data = self._apply_transforms(self.all_data_arrays[file_idx])

        for row in range(self.table.rowCount()):
            ascii_chars = []
            for col in range(16):
                byte_idx = row * 16 + col
                val = data[byte_idx]

                item = QTableWidgetItem(f"{val:02X}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(self.get_heatmap_color(self.variance_scores[byte_idx]))
                item.setForeground(QColor(0, 0, 0))
                self.table.setItem(row, col, item)

                ascii_chars.append(chr(val) if 32 <= val <= 126 else '.')

            ascii_item = QTableWidgetItem("".join(ascii_chars))
            ascii_item.setBackground(QColor(240, 240, 240))
            ascii_item.setForeground(QColor(0, 0, 0))
            self.table.setItem(row, 16, ascii_item)

    # ── Inspector ───────────────────────────────────────────────────────

    def _update_inspector(self, byte_idx):
        file_idx = self.file_combo.currentIndex()
        if file_idx < 0:
            return
        data = self._apply_transforms(self.all_data_arrays[file_idx])
        variance = int(self.variance_scores[byte_idx])

        val = data[byte_idx]

        addr = f"0x{byte_idx:04X}"
        modes = []
        if self.invert_cb.isChecked(): modes.append("Inverted")
        if self.byteswap_cb.isChecked(): modes.append("Byte-Swapped")
        mode_str = ", ".join(modes) if modes else "Standard"

        lines = []
        lines.append(f"<h3>Address {addr}</h3>")
        lines.append(f"<b>Mode:</b> {mode_str}")
        if len(self.active_file_indices) > 1:
            lines.append(f"<b>Variance:</b> {variance}")
        lines.append("<hr>")

        # ── Single Byte ─────────────────────────────────────────────
        lines.append("<b>━━ Single Byte ━━</b><br>")
        lines.append(f"<b>Hex:</b> 0x{val:02X}")
        lines.append(f"<b>Decimal:</b> {val}")
        lines.append(f"<b>Signed:</b> {val if val < 128 else val - 256}")
        lines.append(f"<b>Binary:</b> {format_binary(val)}")
        lines.append(f"<b>Inverted:</b> 0x{bit_invert(val):02X} (dec {bit_invert(val)})")
        lines.append(f"<b>Nibble Swap:</b> 0x{nibble_swap(val):02X} (dec {nibble_swap(val)})")
        lines.append(f"<b>Bit Reverse:</b> 0x{bit_reverse(val):02X}")
        bcd = bcd_decode_bytes([val])
        lines.append(f"<b>BCD:</b> {bcd if bcd else 'N/A'}")
        lines.append(f"<b>ASCII:</b> {'&apos;' + chr(val) + '&apos;' if 32 <= val <= 126 else 'N/A'}")

        # ── 16-bit Word ─────────────────────────────────────────────
        if byte_idx + 1 < self.num_bytes:
            val2 = data[byte_idx + 1]
            be16 = (val << 8) | val2
            le16 = (val2 << 8) | val
            lines.append("<hr>")
            lines.append(f"<b>━━ 16-bit @ {addr} ━━</b><br>")
            lines.append(f"<b>Big Endian:</b> 0x{be16:04X} (dec {be16})")
            lines.append(f"<b>Little Endian:</b> 0x{le16:04X} (dec {le16})")
            bcd16 = bcd_decode_bytes([val, val2])
            lines.append(f"<b>BCD (BE):</b> {bcd16 if bcd16 else 'N/A'}")

        # ── 24-bit (3 byte) ─────────────────────────────────────────
        if byte_idx + 2 < self.num_bytes:
            val3 = data[byte_idx + 2]
            be24 = (val << 16) | (val2 << 8) | val3
            lines.append("<hr>")
            lines.append(f"<b>━━ 24-bit @ {addr} ━━</b><br>")
            lines.append(f"<b>Big Endian:</b> 0x{be24:06X} (dec {be24})")
            bcd24 = bcd_decode_bytes([val, val2, val3])
            lines.append(f"<b>BCD (BE):</b> {bcd24 if bcd24 else 'N/A'}")

        # ── Per-File Breakdown ──────────────────────────────────────
        lines.append("<hr>")
        lines.append("<b>━━ Per-File Values ━━</b><br>")
        lines.append("<table width='100%' style='border-collapse:collapse;'>")
        lines.append("<tr><th align='left'>File</th><th align='left'>Hex</th><th align='left'>Dec</th></tr>")

        for f_idx in self.active_file_indices:
            fname = self.all_bin_files[f_idx]
            fdata = self._apply_transforms(self.all_data_arrays[f_idx])
            fval = fdata[byte_idx]
            # Highlight if different from selected file
            highlight = "" if fval == val else " style='background-color:#fff3cd;'"
            # Truncate long filenames
            short_name = fname[:25] + "…" if len(fname) > 25 else fname
            lines.append(
                f"<tr{highlight}>"
                f"<td style='padding:2px 4px;'>{short_name}</td>"
                f"<td style='padding:2px 4px;'><b>{fval:02X}</b></td>"
                f"<td style='padding:2px 4px;'>{fval}</td>"
                f"</tr>"
            )
        lines.append("</table>")

        self.inspector_text.setText("<br>".join(lines))
        self.inspector_text.repaint()


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    directory = "Files"
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' not found.")
        return

    bin_files, data_arrays = load_bin_files(directory)
    if not data_arrays:
        print("No valid 1024-byte .bin files found.")
        return

    app = QApplication(sys.argv)
    viewer = HexHeatmapViewer(bin_files, data_arrays)
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
