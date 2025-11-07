# 릴리즈 관리자 사용 가이드

## 개요

`release_manager.py`는 GitHub Releases를 생성하고 관리하는 자동화 스크립트입니다.

## 사전 준비

### 1. GitHub Personal Access Token 생성

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" 클릭
3. 토큰 이름 입력 (예: "Release Manager")
4. 권한 선택:
   - ✅ `repo` (전체 저장소 접근)
5. "Generate token" 클릭
6. **토큰을 복사하여 안전하게 보관** (다시 볼 수 없음)

### 2. 환경변수 설정

#### 방법 1: 자동 설정 스크립트 (권장)
```bash
python tools/setup_token.py
```
이 스크립트가 토큰을 입력받아 환경변수를 자동으로 설정합니다.

#### 방법 2: 수동 설정

##### Windows (PowerShell) - 현재 세션만
```powershell
$env:GITHUB_TOKEN = "your_token_here"
```

##### Windows (CMD) - 현재 세션만
```cmd
set GITHUB_TOKEN=your_token_here
```

##### Windows - 영구 설정 (GUI)
1. 시스템 속성 → 환경 변수
2. 사용자 변수에 `GITHUB_TOKEN` 추가
3. 값에 토큰 입력

##### Windows - 영구 설정 (명령줄)
```cmd
setx GITHUB_TOKEN "your_token_here"
```
주의: 새 터미널 창에서만 적용됩니다.

#### Linux/Mac
```bash
export GITHUB_TOKEN="your_token_here"
```

또는 `~/.bashrc` 또는 `~/.zshrc`에 추가:
```bash
export GITHUB_TOKEN="your_token_here"
```

## 사용 방법

### 1. 릴리즈 생성

#### 기본 사용 (현재 버전 사용)
```bash
python tools/release_manager.py create
```

#### 특정 버전으로 생성
```bash
python tools/release_manager.py create --tag v1.0.0
```

#### 파일과 함께 생성
```bash
python tools/release_manager.py create --files dist/SchoolTimetableWidget.exe
```

#### 여러 파일 업로드
```bash
python tools/release_manager.py create \
  --files dist/SchoolTimetableWidget.exe \
          installer/SchoolTimetableWidget_Setup.exe
```

#### 자동으로 빌드 파일 찾기
```bash
python tools/release_manager.py create --auto-files
```
- `dist/` 폴더의 `.exe` 파일 자동 검색
- `installer/` 폴더의 `.exe` 파일 자동 검색

#### 릴리즈 노트 파일 사용
```bash
python tools/release_manager.py create --body-file RELEASE_NOTES.md
```

#### 초안으로 생성 (나중에 발행)
```bash
python tools/release_manager.py create --draft
```

#### 프리릴리즈로 생성
```bash
python tools/release_manager.py create --prerelease
```

#### 전체 옵션 예제
```bash
python tools/release_manager.py create \
  --tag v1.0.0 \
  --name "v1.0.0 - 첫 번째 정식 릴리즈" \
  --body-file RELEASE_NOTES.md \
  --auto-files \
  --token your_token_here
```

### 2. 릴리즈 목록 보기

```bash
python tools/release_manager.py list
```

출력 예시:
```
📦 릴리즈 목록 (3개):

  v1.0.0 - v1.0.0
    발행일: 2024-01-15T10:30:00Z
    URL: https://github.com/.../releases/tag/v1.0.0
    다운로드: 42회

  v0.9.0 - v0.9.0 🔖 [Pre-release]
    발행일: 2024-01-10T08:15:00Z
    URL: https://github.com/.../releases/tag/v0.9.0
    다운로드: 15회
```

### 3. 최신 릴리즈 정보 보기

```bash
python tools/release_manager.py info
```

### 4. 릴리즈 삭제

```bash
python tools/release_manager.py delete --tag v1.0.0
```

⚠️ **주의**: 삭제는 되돌릴 수 없습니다!

## 일반적인 워크플로우

### 완전 자동화 워크플로우

```bash
# 1. 프로그램 빌드
python build_windows.py

# 2. 릴리즈 생성 (자동으로 빌드 파일 찾기)
python tools/release_manager.py create --auto-files

# 완료!
```

### 수동 제어 워크플로우

```bash
# 1. 프로그램 빌드
python build_windows.py

# 2. 릴리즈 노트 작성
# RELEASE_NOTES.md 파일 편집

# 3. 릴리즈 생성 (초안)
python tools/release_manager.py create \
  --body-file RELEASE_NOTES.md \
  --auto-files \
  --draft

# 4. GitHub에서 확인 후 발행
# https://github.com/chuthulhu/school-timetable-widget/releases
```

## 릴리즈 노트 템플릿

`RELEASE_NOTES.md` 예시:

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

## 문제 해결

### 1. "GitHub Token이 필요합니다" 오류

**원인**: 환경변수 `GITHUB_TOKEN`이 설정되지 않음

**해결**:
```bash
# 방법 1: 환경변수 설정
export GITHUB_TOKEN="your_token_here"

# 방법 2: 명령줄에서 직접 지정
python tools/release_manager.py create --token your_token_here
```

### 2. "태그가 이미 존재합니다" 오류

**원인**: 같은 태그로 이미 릴리즈가 생성됨

**해결**:
- 다른 태그 사용: `--tag v1.0.1`
- 기존 릴리즈 삭제 후 재생성
- 기존 릴리즈를 재릴리즈 (GitHub 웹에서)

### 3. "파일이 너무 큽니다" 경고

**원인**: 파일 크기가 100MB 제한 초과

**해결**:
- 파일 압축
- 파일 분할
- GitHub Pro 계정 사용 (2GB 제한)

### 4. 업로드 실패

**원인**: 네트워크 문제, 권한 문제 등

**해결**:
- 인터넷 연결 확인
- 토큰 권한 확인 (`repo` 권한 필요)
- 타임아웃 증가 (코드 수정 필요)

## 고급 사용법

### 배치 스크립트 예제 (Windows)

`release.bat`:
```batch
@echo off
echo 빌드 중...
python build_windows.py

echo 릴리즈 생성 중...
python tools/release_manager.py create --auto-files

echo 완료!
pause
```

### 셸 스크립트 예제 (Linux/Mac)

`release.sh`:
```bash
#!/bin/bash
set -e

echo "빌드 중..."
python build_windows.py

echo "릴리즈 생성 중..."
python tools/release_manager.py create --auto-files

echo "완료!"
```

## 보안 주의사항

1. **토큰 보안**
   - 토큰을 코드에 하드코딩하지 마세요
   - 환경변수나 설정 파일 사용
   - `.gitignore`에 토큰 포함 파일 추가

2. **권한 최소화**
   - 필요한 최소한의 권한만 부여
   - `repo` 권한만 사용 (전체 저장소 접근)

3. **토큰 만료**
   - 정기적으로 토큰 갱신
   - 만료된 토큰은 즉시 삭제

## 참고

- GitHub API 문서: https://docs.github.com/en/rest/releases
- Personal Access Tokens: https://github.com/settings/tokens
- 이 프로젝트 Releases: https://github.com/chuthulhu/school-timetable-widget/releases

