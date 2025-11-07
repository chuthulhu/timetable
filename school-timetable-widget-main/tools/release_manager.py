"""
GitHub Releases 생성 및 관리 스크립트
사용법: python tools/release_manager.py [명령] [옵션]
"""
import sys
import os
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from utils.version import get_version, VERSION_STRING
from utils.paths import APP_NAME

GITHUB_REPO = "chuthulhu/school-timetable-widget"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"


class ReleaseManager:
    """GitHub Releases 관리 클래스"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Args:
            token: GitHub Personal Access Token (없으면 환경변수 GITHUB_TOKEN 사용)
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        if not self.token:
            raise ValueError(
                "GitHub Token이 필요합니다.\n"
                "환경변수 GITHUB_TOKEN을 설정하거나 --token 옵션을 사용하세요.\n"
                "토큰 생성: https://github.com/settings/tokens"
            )
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_latest_release(self) -> Optional[Dict]:
        """최신 릴리즈 정보 가져오기"""
        try:
            response = requests.get(
                f"{GITHUB_API_BASE}/releases/latest",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None  # 릴리즈가 없음
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"오류: 최신 릴리즈 조회 실패 - {e}")
            return None
    
    def get_all_releases(self) -> List[Dict]:
        """모든 릴리즈 목록 가져오기"""
        try:
            response = requests.get(
                f"{GITHUB_API_BASE}/releases",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"오류: 릴리즈 목록 조회 실패 - {e}")
            return []
    
    def get_release_by_tag(self, tag: str) -> Optional[Dict]:
        """특정 태그의 릴리즈 정보 가져오기"""
        try:
            response = requests.get(
                f"{GITHUB_API_BASE}/releases/tags/{tag}",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"오류: 릴리즈 조회 실패 - {e}")
            return None
    
    def create_release(
        self,
        tag: str,
        name: Optional[str] = None,
        body: Optional[str] = None,
        draft: bool = False,
        prerelease: bool = False,
        files: Optional[List[str]] = None
    ) -> bool:
        """
        새 릴리즈 생성
        
        Args:
            tag: 버전 태그 (예: v1.0.0)
            name: 릴리즈 제목 (없으면 tag 사용)
            body: 릴리즈 노트
            draft: 초안으로 생성 여부
            prerelease: 프리릴리즈 여부
            files: 업로드할 파일 경로 리스트
        """
        # 기존 릴리즈 확인
        existing = self.get_release_by_tag(tag)
        if existing:
            print(f"경고: 태그 {tag}가 이미 존재합니다.")
            response = input("기존 릴리즈를 삭제하고 새로 생성하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                print("취소되었습니다.")
                return False
            
            # 기존 릴리즈 삭제
            if not self.delete_release(existing['id']):
                print("기존 릴리즈 삭제 실패")
                return False
        
        # 릴리즈 생성
        data = {
            "tag_name": tag,
            "name": name or tag,
            "body": body or f"릴리즈 {tag}",
            "draft": draft,
            "prerelease": prerelease
        }
        
        try:
            response = requests.post(
                f"{GITHUB_API_BASE}/releases",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            release = response.json()
            print(f"✅ 릴리즈 생성 완료: {tag}")
            print(f"   URL: {release['html_url']}")
            
            # 파일 업로드
            if files:
                upload_url = release.get('upload_url', '').split('{')[0]  # {?name,label} 제거
                self.upload_assets(release['id'], files, upload_url)
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ 릴리즈 생성 실패: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"   상세: {error_data.get('message', '알 수 없는 오류')}")
                except:
                    pass
            return False
    
    def upload_assets(self, release_id: int, files: List[str], upload_url: Optional[str] = None) -> bool:
        """릴리즈에 파일 업로드"""
        success_count = 0
        
        # upload_url이 없으면 릴리즈 정보에서 가져오기
        if not upload_url:
            release = self.get_release_by_id(release_id)
            if not release:
                print(f"❌ 릴리즈 ID {release_id}를 찾을 수 없습니다.")
                return False
            upload_url = release.get('upload_url', '').split('{')[0]  # {?name,label} 제거
        
        if not upload_url:
            print("❌ 업로드 URL을 찾을 수 없습니다.")
            return False
        
        for file_path in files:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                print(f"⚠️  파일을 찾을 수 없습니다: {file_path}")
                continue
            
            file_name = file_path_obj.name
            file_size = file_path_obj.stat().st_size
            
            # 파일 크기 확인 (100MB 제한)
            if file_size > 100 * 1024 * 1024:
                print(f"⚠️  파일이 너무 큽니다 (100MB 제한): {file_name}")
                continue
            
            print(f"📤 업로드 중: {file_name} ({file_size / 1024 / 1024:.1f} MB)...")
            
            try:
                # GitHub API는 raw binary로 파일 업로드
                # upload_url에 ?name=filename 쿼리 추가
                upload_endpoint = f"{upload_url}?name={file_name}"
                
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    
                    # Content-Type 결정
                    content_type = 'application/octet-stream'
                    if file_name.endswith('.exe'):
                        content_type = 'application/x-msdownload'
                    elif file_name.endswith('.zip'):
                        content_type = 'application/zip'
                    
                    response = requests.post(
                        upload_endpoint,
                        headers={
                            "Authorization": f"token {self.token}",
                            "Accept": "application/vnd.github.v3+json",
                            "Content-Type": content_type
                        },
                        data=file_content,
                        timeout=300  # 큰 파일을 위한 긴 타임아웃
                    )
                    response.raise_for_status()
                    print(f"   ✅ 업로드 완료: {file_name}")
                    success_count += 1
            except requests.exceptions.RequestException as e:
                print(f"   ❌ 업로드 실패: {file_name} - {e}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_data = e.response.json()
                        print(f"      상세: {error_data.get('message', '알 수 없는 오류')}")
                    except:
                        print(f"      응답: {e.response.text[:200]}")
        
        print(f"\n📊 업로드 결과: {success_count}/{len(files)} 파일 성공")
        return success_count > 0
    
    def get_release_by_id(self, release_id: int) -> Optional[Dict]:
        """릴리즈 ID로 릴리즈 정보 가져오기"""
        try:
            response = requests.get(
                f"{GITHUB_API_BASE}/releases/{release_id}",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def delete_release(self, release_id: int) -> bool:
        """릴리즈 삭제"""
        try:
            response = requests.delete(
                f"{GITHUB_API_BASE}/releases/{release_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"릴리즈 삭제 실패: {e}")
            return False
    
    def list_releases(self) -> None:
        """모든 릴리즈 목록 출력"""
        releases = self.get_all_releases()
        
        if not releases:
            print("릴리즈가 없습니다.")
            return
        
        print(f"\n📦 릴리즈 목록 ({len(releases)}개):\n")
        for release in releases:
            tag = release['tag_name']
            name = release['name']
            published = release.get('published_at', 'N/A')
            draft = "📝 [Draft]" if release['draft'] else ""
            prerelease = "🔖 [Pre-release]" if release['prerelease'] else ""
            
            print(f"  {tag} - {name} {draft}{prerelease}")
            print(f"    발행일: {published}")
            print(f"    URL: {release['html_url']}")
            
            # 다운로드 통계
            assets = release.get('assets', [])
            if assets:
                total_downloads = sum(asset.get('download_count', 0) for asset in assets)
                print(f"    다운로드: {total_downloads}회")
            print()


def generate_release_notes(version: str) -> str:
    """기본 릴리즈 노트 생성"""
    return f"""# {version}

