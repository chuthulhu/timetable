"""
애플리케이션 관리 모듈
- 애플리케이션 생명주기 관리
"""
import os
import sys
import signal
import atexit
import logging
import shutil
from typing import Optional

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from utils.version import get_version, get_version_string
from utils.exceptions import handle_exception
from utils.paths import resource_path, ensure_data_directory_exists
from utils.settings_manager import SettingsManager
from notifications.notification_manager import NotificationManager
from gui.widget import Widget
from tray_icon import TrayIcon
from utils.auto_start import (
    is_auto_start_enabled, 
    enable_auto_start, 
    disable_auto_start, 
    get_executable_path
)
from .process_manager import ProcessManager

logger = logging.getLogger(__name__)


class ApplicationManager:
    """애플리케이션 관리 클래스"""
    
    def __init__(self):
        self._cleanup_done = False
        self.app: Optional[QApplication] = None
        self.widget: Optional[Widget] = None
        self.tray_icon: Optional[TrayIcon] = None
        self.settings_manager: Optional[SettingsManager] = None
        self.notification_manager: Optional[NotificationManager] = None
        self.process_manager = ProcessManager()
        self.setup_environment()
    
    def setup_environment(self) -> None:
        """실행 환경 설정"""
        config = {
            "app_name": "학교 시간표 위젯",
            "app_version": get_version(),
            "app_version_string": get_version_string(),
            "data_dir": ensure_data_directory_exists()
        }
        
        # 환경 변수 설정
        os.environ['SCHOOL_TIMETABLE_DATA_DIR'] = config["data_dir"]
        os.environ['SCHOOL_TIMETABLE_VERSION'] = config["app_version"]
        
        # 버전 정보 로깅
        logger.info(
            f"애플리케이션 시작: {config['app_name']} "
            f"{config['app_version_string']}"
        )
        
        # 기본 리소스 복사 (첫 실행 시)
        self.copy_default_resources(config["data_dir"])
    
    def copy_default_resources(self, data_dir: str) -> None:
        """기본 리소스 파일 복사"""
        try:
            csv_path = os.path.join(data_dir, 'default_timetable.csv')
            if not os.path.exists(csv_path) and getattr(sys, 'frozen', False):
                default_csv = resource_path(os.path.join('assets', 'default_timetable.csv'))
                if os.path.exists(default_csv):
                    shutil.copy(default_csv, csv_path)
                else:
                    logger.error(f"기본 시간표 파일을 찾을 수 없습니다: {default_csv}")
        except Exception as e:
            logger.error(f"리소스 복사 중 오류 발생: {e}")
    
    def setup_signal_handlers(self) -> None:
        """시그널 핸들러 설정"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, self.signal_handler)
    
    def signal_handler(self, signum, frame) -> None:
        """시그널 핸들러"""
        logger.info(f"시그널 {signum} 수신: 애플리케이션을 종료합니다.")
        self.cleanup_resources()
        sys.exit(0)
    
    def cleanup_resources(self) -> None:
        """애플리케이션 종료 시 모든 리소스 정리"""
        if self._cleanup_done:
            logger.info("정리 작업이 이미 완료되었습니다.")
            return
        
        logger.info("리소스 정리 시작...")
        
        # 모든 QTimer 중지 시도
        try:
            self.stop_timers()
        except Exception as e:
            logger.error(f"QTimer 중지 중 오류 발생: {e}")
        
        # 프로세스 정리
        try:
            self.process_manager.cleanup_all()
        except Exception as e:
            logger.error(f"프로세스 정리 중 오류: {str(e)}")
        
        logger.info("모든 리소스 정리 완료")
        self._cleanup_done = True
    
    def stop_timers(self) -> None:
        """모든 QTimer 중지"""
        if not self.app:
            return
        
        for obj in self.app.findChildren(QTimer):
            try:
                if obj.isActive():
                    obj.stop()
                    logger.debug(f"QTimer 중지: {obj}")
            except Exception as e:
                logger.error(f"타이머 중지 중 오류: {e}")
    
    def run(self) -> int:
        """애플리케이션 실행"""
        try:
            self.setup_signal_handlers()
            atexit.register(self.final_cleanup)
            
            self.app = QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(False)
            self.app.setApplicationName("학교 시간표 위젯")
            self.app.aboutToQuit.connect(self.cleanup_resources)
            
            self.settings_manager = SettingsManager.get_instance()
            self.notification_manager = NotificationManager.get_instance()
            
            # 애플리케이션 시작 시 자동 시작 설정 동기화
            self._sync_auto_start_setting()
            
            # Widget 생성
            self.widget = Widget(
                settings_manager=self.settings_manager,
                notification_manager=self.notification_manager,
                app_manager=self
            )
            self.widget.cleanup_on_close = self.cleanup_resources
            self.widget.show()
            
            # 트레이 아이콘 생성
            self.tray_icon = TrayIcon(self.widget)
            self.tray_icon.show_action.triggered.connect(self.widget.show)
            self.tray_icon.exit_action.triggered.connect(self.safe_exit)
            
            if not self.tray_icon.isSystemTrayAvailable() or not self.tray_icon.isVisible():
                logger.warning("시스템 트레이를 사용할 수 없거나 아이콘이 표시되지 않습니다.")
                from PyQt5.QtGui import QIcon
                self.tray_icon.setIcon(
                    QIcon(resource_path(os.path.join('assets', 'app_icon.ico')))
                )
            
            self.tray_icon.show()
            
            exit_code = self.app.exec_()
            logger.info(f"앱 종료됨 (코드: {exit_code}), 리소스 정리 시작")
            self.cleanup_resources()
            return exit_code
            
        except Exception as e:
            logger.exception(f"애플리케이션 실행 중 오류 발생: {e}")
            self.cleanup_resources()
            return 1
    
    def safe_exit(self) -> None:
        """안전한 종료"""
        logger.info("트레이 아이콘에서 종료 요청됨")
        if self.widget:
            self.widget.hide()
        if self.tray_icon:
            self.tray_icon.hide()
        self.cleanup_resources()
        logger.info("애플리케이션 정상 종료")
        
        if QApplication.instance():
            QApplication.instance().quit()
    
    def _sync_auto_start_setting(self) -> None:
        """애플리케이션 시작 시 자동 시작 설정을 시스템 상태와 동기화"""
        try:
            import platform
            from utils.paths import APP_NAME
            
            if platform.system() != "Windows":
                logger.debug("Windows가 아닌 OS에서는 자동 시작 동기화를 건너뜁니다.")
                return
            
            if not hasattr(self, 'settings_manager') or self.settings_manager is None:
                logger.error("SettingsManager가 초기화되지 않아 자동 시작 설정을 동기화할 수 없습니다.")
                return
            
            current_setting_enabled = getattr(self.settings_manager, 'auto_start_enabled', False)
            system_is_enabled = is_auto_start_enabled(app_name_for_shortcut=APP_NAME)
            
            executable_path = get_executable_path()
            icon_path = resource_path("assets/app_icon.ico")
            if not os.path.exists(icon_path):
                icon_path = resource_path("assets/icon.ico")
            if not os.path.exists(icon_path):
                icon_path = executable_path
            
            if current_setting_enabled != system_is_enabled:
                logger.info(
                    f"자동 시작 설정 동기화 필요: "
                    f"설정({current_setting_enabled}), 시스템({system_is_enabled})"
                )
                
                if current_setting_enabled:
                    if enable_auto_start(
                        app_name_for_shortcut=APP_NAME,
                        target_path=executable_path,
                        icon_location=icon_path
                    ):
                        logger.info("시스템 자동 시작 활성화됨 (설정 동기화).")
                    else:
                        logger.error("시스템 자동 시작 활성화 실패 (설정 동기화).")
                        self.settings_manager.set_auto_start(False)
                else:
                    if disable_auto_start(app_name_for_shortcut=APP_NAME):
                        logger.info("시스템 자동 시작 비활성화됨 (설정 동기화).")
                    else:
                        logger.error("시스템 자동 시작 비활성화 실패 (설정 동기화).")
            else:
                logger.debug(f"자동 시작 설정과 시스템 상태 일치: {current_setting_enabled}")
                
        except ImportError as e:
            logger.warning(
                f"자동 시작 관련 모듈(pywin32 등)을 찾을 수 없어 "
                f"자동 시작 설정을 동기화할 수 없습니다: {e}"
            )
        except Exception as e:
            logger.error(f"자동 시작 설정 동기화 중 오류 발생: {e}", exc_info=True)
    
    def final_cleanup(self) -> None:
        """최종 정리 작업"""
        if not self._cleanup_done:
            logger.info("프로그램 종료: 최종 정리 작업 수행")
            self.cleanup_resources()
        logger.info("프로그램 정상 종료 완료")

