SetTitleMatchMode, 2
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

^CapsLock::
{
    SetCapsLockState, % GetKeyState("CapsLock","T") ? "Off" : "On" ; Toggle the state of CapsLock LED
    return
}

!CapsLock::
{
    WinClose, % "InfiniPy ahk_class TkTopLevel ahk_exe python.exe"
    Run, run_gui_shell.bat    
    return
}

+CapsLock:: ; avoid accidental press shift+Capslock which switch the the case
CapsLock::
{
    SetKeyDelay, 10
    SetWinDelay, 10
    WinShow, % "InfiniPy ahk_class TkTopLevel ahk_exe python.exe"
    WinActivate, % "InfiniPy ahk_class TkTopLevel ahk_exe python.exe"
    Send, ^g
    return
}