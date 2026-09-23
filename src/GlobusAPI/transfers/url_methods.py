"""
   Copyright [2026] [Rosalind Franklin Institute]

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

import os
import typing

from globus_sdk import TransferClient
from globus_sdk.scopes import TransferScopes

import GlobusAPI.transfers.transfer_methods as transfer_methods

from ..logging.logging import get_logger
from ..output.file_output import output
from .transfer_client import transfer_client

logger = get_logger(stdout=True)


def get_url(
    confidential_client_id: str,
    confidential_client_secret: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    path: str = "/",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> str:
    """Get the URL for a particular file in specific guest collection.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        collection_name (typing.Optional[str], optional): The name of the collection where the file for which the URL is
                                                          to be created. Either `collection_name` or `collection id`
                                                          must be provided. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection  where the file for which
                                                        the URL is to be created. Either `collection_name` or
                                                        `collection_id` must be provided. Defaults to None.
        path (str, optional): Path within the collection where the file is located. Defaults to `/`.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        str: The URL of a particular file in specific guest collection.

    Raises:
        ex: Fail to get url

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    URL_response = _get_url(
        current_transfer_client=current_transfer_client,
        collection_name=collection_name,
        collection_id=collection_id,
        path=path,
    )

    output(URL_response, json_filename=json, yaml_filename=yaml)

    return URL_response


def _get_url(
    current_transfer_client: TransferClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    path: str = "/",
) -> str:
    """Private method used by `get_url`. Get the URL for a particular file in specific collection.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        collection_name (typing.Optional[str], optional): The name of the collection where the file for which the URL is
                                                          to be created. Either `collection_name` or `collection id`
                                                          must be provided. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection  where the file for which
                                                        the URL is to be created. Either `collection_name` or
                                                        `collection_id` must be provided. Defaults to None.
        path (str, optional): Path within the collection where the file is located. Defaults to `/`.

    Returns:
        str: The URL of a particular file in specific collection.

    Raises:
        ex: Fail to get valid URL that point to existing path in the collections
        ValueError: Raises an error if no collection with the provided name is found
        ValueError: Raises an error if multiple collection with the provided name are found

    """

    collection = transfer_methods._get_monitored_collection(
        current_transfer_client=current_transfer_client,
        collection_name=collection_name,
        collection_id=collection_id,
    )

    if len(collection) == 1:
        try:
            stat_response = current_transfer_client.operation_stat(
                collection[0]["id"], path
            )
            if "code" in stat_response:
                if stat_response[0]["code"] == "NotFound":
                    raise ValueError(stat_response[0]["message"])
            url_base = f"https://app.globus.org/file-manager?origin_id={collection[0]['id']}&origin_path=/"
            if path[-1] != "/":
                path = os.path.dirname(path)
            URL_response = "/".join([url_base.rstrip("/"), path.lstrip("/")])

            logger.info(URL_response)
            return URL_response

        except Exception as ex:
            logger.exception("Failed to get valid URL...", exc_info=ex)
            raise ex

    elif len(collection) > 1:
        logger.error(
            f"""Multiple collections with name {collection_name} exist, please use a collection_id argument for
                disambiguation. The URL could not be retrieved."""
        )
        raise ValueError(
            f"""Multiple collections with name {collection_name} exist, please use a collection_id argument for
            disambiguation. The URL could not be retrieved."""
        )
    else:
        logger.error(
            f"Collection of name {collection_name} does not exist, the URL could not be retrieved."
        )
        raise ValueError(
            f"Collection of name {collection_name} does not exist, The URL could not be retrieved."
        )
