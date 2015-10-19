import os
import subprocess

subprocess.call([os.path.dirname(os.path.abspath(__file__))+'/hadestunnel.sh'], shell=True)