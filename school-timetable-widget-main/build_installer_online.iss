; Inno Setup 스크립트 - 온라인 설치 프로그램
; 작은 설치 파일이 GitHub에서 실제 프로그램을 다운로드하여 설치
; 사용법: Inno Setup Compiler로 이 파일을 열어 컴파일

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
OutputBaseFilename=SchoolTimetableWidget_Online_Setup
SetupIconFile=src\assets\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
; 온라인 설치 프로그램이므로 작은 크기
MinVersion=6.1

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "시작 프로그램에 추가"; GroupDescription: "추가 옵션"; Flags: unchecked

[Files]
; 실제 프로그램 파일은 다운로드하므로 여기에는 다운로더만 포함
; (다운로더는 [Code] 섹션에서 구현)

[Icons]
Name: "{group}\학교 시간표 위젯"; Filename: "{app}\SchoolTimetableWidget.exe"
Name: "{group}\{cm:UninstallProgram,학교 시간표 위젯}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\학교 시간표 위젯"; Filename: "{app}\SchoolTimetableWidget.exe"; Tasks: desktopicon
Name: "{userstartup}\학교 시간표 위젯"; Filename: "{app}\SchoolTimetableWidget.exe"; Tasks: startup

[Code]
// GitHub Releases API를 사용하여 최신 버전 다운로드
const
  GITHUB_REPO = 'chuthulhu/school-timetable-widget';
  GITHUB_API_URL = 'https://api.github.com/repos/' + GITHUB_REPO + '/releases/latest';
  DOWNLOAD_TIMEOUT = 30000; // 30초

var
  DownloadPage: TDownloadWizardPage;
  DownloadProgressBar: TNewProgressBar;
  DownloadStatusLabel: TLabel;
  DownloadCanceled: Boolean;

// HTTP 다운로드 함수 (WinInet 사용)
function DownloadFile(Url, FileName: String): Boolean;
var
  InetHandle, FileHandle: LongWord;
  Buffer: array[0..1023] of Byte;
  BytesRead, BytesWritten: DWord;
  TotalSize, DownloadedSize: Int64;
  StatusCode: array[0..255] of Char;
  StatusCodeLen: DWord;
begin
  Result := False;
  DownloadedSize := 0;
  
  try
    // WinInet 초기화
    InetHandle := InternetOpen('Inno Setup', INTERNET_OPEN_TYPE_PRECONFIG, '', '', 0);
    if InetHandle = 0 then
    begin
      MsgBox('인터넷 연결을 초기화할 수 없습니다.', mbError, MB_OK);
      Exit;
    end;
    
    try
      // URL 열기
      FileHandle := InternetOpenUrl(InetHandle, PChar(Url), '', 0, INTERNET_FLAG_RELOAD, 0);
      if FileHandle = 0 then
      begin
        MsgBox('다운로드 URL을 열 수 없습니다: ' + Url, mbError, MB_OK);
        Exit;
      end;
      
      try
        // Content-Length 헤더 읽기
        StatusCodeLen := SizeOf(StatusCode);
        if HttpQueryInfo(FileHandle, HTTP_QUERY_CONTENT_LENGTH, @StatusCode, StatusCodeLen, 0) then
          TotalSize := StrToInt64Def(String(StatusCode), 0)
        else
          TotalSize := 0;
        
        // 파일 생성
        if FileExists(FileName) then
          DeleteFile(FileName);
        FileHandle := CreateFile(FileName, GENERIC_WRITE, 0, nil, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, 0);
        if FileHandle = INVALID_HANDLE_VALUE then
        begin
          MsgBox('파일을 생성할 수 없습니다: ' + FileName, mbError, MB_OK);
          Exit;
        end;
        
        try
          // 다운로드 진행
          repeat
            if DownloadCanceled then
            begin
              Result := False;
              Exit;
            end;
            
            if not InternetReadFile(FileHandle, @Buffer, SizeOf(Buffer), BytesRead) then
              Break;
            
            if BytesRead > 0 then
            begin
              WriteFile(FileHandle, Buffer, BytesRead, BytesWritten, nil);
              DownloadedSize := DownloadedSize + BytesRead;
              
              // 진행률 업데이트
              if TotalSize > 0 then
              begin
                DownloadProgressBar.Position := (DownloadedSize * 100) div TotalSize;
                DownloadStatusLabel.Caption := Format('다운로드 중: %d / %d KB', 
                  [DownloadedSize div 1024, TotalSize div 1024]);
              end
              else
              begin
                DownloadStatusLabel.Caption := Format('다운로드 중: %d KB', [DownloadedSize div 1024]);
              end;
            end;
          until BytesRead = 0;
          
          Result := True;
        finally
          CloseHandle(FileHandle);
        end;
      finally
        InternetCloseHandle(FileHandle);
      end;
    finally
      InternetCloseHandle(InetHandle);
    end;
  except
    Result := False;
    MsgBox('다운로드 중 오류가 발생했습니다.', mbError, MB_OK);
  end;
end;

