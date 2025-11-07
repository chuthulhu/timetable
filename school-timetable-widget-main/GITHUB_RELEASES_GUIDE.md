# GitHub Releases 완전 가이드

## GitHub Releases란?

GitHub Releases는 소프트웨어의 특정 버전을 배포하고 관리하는 기능입니다. 소스 코드의 특정 시점(태그)과 함께 바이너리 파일, 릴리즈 노트 등을 함께 배포할 수 있습니다.

## 왜 GitHub Releases를 사용하나요?

### 장점
1. **버전 관리**: 각 릴리즈를 명확하게 태그로 관리
2. **파일 배포**: 실행 파일, 설치 프로그램 등을 직접 업로드
3. **릴리즈 노트**: 변경 사항을 사용자에게 알림
4. **자동 다운로드**: API를 통해 최신 버전 자동 확인 및 다운로드
5. **다운로드 통계**: 각 릴리즈의 다운로드 수 추적
6. **무료 호스팅**: GitHub에서 파일을 무료로 호스팅

### 이 프로젝트에서의 사용
- **자동 업데이트**: `src/core/updater.py`에서 최신 버전 확인
- **온라인 설치**: `installer_downloader.py`에서 최신 버전 다운로드
- **배포 관리**: 각 버전의 실행 파일 배포

## GitHub Releases 생성 방법

### 1. 웹 인터페이스로 생성 (권장)

#### 단계별 가이드

1. **GitHub 저장소로 이동**
   ```
   https://github.com/chuthulhu/school-timetable-widget
   ```

2. **Releases 섹션으로 이동**
   - 저장소 페이지 오른쪽 사이드바에서 "Releases" 클릭
   - 또는 URL 직접 접근: `https://github.com/chuthulhu/school-timetable-widget/releases`

3. **새 릴리즈 생성**
   - "Draft a new release" 버튼 클릭
   - 또는 "Releases" 페이지에서 "Create a new release" 클릭

4. **태그 선택/생성**
   - **태그 이름**: 버전 번호 입력 (예: `v1.0.0`)
   - **태그 타입**: 
     - "Create new tag" 선택 (처음 릴리즈하는 경우)
     - 또는 기존 태그 선택 (재릴리즈)
   - **브랜치**: 보통 `main` 또는 `master` 선택

5. **릴리즈 제목 입력**
   - 예: `v1.0.0` 또는 `학교 시간표 위젯 v1.0.0`

6. **릴리즈 노트 작성**
   ```
   ## 새로운 기능
   - 새로운 기능 1
   - 새로운 기능 2
   
   ## 버그 수정
   - 버그 수정 1
   - 버그 수정 2
   
   ## 변경 사항
   - 변경 사항 1
   - 변경 사항 2
   ```

7. **파일 업로드 (Assets)**
   - "Attach binaries by dropping them here or selecting them" 영역에 파일 드래그 앤 드롭
   - 또는 "choose your files" 클릭하여 파일 선택
   - 업로드할 파일:
     - `SchoolTimetableWidget.exe` (메인 실행 파일)
     - `SchoolTimetableWidget_Setup.exe` (설치 프로그램, 선택적)
     - `SchoolTimetableWidget_Online_Setup.exe` (온라인 설치 프로그램, 선택적)

8. **릴리즈 발행**
   - "Publish release" 버튼 클릭
   - 또는 "Save draft"로 저장 후 나중에 발행

### 2. GitHub CLI로 생성

```bash
# GitHub CLI 설치 필요
gh release create v1.0.0 \
  --title "v1.0.0" \
  --notes "릴리즈 노트 내용" \
  dist/SchoolTimetableWidget.exe
```

### 3. GitHub API로 생성

