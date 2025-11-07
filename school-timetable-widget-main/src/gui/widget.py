from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import datetime
import json
import logging

# 새로 추가: Qt 경고 메시지 억제
os.environ["QT_LOGGING_RULES"] = "qt.qpa.*=false"

# 사용자 정의 모듈
from notifications.notification_manager import NotificationManager
from utils.settings_manager import SettingsManager
from utils.styling import (
    hex_to_rgba, generate_header_style, generate_cell_style, 
    generate_current_style, generate_drag_style
)
from .dialogs.time_dialog import TimeRangeDialog
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.timetable_dialog import TimetableEditDialog

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# 드래그/리사이징 관련 로직을 별도 믹스인 클래스로 분리
class DragResizeMixin:
    def init_drag_resize(self):
        self.dragging = False
        self.resizing = False
        self.drag_start_pos = None
        self.resize_start_pos = None
        self.initial_size = self.size()
    
    def handle_mouse_press(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # 드래그/리사이징 시작 시 모든 셀 크기 조정 타이머를 취소
            if hasattr(self, 'resize_timer'):
                self.resize_timer.stop()
            
            # 위치가 고정되어 있으면 크기 조절만 허용
            if self.settings_manager.is_position_locked:
                if event.pos().x() >= self.rect().width() - 20 and event.pos().y() >= self.rect().height() - 20:
                    self.resizing = True
                    self.resize_start_pos = event.globalPos()
                    self.initial_size = self.size()
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
            else:
                # 위치 고정이 아닐 때는 기존과 동일하게 동작
                if event.pos().x() >= self.rect().width() - 20 and event.pos().y() >= self.rect().height() - 20:
                    self.resizing = True
                    self.resize_start_pos = event.globalPos()
                    self.initial_size = self.size()
                    self.setCursor(QtCore.Qt.SizeFDiagCursor)
                else:
                    self.dragging = True
                    self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
                    self.setCursor(QtCore.Qt.ClosedHandCursor)
                    # 드래그 모드에서 스타일 변경
                    drag_bg_rgba = hex_to_rgba(self.settings_manager.header_bg_color, self.settings_manager.header_opacity)
                    border_rgba = hex_to_rgba(self.settings_manager.border_color, self.settings_manager.border_opacity)
                    drag_style = generate_drag_style(
                        drag_bg_rgba, 
                        self.settings_manager.header_text_color, 
                        border_rgba,
                        self.settings_manager.font_family,
                        self.settings_manager.font_size
                    )
                    for header in self.day_headers.values():
                        header.setStyleSheet(drag_style)
    
    def handle_mouse_move(self, event):
        if self.resizing:
            diff = event.globalPos() - self.resize_start_pos
            new_width = max(self.minimumWidth(), self.initial_size.width() + diff.x())
            new_height = max(self.minimumHeight(), self.initial_size.height() + diff.y())
            self.resize(new_width, new_height)
        elif self.dragging and event.buttons() == QtCore.Qt.LeftButton and not self.settings_manager.is_position_locked:
            # 위치 고정이 아닐 때만 드래그 허용
            # 드래그 중에는 셀 크기 조정 타이머를 취소하여 모니터 이동 시 발생하는 resizeEvent로 인한 셀 크기 변경 방지
            if hasattr(self, 'resize_timer'):
                self.resize_timer.stop()
            self.move(event.globalPos() - self.drag_start_pos)
        else:
            if event.pos().x() >= self.rect().width() - 20 and event.pos().y() >= self.rect().height() - 20:
                self.setCursor(QtCore.Qt.SizeFDiagCursor)
            else:
                self.setCursor(QtCore.Qt.ArrowCursor)
    
    def handle_mouse_release(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            was_resizing = self.resizing
            was_dragging = self.dragging
            self.resizing = False
            self.dragging = False
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.update_styles()
            # 위치 및 크기 저장
            self.save_widget_position()
            
            # 리사이징이 끝났을 때만 셀 크기 조정
            if was_resizing:
                # 약간의 지연을 두어 레이아웃이 완전히 업데이트된 후 실행
                QtCore.QTimer.singleShot(200, self.adjust_cell_sizes)
            elif was_dragging:
                # 드래그 중 모니터 이동 시 위젯 크기가 변경될 수 있으므로 드래그 종료 시에도 셀 크기 조정
                # 모니터 변경 후 레이아웃이 완전히 안정화될 때까지 충분한 지연
                # DPI 변경도 함께 확인
                QtCore.QTimer.singleShot(300, self._check_and_adjust_for_dpi_change)

class Widget(DragResizeMixin, QtWidgets.QWidget):
    def __init__(
        self, 
        settings_manager=None, 
        notification_manager=None, 
        app_manager=None, 
        parent=None
    ):
        super().__init__(parent)
        
        # 매니저 인스턴스 설정
        self.settings_manager = (
            settings_manager if settings_manager 
            else SettingsManager.get_instance()
        )
        self.notification_manager = (
            notification_manager if notification_manager 
            else NotificationManager.get_instance()
        )
        self.app_manager = app_manager
        
        # 프레임 없는 창으로 설정
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnBottomHint |  # 창을 항상 맨 아래에 표시
            QtCore.Qt.Tool |  # 작업 표시줄에 표시되지 않음
            QtCore.Qt.FramelessWindowHint  # 프레임 없음
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 배경을 완전 투명하게 설정
        self.setMouseTracking(True)
        
        # DPI 스케일링 지원 활성화 (모니터 간 이동 시 DPI 변경 처리)
        self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, False)
        
        # 현재 교시 및 요일 정보 초기화
        self.current_period = None
        self.current_day_idx = None
        
        # 현재 스크린의 DPI 정보 저장 (모니터 간 이동 시 DPI 변경 감지용)
        self.last_screen_dpi = None
        self.last_screen_device_pixel_ratio = None
        
        # 드래그 및 리사이징 관련 변수 초기화 (init_ui 이전에 호출)
        self.init_drag_resize()
        
        # 위젯 초기화
        self.init_ui()
        
        # 초기 DPI 정보 저장
        current_global_pos = self.mapToGlobal(self.rect().center()) if self.isVisible() else QtCore.QPoint(0, 0)
        current_screen = QtWidgets.QApplication.screenAt(current_global_pos) if self.isVisible() else QtWidgets.QApplication.primaryScreen()
        if current_screen:
            self.last_screen_dpi = current_screen.logicalDotsPerInch()
            self.last_screen_device_pixel_ratio = current_screen.devicePixelRatio()
        
        # 타이머 설정 (매 분마다 현재 교시 업데이트)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_current_period)
        self.timer.start(60000)  # 60초 (1분) 마다 실행
        
        # 셀 크기 조정을 위한 지연 타이머 (모니터 변경 시 사용)
        self.resize_timer = QtCore.QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.adjust_cell_sizes)
        
        # 현재 시간에 맞는 교시 하이라이트
        self.update_current_period()
        
        # 마우스 우클릭 메뉴
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.cleanup_on_close = None  # 종료 시 호출할 정리 함수
    
    def init_ui(self):
        """UI 초기화"""
        # 위젯 크기 설정
        self.setMinimumSize(400, 300)
        
        # 저장된 위젯 위치 불러오기 및 적용
        self.apply_saved_position()
        
        # 전체 레이아웃
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        # 시간표 그리드 레이아웃
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setSpacing(4)
        
        # 요일 헤더 생성 (1행)
        self.day_headers = {}
        days = ["", "월", "화", "수", "목", "금"]
        for col, day in enumerate(days):
            label = QtWidgets.QLabel(day)
            label.setAlignment(QtCore.Qt.AlignCenter)
            # 마우스 이벤트 추적 설정
            label.setMouseTracking(True)
            label.enterEvent = lambda event, lbl=label: self.on_label_hover_enter(event, lbl)
            label.leaveEvent = lambda event, lbl=label: self.on_label_hover_leave(event, lbl)
            self.grid_layout.addWidget(label, 0, col)
            self.day_headers[col] = label
        
        # 교시 헤더 및 셀 생성 (2행부터)
        self.period_headers = {}
        self.cell_widgets = {}
        
        for row in range(1, 8):  # 1교시부터 7교시까지
            # 교시 헤더 (첫 번째 열)
            period_label = QtWidgets.QLabel(f"{row}")
            period_label.setAlignment(QtCore.Qt.AlignCenter)
            # 마우스 이벤트 추적 설정
            period_label.setMouseTracking(True)
            period_label.enterEvent = lambda event, lbl=period_label: self.on_label_hover_enter(event, lbl)
            period_label.leaveEvent = lambda event, lbl=period_label: self.on_label_hover_leave(event, lbl)
            self.grid_layout.addWidget(period_label, row, 0)
            self.period_headers[row] = period_label
            
            # 각 요일별 셀 (2-6열)
            for col in range(1, 6):  # 월화수목금
                cell = QtWidgets.QLabel()
                cell.setAlignment(QtCore.Qt.AlignCenter)
                cell.setWordWrap(True)
                # 셀 크기를 레이아웃이 완전히 제어하도록 설정 (내용에 따라 크기 변경 방지)
                # Ignored 정책을 사용하면 위젯이 자신의 크기를 제안하지 않고 레이아웃이 완전히 제어
                cell.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
                # 셀의 최소/최대 크기를 설정하여 내용에 의존하지 않도록 함
                # DPI 변경 시에도 셀 크기가 내용에 의해 변경되지 않도록 최소 크기를 0으로 설정
                cell.setMinimumSize(0, 0)
                cell.setMaximumSize(16777215, 16777215)  # QWIDGETSIZE_MAX
                # 마우스 이벤트 추적 설정
                cell.setMouseTracking(True)
                cell.enterEvent = lambda event, c=cell: self.on_cell_hover_enter(event, c)
                cell.leaveEvent = lambda event, c=cell: self.on_cell_hover_leave(event, c)
                self.grid_layout.addWidget(cell, row, col)
                self.cell_widgets[(row, col)] = cell
        
        main_layout.addLayout(self.grid_layout)
        self.setLayout(main_layout)
        
        # 그리드 레이아웃 크기 조정을 위한 초기 설정
        self.setup_grid_sizing()
        
        # 스타일 적용
        self.update_styles()
        
        # 시간표 데이터 표시
        self.update_timetable_display()
    
    def setup_grid_sizing(self):
        """그리드 레이아웃의 셀 크기를 균등하게 설정"""
        self.adjust_cell_sizes()
    
    def adjust_cell_sizes(self):
        """셀의 가로와 세로를 균등하게 조정 (헤더 제외)"""
        # 드래그/리사이징 중일 때는 실행하지 않음 (속성이 초기화된 경우에만 체크)
        # 모니터 이동 중에도 드래그가 계속되므로 이 체크가 중요함
        if hasattr(self, 'resizing') and hasattr(self, 'dragging'):
            if self.resizing or self.dragging:
                return
        
        # 위젯이 아직 표시되지 않았거나 크기가 0이면 실행하지 않음
        if not self.isVisible() or self.width() <= 0 or self.height() <= 0:
            return
        
        # 전체 위젯 크기에서 마진 제외
        margins = self.layout().contentsMargins()
        available_width = self.width() - margins.left() - margins.right()
        available_height = self.height() - margins.top() - margins.bottom()
        
        # 유효하지 않은 크기면 실행하지 않음
        if available_width <= 0 or available_height <= 0:
            return
        
        # 교시 헤더 열(0열) 크기 설정
        # DPI 변경에 대응하기 위해 sizeHint() 대신 고정값 사용
        # DPI가 높은 모니터에서도 일관된 크기 유지
        if self.period_headers:
            # sizeHint()를 사용하되, DPI를 고려한 최소값 설정
            header_col_width_hint = self.period_headers[1].sizeHint().width()
            # 현재 스크린의 DPI를 고려하여 최소 크기 계산
            current_global_pos = self.mapToGlobal(self.rect().center())
            current_screen = QtWidgets.QApplication.screenAt(current_global_pos)
            if current_screen is None:
                current_screen = QtWidgets.QApplication.primaryScreen()
            
            if current_screen:
                dpi_ratio = current_screen.logicalDotsPerInch() / 96.0  # 96 DPI 기준
                # 기본 최소 크기(40px)에 DPI 비율 적용
                min_header_width = int(40 * dpi_ratio)
                header_col_width = max(min_header_width, header_col_width_hint)
            else:
                header_col_width = max(40, header_col_width_hint)
        else:
            header_col_width = 40
        
        self.grid_layout.setColumnMinimumWidth(0, header_col_width)
        self.grid_layout.setColumnStretch(0, 0)
        
        # 요일 헤더 행(0행) 크기 설정
        # DPI 변경에 대응하기 위해 sizeHint() 대신 고정값 사용
        if self.day_headers:
            header_row_height_hint = self.day_headers[1].sizeHint().height()
            # 현재 스크린의 DPI를 고려하여 최소 크기 계산
            current_global_pos = self.mapToGlobal(self.rect().center())
            current_screen = QtWidgets.QApplication.screenAt(current_global_pos)
            if current_screen is None:
                current_screen = QtWidgets.QApplication.primaryScreen()
            
            if current_screen:
                dpi_ratio = current_screen.logicalDotsPerInch() / 96.0  # 96 DPI 기준
                # 기본 최소 크기(30px)에 DPI 비율 적용
                min_header_height = int(30 * dpi_ratio)
                header_row_height = max(min_header_height, header_row_height_hint)
            else:
                header_row_height = max(30, header_row_height_hint)
        else:
            header_row_height = 30
        
        self.grid_layout.setRowMinimumHeight(0, header_row_height)
        self.grid_layout.setRowStretch(0, 0)
        
        # 셀 열(1-5열) 크기 균등 설정
        # setColumnMinimumWidth를 사용하지 않고 stretch만 사용하여 레이아웃이 자연스럽게 크기를 조정하도록 함
        # 이렇게 하면 정사각형으로 고정되지 않고 위젯 크기에 따라 자동으로 조정됨
        for col in range(1, 6):
            self.grid_layout.setColumnStretch(col, 1)  # 모든 열에 동일한 stretch
        
        # 셀 행(1-7행) 크기 균등 설정
        # setRowMinimumHeight를 사용하지 않고 stretch만 사용하여 레이아웃이 자연스럽게 크기를 조정하도록 함
        for row in range(1, 8):
            self.grid_layout.setRowStretch(row, 1)  # 모든 행에 동일한 stretch
        
        # 셀 위젯의 크기 정책이 이미 Ignored로 설정되어 있으므로
        # 레이아웃이 stretch 비율에 따라 균등하게 크기를 할당함
    
    def apply_saved_position(self):
        """
        저장된 위치와 크기 적용 (멀티모니터 지원)
        - 저장된 screen_info(geometry, name)가 있으면 해당 스크린 기준으로 복원
        - 없거나 스크린이 사라졌으면 primaryScreen 기준 fallback
        """
        pos = self.settings_manager.widget_position
        size = self.settings_manager.widget_size
        screen_info = getattr(self.settings_manager, 'widget_screen_info', None)

        # 현재 연결된 모든 스크린 정보
        screens = QtWidgets.QApplication.screens()
        target_screen = None

        # 저장된 스크린 정보가 있으면 해당 스크린 찾기 (geometry 우선, name fallback)
        if screen_info:
            for screen in screens:
                if (
                    'geometry' in screen_info and
                    screen.geometry().getRect() == tuple(screen_info['geometry'])
                ) or (
                    'name' in screen_info and
                    screen.name() == screen_info['name']
                ):
                    target_screen = screen
                    break
        # 없으면 primaryScreen 사용
        if not target_screen:
            target_screen = QtWidgets.QApplication.primaryScreen()

        screen_geom = target_screen.geometry()
        
        # 위젯이 화면 경계를 벗어나지 않도록 위치 조정
        # 위젯의 너비와 높이를 고려
        widget_width = size.get("width", self.width()) # 저장된 크기가 없다면 현재 크기 사용
        widget_height = size.get("height", self.height())

        # x 좌표 조정
        min_x = screen_geom.left()
        max_x = screen_geom.right() - widget_width
        # max_x가 min_x보다 작아지는 경우 (화면보다 위젯이 넓은 경우), x는 min_x로 설정
        if max_x < min_x:
            max_x = min_x
        
        final_x = max(min_x, min(pos.get("x", screen_geom.left()), max_x))

        # y 좌표 조정
        min_y = screen_geom.top()
        max_y = screen_geom.bottom() - widget_height
        # max_y가 min_y보다 작아지는 경우 (화면보다 위젯이 높은 경우), y는 min_y로 설정
        if max_y < min_y:
            max_y = min_y
            
        final_y = max(min_y, min(pos.get("y", screen_geom.top()), max_y))

        self.move(final_x, final_y)
        self.resize(widget_width, widget_height)
        
        # 위치 적용 후 셀 크기 조정 (모니터 변경 시 레이아웃이 완전히 업데이트될 때까지 충분한 지연)
        # 여러 번의 이벤트가 발생할 수 있으므로 더 긴 지연 시간 사용
        QtCore.QTimer.singleShot(300, self.adjust_cell_sizes)

    def save_widget_position(self):
        """
        현재 위젯의 위치와 크기 및 스크린 정보 저장 (멀티모니터 지원)
        - 현재 위젯이 속한 스크린의 geometry, name을 함께 settings에 저장
        """
        pos = self.pos()
        size = self.size()
        # 현재 위젯이 속한 스크린 정보 저장
        current_global_pos = self.mapToGlobal(self.rect().center())
        screen = QtWidgets.QApplication.screenAt(current_global_pos)
        
        if screen is None:
            logger.warning(f"위젯 중심점({current_global_pos})에 해당하는 스크린을 찾지 못했습니다. Primary screen으로 대체합니다.")
            screen = QtWidgets.QApplication.primaryScreen()
            if screen is None: # Primary screen 마저 없는 극단적인 경우 (이론상 발생하기 어려움)
                logger.error("Primary screen도 찾을 수 없습니다. screen_info를 None으로 설정합니다.")
                screen_info = None
            else:
                screen_info = {
                    'geometry': screen.geometry().getRect(),
                    'name': screen.name()
                }
        else:
            screen_info = {
                'geometry': screen.geometry().getRect(),  # (x, y, w, h)
                'name': screen.name()
            }
        logger.debug(f"Saving widget position. Screen info: {screen_info}, Widget pos: {pos}, Widget size: {size}")
        self.settings_manager.save_widget_position(pos.x(), pos.y(), size.width(), size.height(), screen_info)
    
    def update_styles(self):
        """모든 위젯에 현재 스타일 설정 적용"""
        # 스타일 정보 가져오기
        sm = self.settings_manager
        
        # 헤더 배경색을 RGBA 형식으로 변환
        header_bg_rgba = hex_to_rgba(sm.header_bg_color, sm.header_opacity)
        cell_bg_rgba = hex_to_rgba(sm.cell_bg_color, sm.cell_opacity)
        current_bg_rgba = hex_to_rgba(sm.current_period_color, sm.current_period_opacity)
        border_rgba = hex_to_rgba(sm.border_color, sm.border_opacity)
        
        # 헤더 스타일 적용 - 개별 헤더 폰트 사용
        header_style = generate_header_style(
            header_bg_rgba, 
            sm.header_text_color, 
            sm.header_font_family,  # 헤더 전용 폰트
            sm.header_font_size     # 헤더 폰트 크기
        )
        
        # 셀 스타일 적용 - 개별 셀 폰트 사용
        cell_style = generate_cell_style(
            cell_bg_rgba, 
            sm.cell_text_color, 
            border_rgba, 
            sm.cell_font_family,    # 셀 전용 폰트
            sm.cell_font_size       # 셀 폰트 크기
        )
        
        # 현재 교시 스타일 적용 - 개별 셀 폰트 사용
        current_style = generate_current_style(
            current_bg_rgba, 
            sm.cell_text_color, 
            border_rgba, 
            sm.cell_font_family,    # 셀 전용 폰트
            sm.cell_font_size       # 셀 폰트 크기
        )
        
        # 요일 헤더 스타일 적용
        for col, label in self.day_headers.items():
            label.setStyleSheet(header_style)
        
        # 교시 헤더 스타일 적용
        for row, label in self.period_headers.items():
            label.setStyleSheet(header_style)
        
        # 셀 스타일 적용
        for (row, col), cell in self.cell_widgets.items():
            # 현재 교시이면 강조 스타일 적용
            if row == self.current_period and col == self.current_day_idx:
                cell.setStyleSheet(current_style)
            else:
                cell.setStyleSheet(cell_style)
    
    def update_timetable_display(self):
        """시간표 데이터를 화면에 표시"""
        # 각 요일과 교시에 맞는 데이터 표시
        days = ["월", "화", "수", "목", "금"]
        timetable_data = self.settings_manager.timetable_data
        
        for day_idx, day in enumerate(days, 1):
            for period in range(1, 8):
                cell = self.cell_widgets.get((period, day_idx))
                if cell:
                    # 해당 요일과 교시에 맞는 과목 가져오기
                    subject = timetable_data.get(day, {}).get(str(period), "")
                    cell.setText(subject)
    
    def update_current_period(self):
        """현재 시간에 맞는 교시 계산"""
        now = QtCore.QTime.currentTime()
        today = datetime.datetime.now().weekday()  # 0=월요일, 1=화요일, ..., 6=일요일
        
        # 주말이 아닌 경우에만 요일 인덱스 계산 (인덱스 1=월, 2=화, ..., 5=금)
        self.current_day_idx = today + 1 if 0 <= today <= 4 else None
        
        # 이전 현재 교시 저장
        prev_period = self.current_period
        
        # 현재 교시 계산
        self.current_period = self.settings_manager.get_current_period(now)
        
        # 현재 교시가 변경되었으면 스타일 업데이트 및 알림
        if prev_period != self.current_period:
            self.update_styles()
            
            # 알림 관리자에 상태 전달
            self.notification_manager.check_notifications(
                self.current_period, 
                self.current_day_idx, 
                self.settings_manager.timetable_data
            )
            
        # 최적화: 다음 교시 시작/종료 시간에 맞춰 타이머 재설정
        self.set_next_update_timer()
    
    def set_next_update_timer(self):
        """다음 교시 변경 시간에 맞춰 타이머 재설정"""
        now = QtCore.QTime.currentTime()
        next_update_msec = 60000  # 기본값: 1분
        
        # 현재 교시가 있는 경우, 종료 시간까지 남은 시간 계산
        if self.current_period:
            current_end_time = self.settings_manager.time_ranges.get(self.current_period, {}).get("end")
            if current_end_time:
                msec_to_end = now.msecsTo(current_end_time)
                if msec_to_end > 0:
                    next_update_msec = min(next_update_msec, msec_to_end + 1000)  # 1초 추가하여 확실히 넘어가게
        
        # 다음 교시 시작 시간 확인
        next_period = (self.current_period or 0) + 1 if self.current_period != 7 else None
        if next_period and 1 <= next_period <= 7:
            next_start_time = self.settings_manager.time_ranges.get(next_period, {}).get("start")
            if (next_start_time):
                msec_to_start = now.msecsTo(next_start_time)
                if msec_to_start > 0:
                    next_update_msec = min(next_update_msec, msec_to_start + 1000)
        
        # 예고 알림을 위한 시간 계산
        if next_period and self.notification_manager.next_period_warning:
            warning_minutes = self.notification_manager.warning_minutes
            next_start_time = self.settings_manager.time_ranges.get(next_period, {}).get("start")
            if next_start_time:
                warning_time = next_start_time.addSecs(-warning_minutes * 60)
                msec_to_warning = now.msecsTo(warning_time)
                if msec_to_warning > 0:
                    next_update_msec = min(next_update_msec, msec_to_warning + 500)
        
        # 너무 긴 대기 시간은 최대 10분으로 제한 (안전장치)
        next_update_msec = min(next_update_msec, 600000)  
        
        # 타이머 재설정
        self.timer.stop()
        self.timer.setInterval(max(1000, next_update_msec))  # 최소 1초
        self.timer.start()
        
        logger.debug(f"다음 업데이트 예약: {next_update_msec/1000:.1f}초 후")
    
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트 처리"""
        self.handle_mouse_press(event)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리"""
        self.handle_mouse_move(event)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트 처리"""
        self.handle_mouse_release(event)
        super().mouseReleaseEvent(event)
    
    def resizeEvent(self, event):
        """위젯 크기 변경 시 셀 크기 조정"""
        super().resizeEvent(event)
        # 드래그/리사이징 중일 때는 셀 크기 조정을 하지 않음 (성능 최적화)
        # 드래그 중 모니터 이동 시에도 resizeEvent가 발생할 수 있으므로 반드시 체크 필요
        if self.resizing or self.dragging:
            # 드래그/리사이징 중에는 타이머도 완전히 중지하여 드래그 종료 후 실행되는 것을 방지
            self.resize_timer.stop()
            return
        
        # 모니터 변경 등으로 인한 크기 변경 시 레이아웃이 완전히 업데이트될 때까지 약간의 지연
        # 타이머를 사용하여 연속된 resize 이벤트를 하나로 묶어 처리
        # 지연 시간을 늘려서 레이아웃이 완전히 안정화된 후에 실행
        self.resize_timer.stop()
        self.resize_timer.start(150)  # 150ms 지연 (이전 50ms에서 증가)
    
    def showEvent(self, event):
        """위젯이 표시될 때 셀 크기 조정"""
        super().showEvent(event)
        # 모니터 간 이동 후 표시될 때 셀 크기 재조정
        # 드래그/리사이징 중이 아닐 때만 실행
        # hasattr 체크를 추가하여 초기화 전에 호출되는 경우 방지
        if hasattr(self, 'resizing') and hasattr(self, 'dragging'):
            if not (self.resizing or self.dragging):
                # 모니터 변경 시 레이아웃이 완전히 업데이트될 때까지 충분한 지연
                # DPI 변경도 함께 확인
                QtCore.QTimer.singleShot(300, self._check_and_adjust_for_dpi_change)
    
    def changeEvent(self, event):
        """위젯 상태 변경 이벤트 처리 (모니터 변경 감지)"""
        super().changeEvent(event)
        # 모니터 변경이나 기타 상태 변경 시 셀 크기 재조정
        # QEvent.ActivationChange: 위젯이 활성화/비활성화될 때
        # QEvent.WindowStateChange: 창 상태가 변경될 때
        if event.type() in (QtCore.QEvent.WindowStateChange, QtCore.QEvent.ActivationChange):
            # 드래그/리사이징 중이 아닐 때만 실행
            # hasattr 체크를 추가하여 초기화 전에 호출되는 경우 방지
            # 드래그 중 모니터 이동 시에도 이 이벤트가 발생할 수 있으므로 체크가 중요함
            if hasattr(self, 'resizing') and hasattr(self, 'dragging'):
                if not (self.resizing or self.dragging):
                    # 모니터 변경 시 레이아웃이 완전히 업데이트될 때까지 충분한 지연
                    # DPI 변경도 함께 확인
                    QtCore.QTimer.singleShot(300, self._check_and_adjust_for_dpi_change)
    
    def _check_and_adjust_for_dpi_change(self):
        """DPI 변경 확인 및 셀 크기 조정"""
        # 현재 위젯이 속한 스크린의 DPI 정보 가져오기
        current_global_pos = self.mapToGlobal(self.rect().center())
        current_screen = QtWidgets.QApplication.screenAt(current_global_pos)
        
        if current_screen is None:
            current_screen = QtWidgets.QApplication.primaryScreen()
        
        if current_screen:
            # 현재 스크린의 DPI 정보
            current_dpi = current_screen.logicalDotsPerInch()
            current_device_pixel_ratio = current_screen.devicePixelRatio()
            
            # DPI가 변경되었는지 확인
            dpi_changed = (
                self.last_screen_dpi is not None and 
                self.last_screen_dpi != current_dpi
            ) or (
                self.last_screen_device_pixel_ratio is not None and 
                self.last_screen_device_pixel_ratio != current_device_pixel_ratio
            )
            
            # DPI 정보 업데이트
            self.last_screen_dpi = current_dpi
            self.last_screen_device_pixel_ratio = current_device_pixel_ratio
            
            if dpi_changed:
                logger.debug(f"DPI 변경 감지: DPI={current_dpi}, DevicePixelRatio={current_device_pixel_ratio}")
                # DPI 변경 시 셀 크기 재조정 (약간의 추가 지연)
                QtCore.QTimer.singleShot(100, self.adjust_cell_sizes)
            else:
                # DPI 변경이 없어도 일반적인 셀 크기 조정
                self.adjust_cell_sizes()
    
    def show_context_menu(self, pos):
        """마우스 우클릭 메뉴 표시"""
        menu = QtWidgets.QMenu(self)
        
        edit_action = menu.addAction("시간표 편집")
        edit_action.triggered.connect(self.show_timetable_edit_dialog)
        
        time_action = menu.addAction("시간 설정")
        time_action.triggered.connect(self.show_time_dialog)
        
        settings_action = menu.addAction("설정")
        settings_action.triggered.connect(self.show_settings_dialog)
        
        # 위치 고정 토글 메뉴 추가
        lock_action = menu.addAction("위치 고정")
        lock_action.setCheckable(True)
        lock_action.setChecked(self.settings_manager.is_position_locked)
        lock_action.triggered.connect(self.toggle_position_lock)
        
        # 공유 및 백업 메뉴
        menu.addSeparator()
        sharing_menu = menu.addMenu("공유 및 백업")
        
        import_action = sharing_menu.addAction("파일에서 가져오기")
        import_action.triggered.connect(self.show_import_dialog)
        
        backup_action = sharing_menu.addAction("백업/복원")
        backup_action.triggered.connect(self.show_backup_dialog)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("종료")
        exit_action.triggered.connect(self.close)
        
        # 메뉴 표시
        menu.exec_(self.mapToGlobal(pos))

    def show_import_dialog(self):
        """데이터 가져오기 대화상자 표시"""
        from .dialogs.import_dialog import ImportDialog
        dialog = ImportDialog(self)
        dialog.exec_()

    def show_backup_dialog(self):
        """백업 관리 대화상자 표시"""
        from .dialogs.backup_dialog import BackupRestoreDialog
        dialog = BackupRestoreDialog(self)
        dialog.exec_()

    def toggle_position_lock(self):
        """위치 고정 상태 토글"""
        self.settings_manager.toggle_position_lock()
        self.save_widget_position()
    
    def show_timetable_edit_dialog(self):
        """시간표 편집 대화상자 표시"""
        dialog = TimetableEditDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.update_timetable_display()
    
    def show_time_dialog(self):
        """시간 설정 대화상자 표시"""
        dialog = TimeRangeDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.update_current_period()  # 현재 교시 업데이트
    
    def show_settings_dialog(self):
        """설정 대화상자 표시"""
        dialog = SettingsDialog(self)
        # SettingsDialog의 settings_applied 시그널을 Widget의 update_styles 메서드에 연결
        dialog.settings_applied.connect(self.update_styles)
        
        # dialog.exec_()는 사용자가 대화상자를 닫을 때까지 블로킹합니다.
        # "확인" 또는 "적용" 후 "취소"가 아닌 방식으로 닫히면 Accepted 반환.
        # "적용" 버튼을 누르면 apply_settings가 호출되고 settings_applied 시그널이 발생하여
        # update_styles가 즉시 호출됩니다.
        # "확인" 버튼을 누르면 accept()가 호출되고, accept() 내부에서 apply_settings가 호출되어
        # settings_applied 시그널이 발생하여 update_styles가 호출됩니다.
        # 따라서 dialog.exec_() 이후에 별도로 self.update_styles()를 호출할 필요는 없습니다.
        dialog.exec_()
        # if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # self.update_styles() # 시그널로 처리되므로 이 부분은 필요 없음
    
    def closeEvent(self, event):
        """위젯 종료 시 호출되는 이벤트"""
        logger.info("위젯 종료 이벤트 발생")
        try:
            if self.cleanup_on_close:
                logger.info("종료 시 리소스 정리 함수 호출")
                self.cleanup_on_close()  # 정리 함수 호출
            else:
                logger.warning("등록된 종료 정리 함수 없음")
            
            logger.info("애플리케이션 종료 요청")
            QtWidgets.QApplication.instance().quit() # 표준 종료 요청
            event.accept() # 이벤트 수락 (위젯 닫힘 허용)
            
        except Exception as e:
            logger.error(f"종료 처리 중 오류: {e}")
            # 오류 발생 시에도 일단 종료 시도는 하되, 이벤트를 무시하여
            # 애플리케이션이 즉시 꺼지지 않도록 할 수도 있습니다.
            # 하지만 여기서는 일단 accept()로 통일합니다.
            QtWidgets.QApplication.instance().quit()
            event.accept()
        # super().closeEvent(event) # event.accept() 또는 event.ignore()로 대체됨

    # 호버 이벤트 처리 메서드 추가
    def on_label_hover_enter(self, event, label):
        """라벨에 마우스가 올라갔을 때 호출"""
        # 필요한 경우 호버 효과 구현
        pass
    
    def on_label_hover_leave(self, event, label):
        """라벨에서 마우스가 나갔을 때 호출"""
        # 필요한 경우 호버 효과 제거
        pass
    
    def on_cell_hover_enter(self, event, cell):
        """셀에 마우스가 올라갔을 때 호출"""
        # 필요한 경우 호버 효과 구현
        pass
    
    def on_cell_hover_leave(self, event, cell):
        """셀에서 마우스가 나갔을 때 호출"""
        # 필요한 경우 호버 효과 제거
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())