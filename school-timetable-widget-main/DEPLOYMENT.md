# Windows 배포 가이드

## 배포 방법

> **온라인 설치 프로그램**: 작은 설치 파일만 배포하고 GitHub에서 자동으로 다운로드하는 방식도 지원합니다. 자세한 내용은 [ONLINE_INSTALLER_GUIDE.md](ONLINE_INSTALLER_GUIDE.md)를 참조하세요.

> **자동 릴리즈 관리**: GitHub Releases 생성과 관리를 자동화할 수 있습니다. 자세한 내용은 [tools/RELEASE_MANAGER_GUIDE.md](tools/RELEASE_MANAGER_GUIDE.md)를 참조하세요.

### 방법 1: PyInstaller를 사용한 단일 실행 파일 생성 (권장)

#### 1. 필요한 패키지 설치
```bash
pip install pyinstaller
```

#### 2. 빌드 실행
```bash
python build_windows.py
```

또는 직접 PyInstaller 실행:
```bash
pyinstaller build_windows.spec
```

#### 3. 결과
- `dist/SchoolTimetableWidget.exe` - 단일 실행 파일
- 사용자는 이 파일 하나만 다운로드하여 실행 가능

#### 장점
- 간단한 배포 (단일 파일)
- Python 설치 불필요
- 빠른 실행

#### 단점
- 파일 크기가 큼 (약 50-100MB)
- 첫 실행이 약간 느릴 수 있음

---

### 방법 2: 인스톨러 생성 (전문적인 배포)

#### 1. 빌드 먼저 실행
```bash
python build_windows.py
```

#### 2. Inno Setup 설치
- 다운로드: https://jrsoftware.org/isdl.php
- 무료 오픈소스 인스톨러 생성 도구

#### 3. 인스톨러 생성
1. Inno Setup Compiler 실행
2. `build_installer.iss` 파일 열기
3. "Build" → "Compile" 클릭

#### 4. 결과
- `installer/SchoolTimetableWidget_Setup.exe` - 설치 프로그램
- 사용자는 설치 프로그램을 실행하여 설치

#### 장점
- 전문적인 배포 방식
- 시작 메뉴, 바탕화면 바로가기 자동 생성
- 제거 프로그램 포함
- 사용자 경험 향상

#### 단점
- Inno Setup 설치 필요
- 추가 빌드 단계 필요

---

## 배포 체크리스트

### 빌드 전 확인사항
- [ ] `requirements.txt`의 모든 필수 패키지가 설치되어 있는지 확인
- [ ] `src/assets/app_icon.ico` 파일이 존재하는지 확인
- [ ] 테스트 실행하여 모든 기능이 정상 작동하는지 확인

### 빌드 후 확인사항
- [ ] 생성된 exe 파일이 정상 실행되는지 확인
- [ ] 다른 Windows PC에서 테스트 (Python 미설치 환경)
- [ ] 모든 기능이 정상 작동하는지 확인
- [ ] 아이콘이 올바르게 표시되는지 확인

### 배포 전 확인사항
- [ ] 버전 번호 확인 (`src/utils/version.py`)
- [ ] README.md 최신화
- [ ] 릴리즈 노트 작성
- [ ] 바이러스 검사 (False Positive 가능성 있음)

---

## 배포 파일 구조

### 방법 1 (단일 실행 파일)
```
배포 폴더/
└── SchoolTimetableWidget.exe
```

### 방법 2 (인스톨러)
```
배포 폴더/
└── SchoolTimetableWidget_Setup.exe
```

---

## 문제 해결

### 빌드 오류
1. **ModuleNotFoundError**: `hiddenimports`에 누락된 모듈 추가
2. **리소스 파일 누락**: `datas` 섹션에 파일 경로 확인
3. **아이콘 오류**: `src/assets/app_icon.ico` 파일 존재 확인

### 실행 오류
1. **DLL 누락**: Visual C++ Redistributable 설치 필요
2. **경로 오류**: `resource_path()` 함수가 올바르게 작동하는지 확인
3. **권한 오류**: 관리자 권한으로 실행 시도

### 바이러스 오탐
- PyInstaller로 빌드된 파일은 때때로 바이러스로 오탐지될 수 있음
- 해결 방법:
  1. 코드 서명 인증서로 서명
  2. 주요 백신 업체에 화이트리스트 신청
  3. 사용자에게 오탐지 가능성 안내

---

## 추가 최적화

### 파일 크기 줄이기
- `excludes`에 불필요한 모듈 추가
- UPX 압축 사용 (기본 활성화)
- 콘솔 모드 비활성화 (`console=False`)

### 실행 속도 향상
- `--onefile` 대신 `--onedir` 사용 고려 (더 빠른 실행)
- 필요한 모듈만 포함

---

## 배포 채널

### GitHub Releases (권장)
1. GitHub 저장소의 Releases 섹션으로 이동
2. "Draft a new release" 클릭
3. 버전 태그 및 릴리즈 노트 작성
4. 빌드된 exe 파일 업로드

> **상세 가이드**: GitHub Releases 사용 방법에 대한 자세한 내용은 [GITHUB_RELEASES_GUIDE.md](GITHUB_RELEASES_GUIDE.md)를 참조하세요.

### 직접 배포
- 웹사이트, 클라우드 스토리지 등에 업로드
- 다운로드 링크 제공

---

## 참고 사항

- **코드 서명**: 신뢰성 향상을 위해 코드 서명 인증서 사용 권장
- **업데이트 메커니즘**: 현재 구현된 자동 업데이트 기능 활용
- **사용자 데이터**: `%APPDATA%\SchoolTimetableWidget\`에 저장됨 (설치와 무관)

