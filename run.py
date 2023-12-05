import os
import psutil
import subprocess
import utility as utl

directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))
pid_this_thread = int(os.getpid())
result = utl.get_pids_by_full_script_name(f"{directory}/{filename}")
for pid in result:
    if pid_this_thread != pid:
        try:
            pid = psutil.Process(pid)
            pid.terminate()
        except:
            pass

subprocess.Popen(["python3", f"{directory}/bot.py"])
subprocess.Popen(["python3", f"{directory}/cr.settings.py"])
subprocess.Popen(["python3", f"{directory}/tl.send-to-pv.py"])