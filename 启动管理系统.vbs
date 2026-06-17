Set fso = CreateObject("Scripting.FileSystemObject")
Set ws = CreateObject("Wscript.Shell")

projectDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonExe = projectDir & "\.venv\Scripts\pythonw.exe"
qtBinDir = projectDir & "\.venv\Lib\site-packages\PyQt5\Qt5\bin"
qtPluginDir = projectDir & "\.venv\Lib\site-packages\PyQt5\Qt5\plugins"

Set env = ws.Environment("PROCESS")
env("QT_PLUGIN_PATH") = qtPluginDir
env("PATH") = qtBinDir & ";" & env("PATH")

ws.CurrentDirectory = projectDir
ws.Run """" & pythonExe & """ main.py", 1, False