// JSON 파싱 (간단한 버전)
function ExtractJsonValue(Json, Key: String): String;
var
  KeyPos, StartPos, EndPos: Integer;
begin
  Result := '';
  KeyPos := Pos('"' + Key + '"', Json);
  if KeyPos > 0 then
  begin
    StartPos := Pos(':', Json, KeyPos);
    if StartPos > 0 then
    begin
      StartPos := Pos('"', Json, StartPos) + 1;
      EndPos := Pos('"', Json, StartPos);
      if EndPos > StartPos then
        Result := Copy(Json, StartPos, EndPos - StartPos);
    end;
  end;
end;

// GitHub Releases API에서 다운로드 URL 가져오기
function GetDownloadUrlFromGitHub: String;
var
  JsonData: AnsiString;
  InetHandle, FileHandle: LongWord;
  Buffer: array[0..4095] of Byte;
  BytesRead: DWord;
  AssetsStart, AssetUrlStart, AssetUrlEnd: Integer;
begin
  Result := '';
  
  try
    InetHandle := InternetOpen('Inno Setup', INTERNET_OPEN_TYPE_PRECONFIG, '', '', 0);
    if InetHandle = 0 then Exit;
    
    try
      FileHandle := InternetOpenUrl(InetHandle, PChar(GITHUB_API_URL), '', 0, INTERNET_FLAG_RELOAD, 0);
      if FileHandle = 0 then Exit;
      
      try
        JsonData := '';
        repeat
          if InternetReadFile(FileHandle, @Buffer, SizeOf(Buffer), BytesRead) then
          begin
            if BytesRead > 0 then
              JsonData := JsonData + StringOf(Buffer, BytesRead);
          end
          else
            Break;
        until BytesRead = 0;
        
        // assets 배열에서 .exe 파일 찾기
        AssetsStart := Pos('"assets"', JsonData);
        if AssetsStart > 0 then
        begin
          AssetUrlStart := Pos('"browser_download_url"', JsonData, AssetsStart);
          if AssetUrlStart > 0 then
          begin
            AssetUrlStart := Pos('"', JsonData, AssetUrlStart + Length('"browser_download_url"')) + 1;
            AssetUrlEnd := Pos('"', JsonData, AssetUrlStart);
            if AssetUrlEnd > AssetUrlStart then
            begin
              Result := Copy(JsonData, AssetUrlStart, AssetUrlEnd - AssetUrlStart);
              // .exe 파일만 선택
              if Pos('.exe', Result) = 0 then
                Result := '';
            end;
          end;
        end;
      finally
        InternetCloseHandle(FileHandle);
      end;
    finally
      InternetCloseHandle(InetHandle);
    end;
  except
    Result := '';
  end;
end;

// 다운로드 페이지 초기화
procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
end;

// 설치 시작 전 다운로드
function InitializeSetup(): Boolean;
var
  DownloadUrl, TempFile: String;
  Version: String;
begin
  Result := True;
  DownloadCanceled := False;
  
  // 인터넷 연결 확인
  if not InternetConnected then
  begin
    if MsgBox('인터넷 연결이 필요합니다.' + #13#10 + 
              '오프라인 설치를 계속하시겠습니까?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
    Exit;
  end;
  
  // GitHub에서 다운로드 URL 가져오기
  DownloadStatusLabel.Caption := '최신 버전 확인 중...';
  DownloadUrl := GetDownloadUrlFromGitHub;
  
  if DownloadUrl = '' then
  begin
    if MsgBox('최신 버전을 확인할 수 없습니다.' + #13#10 + 
              '계속하시겠습니까?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
    Exit;
  end;
  
  // 다운로드 페이지 표시
  DownloadPage.Clear;
  DownloadPage.Add(DownloadUrl, 'SchoolTimetableWidget.exe', '');
  
  try
    try
      DownloadPage.Show;
      try
        DownloadPage.Download;
        Result := True;
      except
        if DownloadPage.AbortedByUser then
        begin
          Result := False;
          MsgBox('다운로드가 취소되었습니다.', mbInformation, MB_OK);
        end
        else
        begin
          SuppressibleMsgBox('다운로드 중 오류가 발생했습니다: ' + GetExceptionMessage, mbCriticalError, MB_OK, IDOK);
          Result := False;
        end;
      end;
    finally
      DownloadPage.Hide;
    end;
  except
    Result := False;
  end;
end;

// 다운로드한 파일을 설치 위치로 복사
procedure CurStepChanged(CurStep: TSetupStep);
var
  DownloadedFile: String;
begin
  if CurStep = ssInstall then
  begin
    DownloadedFile := ExpandConstant('{tmp}\SchoolTimetableWidget.exe');
    if FileExists(DownloadedFile) then
    begin
      FileCopy(DownloadedFile, ExpandConstant('{app}\SchoolTimetableWidget.exe'), False);
    end
    else
    begin
      MsgBox('다운로드한 파일을 찾을 수 없습니다.', mbError, MB_OK);
      Abort;
    end;
  end;
end;

