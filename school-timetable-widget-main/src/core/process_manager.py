"""
프로세스 관리 모듈
- 애플리케이션 종료 시 프로세스 정리 담당
"""
import os
import logging
import multiprocessing
import psutil
from typing import Optional

# Windows 환경에서 사용할 추가 모듈
try:
    import win32api
    import win32con
    import win32process
    WINDOWS_MODULES_AVAILABLE = True
except ImportError:
    WINDOWS_MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)


class ProcessManager:
    """프로세스 관리 클래스"""
    
    def __init__(self):
        self.logger = logger
    
    def force_terminate_process(self, pid: int) -> bool:
        """프로세스를 강제로 종료 (Windows 환경에 최적화)"""
        try:
            if WINDOWS_MODULES_AVAILABLE:
                PROCESS_TERMINATE = 1
                handle = win32api.OpenProcess(PROCESS_TERMINATE, False, pid)
                if handle:
                    win32api.TerminateProcess(handle, 0)
                    win32api.CloseHandle(handle)
                    self.logger.info(f"Windows API로 프로세스 종료: {pid}")
                    return True
            # 일반적인 방식으로 프로세스 종료 시도
            process = psutil.Process(pid)
            process.kill()
            return True
        except Exception as e:
            self.logger.error(f"프로세스 {pid} 종료 실패: {str(e)}")
            return False
    
    def cleanup_child_processes(self) -> None:
        """현재 프로세스의 모든 자식 프로세스 종료"""
        try:
            current_pid = os.getpid()
            current_process = psutil.Process(current_pid)
            children = current_process.children(recursive=True)
            self.logger.info(f"종료할 자식 프로세스 수: {len(children)}")
            
            for idx, child in enumerate(children):
                try:
                    self.logger.info(
                        f"프로세스 종료 시도 {idx+1}/{len(children)}: "
                        f"PID {child.pid}, 이름: {child.name()}"
                    )
                    child.terminate()
                except Exception as e:
                    self.logger.error(f"프로세스 종료 중 오류 (PID {child.pid}): {str(e)}")
            
            gone, alive = psutil.wait_procs(children, timeout=1)
            self.logger.info(
                f"정상 종료된 프로세스: {len(gone)}, "
                f"강제 종료 필요한 프로세스: {len(alive)}"
            )
            
            for child in alive:
                try:
                    self.logger.info(f"프로세스 강제 종료 (PID {child.pid}): {child.name()}")
                    self.force_terminate_process(child.pid)
                except Exception as e:
                    self.logger.error(f"프로세스 강제 종료 중 오류 (PID {child.pid}): {str(e)}")
        except Exception as e:
            self.logger.error(f"프로세스 정리 중 예외 발생: {str(e)}")
    
    def cleanup_multiprocessing_children(self) -> None:
        """multiprocessing 모듈의 자식 프로세스 정리"""
        try:
            active_children = multiprocessing.active_children()
            self.logger.info(f"활성 multiprocessing 자식 프로세스: {len(active_children)}")
            
            for child in active_children:
                self.logger.info(f"multiprocessing 자식 종료: {child.name} (PID: {child.pid})")
                child.terminate()
                child.join(0.5)
        except Exception as e:
            self.logger.error(f"multiprocessing 정리 중 오류: {str(e)}")
    
    def cleanup_all(self) -> None:
        """모든 프로세스 정리 작업 수행"""
        self.cleanup_child_processes()
        self.cleanup_multiprocessing_children()
        
        # 메모리 정리 시도
        try:
            import gc
            gc.collect()
        except Exception:
            pass

