import win32gui
import win32clipboard
import win32.lib.win32con as win32con

def get_clipboard_text():
    win32clipboard.OpenClipboard()
    text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    return text