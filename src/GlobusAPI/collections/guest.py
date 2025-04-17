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

import time
import typing

from globus_sdk import GCSClient, GuestCollectionDocument
from globus_sdk.response import GlobusHTTPResponse

from ..logging.logging import get_logger
from ..output.file_output import output
from .utils import (
    gcs_client,
    get_collection,
    get_collection_from_name,
    get_collection_list,
)

logger = get_logger()


def wait_period_verification(wait_period: str = "00:00:30") -> int:
    """Wait period string verification and conversion to seconds

    Args:
        wait_period (str, optional): A string that specifies the period of time to wait. It should in a "ss" or "mm:ss"
                                    or "hh:mm:ss" format. Defaults to "00:00:30".

    Returns:
        int: wait period as a number of seconds

    Raises:
        ValueError: If wait_period is not in the correct time format or if time input is not valid

    """

    interval = wait_period.split(":")
    if len(interval) > 3:
        logger.error(
            'Incorrect wait_period argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
        )
        raise ValueError(
            'Incorrect wait_period argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
        )
    for i in interval:
        if int(i) < 0 or int(i) > 59:
            logger.error(
                """Invalid wait_period argument. It should follow
                   the "ss" or "mm:ss" or "hh:mm:ss" time formats."""
            )
            raise ValueError(
                """Incorrect wait_period argument.
                   Use "ss" or "mm:ss" or "hh:mm:ss" time formats"""
            )

    if len(interval) == 1:
        interval = int(interval[0])
    elif len(interval) == 2:
        interval = int(interval[1]) * 60 + int(interval[0])
    else:
        interval = (int(interval[0]) * 60 + int(interval[1])) * 60 + int(interval[2])
    if interval < 0:
        logger.error("Invalid wait_period argument, as it is less than 0 seconds.")
        raise ValueError("Invalid wait_period argument, as it is less than 0 seconds.")

    return interval


