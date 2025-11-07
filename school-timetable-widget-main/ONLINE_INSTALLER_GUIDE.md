# 온라인 설치 프로그램 가이드

## 개요

온라인 설치 프로그램은 작은 다운로더만 배포하고, 실행 시 GitHub에서 실제 프로그램을 다운로드하여 설치하는 방식입니다.

## 장점

1. **작은 초기 다운로드 크기**: 다운로더만 배포 (약 5-10MB)
2. **항상 최신 버전**: GitHub Releases에서 최신 버전 자동 다운로드
3. **업데이트 용이**: GitHub에 새 버전만 업로드하면 자동으로 최신 버전 설치
4. **배포 간소화**: 작은 파일만 배포하면 됨

## 단점

1. **인터넷 연결 필요**: 설치 시 인터넷 연결 필수
2. **다운로드 시간**: 실제 프로그램 다운로드 시간 소요
3. **GitHub 의존성**: GitHub 서비스에 의존

## 구현 방법

### 방법 1: Python 다운로더 (권장)

#### 1. 다운로더 빌드
```bash
# requests 설치
pip install requests pyinstaller

# 다운로더 빌드
pyinstaller build_installer_downloader.spec
```

#### 2. 결과
- `dist/SchoolTimetableWidget_Installer.exe` (약 5-10MB)
- 이 파일을 사용자에게 배포

#### 3. 사용자 사용 방법
1. `SchoolTimetableWidget_Installer.exe` 다운로드
2. 실행
3. 자동으로 GitHub에서 최신 버전 다운로드 및 설치

### 방법 2: Inno Setup 온라인 설치 프로그램

#### 1. Inno Setup 설치
- 다운로드: https://jrsoftware.org/isdl.php

#### 2. 빌드
1. Inno Setup Compiler 실행
2. `build_installer_online.iss` 파일 열기
3. "Build" → "Compile" 클릭

#### 3. 결과
- `installer/SchoolTimetableWidget_Online_Setup.exe` (약 1-2MB)
- 이 파일을 사용자에게 배포

## GitHub Releases 설정

### 1. 릴리즈 생성
1. GitHub 저장소의 "Releases" 섹션으로 이동
2. "Draft a new release" 클릭
3. 버전 태그 입력 (예: `v1.0.0`)
4. 릴리즈 노트 작성
5. **Assets** 섹션에 `SchoolTimetableWidget.exe` 파일 업로드
6. "Publish release" 클릭

### 2. 파일 이름 규칙
- 다운로더는 `SchoolTimetableWidget*.exe` 패턴을 찾습니다
- 권장 파일명: `SchoolTimetableWidget_v1.0.0.exe`

## 배포 워크플로우

### 개발자 작업
1. 프로그램 빌드 (`python build_windows.py`)
2. `dist/SchoolTimetableWidget.exe` 생성
3. GitHub Releases에 업로드
4. 다운로더만 배포 (작은 파일)

### 사용자 작업
1. 작은 설치 프로그램 다운로드
2. 실행
3. 자동으로 최신 버전 다운로드 및 설치

## 비교

| 방식 | 초기 다운로드 | 설치 시간 | 업데이트 | 인터넷 필요 |
|------|-------------|----------|---------|-----------|
| **오프라인 설치** | 50-100MB | 빠름 | 수동 | 불필요 |
| **온라인 설치** | 5-10MB | 느림 (다운로드) | 자동 | 필요 |

## 권장 사항

### 온라인 설치 프로그램 사용 시나리오
- ✅ 정기적인 업데이트가 있는 경우
- ✅ 사용자가 최신 버전을 원하는 경우
- ✅ 초기 다운로드 크기를 줄이고 싶은 경우
- ✅ GitHub Releases를 활용하는 경우

### 오프라인 설치 프로그램 사용 시나리오
- ✅ 인터넷 연결이 불안정한 환경
- ✅ 오프라인 설치가 필요한 경우
- ✅ 한 번 설치하고 오래 사용하는 경우

## 하이브리드 방식

두 가지 방식을 모두 제공할 수 있습니다:

1. **온라인 설치 프로그램**: 작은 파일, 최신 버전 자동 다운로드
2. **오프라인 설치 프로그램**: 큰 파일, 인터넷 불필요

사용자가 선택할 수 있도록 두 가지 모두 배포하는 것을 권장합니다.

## 문제 해결

### 다운로드 실패
- 인터넷 연결 확인
- GitHub 서비스 상태 확인
- 방화벽/프록시 설정 확인

### 버전 확인 실패
- GitHub API 레이트 리밋 확인
- 릴리즈가 올바르게 생성되었는지 확인
- 파일 이름이 올바른지 확인

### 설치 실패
- 관리자 권한 확인
- 디스크 공간 확인
- 바이러스 백신 소프트웨어 확인

