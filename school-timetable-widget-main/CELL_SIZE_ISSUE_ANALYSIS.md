# 셀 크기 변경 문제 분석

## 문제 현상
- 드래그 중 모니터 간 이동 시 셀 크기가 변경됨
- 최소 크기로 조정한 상태에서 DPI가 다른 모니터로 이동 시 셀 크기가 달라짐

## 현재 구현된 보호 장치

### 1. 드래그/리사이징 중 보호
- `adjust_cell_sizes()`: `self.resizing` 또는 `self.dragging`이 True이면 즉시 return
- `resizeEvent()`: 드래그/리사이징 중이면 타이머 중지하고 return
- `showEvent()`: 드래그/리사이징 중이면 실행하지 않음
- `changeEvent()`: 드래그/리사이징 중이면 실행하지 않음

### 2. 타이머 관리
- `handle_mouse_press()`: 드래그/리사이징 시작 시 모든 타이머 취소
- `handle_mouse_move()`: 드래그 중 매번 타이머 취소
- `resizeEvent()`: 드래그/리사이징 중 타이머 완전 중지

### 3. DPI 변경 처리
- `_check_and_adjust_for_dpi_change()`: DPI 변경 감지 및 처리
- 헤더 크기 계산 시 DPI 비율 고려

### 4. 셀 위젯 설정
- `QSizePolicy.Ignored`: 셀 위젯이 크기를 제안하지 않음
- `setMinimumSize(0, 0)`: 최소 크기를 0으로 설정하여 내용에 의존하지 않음
- `setMaximumSize(16777215, 16777215)`: 최대 크기 제한 없음

## 셀 크기 조정이 호출되는 경로

1. **초기화 시**: `setup_grid_sizing()` → `adjust_cell_sizes()`
2. **위젯 크기 변경**: `resizeEvent()` → `resize_timer` (150ms 지연) → `adjust_cell_sizes()`
3. **위젯 표시**: `showEvent()` → `_check_and_adjust_for_dpi_change()` (300ms 지연)
4. **상태 변경**: `changeEvent()` → `_check_and_adjust_for_dpi_change()` (300ms 지연)
5. **리사이징 종료**: `handle_mouse_release()` → `adjust_cell_sizes()` (200ms 지연)
6. **드래그 종료**: `handle_mouse_release()` → `_check_and_adjust_for_dpi_change()` (300ms 지연)
7. **위치 복원**: `apply_saved_position()` → `adjust_cell_sizes()` (300ms 지연)
8. **DPI 변경**: `_check_and_adjust_for_dpi_change()` → `adjust_cell_sizes()` (100ms 지연)

## 잠재적 문제점

### 1. 타이머 경쟁 조건
- 여러 타이머가 동시에 실행될 수 있음
- `singleShot` 타이머는 취소할 수 없음 (이미 시작된 경우)

### 2. 이벤트 순서
- 드래그 중 모니터 이동 시 여러 이벤트가 순차적으로 발생
- `move()` → `resizeEvent()` → `showEvent()` → `changeEvent()` 등
- 각 이벤트가 타이머를 설정하면 드래그 종료 후 여러 번 실행될 수 있음

### 3. DPI 변경 감지 타이밍
- `_check_and_adjust_for_dpi_change()`가 호출될 때 이미 `self.dragging`이 False일 수 있음
- 드래그 종료 후 DPI 변경이 감지되면 셀 크기가 변경될 수 있음

## 권장 사항

현재 구현은 대부분의 경우를 처리하지만, 완벽하지 않을 수 있습니다.
문제가 지속되면 다음을 고려할 수 있습니다:

1. **디버깅 로그 추가**: 각 이벤트와 타이머 실행 시점을 로그로 기록
2. **타이머 통합**: 모든 셀 크기 조정을 하나의 타이머로 통합하고, 새로운 요청 시 기존 타이머 취소
3. **드래그 종료 후 지연 증가**: 드래그 종료 후 더 긴 지연 시간(500ms 이상)을 두어 모든 이벤트가 완료된 후 처리

## 현재 상태

모든 보호 장치가 구현되어 있으며, 대부분의 경우 정상 동작할 것으로 예상됩니다.
문제가 지속되면 추가 디버깅이 필요할 수 있습니다.

