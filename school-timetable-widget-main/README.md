# 학교 시간표 위젯

Windows용 학교 시간표 위젯입니다. 바탕화면에 시간표를 표시하고, 현재 교시를 자동으로 하이라이트합니다.

## ✨ 주요 기능

- 📅 **시간표 표시**: 바탕화면에 시간표 위젯 표시
- 🎨 **커스터마이징**: 색상, 폰트, 투명도 등 스타일 커스터마이징
- 📍 **드래그 앤 드롭**: 마우스로 자유롭게 위치 이동
- 🔧 **크기 조절**: 우측 하단 모서리를 드래그하여 크기 조절
- 🖥️ **멀티모니터 지원**: 여러 모니터에서 사용 가능
- 📐 **DPI 스케일링**: 다양한 DPI 설정 지원
- 🔔 **시스템 트레이**: 시스템 트레이에서 실행 상태 관리
- 🚀 **자동 시작**: Windows 시작 시 자동 실행 옵션
- 🔄 **자동 업데이트**: 최신 버전 자동 확인 및 다운로드
- 💾 **백업/복원**: 시간표 데이터 백업 및 복원 기능
- 📤 **데이터 가져오기**: 파일에서 시간표 데이터 가져오기

## 📥 다운로드 및 설치

### 최신 버전 다운로드

1. [최신 릴리즈 다운로드](https://github.com/chuthulhu/school-timetable-widget/releases/latest)
2. `SchoolTimetableWidget.exe` 파일을 다운로드하세요.

### 설치 및 실행

1. 다운로드한 `SchoolTimetableWidget.exe` 파일을 실행하세요.
2. 최초 실행 시 Windows SmartScreen 경고가 나타날 수 있습니다.
   - "추가 정보" → "실행"을 선택하세요.
3. 별도의 설치 과정 없이 바로 실행됩니다.
4. 시스템 트레이에 아이콘이 표시됩니다.

### 사용 방법

1. **시간표 편집**: 위젯을 우클릭 → "시간표 편집"
2. **교시 시간 설정**: 위젯을 우클릭 → "교시 시간 설정"
3. **스타일 변경**: 위젯을 우클릭 → "위젯 설정"
4. **위치 이동**: 위젯을 드래그하여 원하는 위치로 이동
5. **크기 조절**: 우측 하단 모서리를 드래그하여 크기 조절
6. **위치 고정**: 위젯을 우클릭 → "위치 고정" (드래그 방지)

## 🔄 업데이트

### 자동 업데이트

프로그램이 시작될 때 자동으로 최신 버전을 확인합니다. 새 버전이 있으면 알림이 표시되고, 다운로드 후 자동으로 업데이트됩니다.

### 수동 업데이트

1. [최신 릴리즈](https://github.com/chuthulhu/school-timetable-widget/releases/latest)에서 새 버전 다운로드
2. 기존 `SchoolTimetableWidget.exe` 파일을 새 파일로 교체
3. 프로그램 재실행

## 💻 개발 환경에서 실행

### 사전 요구사항

- Python 3.8 이상
- Windows 10 이상

### 1. 저장소 클론

```bash
git clone https://github.com/chuthulhu/school-timetable-widget.git
cd school-timetable-widget
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 실행

프로젝트 루트에서:
```bash
python src/main.py
```

또는 src 디렉토리에서:
```bash
cd src
python main.py
```

### 4. 선택적 의존성 (기능별)

Windows 알림 기능:
```bash
pip install win10toast
```

Windows 자동 시작 기능:
```bash
pip install pywin32
```

## 🛠️ 빌드 및 배포

### Windows 실행 파일 빌드

```bash
# PyInstaller 설치
pip install pyinstaller

# 빌드 실행
python build_windows.py
```

빌드된 파일은 `dist/SchoolTimetableWidget.exe`에 생성됩니다.

자세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참조하세요.

## 📁 프로젝트 구조

```
school-timetable-widget/
├── src/                    # 소스 코드
│   ├── main.py            # 애플리케이션 진입점
│   ├── core/              # 핵심 모듈
│   ├── gui/               # GUI 모듈
│   ├── utils/             # 유틸리티 모듈
│   └── notifications/      # 알림 모듈
├── tools/                 # 개발 도구
├── tests/                 # 테스트 코드
└── requirements.txt       # Python 의존성
```

자세한 프로젝트 구조는 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)를 참조하세요.

## 📝 데이터 저장 위치

사용자 데이터는 다음 위치에 저장됩니다:

- **Windows**: `%APPDATA%\SchoolTimetableWidget\`
  - 시간표 데이터: `timetable_data.json`
  - 교시 시간 설정: `time_settings.json`
  - 스타일 설정: `style_settings.json`
  - 위젯 설정: `widget_settings.json`
  - 백업 파일: `backups/`

## 🐛 문제 해결

### Windows SmartScreen 경고

최초 실행 시 Windows SmartScreen 경고가 나타날 수 있습니다. 이는 코드 서명 인증서가 없기 때문입니다. "추가 정보" → "실행"을 선택하여 실행하세요.

### 위젯이 보이지 않을 때

1. 시스템 트레이 아이콘을 확인하세요.
2. 다른 창 뒤에 숨어 있을 수 있습니다. 작업 표시줄에서 프로그램을 클릭하세요.
3. 다른 모니터에 있을 수 있습니다. 모든 모니터를 확인하세요.

### 설정이 저장되지 않을 때

1. `%APPDATA%\SchoolTimetableWidget\` 폴더의 쓰기 권한을 확인하세요.
2. 바이러스 백신 소프트웨어가 차단하고 있는지 확인하세요.

## 🤝 기여하기

버그 리포트, 기능 제안, Pull Request를 환영합니다!

1. 이 저장소를 포크하세요.
2. 새 기능 브랜치를 생성하세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`)
5. Pull Request를 열어주세요.

## 📄 라이선스

이 프로젝트의 라이선스 정보는 저장소의 LICENSE 파일을 참조하세요.

## 🔗 관련 문서

- [배포 가이드](DEPLOYMENT.md)
- [GitHub Releases 가이드](GITHUB_RELEASES_GUIDE.md)
- [온라인 설치 프로그램 가이드](ONLINE_INSTALLER_GUIDE.md)
- [프로젝트 구조](PROJECT_STRUCTURE.md)

## 📧 문의

문제가 발생하거나 질문이 있으시면 [Issues](https://github.com/chuthulhu/school-timetable-widget/issues)에 등록해주세요.

---

**학교 시간표 위젯 v1.0.0** - 바탕화면에 시간표를 표시하는 간단하고 편리한 도구입니다.
