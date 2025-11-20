#!/usr/bin/env python3
import os
import subprocess

def install_libr():
    if 'VIRTUAL_ENV' not in os.environ:
        raise RuntimeError("NOT FIND")
    out = subprocess.run(['pip', 'install']+ ['beautifulsoup4', 'pytest'], capture_output=True, text=True)
    return out

def look_all_list_installed_libr():
    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True).stdout
    return result

def write_to_file(filename:str):
    with open(filename,'w') as file:
        file.write(look_all_list_installed_libr())

if __name__ == '__main__':

    output = install_libr()
    print(output)
    install = look_all_list_installed_libr()
    #print(install)
    write_to_file("requirements.txt")

        
