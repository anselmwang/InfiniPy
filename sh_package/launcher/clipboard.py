import win32.lib.win32con as win32con
import win32clipboard
import win32gui


def get_clipboard_text():
    win32clipboard.OpenClipboard()
    text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    return text

def set_clipboard_text(text: str):
    win32clipboard.OpenClipboard()
    win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()