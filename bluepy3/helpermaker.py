#!/usr/bin/env python3

"""Make the bluepy3-helper binary executable on demand.

Usage:
    import this module then call the function `make_helper(version="x.xx")` or
    execute `helpermaker --version x.xx` from the CLI
"""

import argparse
import logging.handlers
import os
import platform
import shlex
import subprocess  # nosec: B404
import sys

try:
    import tomllib as tl
except ModuleNotFoundError:
    import tomli as tl  # type: ignore[no-redef]

# We distinguish between three versions:
# VERSION
#   bluepy3 package (read from pyproject.toml)
# BLUEZ_VERSION
#   the version of BlueZ (https://github.com/bluez/bluez) against which
#   the bluepy3-helper.c will be compiled. By default this will be the
#   version of bluetooth that is installed. This is discovered using
#   `bluetoothctl --version` and can be overriden by the user/client by
#   calling:
#       - `make_helper(version="x.xx")` from a Python script or
#       - `helpermaker --version x.xx` from the CLI
#   where "x.xx" is the required version (str).
# BUILD_VERSION
#   the version that `bluepy3-helper` will get during the build.

APP_ROOT: str = os.path.dirname(__file__)

# Configure the logging module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(module)s.%(funcName)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers = []
)

log = logging.getLogger(__name__)

def get_btctl_version() -> str:
    version = os.environ.get('BLUEZ_VERSION')
    if version is not None:
        return version
    args: list[str] = ["bluetoothctl", "version"]
    try:
        _exit_code = (
            subprocess.check_output(
                args, shell=False, encoding="utf-8", timeout=5.0
            )  # nosec B603
            .strip("\n")
            .strip("'")
        ).split()
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise Exception("bluetoothctl not installed, can't find bluez version")
    return f"{_exit_code[1]}"


def get_project_version() -> str:
    """Lookup the project version in pyproject.toml."""
    _pv = "pyproject.toml not found."
    try:
        toml_path = f"{APP_ROOT}/pyproject.toml"
        with open(toml_path, mode="rb") as _fp:
            TOML_CONTENTS = tl.load(_fp)
            _pv = str(TOML_CONTENTS["project"]["version"])
    except FileNotFoundError:
        pass
    return _pv

class LogType:
    STDOUT = 1
    SYSLOG = 2

def build(bluez_version: str = 'installed', debug: str = '', log_type: int = LogType.STDOUT) -> None:
    if platform.system().lower() != 'linux':
        raise Exception('build_helper() can only be called on Linux')

    if log_type == LogType.STDOUT:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.handlers.SysLogHandler(address="/dev/log", facility=logging.handlers.SysLogHandler.LOG_DAEMON)
    log.addHandler(handler)

    version = get_project_version()
    bluez_version = bluez_version
    if bluez_version == 'installed':
        bluez_version = get_btctl_version()
    build_version = f"{version}-{bluez_version}"
    debug = debug

    log.info(f"Executing from here    : {APP_ROOT}")
    log.info(f"Package version        : {version}")
    log.info(f"Bluez version   : {bluez_version}")
    log.info(f"Building helper version {build_version} in {APP_ROOT}")

    """Do the custom compiling of the bluepy3-helper executable from the makefile"""
    cmd: str = ""
    # create the version.h containing the build version
    version_h_path = f"{APP_ROOT}/version.h"
    with open(version_h_path, "w", encoding="utf-8") as verfile:
        verfile.write(f'#define VERSION_STRING "{build_version}"\n')

    makefile_path = f"{APP_ROOT}/Makefile"

    # read the Makefile
    with open(makefile_path, "r", encoding="utf-8") as makefile:
        lines: list[str] = makefile.readlines()
    # write the Makefile while inserting the desired BlueZ version
    with open(makefile_path, "w", encoding="utf-8") as makefile:
        for line in lines:
            if line.startswith("BLUEZ_VERSION"):
                line = f"BLUEZ_VERSION={bluez_version}\n"
            makefile.write(line)
    cpus = os.cpu_count()
    for cmd in [f"make -C {APP_ROOT} clean", f"make {debug} -C {APP_ROOT} -j{cpus}"]:
        log.info(f"Execute {cmd}")
        msgs: bytes = b""
        try:
            msgs = subprocess.check_output(  # noqa: F841  # pylint: disable=unused-variable
                shlex.split(cmd), stderr=subprocess.STDOUT
            )  # nosec: B603
        except subprocess.CalledProcessError as e:
            log.error(f"Command was:\n    {repr(cmd)} in {os.getcwd()}")
            log.error(f"Return code was\n    {e.returncode}")
            err_out: str = e.output.decode("utf-8")
            log.error(f"Output was:\n    {err_out}")
            log.info(
                f"Failed to compile bluepy3-helper version {build_version}."
                f"Exiting install."
            )
            sys.exit(1)
        log.info(f"Returned message:\n{msgs.decode(encoding='utf-8')}")


def main() -> None:

    # fmt: off
    parser = argparse.ArgumentParser(description="Compile the bluepy3-helper binary.")

    parser.add_argument("-b", "--build", type=str, default='installed', help="version of BlueZ against which to compile the binary")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debugging mode in the binary")

    args = parser.parse_args()

    debug = "DEBUGGING=1" if args.debug else ""
    build(bluez_version=args.build, debug=debug)


if __name__ == "__main__":
    main()
