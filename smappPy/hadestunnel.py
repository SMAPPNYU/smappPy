import os
import subprocess

#change the permissions on the hadestunnel.sh file so that it's executable
subprocess.call(['chmod', '755', os.path.dirname(os.path.abspath(__file__))+'/hadestunnel.sh'])

subprocess.call(['chmod', '755', os.path.dirname(os.path.abspath(__file__))+'/hadesexpect.sh'])

#call the shell script as a child
subprocess.call(['sh', os.path.dirname(os.path.abspath(__file__))+'/hadestunnel.sh'])
