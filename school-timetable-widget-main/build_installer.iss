; Inno Setup 스크립트 - Windows 인스톨러 생성용
; 사용법: Inno Setup Compiler로 이 파일을 열어 컴파일
; 다운로드: https://jrsoftware.org/isdl.php

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName=학교 시간표 위젯
AppVersion=1.0.0
AppPublisher=TimeTableDev
AppPublisherURL=https://github.com/chuthulhu/school-timetable-widget
AppSupportURL=https://github.com/chuthulhu/school-timetable-widget
AppUpdatesURL=https://github.com/chuthulhu/school-timetable-widget
DefaultDirName={autopf}\SchoolTimetableWidget
DefaultGroupName=학교 시간표 위젯
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=SchoolTimetableWidget_Setup
SetupIconFile=src\assets\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "시작 프로그램에 추가"; GroupDescription: "추가 옵션"; Flags: unchecked

[Files]
Source: "dist\SchoolTimetableWidget.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\학교 시간표 위젯"; Filename: "{app}\SchoolTimetableWidget.exe"
Name: "{group}\{cm:UninstallProgram,학교 시간표 위젯}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\학교 시간표 위젯"; Filename: "{app}\SchoolTimetableWidget.exe"; Tasks: desktopicon
Name: "{userstartup}\학교 시간표 위젯"; Filename: "{app}\SchoolTimetableWidget.exe"; Tasks: startup

[Run]
Filename: "{app}\SchoolTimetableWidget.exe"; Description: "{cm:LaunchProgram,학교 시간표 위젯}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 설치 후 실행 파일에 대한 정보 표시
  end;
end;

