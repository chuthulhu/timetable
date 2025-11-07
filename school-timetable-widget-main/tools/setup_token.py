"""
GitHub Token 설정 도우미 스크립트
Windows에서 환경변수를 영구적으로 설정합니다.
"""
import os
import sys
import subprocess
from pathlib import Path

def set_token_permanent_windows(token: str):
    """Windows에서 환경변수를 영구적으로 설정"""
    try:
        # 사용자 환경변수에 설정
        subprocess.run([
            'setx', 'GITHUB_TOKEN', token
        ], check=True, shell=True)
        print("✅ 환경변수 GITHUB_TOKEN이 설정되었습니다.")
        print("   (새 터미널 창에서 적용됩니다)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 환경변수 설정 실패: {e}")
        return False
    except FileNotFoundError:
        print("❌ setx 명령을 찾을 수 없습니다.")
        print("   수동으로 환경변수를 설정하세요:")
        print("   1. 시스템 속성 → 환경 변수")
        print("   2. 사용자 변수에 GITHUB_TOKEN 추가")
        return False

def set_token_current_session(token: str):
    """현재 세션에만 환경변수 설정"""
    os.environ['GITHUB_TOKEN'] = token
    print("✅ 현재 세션에 환경변수가 설정되었습니다.")
    print("   (이 터미널 창에서만 유효합니다)")

def main():
    print("=" * 60)
    print("GitHub Token 설정 도우미")
    print("=" * 60)
    print()
    
    # 현재 환경변수 확인
    current_token = os.environ.get('GITHUB_TOKEN')
    if current_token:
        masked_token = current_token[:10] + "..." + current_token[-4:] if len(current_token) > 14 else "***"
        print(f"현재 설정된 토큰: {masked_token}")
        response = input("기존 토큰을 변경하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("취소되었습니다.")
            return
        print()
    
    print("GitHub Personal Access Token을 입력하세요.")
    print("토큰 생성: https://github.com/settings/tokens")
    print("(repo 권한 필요)")
    print()
    token = input("GitHub Token: ").strip()
    
    if not token:
        print("토큰이 입력되지 않았습니다.")
        sys.exit(1)
    
    print()
    print("설정 방법을 선택하세요:")
    print("1. 영구 설정 (모든 터미널에서 사용 가능)")
    print("2. 현재 세션만 (이 터미널 창에서만 유효)")
    print()
    choice = input("선택 (1/2): ").strip()
    
    if choice == '1':
        if sys.platform == 'win32':
            set_token_permanent_windows(token)
        else:
            print("Linux/Mac에서는 다음 명령을 실행하세요:")
            print(f'export GITHUB_TOKEN="{token}"')
            print("또는 ~/.bashrc 또는 ~/.zshrc에 추가:")
            print(f'echo \'export GITHUB_TOKEN="{token}"\' >> ~/.bashrc')
    elif choice == '2':
        set_token_current_session(token)
    else:
        print("잘못된 선택입니다.")
        sys.exit(1)
    
    print()
    print("설정 완료!")
    print()
    print("다음 명령으로 릴리즈를 생성할 수 있습니다:")
    print("  python tools/release_manager.py create --auto-files")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n취소되었습니다.")
        sys.exit(1)

