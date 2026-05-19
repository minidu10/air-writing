# Creates an "Air Writing" shortcut on the user's Desktop.
# Run this once after cloning. Re-running is safe (overwrites).

$ProjectDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$LauncherPath = Join-Path $ProjectDir 'launch.bat'
$SilentPath   = Join-Path $ProjectDir 'launch_silent.vbs'
$Desktop      = [Environment]::GetFolderPath('Desktop')

if (-not (Test-Path $LauncherPath)) {
    Write-Error "launch.bat not found at $LauncherPath"
    exit 1
}

$WshShell = New-Object -ComObject WScript.Shell

# Visible launcher (shows console — useful for debugging or watching logs).
$Shortcut = $WshShell.CreateShortcut((Join-Path $Desktop 'Air Writing.lnk'))
$Shortcut.TargetPath       = $LauncherPath
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description      = 'Air Writing - Hand Gesture Text Input'
$Shortcut.WindowStyle      = 7   # Minimized — console stays out of the way
$Shortcut.IconLocation     = "$env:SystemRoot\System32\shell32.dll,138"
$Shortcut.Save()

# Silent launcher (no console at all — clean experience once it's working).
$ShortcutSilent = $WshShell.CreateShortcut((Join-Path $Desktop 'Air Writing (silent).lnk'))
$ShortcutSilent.TargetPath       = $SilentPath
$ShortcutSilent.WorkingDirectory = $ProjectDir
$ShortcutSilent.Description      = 'Air Writing - silent launch (no console)'
$ShortcutSilent.IconLocation     = "$env:SystemRoot\System32\shell32.dll,138"
$ShortcutSilent.Save()

Write-Host "Created on Desktop:"
Write-Host "  - Air Writing.lnk           (visible console, recommended first run)"
Write-Host "  - Air Writing (silent).lnk  (no console)"
