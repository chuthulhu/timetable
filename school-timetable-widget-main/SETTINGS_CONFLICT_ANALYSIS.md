# 위젯 설정 충돌 분석

## 발견된 잠재적 충돌 문제

### 1. 셀 크기 비율 저장 타이밍 충돌 ⚠️

**문제점:**
- `adjust_cell_sizes()`에서 500ms 지연 후 `save_widget_settings()` 호출
- `save_widget_position()`에서 즉시 `save_widget_settings()` 호출
- 두 메서드가 거의 동시에 호출되면 마지막 저장만 유지됨

**발생 시나리오:**
1. 사용자가 위젯 크기 조절 (리사이징)
2. `handle_mouse_release()` → `save_widget_position()` → 즉시 저장
3. `handle_mouse_release()` → `adjust_cell_sizes()` → 500ms 후 저장
4. 결과: 셀 크기 비율이 저장되기 전에 위젯 크기가 덮어씌워질 수 있음

**위치:**
- `src/gui/widget.py:373` - `adjust_cell_sizes()`에서 500ms 지연 저장
- `src/gui/widget.py:465` - `save_widget_position()`에서 즉시 저장

### 2. `_restore_cell_sizes()`에서 `resize()` 호출 시 무한 루프 가능성 ⚠️

**문제점:**
- `_restore_cell_sizes()`에서 `resize()` 호출
- `resize()` → `resizeEvent()` → `adjust_cell_sizes()` → 다시 저장
- 순환 호출 가능성

**발생 시나리오:**
1. `showEvent()` → `_restore_cell_sizes()` 호출
2. `_restore_cell_sizes()`에서 `resize()` 호출
3. `resizeEvent()` 발생 → `adjust_cell_sizes()` 호출
4. `adjust_cell_sizes()`에서 다시 셀 크기 비율 저장
5. 결과: 무한 루프 또는 불필요한 반복 호출

**위치:**
- `src/gui/widget.py:715` - `_restore_cell_sizes()`에서 `resize()` 호출
- `src/gui/widget.py:619` - `resizeEvent()`에서 `adjust_cell_sizes()` 호출

### 3. 여러 타이머가 동시에 실행될 수 있음 ⚠️

**문제점:**
- `adjust_cell_sizes()` 저장 타이머 (500ms)
- `resize_timer` (150ms)
- `showEvent` 타이머 (100ms, 300ms)
- `changeEvent` 타이머 (300ms)
- 여러 타이머가 동시에 실행되면 설정이 덮어씌워질 수 있음

**위치:**
- 여러 곳에서 `QTimer.singleShot()` 사용

### 4. SettingsDialog와 위젯 간 설정 충돌 ⚠️

**문제점:**
- SettingsDialog에서 위젯 크기 변경 시 `save_widget_position()` 호출
- 동시에 위젯에서도 자동으로 저장
- 두 저장이 충돌할 수 있음

**위치:**
- `src/gui/dialogs/settings_dialog.py:623` - SettingsDialog에서 저장
- `src/gui/widget.py:465` - 위젯에서 저장

### 5. `apply_saved_position()`에서 `resize()` 후 `adjust_cell_sizes()` 호출 ⚠️

**문제점:**
- `apply_saved_position()`에서 `resize()` 호출
- `resize()` → `resizeEvent()` → `adjust_cell_sizes()` 호출
- 그런데 `apply_saved_position()`에서도 300ms 후 `adjust_cell_sizes()` 호출
- 중복 호출 가능성

**위치:**
- `src/gui/widget.py:431` - `resize()` 호출
- `src/gui/widget.py:435` - `adjust_cell_sizes()` 호출
- `src/gui/widget.py:619` - `resizeEvent()`에서도 `adjust_cell_sizes()` 호출

## 권장 수정 사항

### 1. 설정 저장 통합 및 디바운싱
- 모든 설정 저장을 하나의 타이머로 통합
- 마지막 변경 후 일정 시간(예: 1초) 후에만 저장

### 2. `_restore_cell_sizes()`에서 플래그 사용
- 복원 중임을 나타내는 플래그 추가
- 복원 중에는 `adjust_cell_sizes()`에서 저장하지 않음

### 3. `apply_saved_position()` 중복 호출 방지
- `apply_saved_position()` 실행 중 플래그 추가
- 플래그가 설정되어 있으면 `resizeEvent()`에서 `adjust_cell_sizes()` 호출하지 않음

### 4. SettingsDialog와 위젯 간 동기화
- SettingsDialog에서 변경 시 위젯에 알림
- 위젯에서 자동 저장 중지

