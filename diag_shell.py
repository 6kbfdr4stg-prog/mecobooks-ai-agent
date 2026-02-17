import os
import datetime

content = f"Shell execution test at {datetime.datetime.now()}\n"
os.system(f"echo '{content}' > py_shell_test.txt")
print("Python script execution finished")
