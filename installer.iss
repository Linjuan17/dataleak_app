#define MyAppName "DataLeakDetector"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DataLeakDetector"
#define MyAppExeName "DataLeakDetector.exe"

[Setup]
AppId={{7B4E9D2E-8F56-4C9C-9D8E-DataLeakDetector}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=DataLeakDetector_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务："; Flags: unchecked

[Files]
Source: "dist\DataLeakDetector.exe"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\DataLeakDetector_Data"
Name: "{app}\DataLeakDetector_Data\recordings"
Name: "{app}\DataLeakDetector_Data\risk_stage1"
Name: "{app}\analysis_history"
Name: "{app}\output"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

