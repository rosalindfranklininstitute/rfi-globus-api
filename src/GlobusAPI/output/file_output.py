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

import json
import os
import typing

import yaml
from globus_sdk import GlobusHTTPResponse

from ..logging.logging import get_logger

logger = get_logger(stdout=True)


def output(
    content: object,
    json_filename: typing.Optional[str] = None,
    yaml_filename: typing.Optional[str] = None,
):
    """Output command result in either yaml or json file to be used in Apache Airflow DAGs

    Args:
        content (object, required): object with the command result
        json_filename (typing.Optional[str], optional): json filename if used. Either the `json_filename` or the
                                                       `yaml_filename` have to be provided. Defaults to None.
        yaml_filename (typing.Optional[str], optional): yaml filename if used. Either the `json_filename` or the
                                                       `yaml_filename` have to be provided. Defaults to None.

    """
    if json_filename:
        write_json_output(content, json_filename)
    if yaml_filename:
        write_yaml_output(content, yaml_filename)
    if json_filename is None and yaml_filename is None:
        logger.info("No output specified")


def write_json_output(content: typing.Union[GlobusHTTPResponse, object], filename: str):
    """Write object content to a json file

    Args:
        content (typing.Union[GlobusHTTPResponse, object], required): object with the command result
        filename (typing.Optional[str], optional): json filename to be used

    Raises:
        ex: Failed to save to JSON file

    """
    logger.info(f"Saving results as JSON to {filename}")
    if type(content) == GlobusHTTPResponse:
        content = content.data
    try:
        if (not os.path.exists(os.path.dirname(filename))) and (
            os.path.dirname(filename) != ""
        ):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as fp:
            json.dump(content, fp)
    except Exception as ex:
        logger.exception("Failed to save results to JSON...", exc_info=ex)


def write_yaml_output(content: typing.Union[GlobusHTTPResponse, object], filename: str):
    """Write object content to a yaml file

    Args:
        content (typing.Union[GlobusHTTPResponse, object], required): object with the command result
        filename (typing.Optional[str], optional): yaml filename to be used

    Raises:
        ex: Failed to save to YAML file

    """
    logger.info(f"Saving results as YAML to {filename}")
    if type(content) == GlobusHTTPResponse:
        content = content.data
    try:
        if (not os.path.exists(os.path.dirname(filename))) and (
            os.path.dirname(filename) != ""
        ):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as fp:
            yaml.dump(content, fp)
    except Exception as ex:
        logger.exception("Failed to save results to YAML...", exc_info=ex)
