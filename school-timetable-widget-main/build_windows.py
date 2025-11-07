"""
Windows 배포용 빌드 스크립트
사용법: python build_windows.py
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_pyinstaller():
    """PyInstaller가 설치되어 있는지 확인"""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("PyInstaller가 설치되어 있지 않습니다.")
        print("다음 명령으로 설치하세요: pip install pyinstaller")
        return False

def build_executable():
    """실행 파일 빌드"""
    project_root = Path(__file__).parent
    spec_file = project_root / 'build_windows.spec'
    
    if not spec_file.exists():
        print(f"스펙 파일을 찾을 수 없습니다: {spec_file}")
        return False
    
    print("빌드를 시작합니다...")
    print(f"스펙 파일: {spec_file}")
    
    # PyInstaller 실행
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', str(spec_file)]
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        print("\n빌드가 완료되었습니다!")
        print(f"실행 파일 위치: {project_root / 'dist' / 'SchoolTimetableWidget.exe'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n빌드 실패: {e}")
        return False

def create_installer():
    """인스톨러 생성 (선택적)"""
    print("\n인스톨러 생성을 원하시면 Inno Setup 또는 NSIS를 사용하세요.")
    print("Inno Setup 예제 스크립트: build_installer.iss")

def main():
    """메인 함수"""
    print("=" * 60)
    print("학교 시간표 위젯 - Windows 배포 빌드")
    print("=" * 60)
    
    if not check_pyinstaller():
        sys.exit(1)
    
    # 기존 빌드 폴더 정리 확인
    project_root = Path(__file__).parent
    build_dir = project_root / 'build'
    dist_dir = project_root / 'dist'
    
    if build_dir.exists() or dist_dir.exists():
        response = input("\n기존 빌드 폴더를 삭제하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            if build_dir.exists():
                shutil.rmtree(build_dir)
                print(f"삭제됨: {build_dir}")
            if dist_dir.exists():
                shutil.rmtree(dist_dir)
                print(f"삭제됨: {dist_dir}")
    
    # 빌드 실행
    if build_executable():
        print("\n" + "=" * 60)
        print("빌드 성공!")
        print("=" * 60)
        print("\n다음 단계:")
        print("1. dist/SchoolTimetableWidget.exe 파일을 테스트하세요")
        print("2. 필요시 인스톨러를 생성하세요")
        print("3. 배포 준비가 완료되었습니다!")
    else:
        print("\n빌드 실패. 오류 메시지를 확인하세요.")
        sys.exit(1)

if __name__ == '__main__':
    main()

