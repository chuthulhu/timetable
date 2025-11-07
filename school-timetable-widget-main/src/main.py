"""
학교 시간표 위젯 메인 진입점
"""
import logging
import os
import sys
import tempfile
import subprocess
from typing import Optional

from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt5.QtCore import Qt

from utils.version import get_version, get_version_string
from utils.exceptions import handle_exception
from core.application_manager import ApplicationManager
from core.updater import Updater

# 로거 설정
def setup_logging() -> logging.Logger:
    """로깅 설정"""
    from utils.paths import get_log_directory, APP_NAME
    
    log_dir_path = get_log_directory()
    log_file_name = f"{APP_NAME}.log"
    log_file_path = os.path.join(log_dir_path, log_file_name)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("SchoolTimetable")

logger = setup_logging()


def check_and_handle_update() -> bool:
    """
    업데이트 확인 및 처리
    Returns:
        업데이트를 다운로드했으면 True (앱 종료 필요), 아니면 False
    """
    try:
        updater = Updater(get_version())
        if not updater.check_for_update():
            return False
        
        # GUI가 없으면 업데이트 체크만 하고 종료
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        msg = (
            f"새 버전({updater.latest_version})이 출시되었습니다!\n\n"
            f"릴리즈 노트:\n{updater.release_notes}\n\n"
            f"지금 다운로드하시겠습니까?"
        )
        
        reply = QMessageBox.question(
            None, 
            "업데이트 알림", 
            msg, 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return False
        
        # 다운로드 진행
        import os
        dest = os.path.join(
            tempfile.gettempdir(), 
            f"school_timetable_update_{updater.latest_version}.exe"
        )
        
        progress = QProgressDialog("업데이트 다운로드 중...", None, 0, 100)
        progress.setWindowTitle("업데이트")
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        def progress_callback(done: int, total: int) -> None:
            progress.setValue(int(done / total * 100))
        
        ok = updater.download_update(dest, progress_callback=progress_callback)
        progress.close()
        
        if ok:
            QMessageBox.information(
                None, 
                "업데이트 완료", 
                "다운로드가 완료되었습니다.\n프로그램을 종료하면 새 버전이 실행됩니다."
            )
            # 새 업데이터 실행
            subprocess.Popen([dest])
            logger.info("새 업데이터 실행 후 현재 애플리케이션 종료 요청")
            app_instance = QApplication.instance()
            if app_instance:
                app_instance.quit()
            return True
        else:
            QMessageBox.warning(
                None, 
                "업데이트 실패", 
                "업데이트 파일 다운로드에 실패했습니다."
            )
            return False
            
    except Exception as e:
        logger.warning(f"업데이트 확인 중 오류: {e}")
        return False


def main() -> int:
    """메인 함수"""
    try:
        sys.excepthook = handle_exception
        version_str = get_version_string()
        logger.info(f"학교시간표위젯 {version_str} 시작")
        
        # 자동 업데이트 확인 (비동기로 변경 가능)
        if check_and_handle_update():
            return 0
        
        # 애플리케이션 실행
        app_manager = ApplicationManager()
        exit_code = app_manager.run()
        return exit_code
        
    except Exception as e:
        logger.critical(f"심각한 오류 발생: {e}", exc_info=True)
        try:
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("심각한 오류")
            msg_box.setText("프로그램을 시작할 수 없습니다")
            msg_box.setInformativeText(str(e))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
        except Exception:
            print(f"심각한 오류: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    sys.exit(main())
