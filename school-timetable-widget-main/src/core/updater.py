"""
업데이트 관리 모듈
- GitHub에서 최신 버전 확인 및 다운로드
"""
import logging
import re
import requests
from typing import Optional, Callable, Tuple

logger = logging.getLogger(__name__)

GITHUB_REPO = "chuthulhu/school-timetable-widget"
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


class Updater:
    """업데이트 관리 클래스"""
    
    def __init__(self, current_version: str):
        self.current_version = current_version
        self.latest_version: Optional[str] = None
        self.download_url: Optional[str] = None
        self.release_notes: Optional[str] = None
    
    def check_for_update(self) -> bool:
        """업데이트 확인"""
        try:
            resp = requests.get(GITHUB_API_RELEASES, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.latest_version = data.get("tag_name")
                self.release_notes = data.get("body", "")
                
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        self.download_url = asset["browser_download_url"]
                        break
                
                if self.latest_version and self.download_url:
                    return self.is_newer_version(self.latest_version, self.current_version)
            else:
                logger.warning(f"GitHub 릴리즈 정보 조회 실패: {resp.status_code}")
        except Exception as e:
            logger.warning(f"업데이트 확인 중 오류: {e}")
        return False
    
    @staticmethod
    def is_newer_version(latest: str, current: str) -> bool:
        """버전 비교"""
        def parse(v: str) -> list:
            return [int(x) for x in re.findall(r'\d+', v)]
        
        return parse(latest) > parse(current)
    
    def download_update(
        self, 
        dest_path: str, 
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """업데이트 다운로드"""
        if not self.download_url:
            logger.error("다운로드 URL이 없습니다.")
            return False
        
        try:
            with requests.get(self.download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                
                with open(dest_path, 'wb') as f:
                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total:
                                progress_callback(downloaded, total)
            
            return True
        except Exception as e:
            logger.error(f"업데이트 다운로드 실패: {e}")
            return False

