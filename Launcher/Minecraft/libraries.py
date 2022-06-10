from IPMCL import operating_system

import os
import zipfile
import platform


def unzip_natives(base_path: str, libraries: dict, version_name: str):
    version_path = os.path.join(base_path,
                                'versions',
                                version_name
                                )

    version_natives_path = os.path.join(version_path, "natives")

    if not os.path.exists(version_natives_path):
        os.makedirs(version_natives_path)

    for library in libraries:
        try:
            library_path = os.path.join(base_path,
                                        'libraries',
                                        library['downloads']['classifiers'][operating_system]['path']
                                        )

            jar_file = zipfile.ZipFile(library_path)
            for file in jar_file.namelist():
                if os.path.splitext(file)[1] == ".dll":
                    jar_file.extract(file, version_natives_path)

        except KeyError:
            continue
        except PermissionError:
            continue

    return version_natives_path


def library_paths(base_path: str, libraries: dict, version_name: str):
    if platform.system() == "Windows":
        platform_name = 'windows'
        delimiter = ";"
        path_delimiter = "\\"
    elif platform.system() == "Darwin":
        platform_name = 'osx'
        delimiter = ":"
        path_delimiter = "/"
    else:
        platform_name = 'linux'
        delimiter = ":"
        path_delimiter = "/"

    libraries_path = []

    for library in libraries:
        try:
            if "classifiers" not in library['downloads']:
                library_path = os.path.join(base_path,
                                            'libraries',
                                            library['downloads']['artifact']['path']
                                            )

                if "rules" not in library:
                    libraries_path.append(library_path)

                else:
                    for rule in library["rules"]:
                        if rule["action"] == "allow":
                            if "os" in rule and rule["os"]["name"] == platform_name:
                                libraries_path.append(library_path)
                                continue

                            elif "os" not in rule:
                                libraries_path.append(library_path)
                                continue

                        else:
                            if "os" in rule and rule["os"]["name"] != platform_name:
                                libraries_path.append(library_path)
                                continue
        except KeyError:
            continue

    cp = str()

    for library_path in sorted(set(libraries_path), key=libraries_path.index):
        cp += library_path + delimiter

    cp += os.path.join(
        base_path,
        'versions',
        version_name,
        version_name + ".jar"
    )

    cp = cp.replace('/', path_delimiter)

    return cp
