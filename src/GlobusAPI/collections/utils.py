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

import typing

from globus_sdk import GCSClient, TransferClient
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import TransferScopes

import GlobusAPI

from ..logging.logging import get_logger

logger = get_logger()


def gcs_client(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    collection_ids: typing.List[str],
) -> GCSClient:
    """gets a GCS client

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        collection_ids (typing.List[str], required): IDs of the mapped collections that the GCS client will be able to
                                                     process along with any of their guest collections.
                                                     Defaults to None.

    Returns:
        GCSClient: Globus Connect Server Client

    Raises:
        ex: Fail to create GCS Scopes
        ex: Fail to create Authorizer
        ex: Fail to create Transfer Authorizer
        ex: Fail to crate Transfer Client
        ex: Fail to obtain endpoint information
        ex: Fail to create transfer client

    """
    try:
        scopes = GlobusAPI.auth.scopes.get_collections_scope(
            endpoint_id=endpoint_id,
            collection_ids=collection_ids,
        )

    except Exception as ex:
        logger.exception("Failed to create GCS scopes...", exc_info=ex)
        raise ex

    try:
        gcs_authorizer = GlobusAPI.auth.authorizer.get_client_credentials_authorizer(
            confidential_client_id, confidential_client_secret, scopes
        )

    except Exception as ex:
        logger.exception("Failed to create authorizer...", exc_info=ex)
        raise ex

    try:
        transfer_authorizer = (
            GlobusAPI.auth.authorizer.get_client_credentials_authorizer(
                confidential_client_id, confidential_client_secret, TransferScopes.all
            )
        )

    except Exception as ex:
        logger.exception("Failed to create transfer authorizer...", exc_info=ex)
        raise ex

    try:
        transfer_client = TransferClient(authorizer=transfer_authorizer)

    except Exception as ex:
        logger.exception("Failed to create transfer client...", exc_info=ex)
        raise ex

    try:
        endpoint_info = transfer_client.get_endpoint(endpoint_id)
        server_address = endpoint_info["gcs_manager_url"] + "/api"

    except Exception as ex:
        logger.exception("Failed to obtain endpoint info...", exc_info=ex)
        raise ex

    try:
        current_gcs_client = GCSClient(server_address, authorizer=gcs_authorizer)
        logger.info(f"GCSClient Created for {server_address}")

        return current_gcs_client

    except Exception as ex:
        logger.exception("Failed to create gcs client...", exc_info=ex)
        raise ex


