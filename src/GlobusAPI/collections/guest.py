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
from globus_sdk._missing import MISSING, MissingType
from globus_sdk.response import GlobusHTTPResponse

from ..logging.logging import get_logger
from ..output.file_output import output
from ..utilities.utils import time_string_to_integer_seconds
from .utils import (
    gcs_client,
    get_collection,
    get_collection_from_name,
    get_collection_list,
)

logger = get_logger()


def create_guest_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    collection_name: str,
    endpoint_id: str,
    mapped_collection_id: str,
    base_path: str = "/",
    status_change_check_interval: str = "00:00:30",
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
        status_change_check_interval (str, optional): Time interval between status change checks for the
                                                      creation of the guest collection.
                                                      Accepted formats are "ss", "mm:ss", "hh:mm:ss".
                                                      Defaults to "00:00:30" meaning every 30 seconds.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: status of the created guest collection

    Raises:
        ex: Raises an exception if the submission of the guest collection creation failed
        ValueError: Raises an error if a guest collection with the same name already exists
        ValueError: Raises an error if multiple guest collections with the same name already exist

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
        status_change_check_interval=status_change_check_interval,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _create_guest_collection(
    current_gcs_client: GCSClient,
    collection_name: str,
    mapped_collection_id: str,
    base_path: str = "/",
    status_change_check_interval: str = "00:00:30",
) -> GlobusHTTPResponse:
    """private method of `create_guest_collection`. Creates a guest collection on a given path of the guest collection.

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client.
        collection_name (str, required): The name of the collection.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        base_path (str, optional): The base path in the mapped collection to be exposed by the guest collection.
                                   Defaults to "/".
        status_change_check_interval (str, optional): Time interval between status change checks for the
                                                      creation of the guest collection.
                                                      Accepted formats are "ss", "mm:ss", "hh:mm:ss".
                                                      Defaults to "00:00:30" meaning every 30 seconds.

    Returns:
        GlobusHTTPResponse: showing the status of the created collection

    Raises:
        ex: Raises an exception if the submission of the guest collection creation failed
        ValueError: Raises an error if a guest collection with the same name already exists
        ValueError: Raises an error if multiple guest collections with the same name already exist

    """

    collection = get_collection_from_name(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        filter_to_help="guest_collections",
    )

    if len(collection) == 0:
        try:
            collection_document = GuestCollectionDocument(
                public=False,
                collection_base_path=base_path,
                display_name=collection_name,
                mapped_collection_id=mapped_collection_id,
            )
            gcs_response = current_gcs_client.create_collection(collection_document)
            logger.info(
                f"""Guest Collection {collection_name} successfully submitted for creation on mapped
                    collection:{mapped_collection_id}."""
            )
        except Exception as ex:
            logger.exception("Failed to submit collection creation...", exc_info=ex)
            raise ex

        is_guest_collection_creation_pending_flag = True
        check_interval = time_string_to_integer_seconds(
            time_string=status_change_check_interval
        )
        while is_guest_collection_creation_pending_flag:
            time.sleep(check_interval)
            collection = get_collection_from_name(
                current_gcs_client=current_gcs_client,
                collection_name=collection_name,
                filter_to_help="guest_collections",
            )
            for col in collection:
                if col["id"] == gcs_response["id"]:
                    is_guest_collection_creation_pending_flag = False
            if len(collection) > 1:
                logger.warning(
                    f"""More than one collection with name {collection_name} was detected, most probably by simultaneous
                        calls of the create guest collection command using the same collection_name.
                        The one created by this call is the one with uuid: {gcs_response['id']}"""
                )

        logger.info(
            f"""Guest Collection {collection_name} successfully created on mapped
                collection:{mapped_collection_id}."""
        )

        return gcs_response

    elif len(collection) > 1:
        logger.warning(
            f"Multiple collections with the name {collection_name} exist, no collection was created."
        )
        return None
    else:
        logger.warning(
            f"Collection of name {collection_name} exists, no collection was created."
        )
        return None


