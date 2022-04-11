import subprocess

cmd = subprocess.Popen("rm -rf ZeroXRequests", shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
print(str(cmd.stdout.read()) + "\n" + str(cmd.stderr.read()))
cmd = subprocess.Popen("git clone https://github.com/rafax00/ZeroXRequests.git", shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
print(str(cmd.stdout.read()) + "\n" + str(cmd.stderr.read()))
