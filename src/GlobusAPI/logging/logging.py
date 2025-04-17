"""
   Copyright [2025] [Rosalind Franklin Institute]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import io
import logging
import socket
import sys
import typing
from collections.abc import Callable

import yaml


def get_logger(
    namespace: str = "GLOBUS_API", level: int = logging.DEBUG, stdout: bool = False
) -> logging.Logger:
    """Configure the custom_logging of this module

    Args:
        namespace (str, optional): custom_logging namespace
        level (int, optional): custom_logging level
        stdout (bool, optional): display logs using standard output

    Returns:
        Logger (logging.Logger): A logger to be used by GLOBUS_API
    """

    HOSTNAME = socket.gethostname()

    class HostnameFilter(logging.Filter):
        def filter(self, record):
            record.hostname = HOSTNAME
            return True

    # Create a unique logger
    logging.getLogger().handlers.clear()
    logger = logging.getLogger(namespace)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addFilter(HostnameFilter())

    # Format the logging to include the hostname
    formatter = logging.Formatter(
        "%(asctime)s | %(hostname)s | %(levelname)10s | %(filename)s:%(lineno)s | %(message)s"
    )

    if stdout:
        # Mirror logging to stdout
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(level)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

    return logger


def dump(
    logger_debug_func: Callable,
    input_object: dict,
    prefix: str = "",
    obfuscate: typing.Optional[list] = None,
):
    """Reformat the logs to hide confidential information and for display

    Args:
        logger_debug_func (Callable, required): The logger debug method-function
        input_object (dict, required): Dictionary of an object to be displayed in the logs
        prefix (str, optional): define prefix to be associated with the object to display in the logs
        obfuscate (typing.Optional[list], optional): list of fields to be hidden in the logs

    """

    with io.StringIO() as stream:
        yaml.dump(input_object, stream)
        data = stream.getvalue()
        if obfuscate is None:
            obfuscate = list()
        for value in obfuscate:
            data = data.replace(value, "SECRET")
        for line in data.strip("\n").split("\n"):
            logger_debug_func(f"{prefix} {line}")


def dump_with_auto_obfuscation(
    logger_debug_func: Callable, input_object: dict, prefix: str = ""
):
    """Reformat the logs to hide `confidential_client_secret` from display

    Args:
        logger_debug_func (Callable, required): The logger debug method-function
        input_object (dict, required): Dictionary of an object to be displayed in the logs
        prefix (str, optional): define prefix to be associated with the object to display in the logs

    Raises:
        ex: No confidential client secret was provided

    """
    logger = get_logger(stdout=True)
    try:
        if input_object["ctx"]["confidential_client_secret"] is not None:
            dump(
                logger_debug_func,
                input_object,
                prefix=prefix,
                obfuscate=[input_object["ctx"]["confidential_client_secret"]],
            )

    except Exception as ex:
        logger.exception("No confidential client secret was provided...", exc_info=ex)
        raise ex