def delete_guest_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    status_change_check_interval: str = "00:00:30",
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
        status_change_check_interval (str, optional): Time interval between status change checks for the
                                                      deletion of the guest collection.
                                                      Accepted formats are "ss", "mm:ss", "hh:mm:ss".
                                                      Defaults to "00:00:30" meaning every 30 seconds.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: status of the deleted guest collection

    Raises:
        ex: Raises an exception if the submission of the guest collection deletion failed
        ValueError: Raises an error if a guest collection the provided name does not exist
        ValueError: Raises an error if multiple guest collections with the same name already exist

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
        status_change_check_interval=status_change_check_interval,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _delete_guest_collection(
    current_gcs_client: GCSClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    status_change_check_interval: str = "00:00:30",
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
        status_change_check_interval (str, optional): Time interval between status change checks for the
                                                      deletion of the guest collection.
                                                      Accepted formats are "ss", "mm:ss", "hh:mm:ss".
                                                      Defaults to "00:00:30" meaning every 30 seconds.

    Returns:
        GlobusHTTPResponse: status of the deleted guest collection

    Raises:
        ex: Raises an exception if the submission of the guest collection deletion failed
        ValueError: Raises an error if a guest collection the provided name does not exist
        ValueError: Raises an error if multiple guest collections with the same name already exist

    """

    collection = get_collection(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        collection_id=collection_id,
        filter_to_help="guest_collections",
    )

    if len(collection) == 1:
        try:
            gcs_response = current_gcs_client.delete_collection(collection[0]["id"])
            logger.info(f"Guest Collection {collection_name} submitted for deletion")
        except Exception as ex:
            logger.exception("Failed to submit collection deletion...", exc_info=ex)
            raise ex

        is_guest_collection_deletion_pending_flag = True
        check_interval = time_string_to_integer_seconds(
            time_string=status_change_check_interval
        )
        while is_guest_collection_deletion_pending_flag:
            time.sleep(check_interval)
            collection = get_collection_from_name(
                current_gcs_client=current_gcs_client,
                collection_name=collection_name,
                filter_to_help="guest_collections",
            )
            if len(collection) == 0:
                is_guest_collection_deletion_pending_flag = False
            else:
                is_guest_collection_deletion_pending_flag = False
                for col in collection:
                    if col["id"] == gcs_response["id"]:
                        is_guest_collection_deletion_pending_flag = True

        if len(collection) > 0:
            logger.warning(
                f"""More than one collection with name {collection_name} was detected. The one deleted by this call is
                    the one with uuid: {gcs_response['id']}"""
            )

        return gcs_response
    elif len(collection) > 1:
        logger.error(
            f"""Multiple collections found that are named: {collection_name}. No collection was deleted.
                Please use a collection_id argument for disambiguation."""
        )
        raise ValueError(
            f"""Multiple collections found that are named: {collection_name}. No collection was deleted.
            Please use a collection_id argument for disambiguation."""
        )
    else:
        logger.warning(
            f"Guest Collection {collection_name} does not exist and has not been deleted."
        )
        return None


def update_guest_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    new_collection_name: typing.Optional[str] = None,
    public: typing.Optional[bool] = False,
    status_change_check_interval: str = "00:00:30",
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
        status_change_check_interval (str, optional): Time interval between status change checks for the
                                                      update of the guest collection.
                                                      Accepted formats are "ss", "mm:ss", "hh:mm:ss".
                                                      Defaults to "00:00:30" meaning every 30 seconds.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: status of the updated collection

    Raises:
        ex: Raises an exception if the submission of the guest collection update failed
        ValueError: Raises an error if a guest collection the provided name does not exist
        ValueError: Raises an error if multiple guest collections with the same name already exist

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
        status_change_check_interval=status_change_check_interval,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _update_guest_collection(
    current_gcs_client: GCSClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    new_collection_name: typing.Optional[str] = None,
    public: typing.Optional[bool] = False,
    status_change_check_interval: str = "00:00:30",
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
        status_change_check_interval (str, optional): Time interval between status change checks for the
                                                      update of the guest collection.
                                                      Accepted formats are "ss", "mm:ss", "hh:mm:ss".
                                                      Defaults to "00:00:30" meaning every 30 seconds.

    Returns:
        GlobusHTTPResponse: status of the updates to a collection

    Raises:
        ex: Raises an exception if the submission of the guest collection update failed
        ValueError: Raises an error if a guest collection the provided name does not exist
        ValueError: Raises an error if multiple guest collections with the same name already exist

    """

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
        try:
            collection_document = GuestCollectionDocument(
                public=public,
                display_name=new_collection_name,
            )
            gcs_response = current_gcs_client.update_collection(
                collection[0]["id"], collection_document
            )
        except Exception as ex:
            logger.exception("Failed to update collection...", exc_info=ex)
            raise ex

        is_guest_collection_update_pending_flag = True
        check_interval = time_string_to_integer_seconds(
            time_string=status_change_check_interval
        )
        while is_guest_collection_update_pending_flag:
            time.sleep(check_interval)
            collection = get_collection_from_name(
                current_gcs_client=current_gcs_client,
                collection_name=new_collection_name,
                filter_to_help="guest_collections",
            )
            for col in collection:
                if (
                    col["id"] == gcs_response["id"]
                    and col["display_name"] == new_collection_name
                    and col["public"] == public
                ):
                    is_guest_collection_update_pending_flag = False
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
        if len(collection) > 1:
            logger.warning(
                f"""More than one collection with name {collection_name} was detected. The one updated by this call is
                    the one with uuid: {gcs_response['id']}"""
            )
        return gcs_response
    elif len(collection) > 1:
        logger.error(
            f"""Multiple collections with name {collection_name} exist, please use a collection_id argument for
                disambiguation. No collection was updated."""
        )
        raise ValueError(
            f"""Multiple collections with name {collection_name} exist, please use a collection_id argument for
            disambiguation. No collection was updated."""
        )
    else:
        logger.error(
            f"Collection of name {collection_name} does not exist, no collection was update."
        )
        raise ValueError(
            f"Collection of name {collection_name} does not exist, no collection was update."
        )


def get_guest_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    filter_to_help: typing.Union[str, typing.Iterable[str], MissingType] = MISSING,
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
        filter_to_help (typing.Union[str, typing.Iterable[str], MissingType], optional): filter by either
                                                                                         "mapped_collections",
                                                                                         "guest_collections",
                                                                                         "managed_by_me",
                                                                                         "created_by_me".
                                                                                         or any combination of the
                                                                                         above added as an iterable
                                                                                         of strings.
                                                                                         Defaults to MISSING.
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
    filter_to_help: typing.Union[str, typing.Iterable[str], MissingType] = MISSING,
    include: typing.Union[str, typing.Iterable[str], MissingType] = MISSING,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Get a list of guest collections
    Args:
        confidential_client_id (str): The uuid of the confidential client that you are using.
        confidential_client_secret (str): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        filter_to_help (typing.Union[str, typing.Iterable[str], MissingType], optional): filter by
                                                                                         "mapped_collections",
                                                                                         "guest_collections",
                                                                                         "managed_by_me",
                                                                                         "created_by_me".
                                                                                         Defaults to MISSING.
        include (typing.Union[str, typing.Iterable[str], MissingType], optional): Names of additional documents to
                                                                                  include in the response.
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
                                                                                  Defaults to MISSING.
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
