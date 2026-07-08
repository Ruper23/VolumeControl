[Setup]
AppName=VolumeControl
AppVersion=1.0.0
AppPublisher=Ruper
DefaultDirName={autopf}\VolumeControl
DefaultGroupName=VolumeControl
OutputDir=installer_output
OutputBaseFilename=VolumeControl-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\VolumeControl.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "dist\VolumeControl.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\VolumeControl"; Filename: "{app}\VolumeControl.exe"
Name: "{group}\{cm:UninstallProgram,VolumeControl}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Volume Control"; Filename: "{app}\VolumeControl.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\VolumeControl.exe"; Description: "{cm:LaunchProgram,VolumeControl}"; Flags: nowait postinstall skipifsilent
