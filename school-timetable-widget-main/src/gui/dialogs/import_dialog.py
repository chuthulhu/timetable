from PyQt5 import QtWidgets, QtCore, QtGui
import json

class ImportDialog(QtWidgets.QDialog):
    """시간표 가져오기 대화상자"""
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
        self.parent = parent
        self.settings_manager = parent.settings_manager
        self.setWindowTitle("시간표 가져오기")
        self.setMinimumSize(500, 400)
        
        # 가져오기 데이터 변수 초기화
        self.imported_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        layout = QtWidgets.QVBoxLayout()
        
        # 파일 가져오기 영역
        file_info = QtWidgets.QLabel("JSON 파일에서 시간표와 설정을 가져올 수 있습니다.")
        file_info.setWordWrap(True)
        layout.addWidget(file_info)
        
        # 파일 선택 버튼
        file_btn_layout = QtWidgets.QHBoxLayout()
        load_file_btn = QtWidgets.QPushButton("JSON 파일 열기")
        load_file_btn.clicked.connect(self.open_json_file)
        file_btn_layout.addWidget(load_file_btn)
        file_btn_layout.addStretch(1)
        layout.addLayout(file_btn_layout)
        
        # 가져오기 결과 표시 영역
        result_group = QtWidgets.QGroupBox("가져오기 결과")
        result_layout = QtWidgets.QVBoxLayout()
        
        self.result_text = QtWidgets.QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # 버튼 영역
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.import_btn = QtWidgets.QPushButton("시간표에 적용")
        self.import_btn.clicked.connect(self.apply_imported_data)
        self.import_btn.setEnabled(False)
        buttons_layout.addWidget(self.import_btn)
        
        close_btn = QtWidgets.QPushButton("닫기")
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
    def open_json_file(self):
        """JSON 파일 열기"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "JSON 파일 열기", "", "JSON 파일 (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.imported_data = json.load(f)
                
            # 결과 표시
            self.display_imported_data()
            
        except Exception as e:
            self.result_text.setText(f"JSON 파일 처리 중 오류가 발생했습니다:\n{str(e)}")
    
    def display_imported_data(self):
        """가져온 데이터 내용 표시"""
        if not self.imported_data:
            self.result_text.setText("가져온 데이터가 없습니다.")
            self.import_btn.setEnabled(False)
            return
        
        result = "가져온 데이터:\n\n"
        
        # 시간표 데이터
        if "timetable" in self.imported_data:
            timetable = self.imported_data["timetable"]
            result += "■ 시간표 데이터\n"
            for day in ["월", "화", "수", "목", "금"]:
                if day in timetable:
                    result += f"  {day}요일: "
                    periods = []
                    for period, subject in timetable[day].items():
                        if subject:  # 내용이 있는 경우만 표시
                            periods.append(f"{period}교시({subject})")
                    result += ", ".join(periods) + "\n"
            result += "\n"
        
        # 시간 설정
        if "time_settings" in self.imported_data:
            time_settings = self.imported_data["time_settings"]
            result += "■ 교시별 시간 설정\n"
            for period, times in sorted(time_settings.items(), key=lambda x: int(x[0])):
                result += f"  {period}교시: {times['start']} ~ {times['end']}\n"
        
        self.result_text.setText(result)
        self.import_btn.setEnabled(True)
    
    def apply_imported_data(self):
        """가져온 데이터를 현재 설정에 적용"""
        if not self.imported_data:
            return
            
        # 적용할 데이터 선택 대화상자
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("가져오기 옵션")
        layout = QtWidgets.QVBoxLayout()
        
        # 시간표 데이터 옵션
        timetable_check = QtWidgets.QCheckBox("시간표 데이터")
        timetable_check.setEnabled("timetable" in self.imported_data)
        timetable_check.setChecked(timetable_check.isEnabled())
        layout.addWidget(timetable_check)
        
        # 시간 설정 옵션
        time_settings_check = QtWidgets.QCheckBox("교시별 시간 설정")
        time_settings_check.setEnabled("time_settings" in self.imported_data)
        time_settings_check.setChecked(time_settings_check.isEnabled())
        layout.addWidget(time_settings_check)
        
        # 경고 메시지
        warning_label = QtWidgets.QLabel("경고: 선택한 데이터는 현재 설정을 덮어씁니다.")
        warning_label.setStyleSheet("color: red;")
        layout.addWidget(warning_label)
        
        # 버튼
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        # 대화상자 실행
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return
        
        # 선택된 데이터 적용
        applied = False
        
        # 시간표 데이터 적용
        if timetable_check.isChecked() and "timetable" in self.imported_data:
            self.settings_manager.update_timetable_data(self.imported_data["timetable"])
            applied = True
        
        # 시간 설정 적용
        if time_settings_check.isChecked() and "time_settings" in self.imported_data:
            time_settings = self.imported_data["time_settings"]
            
            # QTime 객체로 변환
            for period, times in time_settings.items():
                period = int(period)
                start_hour, start_min = map(int, times["start"].split(':'))
                end_hour, end_min = map(int, times["end"].split(':'))
                
                self.settings_manager.time_ranges[period] = {
                    "start": QtCore.QTime(start_hour, start_min),
                    "end": QtCore.QTime(end_hour, end_min)
                }
            
            # 설정 저장
            self.settings_manager.save_time_settings()
            applied = True
        
        # 부모 위젯에 변경사항 반영
        if applied:
            if hasattr(self.parent, "update_timetable_display"):
                self.parent.update_timetable_display()
            if hasattr(self.parent, "update_current_period"):
                self.parent.update_current_period()
                
            QtWidgets.QMessageBox.information(
                self, 
                "가져오기 완료", 
                "선택한 데이터가 성공적으로 적용되었습니다."
            )
            
    def closeEvent(self, event):
        """대화상자 닫힐 때 호출"""
        super().closeEvent(event)
