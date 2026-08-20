SetTitleMatchMode, 2
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; WinClose only sends WM_CLOSE, which ui.py's on_closing() intercepts and
; turns into a no-op (it just re-iconifies), so the old process never actually
; exits and a second one piles up. Kill it by PID instead.
WinGet, OldPID, PID, % "InfiniPy ahk_class TkTopLevel ahk_exe python.exe"
if OldPID
    Process, Close, %OldPID%
Run, run_gui_shell.bat    

{
    SetCapsLockState, % GetKeyState("CapsLock","T") ? "Off" : "On" ; Toggle the state of CapsLock LED
    return
}

!CapsLock::
{
    ; See the comment above the startup block: WinClose alone leaves the old
    ; process alive because on_closing() refuses WM_CLOSE.
    WinGet, OldPID, PID, % "InfiniPy ahk_class TkTopLevel ahk_exe python.exe"
    if OldPID
        Process, Close, %OldPID%
    Run, run_gui_shell.bat    
    return
}

; +CapsLock:: ; avoid accidental press shift+Capslock which switch the the case
; ^CapsLock:: ; Ctrl CapsLock
CapsLock::
{
    SetKeyDelay, 10
    SetWinDelay, 10
    ; WinShow (ShowWindow SW_SHOW) was here, but it is a no-op: it does not
    ; un-minimize a window, and the app never hides itself with withdraw(),
    ; only with wm_state("iconic"). WinRestore makes the un-minimize explicit
    ; instead of relying on WinActivate's internal restore.
    WinRestore, % "InfiniPy ahk_class TkTopLevel ahk_exe python.exe"
    WinActivate, % "InfiniPy ahk_class TkTopLevel ahk_exe python.exe"
    Send, ^g
    return
}