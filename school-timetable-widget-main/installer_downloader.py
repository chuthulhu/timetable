"""
온라인 설치 프로그램용 다운로더
작은 Python 스크립트로 GitHub에서 실제 프로그램을 다운로드
이 파일을 PyInstaller로 빌드하여 작은 설치 프로그램으로 사용
"""
import sys
import os
import json
import requests
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple

GITHUB_REPO = "chuthulhu/school-timetable-widget"
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def check_internet():
    """인터넷 연결 확인"""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

def get_latest_release_info() -> Optional[dict]:
    """GitHub에서 최신 릴리즈 정보 가져오기"""
    try:
        response = requests.get(GITHUB_API_RELEASES, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"릴리즈 정보 조회 실패: {e}")
    return None

def find_exe_asset(release_data: dict) -> Optional[str]:
    """릴리즈에서 .exe 파일 찾기"""
    assets = release_data.get("assets", [])
    # 우선순위: SchoolTimetableWidget*.exe 패턴
    for asset in assets:
        name = asset["name"]
        if name.endswith(".exe") and "SchoolTimetableWidget" in name:
            return asset["browser_download_url"]
    # 없으면 첫 번째 .exe 파일
    for asset in assets:
        if asset["name"].endswith(".exe"):
            return asset["browser_download_url"]
    return None

def download_file(url: str, dest_path: str, progress_callback=None) -> Tuple[bool, str]:
    """파일 다운로드"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size:
                        progress = int((downloaded / total_size) * 100)
                        progress_callback(progress, downloaded, total_size)
        
        return True, "다운로드 완료"
    except Exception as e:
        return False, str(e)

def main():
    """메인 함수"""
    print("=" * 60)
    print("학교 시간표 위젯 - 온라인 설치 프로그램")
    print("=" * 60)
    print()
    
    # 인터넷 연결 확인
    print("인터넷 연결 확인 중...")
    if not check_internet():
        print("오류: 인터넷 연결이 필요합니다.")
        input("Enter 키를 눌러 종료하세요...")
        sys.exit(1)
    print("인터넷 연결 확인됨")
    print()
    
    # 최신 릴리즈 정보 가져오기
    print("최신 버전 확인 중...")
    release_data = get_latest_release_info()
    if not release_data:
        print("오류: 최신 버전을 확인할 수 없습니다.")
        input("Enter 키를 눌러 종료하세요...")
        sys.exit(1)
    
    version = release_data.get("tag_name", "알 수 없음")
    print(f"최신 버전: {version}")
    print()
    
    # 다운로드 URL 찾기
    print("다운로드 URL 확인 중...")
    download_url = find_exe_asset(release_data)
    if not download_url:
        print("오류: 다운로드할 파일을 찾을 수 없습니다.")
        input("Enter 키를 눌러 종료하세요...")
        sys.exit(1)
    print(f"다운로드 URL: {download_url}")
    print()
    
    # 임시 파일 경로
    temp_dir = tempfile.gettempdir()
    exe_name = "SchoolTimetableWidget.exe"
    temp_file = os.path.join(temp_dir, f"SchoolTimetableWidget_{version}_{exe_name}")
    
    # 다운로드 진행
    print("파일 다운로드 중...")
    print("(이 작업은 몇 분이 걸릴 수 있습니다)")
    print()
    
    def progress_callback(percent, downloaded, total):
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        print(f"\r진행률: {percent}% ({downloaded_mb:.1f} MB / {total_mb:.1f} MB)", end="", flush=True)
    
    success, message = download_file(download_url, temp_file, progress_callback)
    print()
    print()
    
    if not success:
        print(f"오류: 다운로드 실패 - {message}")
        input("Enter 키를 눌러 종료하세요...")
        sys.exit(1)
    
    print("다운로드 완료!")
    print()
    
    # 설치 위치 선택
    default_dir = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "SchoolTimetableWidget")
    install_dir = input(f"설치 위치 (기본값: {default_dir}): ").strip()
    if not install_dir:
        install_dir = default_dir
    
    # 설치 디렉토리 생성
    try:
        os.makedirs(install_dir, exist_ok=True)
    except Exception as e:
        print(f"오류: 설치 디렉토리를 생성할 수 없습니다: {e}")
        input("Enter 키를 눌러 종료하세요...")
        sys.exit(1)
    
    # 파일 복사
    print(f"파일 설치 중: {install_dir}")
    install_file = os.path.join(install_dir, exe_name)
    try:
        import shutil
        shutil.copy2(temp_file, install_file)
        print("설치 완료!")
    except Exception as e:
        print(f"오류: 파일 복사 실패 - {e}")
        input("Enter 키를 눌러 종료하세요...")
        sys.exit(1)
    
    # 임시 파일 삭제
    try:
        os.remove(temp_file)
    except:
        pass
    
    # 실행 여부 확인
    print()
    run_now = input("설치된 프로그램을 지금 실행하시겠습니까? (y/n): ").strip().lower()
    if run_now == 'y':
        try:
            subprocess.Popen([install_file])
        except Exception as e:
            print(f"프로그램 실행 실패: {e}")
    
    print()
    print("설치가 완료되었습니다!")
    input("Enter 키를 눌러 종료하세요...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n설치가 취소되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n오류 발생: {e}")
        input("Enter 키를 눌러 종료하세요...")
        sys.exit(1)

