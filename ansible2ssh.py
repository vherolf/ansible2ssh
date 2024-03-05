#!/usr/bin/env python

# ssh config generator for dynamic ansible inventories
import yaml
from yaml.loader import SafeLoader

import argparse
import os
import socket
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

from os.path import expanduser
from pathlib import Path
import shutil
from datetime import datetime

# define users home directory
home = Path.home()

currentDir = Path.cwd()

sshDir = Path(home, '.ssh')
sshArchive = Path(home, '.sshArchive')
sshArchive.mkdir(parents=True, exist_ok=True)
sshKeys = Path(home, '.sshKeys')
known_hosts = Path(sshDir, 'known_hosts')
# safe known_hosts
try:
    shutil.copy(known_hosts, sshKeys)
except FileNotFoundError as err:
    print(err)

if Path(sshDir).is_dir():
    sshDir.rename(Path(home, sshArchive, f'ssh-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'))   
sshDir.mkdir(parents=True, exist_ok=True)

sshConfig = Path(sshDir, 'config')
# delete content of the file
open(sshConfig, 'w').close()
sshConfig.chmod(0o000600)

sshKnownhostsFile = Path(sshDir, 'known_hosts')
open(sshKnownhostsFile, 'w').close()

if Path(sshKeys).is_dir() and Path(sshDir).is_dir():
    shutil.copytree(sshKeys, sshDir, dirs_exist_ok=True )
else:
    print("create a ~/.sshKeys directory and put your keys there")
    exit()

import paramiko

def add_ssh_host_key(host, known_hosts_file=None)->None:
    try:
        transport = paramiko.Transport(host)
        transport.start_client(event=None,timeout=10)
    except paramiko.SSHException:
        print("failed to negotiate with ", host) 
        return

    key = transport.get_remote_server_key()
    hostfile = paramiko.HostKeys(filename=known_hosts_file)
    hostfile.add(hostname = host, key=key, keytype=key.get_name())

    hostfile.save(filename=known_hosts_file)
    transport.close()

def generate_ssh_from_ansible(inventory_file, proxyjump=False):

    dl = DataLoader()
    im = InventoryManager(loader=dl, sources=[inventory_file])
    vm = VariableManager(loader=dl, inventory=im)
    hosts = im.get_hosts()
    
    with open(sshConfig, 'a') as f:
        for host in hosts:
            host_vars = vm.get_vars(host=host)
            
            # start entry
            print( f"Host {host_vars['inventory_hostname']}", file=f)
            # descriptions
            if 'description' in host_vars:
                print("\t", "# ", host_vars['description'], file=f)
            # Hostname
            if 'ansible_host' in host_vars:
                print(host_vars['ansible_host'])
                print("\t", "Hostname ",  host_vars['ansible_host'], file=f)
                ## add ssh server key to knownhosts file
                ## THIS DOESNT WORK FROM OUTSIDE
                ## maybe find a solution with proxyjump
                #add_ssh_host_key(host_vars['ansible_host'], sshKnownhostsFile)
            # User
            if 'ansible_user' in host_vars:
                print("\t", "User ",  host_vars['ansible_user'], file=f)
                #print( "User ",  host_vars['ansible_user'])
            # private key
            if 'ansible_ssh_private_key_file' in host_vars:
                print("\t", "IdentityFile ", Path(sshDir, host_vars['ansible_ssh_private_key_file']), file=f)
                #print("IdentityFile ", Path(sshDir, host_vars['ansible_ssh_private_key_file']))
            if 'DynamicForward' in host_vars:
                print("\t", "DynamicForward ", host_vars['DynamicForward'], file=f)
            if 'Port' in host_vars:
                print("\t", "Port ", host_vars['Port'], file=f)
            if 'ForwardAgent' in host_vars:
                print("\t", "ForwardAgent ", host_vars['ForwardAgent'], file=f)
            if 'ForwardX11' in host_vars:
                print("\t", "ForwardX11 ", host_vars['ForwardX11'], file=f)
            if 'ForwardX11Trusted' in host_vars:
                print("\t", "ForwardX11Trusted ", host_vars['ForwardX11Trusted'], file=f)
            if 'IdentitiesOnly' in host_vars:
                print("\t", "IdentitiesOnly ", host_vars['IdentitiesOnly'], file=f)
            if proxyjump == True:
                if 'ProxyJump' in host_vars:
                    print("\t", "ProxyJump ", host_vars['ProxyJump'], file=f)           

            f.write("\n")


def main(proxyjump=False):
    inventoryDir = Path(currentDir, 'inventory')
    for inventory_file in inventoryDir.iterdir():
        if inventory_file.is_file():
            print("Inventory File:", inventory_file)
            generate_ssh_from_ansible(str(inventory_file), proxyjump)

    with open('ssh_defaults.yaml') as info:
        info_dict = yaml.load(info, Loader=SafeLoader)
        with open(sshConfig, 'a') as f:
            print("Host *", file=f)
            for key, value in info_dict.items():
                print("\t", key, value, file=f)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='ssh config generator from ansible inventory')
    parser.add_argument('-p','--proxyjump', action=argparse.BooleanOptionalAction, help='Build with Proxy Jump variables from ansible inventory', required=False)

    args = vars(parser.parse_args())

    if args['proxyjump']:
        print("using Proxyjump")
        print()
        main(proxyjump=True)
    else:
        print("no Proxyjump")
        print()
        main(proxyjump=False)
