[Setup]
AppName=DataLeakDetector
AppVersion=1.0
DefaultDirName={pf}\DataLeakDetector
DefaultGroupName=DataLeakDetector
OutputDir=output
OutputBaseFilename=DataLeakDetector_Setup
Compression=lzma
SolidCompression=yes

PrivilegesRequired=admin

[Files]
Source: "dist\DataLeakDetector\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\DataLeakDetector"; Filename: "{app}\DataLeakDetector.exe"
Name: "{commondesktop}\DataLeakDetector"; Filename: "{app}\DataLeakDetector.exe"

[Run]
Filename: "{app}\DataLeakDetector.exe"; Description: "启动程序"; Flags: nowait postinstall
