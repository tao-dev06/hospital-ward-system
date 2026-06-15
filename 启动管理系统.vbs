Set ws = CreateObject("Wscript.Shell")
ws.CurrentDirectory = "C:\Users\Tao\Desktop\hospital_ward_system"
ws.Run "python main.py", 1, False
