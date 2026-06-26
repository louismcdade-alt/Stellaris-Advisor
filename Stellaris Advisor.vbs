' Stellaris Live Advisor — double-click this to open the app.
' Runs the advisor with no console window (uses pythonw), so it behaves like a
' normal desktop app. The advisor window appears on its own.
Set ws = CreateObject("WScript.Shell")
' Run from this script's own folder so the advisor package and templates resolve.
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
ws.CurrentDirectory = scriptDir
' Window style 1 (normal), NOT 0 (hidden): pythonw has no console to hide, so a
' 0 here propagates SW_HIDE through STARTUPINFO to the advisor's own window,
' leaving it running invisibly. 1 lets the window actually show.
ws.Run "pythonw.exe app.py", 1, False