```python
import requests

# GitHub Personal Access Token 필요
headers = {
    "Authorization": f"token YOUR_GITHUB_TOKEN",
    "Accept": "application/vnd.github.v3+json"
}

# 릴리즈 생성
data = {
    "tag_name": "v1.0.0",
    "name": "v1.0.0",
    "body": "릴리즈 노트 내용",
    "draft": False,
    "prerelease": False
}

response = requests.post(
    "https://api.github.com/repos/chuthulhu/school-timetable-widget/releases",
    headers=headers,
    json=data
)
```

## 버전 태그 규칙

### 시맨틱 버저닝 (Semantic Versioning)

형식: `MAJOR.MINOR.PATCH`

- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 이전 버전과 호환되는 기능 추가
- **PATCH**: 이전 버전과 호환되는 버그 수정

예시:
- `v1.0.0` - 첫 번째 정식 릴리즈
- `v1.1.0` - 새로운 기능 추가
- `v1.1.1` - 버그 수정
- `v2.0.0` - 주요 변경 (호환성 깨짐)

### 태그 이름 규칙

이 프로젝트에서는 `v` 접두사를 사용합니다:
- ✅ `v1.0.0`
- ✅ `v1.2.3`
- ❌ `1.0.0` (v 접두사 없음)
- ❌ `version-1.0.0` (다른 형식)

## 파일 이름 규칙

### 권장 파일명

1. **메인 실행 파일**
   ```
   SchoolTimetableWidget.exe
   SchoolTimetableWidget_v1.0.0.exe
   ```

2. **설치 프로그램**
   ```
   SchoolTimetableWidget_Setup.exe
   SchoolTimetableWidget_Setup_v1.0.0.exe
   ```

3. **온라인 설치 프로그램**
   ```
   SchoolTimetableWidget_Online_Setup.exe
   SchoolTimetableWidget_Installer.exe
   ```

### 파일 크기 제한

- GitHub 무료 계정: **파일당 최대 100MB**
- GitHub Pro 계정: **파일당 최대 2GB**
- 전체 릴리즈: **최대 2GB**

## GitHub Releases API 사용

### 현재 프로젝트에서의 사용

#### 1. 최신 릴리즈 정보 가져오기

```python
# src/core/updater.py
GITHUB_REPO = "chuthulhu/school-timetable-widget"
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

response = requests.get(GITHUB_API_RELEASES)
data = response.json()

# 응답 데이터 구조
{
    "tag_name": "v1.0.0",
    "name": "v1.0.0",
    "body": "릴리즈 노트...",
    "assets": [
        {
            "name": "SchoolTimetableWidget.exe",
            "browser_download_url": "https://github.com/.../downloads/.../SchoolTimetableWidget.exe",
            "size": 12345678,
            "download_count": 42
        }
    ]
}
```

#### 2. 특정 릴리즈 정보 가져오기

```python
# 특정 태그의 릴리즈
url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/v1.0.0"
response = requests.get(url)
```

#### 3. 모든 릴리즈 목록 가져오기

```python
url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
response = requests.get(url)
releases = response.json()  # 배열
```

### API 레이트 리밋

- **인증 없이**: 시간당 60회
- **인증 후**: 시간당 5,000회

인증 방법:
```python
headers = {
    "Authorization": "token YOUR_GITHUB_TOKEN"
}
response = requests.get(url, headers=headers)
```

## 배포 워크플로우

### 완전한 배포 프로세스

1. **코드 준비**
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   git tag v1.0.0
   git push origin main
   git push origin v1.0.0
   ```

2. **프로그램 빌드**
   ```bash
   python build_windows.py
   ```

3. **빌드 결과 확인**
   - `dist/SchoolTimetableWidget.exe` 파일 확인

4. **GitHub Releases 생성**
   - 웹 인터페이스에서 릴리즈 생성
   - `dist/SchoolTimetableWidget.exe` 업로드

5. **릴리즈 노트 작성**
   - 변경 사항 요약
   - 새로운 기능 설명
   - 버그 수정 내역

6. **릴리즈 발행**
   - "Publish release" 클릭

### 자동화 스크립트 예제

```python
# release.py
import subprocess
import sys
from pathlib import Path

