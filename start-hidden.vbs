' Get the directory where this VBS script is located
Dim fso, scriptDir, batPath
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = scriptDir & "\start-pyinv-auto.bat"

' Run the batch file hidden
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """" & batPath & """", 0, False
Set WshShell = Nothing
Set fso = Nothing
