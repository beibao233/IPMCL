from System import getDocPath
from IPMCL import setting, config_save

from platform import system
import subprocess
import os
import re


def finder():
    versions = {}

    if system() == 'Windows':
        try:
            for java in os.listdir(os.path.join(getDocPath(38), "Java")):

                java_exec_path = os.path.join(getDocPath(38), "Java", java, 'bin', 'java.exe')

                if os.path.exists(java_exec_path):
                    java_version = subprocess.check_output([java_exec_path, '-version'], stderr=subprocess.STDOUT)

                    java_version = str(re.search(
                        rb'\"(\d+\.\d+).*\"',
                        java_version
                    ).groups()[0]).replace('b', '').replace("'", '')

                    versions[java] = [java_version, java_exec_path]

                    try:
                        if java not in setting['Java']:
                            setting['Java'][java] = [java_version, java_exec_path]

                    except KeyError:
                        setting['Java'] = dict()
                        setting['Java'][java] = [java_version, java_exec_path]

        except FileNotFoundError:
            pass

    config_save()

    return versions
