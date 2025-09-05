from __future__ import annotations

from typing import Dict, Any
from PyQt5 import QtWidgets, QtGui

from core.model import AppConfig


def _hex_from_color(color: QtGui.QColor) -> str:
    return '#' + format(color.rgb() & 0xFFFFFF, '06x')


class ThemeSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, config: AppConfig | None = None, on_preview=None):
        super().__init__(parent)
        self.setWindowTitle("디자인 설정")
        self.setModal(True)
        self.resize(420, 360)
        self._config = config
        self._on_preview = on_preview
        # 원본 토큰 저장(취소 시 복원)
        self._original_preset = (config.theme.preset or "light")
        self._original_tokens: Dict[str, Any] = dict(config.theme.tokens or {})

        tokens: Dict[str, Any] = dict(config.theme.tokens or {})

        main = QtWidgets.QFormLayout(self)

        # Preset
        self.preset = QtWidgets.QComboBox(self)
        self.preset.addItems(["light"])  # dark disabled for now
        self.preset.setCurrentIndex(0)
        self.preset.setEnabled(False)
        main.addRow("테마", self.preset)

        # Font family
        self.font_family = QtWidgets.QFontComboBox(self)
        ff = str(tokens.get("font_family", "Segoe UI"))
        self.font_family.setCurrentFont(QtGui.QFont(ff))
        main.addRow("폰트", self.font_family)

        # Font size
        self.font_size = QtWidgets.QSpinBox(self)
        self.font_size.setRange(8, 48)
        self.font_size.setValue(int(tokens.get("font_size", 12)))
        main.addRow("폰트 크기", self.font_size)

        # Color pickers
        self.color_buttons: Dict[str, QtWidgets.QPushButton] = {}
        for key, label in [
            ("header_bg", "헤더 배경"),
            ("header_text", "헤더 글자"),
            ("cell_bg", "칸 배경"),
            ("cell_text", "칸 글자"),
            ("border", "테두리"),
            ("current_bg", "현재 교시 배경"),
            ("break_border", "쉬는시간 테두리"),
        ]:
            btn = QtWidgets.QPushButton(str(tokens.get(key, "#000000")))
            self._apply_btn_color_style(btn)
            btn.clicked.connect(lambda _, k=key: self._pick_color(k))
            self.color_buttons[key] = btn
            main.addRow(label, btn)

        # opacity & border width
        self.current_alpha = QtWidgets.QDoubleSpinBox(self)
        self.current_alpha.setRange(0.1, 1.0)
        self.current_alpha.setSingleStep(0.1)
        self.current_alpha.setValue(float(tokens.get("current_bg_alpha", "1.0")))
        main.addRow("현재 배경 불투명도", self.current_alpha)

        self.break_border_width = QtWidgets.QSpinBox(self)
        self.break_border_width.setRange(1, 6)
        self.break_border_width.setValue(int(tokens.get("break_border_width", "2")))
        main.addRow("쉬는시간 테두리 두께", self.break_border_width)

        # Buttons
        box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, parent=self
        )
        box.accepted.connect(self.accept)
        box.rejected.connect(self._on_reject)
        main.addRow(box)

        # 실시간 미리보기: 값 변경 신호 연결
        try:
            self.font_family.currentFontChanged.connect(lambda _: self._emit_preview())
        except Exception:
            pass
        self.font_size.valueChanged.connect(lambda _: self._emit_preview())
        self.current_alpha.valueChanged.connect(lambda _: self._emit_preview())
        self.break_border_width.valueChanged.connect(lambda _: self._emit_preview())

    def _apply_btn_color_style(self, btn: QtWidgets.QPushButton):
        try:
            color = btn.text()
            # 간단한 대비 처리: 밝기 기준 텍스트색 선택
            c = QtGui.QColor(color)
            brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
            text = "#000000" if brightness > 128 else "#FFFFFF"
            btn.setStyleSheet(f"background-color: {color}; color: {text};")
        except Exception:
            btn.setStyleSheet("")

    def _pick_color(self, key: str):
        current = self.color_buttons[key].text()
        color = QtGui.QColor(current)
        picked = QtWidgets.QColorDialog.getColor(color, self, "색 선택")
        if picked.isValid():
            hexv = _hex_from_color(picked)
            self.color_buttons[key].setText(hexv)
            self._apply_btn_color_style(self.color_buttons[key])
            self._emit_preview()

    def _collect_tokens_from_ui(self) -> Dict[str, Any]:
        tokens: Dict[str, Any] = {}
        tokens["font_family"] = self.font_family.currentFont().family()
        tokens["font_size"] = int(self.font_size.value())
        for k, btn in self.color_buttons.items():
            tokens[k] = btn.text()
        tokens["current_bg_alpha"] = str(self.current_alpha.value())
        tokens["break_border_width"] = str(self.break_border_width.value())
        return tokens

    def _emit_preview(self):
        if callable(self._on_preview):
            self._on_preview(self._collect_tokens_from_ui())

    def apply_to_config(self) -> AppConfig:
        cfg = self._config
        # preset
        cfg.theme.preset = self.preset.currentText()
        # tokens
        cfg.theme.tokens = self._collect_tokens_from_ui()
        return cfg

    def _on_reject(self):
        # 원본으로 미리보기 되돌리기
        if callable(self._on_preview):
            self._on_preview(dict(self._original_tokens))
        self.reject()


