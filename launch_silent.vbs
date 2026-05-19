' Launches the app with no visible console window.
' Use the desktop shortcut "Air Writing (silent)" or run this file directly.
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
Set ws = CreateObject("WScript.Shell")
ws.Run """" & scriptDir & "\launch.bat""", 0, False
