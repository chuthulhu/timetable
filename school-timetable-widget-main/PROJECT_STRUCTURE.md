# 프로젝트 구조

## 디렉토리 구조

```
school-timetable-widget-main/
├── src/                          # 소스 코드
│   ├── __init__.py              # 패키지 초기화
│   ├── main.py                  # 애플리케이션 진입점
│   ├── assets/                  # 리소스 파일 (아이콘, 기본 데이터)
│   │   ├── app_icon.ico
│   │   ├── icon.ico
│   │   └── default_timetable.csv
│   ├── core/                    # 핵심 모듈
│   │   ├── __init__.py
│   │   ├── application_manager.py  # 애플리케이션 생명주기 관리
│   │   ├── process_manager.py      # 프로세스 관리
│   │   └── updater.py              # 업데이트 관리
│   ├── gui/                     # GUI 모듈
│   │   ├── __init__.py
│   │   ├── widget.py            # 메인 위젯
│   │   ├── components/          # GUI 컴포넌트
│   │   │   ├── color_button.py
│   │   │   └── theme_selector.py
│   │   └── dialogs/             # 대화상자
│   │       ├── backup_dialog.py
│   │       ├── import_dialog.py
│   │       ├── settings_dialog.py
│   │       ├── time_dialog.py
│   │       └── timetable_dialog.py
│   ├── notifications/          # 알림 모듈
│   │   ├── __init__.py
│   │   └── notification_manager.py
│   ├── utils/                   # 유틸리티 모듈
│   │   ├── __init__.py
│   │   ├── auto_start.py        # 자동 시작 관리
│   │   ├── config.py           # 설정 상수
│   │   ├── exceptions.py       # 예외 클래스
│   │   ├── paths.py             # 경로 관리
│   │   ├── settings_manager.py # 설정 관리
│   │   ├── styling.py          # 스타일 관리
│   │   └── version.py          # 버전 관리
│   └── tray_icon.py            # 트레이 아이콘
│
├── tests/                       # 테스트 코드
│   ├── __init__.py
│   └── test_settings_manager.py
│
├── tools/                       # 개발 도구
│   ├── app_icon.ico
│   └── create_icon.py
│
├── data/                       # 기본 설정 파일 (개발/테스트용)
│   ├── style_settings.json
│   ├── time_settings.json
│   ├── timetable_data.json
│   └── widget_settings.json
│
├── .gitignore                  # Git 무시 파일
├── .gitattributes              # Git 속성 파일
├── requirements.txt            # Python 의존성
├── README.md                   # 프로젝트 문서
├── REFACTORING_SUMMARY.md     # 리팩토링 요약
└── PROJECT_STRUCTURE.md       # 이 파일
```

## 주요 디렉토리 설명

### src/
애플리케이션의 모든 소스 코드가 포함된 메인 디렉토리입니다.

- **main.py**: 애플리케이션의 진입점
- **assets/**: 아이콘, 기본 데이터 등 리소스 파일
- **core/**: 애플리케이션의 핵심 비즈니스 로직
- **gui/**: 사용자 인터페이스 관련 코드
- **notifications/**: 알림 기능 관련 코드
- **utils/**: 공통 유틸리티 함수 및 클래스

### tests/
단위 테스트 및 통합 테스트 코드가 포함된 디렉토리입니다.

### tools/
개발 및 빌드에 사용되는 도구 스크립트가 포함된 디렉토리입니다.

### data/
개발 및 테스트에 사용되는 기본 설정 파일이 포함된 디렉토리입니다.
실제 사용자 데이터는 OS 표준 경로에 저장됩니다 (Windows: `%APPDATA%\SchoolTimetableWidget\`).

## Import 경로 규칙

모든 import는 `src/` 디렉토리를 기준으로 합니다:

```python
# src/ 내부에서의 import
from utils.settings_manager import SettingsManager
from core.application_manager import ApplicationManager
from gui.widget import Widget
```

## 실행 방법

프로젝트 루트에서:
```bash
python src/main.py
```

또는 src 디렉토리에서:
```bash
cd src
python main.py
```