def get_collection_from_name(
    current_gcs_client: GCSClient,
    collection_name: str,
    filter_to_help: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Search a collection based on its name and return all info about it.

    Args:
        current_gcs_client (GCSClient, required):  Globus connect server client.
        collection_name (str, required): The name of the collection to search for.
        filter_to_help (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): filter by either
                                                                                             "mapped_collections",
                                                                                             "guest_collections",
                                                                                             "managed_by_me",
                                                                                             "created_by_me".
                                                                                             or any combination of the
                                                                                             above added as an iterable
                                                                                             of strings.
                                                                                             Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: dictionary of collection attributes

    """
    collections = list()
    for collection in current_gcs_client.paginated.get_collection_list(
        filter=filter_to_help
    ).items():
        collections.append(collection)
    collection = [
        collection
        for collection in collections
        if collection["display_name"] == collection_name
    ]

    if len(collection) == 0:
        logger.warning(f"No collection found for {collection_name}")

    return collection


def get_collection_list(
    current_gcs_client: GCSClient,
    mapped_collection_id: typing.Optional[str] = None,
    filter_to_help: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    include: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Return a list of collections

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client. Defaults to None.
        mapped_collection_id (str, required): A mapped collection if the search is limited to only the guest collections
                                              of this mapped collection. Defaults to None.
        filter_to_help (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): Filter the returned set to
                                                                                             any combination of the
                                                                                             following:
                                                                                             "mapped_collections",
                                                                                             "guest_collections",
                                                                                             "managed_by_me",
                                                                                             "created_by_me".
                                                                                             Defaults to None.
        include (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): Names of additional documents to
                                                                                      include in the responser.
                                                                                      Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: list of guest collections

    Raises:
        ex: Fail to get collection list

    """

    try:
        list_of_collections = list()
        for collection in current_gcs_client.paginated.get_collection_list(
            mapped_collection_id=mapped_collection_id,
            filter=filter_to_help,
            include=include,
        ).items():
            list_of_collections.append(collection)
        logger.info(list_of_collections)

        if len(list_of_collections) == 0:
            logger.warning("No collections found")

        return list_of_collections

    except Exception as ex:
        logger.exception("Failed to get collection list...", exc_info=ex)
        raise ex


def get_collection(
    current_gcs_client: GCSClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    filter_to_help: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Get info for a specific collection

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client.
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
    Returns:
        typing.List[GlobusHTTPResponse]: collection details within a one element list. If no collection is found
                                         it returns an empty list.

    Raises:
        ex: Fail to get collection info

    """
    try:
        collections = list()
        for collection in current_gcs_client.paginated.get_collection_list(
            filter=filter_to_help, include=["private_policies"]
        ).items():
            collections.append(collection)

        if collection_id is not None:
            collection_based_on_id = [
                collection
                for collection in collections
                if collection["id"] == collection_id
            ]
            if len(collection_based_on_id) == 0:
                collection_based_on_id = None
                logger.warning(f"No collection with this id: {collection_id} was found")
        else:
            collection_based_on_id = None

        if collection_name is not None:
            collection_based_on_name = [
                collection
                for collection in collections
                if collection["display_name"] == collection_name
            ]
            if len(collection_based_on_name) == 0:
                collection_based_on_name = None
                logger.warning(f"No collection with name: {collection_name} was found")
        else:
            collection_based_on_name = None

        if collection_based_on_name is None and collection_based_on_id is None:
            logger.error(
                "Please provide either a collection name or collection id that corresponds to an existing collection"
            )
            return list()
        elif (
            collection_based_on_name is not None and collection_based_on_id is not None
        ):
            collection = list()
            for collection_i in collection_based_on_id:
                for collection_n in collection_based_on_name:
                    if (
                        collection_i["display_name"] == collection_n["display_name"]
                    ) and (collection_i["id"] == collection_n["id"]):
                        collection.append(collection_i)

            if len(collection) == 0:
                logger.warning(
                    f"""Collections named: {collection_name} were found and collections with id {collection_id}
                        were found, but not a single one that is both named {collection_name} and with id
                        {collection_id}. Please provide either only the collection name or the collection id argument
                        or provide both but make sure that their pair corresponds to a single collection."""
                )
            elif len(collection) > 1:
                logger.warning(
                    f"""Multiple collection_name & collection_id matches were found. This should not be possible
                        since there should be a single collection with id {collection_id}. Please investigate
                        further."""
                )
            return collection
        elif collection_based_on_name is not None:
            collection = collection_based_on_name
            if len(collection) > 1:
                logger.warning(
                    f"""Multiple collections named {collection_name}, were found, please provide a collection_id
                        (a valid one) of the intended collection."""
                )
            return collection
        elif collection_based_on_id is not None:
            collection = collection_based_on_id
            if len(collection) > 1:
                logger.warning(
                    f"""Multiple collections with id {collection_id}, this should not be possible since
                        there should a single collection with id {collection_id}.
                        Please investigate further."""
                )
            return collection

    except Exception as ex:
        logger.exception("Failed to get collection...", exc_info=ex)
        raise ex


def get_storage_gateway_by_name(
    current_gcs_client: GCSClient,
    gateway_name: str,
) -> typing.List[GlobusHTTPResponse]:
    """Get a storage gateway by its name

    Args:
        current_gcs_client (GCSClient, required): GCS client of the endpoint which will have the storage gateway
        gateway_name (str, required):  the display name of the gateway

    Returns:
        dict: Storage Gateway attributes

    Raises:
        ex: Fail to get storage gateway by name

    """
    try:
        storage_gateways = list()
        for collection in current_gcs_client.paginated.get_storage_gateway_list(
            include=["private_policies"]
        ).items():
            storage_gateways.append(collection)
        gateway = [
            gateway
            for gateway in storage_gateways
            if gateway["display_name"] == gateway_name
        ]

        if not gateway:
            logger.warning(f"No collection found for {gateway_name}")

        return gateway

    except Exception as ex:
        logger.exception("Failed to get storage gateway list...", exc_info=ex)
        raise ex
