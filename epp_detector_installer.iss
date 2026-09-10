#define MyAppName "EPP Detector"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Nahuel Soliz"
#define MyAppExeName "EPPDetector.exe"

[Setup]
AppId={{E7A7DA86-7A3B-4B78-92F1-E8A28D51A123}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={localappdata}\EPP Detector
DefaultGroupName=EPP Detector

OutputDir=installer
OutputBaseFilename=EPPDetector-Setup-x64

Compression=lzma2
SolidCompression=yes

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

PrivilegesRequired=lowest

WizardStyle=modern

UninstallDisplayName={#MyAppName}

[Files]
Source: "dist-windows\EPPDetector\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\EPP Detector"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\EPP Detector"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch EPP Detector"; Flags: nowait postinstall skipifsilent