def create_guest_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    collection_name: str,
    endpoint_id: str,
    mapped_collection_id: str,
    base_path: str = "/",
    wait_period: str = "00:00:30",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Create a new guest collection on a base path of a mapped collection

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        collection_name (str, required): The name of the collection that will be created.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        base_path (str, optional): The base path in the mapped collection to be exposed by the guest collection.
                                   Defaults to "/".
        wait_period (str, optional): A string that specifies the period of time to wait after a collection has been
                                     created. It should in a "ss" or "mm:ss"  or "hh:mm:ss" format.
                                     Defaults to "00:00:30".
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: status of the created guest collection

    Raises:
        ex: Raises an exception if the collection has not been created

    """

    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
    )

    gcs_response = _create_guest_collection(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        mapped_collection_id=mapped_collection_id,
        base_path=base_path,
        wait_period=wait_period,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _create_guest_collection(
    current_gcs_client: GCSClient,
    collection_name: str,
    mapped_collection_id: str,
    base_path: str = "/",
    wait_period: str = "00:00:30",
) -> GlobusHTTPResponse:
    """private method of `create_guest_collection`. Creates a guest collection on a given path of the guest collection.

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client.
        collection_name (str, required): The name of the collection.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        base_path (str, optional): The base path in the mapped collection to be exposed by the guest collection.
                                   Defaults to "/".
        wait_period (str, optional): A string that specifies the period of time to wait after a collection has been
                                     created. It should in a "ss" or "mm:ss"  or "hh:mm:ss" format.
                                     Defaults to "00:00:30".

    Returns:
        GlobusHTTPResponse: showing the status of the created collection

    Raises:
        ex: Raises an exception if the collection has not been created
    """

    try:
        collection = get_collection_from_name(
            current_gcs_client=current_gcs_client,
            collection_name=collection_name,
            filter_to_help="guest_collections",
        )

        if not collection:
            collection_document = GuestCollectionDocument(
                public=False,
                collection_base_path=base_path,
                display_name=collection_name,
                mapped_collection_id=mapped_collection_id,
            )
            gcs_response = current_gcs_client.create_collection(collection_document)
            logger.info(
                f"""Guest Collection {collection_name} successfully created on mapped
                    collection:{mapped_collection_id}."""
            )
            # A cooldown period is required so Globus has time to configure changes in guest collections otherwise
            # errors like the following arise:
            # "Bearer", 403, "permission_denied", "None of your identities have been granted a role to access this
            # resource"
            seconds = wait_period_verification(wait_period=wait_period)
            time.sleep(seconds)

            return gcs_response
        else:
            logger.error(
                f"Collection of name {collection_name} exists, no collection was created."
            )

    except Exception as ex:
        logger.exception("Failed to create collection...", exc_info=ex)
        raise ex


def delete_guest_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    wait_period: str = "00:00:30",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Deletes a guest collection

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        collection_name (typing.Optional[str], optional): The name of the collection to delete. Either the
                                                          `collection_name` or the `collection_id` is required.
                                                          Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection the role will be added to.
                                                        Either the `collection_name` or the `collection_id` is required.
                                                        Defaults to None.
        wait_period (str, optional): A string that specifies the period of time to wait after a collection has been
                                     deleted. It should in a "ss" or "mm:ss"  or "hh:mm:ss" format.
                                     Defaults to "00:00:30".
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: status of the deleted guest collection

    Raises:
        ex: if a collection is failed to be deleted
    """

    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
    )

    gcs_response = _delete_guest_collection(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        collection_id=collection_id,
        wait_period=wait_period,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _delete_guest_collection(
    current_gcs_client: GCSClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    wait_period: str = "00:00:30",
) -> GlobusHTTPResponse:
    """A private method used by `delete_guest_collection`. Deletes a guest collection from its name and IP

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client. Defaults to None.
        collection_name (typing.Optional[str], optional): The name of the collection to delete. Either the
                                                          `collection_name` or the `collection_id` is required.
                                                          Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id  of the collection to delete. Either the
                                                        `collection_name` or the `collection_id` is required.
                                                        Defaults to None.
        wait_period (str, optional): A string that specifies the period of time to wait after a collection has been
                                     deleted. It should in a "ss" or "mm:ss"  or "hh:mm:ss" format.
                                     Defaults to "00:00:30".

    Returns:
        GlobusHTTPResponse: status of the deleted guest collection

    Raises:
        ex: if a collection is failed to be deleted

    """

    try:
        collection = get_collection(
            current_gcs_client=current_gcs_client,
            collection_name=collection_name,
            collection_id=collection_id,
            filter_to_help="guest_collections",
        )

        if len(collection) == 1:
            gcs_response = current_gcs_client.delete_collection(collection[0]["id"])
            logger.info(f"Guest Collection {collection_name} successfully deleted")
            # A cooldown period is required so Globus has time to configure changes in guest collections otherwise
            # errors like the following arise:
            # "Bearer", 403, "permission_denied", "None of your identities have been granted a role to access this
            # resource"
            seconds = wait_period_verification(wait_period=wait_period)
            time.sleep(seconds)
            return gcs_response
        elif len(collection) > 1:
            logger.warning(
                f"""Multiple collections found that are named: {collection_name}. No collection was deleted.
                    Please use a collection_id argument for disambiguation."""
            )
        else:
            logger.warning(
                f"Guest Collection {collection_name} does not exist and has not been deleted."
            )

    except Exception as ex:
        logger.exception("Failed to delete collection...", exc_info=ex)
        raise ex


def update_guest_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    new_collection_name: typing.Optional[str] = None,
    public: typing.Optional[bool] = False,
    wait_period: str = "00:00:30",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Update display name and/or public visibility (True/False) on a guest collection

    Args:
        confidential_client_id (str): The uuid of the confidential client that you are using.
        confidential_client_secret (str): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        collection_name (typing.Optional[str], optional): The name of the collection to update. Either the
                                                           `collection_name` or the `collection_id` is required.
                                                           Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection to update. Either the
                                                        `collection_name` or the `collection_id` is required.
                                                        Defaults to None.
        new_collection_name (typing.Optional[str], optional):The new name to call the collection. Defaults to None.
        public (typing.Optional[bool], optional): Set to true to make the guest collection publicly visible to all
                                                  Globus users. Defaults to False.
        wait_period (str, optional): A string that specifies the period of time to wait after a collection has been
                                     updated. It should in a "ss" or "mm:ss"  or "hh:mm:ss" format.
                                     Defaults to "00:00:30".
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: status of the updated collection

    Raises:
        ex: if multiple collections of the same name already exists or if a collection does not exist

    """

    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
    )

    gcs_response = _update_guest_collection(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        collection_id=collection_id,
        new_collection_name=new_collection_name,
        public=public,
        wait_period=wait_period,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _update_guest_collection(
    current_gcs_client: GCSClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    new_collection_name: typing.Optional[str] = None,
    public: typing.Optional[bool] = False,
    wait_period: str = "00:00:30",
) -> GlobusHTTPResponse:
    """A private method used by `update_guest_collection`. Update display name and/or public visibility (True/False) on
       a guest collection

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client.
        collection_name (typing.Optional[str], optional): The name of the collection to update.
                                                          Either the `collection_name` or the `collection_id`
                                                          is required. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection to update. Either the
                                                        `collection_name` or the `collection_id` is required.
                                                        Defaults to None.
        new_collection_name (typing.Optional[str], optional):The new name to call the collection. Defaults to None.
        public (typing.Optional[bool], optional): Sets the visibility of the collection to "public" or "private".
                                                  Defaults to False.
        wait_period (str, optional): A string that specifies the period of time to wait after a collection has been
                                     updated. It should in a "ss" or "mm:ss"  or "hh:mm:ss" format.
                                     Defaults to "00:00:30".
    Returns:
        GlobusHTTPResponse: status of the updates to a collection

    Raises:
        ex: if multiple collections of the same name already exists or if a collection does not exist

    """

    try:
        collection = get_collection(
            current_gcs_client=current_gcs_client,
            collection_name=collection_name,
            collection_id=collection_id,
            filter_to_help="guest_collections",
        )

        if len(collection) == 1:
            if new_collection_name is None:
                new_collection_name = collection[0]["display_name"]
            if public is None:
                public = collection[0]["public"]

            collection_document = GuestCollectionDocument(
                public=public,
                display_name=new_collection_name,
            )
            gcs_response = current_gcs_client.update_collection(
                collection[0]["id"], collection_document
            )
            # A cooldown period is required so Globus has time to configure changes in guest collections otherwise
            # errors like the following arise:
            # "Bearer", 403, "permission_denied", "None of your identities have been granted a role to access this
            # resource"
            seconds = wait_period_verification(wait_period=wait_period)
            time.sleep(seconds)
            if new_collection_name is not None:
                logger.info(
                    f"Guest Collection {collection[0]['display_name']} is now named {new_collection_name}."
                )
            if public is not None:
                if public is True:
                    logger.info(
                        f"Guest Collection {new_collection_name} is set to be visible to the public."
                    )
                else:
                    logger.info(
                        f"Guest Collection {new_collection_name} is set NOT to be visible to the public."
                    )
            return gcs_response
        elif len(collection) > 1:
            logger.error(
                f"""Multiple collections with name {collection_name} exist, please use a collection_id argument for
                    disambiguation. No collection was updated."""
            )
        else:
            logger.error(
                f"Collection of name {collection_name} does not exist, no collection was update."
            )

    except Exception as ex:
        logger.exception("Failed to update collection...", exc_info=ex)
        raise ex


def get_guest_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    filter_to_help: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Get a guest collection from its name or id

    Args:
        confidential_client_id (str): The uuid of the confidential client that you are using.
        confidential_client_secret (str): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        collection_name (typing.Optional[str], optional): The name of the collection that the role will be added to.
                                                          Either the `collection_name` or the `collection_id` is
                                                          required. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection the role will be added to.
                                                        Either the `collection_name` or the `collection_id` is required.
                                                        Defaults to None.
        filter_to_help (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): filter by either
                                                                                             "mapped_collections",
                                                                                             "guest_collections",
                                                                                             "managed_by_me",
                                                                                             "created_by_me".
                                                                                             or any combination of the
                                                                                             above added as an iterable
                                                                                             of strings.
                                                                                             Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: collection details within a one element list. If no collection is found
                                         it returns an empty list.

    Raises:
        ex: No collection with this ID was found

    """

    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
    )

    gcs_response = get_collection(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        collection_id=collection_id,
        filter_to_help=filter_to_help,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def guest_collection_list(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    filter_to_help: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    include: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Get a list of guest collections
    Args:
        confidential_client_id (str): The uuid of the confidential client that you are using.
        confidential_client_secret (str): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        filter_to_help (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): filter by
                                                                                             "mapped_collections",
                                                                                             "guest_collections",
                                                                                             "managed_by_me",
                                                                                             "created_by_me".
                                                                                              Defaults to None.
        include (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): Names of additional documents to
                                                                                      include in the responser.
                                                                                      Normally, only public collection
                                                                                      configuration policy data is
                                                                                      included in the response. If the
                                                                                      query parameter
                                                                                      include=["private_policies"] is
                                                                                      passed to this API, and the caller
                                                                                      has an administrator role on this
                                                                                      collection, the response will
                                                                                      include all private policies for
                                                                                      the collection as well.
                                                                                      Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: a list of guest collections on a mapped collection

    Raises:
        ex: Fail to get collection list

    """
    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
    )

    gcs_response = get_collection_list(
        current_gcs_client=current_gcs_client,
        mapped_collection_id=mapped_collection_id,
        filter_to_help=filter_to_help,
        include=include,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response
