' Stellaris Live Advisor — double-click this to open the app.
' Runs the advisor with no console window (uses pythonw), so it behaves like a
' normal desktop app. The advisor window appears on its own.
Set ws = CreateObject("WScript.Shell")
' Run from this script's own folder so the advisor package and templates resolve.
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
ws.CurrentDirectory = scriptDir
ws.Run "pythonw.exe app.py", 0, False
