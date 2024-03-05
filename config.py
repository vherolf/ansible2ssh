from pathlib import Path

ssh_dir = Path(Path.home(), '.ssh')
sshKeys = Path(Path.cwd(), 'keys')
sshBackup = Path(Path.cwd(), 'sshBackup')
inventory = Path(Path.cwd(), 'inventory')