def build():
    """프로그램 빌드"""
    print("빌드 중...")
    subprocess.run([sys.executable, "build_windows.py"], check=True)
    print("빌드 완료!")

def create_release(version):
    """GitHub Releases 생성"""
    exe_path = Path("dist/SchoolTimetableWidget.exe")
    if not exe_path.exists():
        print("오류: 빌드 파일을 찾을 수 없습니다.")
        return
    
    # GitHub CLI 사용
    subprocess.run([
        "gh", "release", "create", f"v{version}",
        "--title", f"v{version}",
        "--notes", f"릴리즈 v{version}",
        str(exe_path)
    ], check=True)
    print("릴리즈 생성 완료!")

if __name__ == "__main__":
    version = input("버전 번호 입력 (예: 1.0.0): ")
    build()
    create_release(version)
```

## 릴리즈 노트 작성 팁

### 좋은 릴리즈 노트 예시

```markdown
# v1.0.0 - 첫 번째 정식 릴리즈

## 🎉 새로운 기능
- 시간표 위젯 표시 기능
- 드래그 앤 드롭으로 위치 이동
- 커스텀 스타일 설정
- 자동 업데이트 기능

## 🐛 버그 수정
- 모니터 간 이동 시 셀 크기 문제 수정
- DPI 스케일링 문제 해결

## 📝 변경 사항
- UI 개선
- 성능 최적화

## 📥 다운로드
- [SchoolTimetableWidget.exe](링크) - 단일 실행 파일
- [SchoolTimetableWidget_Setup.exe](링크) - 설치 프로그램

## 감사합니다!
이 릴리즈에 기여해주신 모든 분들께 감사드립니다.
```

### 릴리즈 노트 템플릿

```markdown
# v{버전}

## 새로운 기능
- 

## 버그 수정
- 

## 변경 사항
- 

## 다운로드
- [실행 파일](링크)
- [설치 프로그램](링크)
```

## 문제 해결

### 1. 파일 업로드 실패

**문제**: 파일이 너무 큼
- **해결**: 파일 크기 확인 (100MB 제한)
- **대안**: 파일 분할 또는 압축

### 2. API 레이트 리밋 초과

**문제**: API 호출 제한 초과
- **해결**: GitHub Personal Access Token 사용
- **대안**: 요청 간격 조절

### 3. 태그가 이미 존재함

**문제**: 같은 태그 이름으로 릴리즈 생성 불가
- **해결**: 기존 태그 삭제 후 재생성
  ```bash
  git tag -d v1.0.0
  git push origin :refs/tags/v1.0.0
  ```

### 4. 다운로드 URL이 작동하지 않음

**문제**: `browser_download_url`이 404 반환
- **해결**: 
  - 릴리즈가 발행되었는지 확인 (Draft 상태 아님)
  - 파일이 올바르게 업로드되었는지 확인
  - URL 형식 확인

## 유용한 링크

- **GitHub Releases 문서**: https://docs.github.com/en/repositories/releasing-projects-on-github
- **GitHub API 문서**: https://docs.github.com/en/rest/releases
- **시맨틱 버저닝**: https://semver.org/
- **이 프로젝트 Releases**: https://github.com/chuthulhu/school-timetable-widget/releases

## 체크리스트

릴리즈 생성 전 확인사항:
- [ ] 코드가 최신 상태인지 확인
- [ ] 버전 번호가 올바른지 확인 (`src/utils/version.py`)
- [ ] 빌드가 성공적으로 완료되었는지 확인
- [ ] 빌드된 파일이 정상 작동하는지 테스트
- [ ] 릴리즈 노트 작성
- [ ] 파일 이름이 올바른지 확인
- [ ] 태그가 올바르게 생성되었는지 확인
- [ ] 릴리즈가 발행되었는지 확인

