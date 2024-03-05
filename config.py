from pathlib import Path
from dotenv import load_dotenv, dotenv_values
import os


load_dotenv()
print(dotenv_values())
v = dotenv_values()

ssh_dir = Path(Path.home(), '.ssh')
known_hosts = Path(ssh_dir, 'known_hosts')

if 'sshKeys' in v:
    sshKeys = Path(v['sshKeys']).expanduser()
    print(f"load {sshKeys}")
else:
    sshKeys = Path(Path.cwd(), 'keys')
if 'sshBackup' in v:
    sshBackup = Path(v['sshBackup']).expanduser()
    print(f"load {sshBackup}")
else:
    sshBackup = Path(Path.cwd(), 'sshBackup')
if 'inventory' in v:    
    inventory = Path(v['inventory']).expanduser()
    print(f"load {inventory}")
else:
    inventory = Path(Path.cwd(), 'inventory')

