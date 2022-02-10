# from ahk import AHK, daemon
# from ahk.window import Window


# ahk = AHK()

# # ahk.send_event("{Alt Down}{Tab}{Alt Up}", 30)

# # win = ahk.active_window                        # Get the active window
# # win = ahk.win_get(title='Untitled - Notepad')  # by title
# # win = list(ahk.windows())                      # list of all windows
# # print(win)
# # print(win[0].process)

# win = ahk.find_windows(process_name="msedge.exe")
# win = list(win)
# print(win)

from ahk import AHK
from ahk.daemon import AHKDaemon

# daemon = AHKDaemon()
# daemon.start()
daemon = AHK()
import time

start_time = time.time()
# win = daemon.find_windows(process_name="msedge.exe")
# win = list(win)
# print(win)

# result = daemon.run_script("""WinGet, output,ProcessName,ahk_id 0x404f4,,,""")
# result = daemon.run_script("""WinGet, output,List, ahk_exe msedge.exe,,, """)
# print(result)

script = open(r"ahk/get_alt_tab_list.ahk").read()
result = daemon.run_script(script)
print(result)
end_time = time.time()
print(end_time - start_time)