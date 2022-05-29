from IPMCL import setting, config_save

from platform import system
import subprocess
import os
import re


def finder(clear_update=True):
    versions = {}

    if clear_update:
        setting['Java'] = dict()

    if system() == 'Windows':
        from System import getDocPath

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
    elif system() == 'Darwin':
        for m_jvm in subprocess.getstatusoutput("/usr/libexec/java_home -V")[1].split("\n")[1:-1]:
            java = java_version = m_jvm.strip().split(" ")[0]

            java_exec_path = str()

            for java_path in list(reversed(m_jvm.strip().split(" "))):
                if "/" in java_path:
                    java_exec_path = " " + java_path + java_exec_path
                else:
                    java_exec_path = os.path.join(java_exec_path.strip(), "bin", "java")
                    break

            versions[java] = [java_version, java_exec_path]

            try:
                if java not in setting['Java']:
                    setting['Java'][java] = [java_version, java_exec_path]

            except KeyError:
                setting['Java'] = dict()
                setting['Java'][java] = [java_version, java_exec_path]

    config_save()

    return versions

finder()