## 새로운 기능
- 

## 버그 수정
- 

## 변경 사항
- 

## 다운로드
- [실행 파일](링크)
- [설치 프로그램](링크)

---
릴리즈 날짜: {datetime.now().strftime('%Y년 %m월 %d일')}
"""


def find_build_files() -> List[str]:
    """빌드된 파일 찾기"""
    files = []
    
    # dist 폴더 확인
    dist_dir = PROJECT_ROOT / 'dist'
    if dist_dir.exists():
        exe_files = list(dist_dir.glob('*.exe'))
        if exe_files:
            files.extend([str(f) for f in exe_files])
    
    # installer 폴더 확인
    installer_dir = PROJECT_ROOT / 'installer'
    if installer_dir.exists():
        exe_files = list(installer_dir.glob('*.exe'))
        if exe_files:
            files.extend([str(f) for f in exe_files])
    
    return files


def main():
    parser = argparse.ArgumentParser(
        description='GitHub Releases 생성 및 관리',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 현재 버전으로 릴리즈 생성
  python tools/release_manager.py create

  # 특정 버전으로 릴리즈 생성
  python tools/release_manager.py create --tag v1.0.0

  # 파일과 함께 릴리즈 생성
  python tools/release_manager.py create --files dist/SchoolTimetableWidget.exe

  # 릴리즈 목록 보기
  python tools/release_manager.py list

  # 최신 릴리즈 정보 보기
  python tools/release_manager.py info

환경변수:
  GITHUB_TOKEN: GitHub Personal Access Token
  
토큰 설정:
  python tools/setup_token.py  # 자동 설정 스크립트 실행
        """
    )
    
    parser.add_argument(
        'command',
        choices=['create', 'list', 'info', 'delete'],
        help='실행할 명령'
    )
    parser.add_argument(
        '--token',
        help='GitHub Personal Access Token (없으면 GITHUB_TOKEN 환경변수 사용)'
    )
    parser.add_argument(
        '--tag',
        help='버전 태그 (예: v1.0.0, 없으면 현재 버전 사용)'
    )
    parser.add_argument(
        '--name',
        help='릴리즈 제목 (없으면 태그 사용)'
    )
    parser.add_argument(
        '--body',
        help='릴리즈 노트 (없으면 기본 템플릿 사용)'
    )
    parser.add_argument(
        '--body-file',
        help='릴리즈 노트 파일 경로'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='업로드할 파일 경로 (여러 개 가능)'
    )
    parser.add_argument(
        '--draft',
        action='store_true',
        help='초안으로 생성 (발행하지 않음)'
    )
    parser.add_argument(
        '--prerelease',
        action='store_true',
        help='프리릴리즈로 표시'
    )
    parser.add_argument(
        '--auto-files',
        action='store_true',
        help='자동으로 빌드된 파일 찾기 (dist/, installer/ 폴더)'
    )
    
    args = parser.parse_args()
    
    try:
        manager = ReleaseManager(token=args.token)
        
        if args.command == 'create':
            # 태그 결정
            tag = args.tag or VERSION_STRING
            if not tag.startswith('v'):
                tag = f"v{tag}"
            
            # 릴리즈 노트 결정
            if args.body_file:
                with open(args.body_file, 'r', encoding='utf-8') as f:
                    body = f.read()
            elif args.body:
                body = args.body
            else:
                body = generate_release_notes(tag)
                print("기본 릴리즈 노트를 생성했습니다. 수정하시겠습니까? (y/n): ", end='')
                if input().lower() == 'y':
                    import tempfile
                    import subprocess
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                        f.write(body)
                        temp_file = f.name
                    subprocess.run([os.environ.get('EDITOR', 'notepad'), temp_file])
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        body = f.read()
                    os.unlink(temp_file)
            
            # 파일 목록 결정
            files = args.files or []
            if args.auto_files:
                auto_files = find_build_files()
                if auto_files:
                    print(f"\n자동으로 찾은 파일:")
                    for f in auto_files:
                        print(f"  - {f}")
                    files.extend(auto_files)
            
            if not files:
                print("⚠️  업로드할 파일이 없습니다.")
                response = input("계속하시겠습니까? (y/n): ")
                if response.lower() != 'y':
                    return
            
            # 릴리즈 생성
            success = manager.create_release(
                tag=tag,
                name=args.name,
                body=body,
                draft=args.draft,
                prerelease=args.prerelease,
                files=files
            )
            
            if success:
                print(f"\n🎉 릴리즈 생성 완료!")
                if args.draft:
                    print("   (초안 상태 - GitHub에서 발행하세요)")
            else:
                sys.exit(1)
        
        elif args.command == 'list':
            manager.list_releases()
        
        elif args.command == 'info':
            latest = manager.get_latest_release()
            if latest:
                print(f"\n📦 최신 릴리즈: {latest['tag_name']}")
                print(f"   제목: {latest['name']}")
                print(f"   발행일: {latest.get('published_at', 'N/A')}")
                print(f"   URL: {latest['html_url']}")
                
                assets = latest.get('assets', [])
                if assets:
                    print(f"\n   파일:")
                    for asset in assets:
                        size_mb = asset['size'] / 1024 / 1024
                        downloads = asset.get('download_count', 0)
                        print(f"     - {asset['name']} ({size_mb:.1f} MB, {downloads}회 다운로드)")
            else:
                print("릴리즈가 없습니다.")
        
        elif args.command == 'delete':
            if not args.tag:
                print("❌ 삭제할 릴리즈의 태그를 지정하세요: --tag v1.0.0")
                sys.exit(1)
            
            release = manager.get_release_by_tag(args.tag)
            if not release:
                print(f"❌ 태그 {args.tag}의 릴리즈를 찾을 수 없습니다.")
                sys.exit(1)
            
            print(f"삭제할 릴리즈: {release['name']} ({release['tag_name']})")
            response = input("정말 삭제하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                if manager.delete_release(release['id']):
                    print("✅ 릴리즈 삭제 완료")
                else:
                    print("❌ 릴리즈 삭제 실패")
                    sys.exit(1)
            else:
                print("취소되었습니다.")
    
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n취소되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

