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
import time
import typing

import yaml
from globus_sdk import AuthClient, TransferClient, TransferData
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import AuthScopes, TransferScopes

from ..groups.users import auth_client, get_user_uuid
from ..logging.logging import get_logger
from ..output.file_output import output
from .transfer_client import transfer_client

logger = get_logger(stdout=True)


def cancel_tasks(
    confidential_client_id: str,
    confidential_client_secret: str,
    task_ids: str,
    message: str = "Tasks Cancellation",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Cancels Globus tasks based on the provided task UUIDs.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        task_ids (str, required): The UUIDs of the task(s) to cancel. To provide multiple task UUIDs, provide as a
                                  comma-separated list.
        message (str, optional): The message label used to cancel the tasks. Defaults to "Tasks Cancellation".
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of cancelling tasks. Uses standard HTTPS structure.

    Raises:
        ex: Fail to cancel tasks

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    transfer_response = _cancel_tasks(
        current_transfer_client=current_transfer_client,
        task_ids=task_ids,
        message=message,
    )

    output(transfer_response, json_filename=json, yaml_filename=yaml)

    return transfer_response


def _cancel_tasks(
    current_transfer_client: TransferClient,
    task_ids: str,
    message: str = "Tasks Cancellation",
) -> GlobusHTTPResponse:
    """Private method used by `cancel_tasks`. Cancels Globus tasks based on the provided task UUIDs.
    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        task_ids (str, required): The UUIDs of the task(s) to cancel. To provide multiple task UUIDs, provide as a
                                  comma-separated list.
        message (str, optional): The message label used to cancel the tasks. Defaults to "Tasks Cancellation".

    Returns:
        GlobusHTTPResponse: Outcome of task(s) cancellation.

    Raises:
        ex: Fail to cancel tasks

    """
    try:
        iter_task_ids = iter(task_ids.split(","))
        transfer_response = current_transfer_client.endpoint_manager_cancel_tasks(
            iter_task_ids, message
        )
        logger.info(transfer_response)
        return transfer_response

    except Exception as ex:
        logger.exception("Failed to cancel tasks...", exc_info=ex)
        raise ex


def complete_transfer(
    confidential_client_id: str,
    confidential_client_secret: str,
    item_list_filename: str,
    source_collection_id: typing.Optional[str] = None,
    source_collection_name: typing.Optional[str] = None,
    destination_collection_id: typing.Optional[str] = None,
    destination_collection_name: typing.Optional[str] = None,
    label: typing.Optional[str] = None,
    sync_level: typing.Optional[int] = None,
    status_change_check_interval: str = "00:01:00",
    auto_cancel_if_inactive_wait_period: str = "00:00:00",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Globus transfer submission that waits until the transfer is complete, aka either `SUCCEEDED` or `FAILED`. The
       transfer task will be canceled if it gets `INACTIVE` for a time period larger than the one specified in
       `auto_cancel_if_inactive_wait_period`.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        item_list_filename (str, required): The filename of the item list file. It should be either a JSON or YAML file.
                                            It should contain a list of dictionaries.
                                            Each dictionary should have 2 keys `source_path` and `destination_path`,
                                            each containing the corresponding paths in the source and destination
                                            collection respectively.
                                            To transfer whole directories in a recursive manner, both paths should end
                                            with the character `/`.
        source_collection_name (typing.Optional[str], optional): The name of the source collection where data will be
                                                                 transferred from. Either `source_collection_name` or
                                                                 `source_collection_id` must be provided.
                                                                  Defaults to None.
        source_collection_id (typing.Optional[str], optional): The source collection uuid where data will be transferred
                                                               from. Either `source_collection_name` or
                                                               `source_collection_id` must be provided.
                                                               Defaults to None.
        destination_collection_name (typing.Optional[str], optional): The name of the destination collection where data
                                                                      will be transferred to. Either
                                                                      `destination_collection_name` or
                                                                      `destination_collection_id` must be provided.
                                                                      Defaults to None.
        destination_collection_id (typing.Optional[str], optional): The destination collection uuid  where data will be
                                                                    transferred to. Either `destination_collection_name`
                                                                    or destination_collection_id` must be provided.
                                                                    Defaults to None.
        label (typing.Optional[str], optional): The label of the transfer task. Defaults to None.
        sync_level (typing.Optional[int], optional): The sync level of the transfer task.
                                                     If not provided or set to None, the transfer will
                                                     transfer-overwrite any files with the same name that are in the
                                                     same directory in the destination collection.
                                                     If provided the level must be an integer in the 0-3 range, and it
                                                     controls what action is performed if there is already a file with
                                                     the same name in the same directory in the destination collection.
                                                     `0`: Transfer only the files that do not already exist at the
                                                          destination collection.
                                                     `1`: Transfer-overwrite same name, same directory files if their
                                                          size in the destination collection does not match their size
                                                          in the source collection.
                                                     `2`: Transfer-overwrite same name, same directory files if their
                                                          last modified timestamp in the destination collection is
                                                          older than the last modified timestamp in the
                                                          source collection.
                                                     `3`: Transfer-overwrite same name, same directory files if their
                                                           checksums in the source and destination collection do
                                                           not match.
                                                      Defaults to None.
        status_change_check_interval (str, optional): Time interval between status change checks for the transfer.
                                                      Accepted formats are "ss", "mm:ss", "hh:mm:ss".
                                                      Defaults to "00:01:00" meaning every minute.
        auto_cancel_if_inactive_wait_period (str, optional): Once the transfer gets an `INACTIVE` status what should be
                                                             the minimum time it should wait until cancelling the
                                                             transfer task. Accepted formats are "ss", "mm:ss",
                                                             "hh:mm:ss". Defaults to "00:00:00" that the moment it
                                                             detects inactivity if the task is still inactive in the
                                                             next `status_change_check_interval` it cancels it.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
       typing.List[GlobusHTTPResponse]: If the transfer task ends with a `SUCCEEDED` status code, a list of the
                                        successfully transferred files will be returned.
                                        If the transfer task ends with a `FAILED` status code or gets auto-cancelled
                                        due to prolonged, a list of the transfer task events will be returned, to aid
                                        with the troubleshooting of any errors.

    Raises:
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on source collection name and/or source collection id, no source collection was found
        ValueError: Based on source collection name and/or source collection id, more than one source collection was
                    found
        ValueError: Based on destination collection name and/or collection id, no destination collection was found
        ValueError: Based on destination collection name and/or collection id, more than one destination collection was
                    found
        ex: Fail to get monitored collection list
        ValueError: Incorrect time format for `status_change_check_interval`
        ValueError: `status_change_check_interval` is less than 0 seconds
        ValueError: Incorrect time format for `auto_cancel_if_inactive_wait_period`
        ValueError: `auto_cancel_if_inactive_wait_period` is less than 0 seconds
        ex: Fail to load `item_list_filename` file
        ex: Fail to submit task

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    transfer_response = _complete_transfer(
        current_transfer_client=current_transfer_client,
        item_list_filename=item_list_filename,
        source_collection_id=source_collection_id,
        source_collection_name=source_collection_name,
        destination_collection_id=destination_collection_id,
        destination_collection_name=destination_collection_name,
        label=label,
        sync_level=sync_level,
        status_change_check_interval=status_change_check_interval,
        auto_cancel_if_inactive_wait_period=auto_cancel_if_inactive_wait_period,
    )

    output(transfer_response, json_filename=json, yaml_filename=yaml)

    return transfer_response


def _complete_transfer(
    current_transfer_client: TransferClient,
    item_list_filename: str,
    source_collection_id: typing.Optional[str] = None,
    source_collection_name: typing.Optional[str] = None,
    destination_collection_id: typing.Optional[str] = None,
    destination_collection_name: typing.Optional[str] = None,
    label: typing.Optional[str] = None,
    sync_level: typing.Optional[int] = None,
    status_change_check_interval: str = "00:01:00",
    auto_cancel_if_inactive_wait_period: str = "00:00:00",
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `complete_transfer`. Globus transfer submission that waits until the transfer is complete,
       aka either `SUCCEEDED` or `FAILED`. The transfer task will be canceled if it gets `INACTIVE` for a time period
       larger than the one specified in `auto_cancel_if_inactive_wait_period`.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        item_list_filename (str, required): The filename of the item list file. It should be either a JSON or YAML file.
                                            It should contain a list of dictionaries.
                                            Each dictionary should have 2 keys `source_path` and `destination_path`,
                                            each containing the corresponding paths in the source and destination
                                            collection respectively.
                                            To transfer whole directories in a recursive manner, both paths should end
                                            with the character `/`.
        source_collection_name (typing.Optional[str], optional): The name of the source collection where data will be
                                                                 transferred from. Either `source_collection_name` or
                                                                 `source_collection_id` must be provided.
                                                                  Defaults to None.
        source_collection_id (typing.Optional[str], optional): The source collection uuid where data will be transferred
                                                               from. Either `source_collection_name` or
                                                               `source_collection_id` must be provided.
                                                               Defaults to None.
        destination_collection_name (typing.Optional[str], optional): The name of the destination collection where data
                                                                      will be transferred to. Either
                                                                      `destination_collection_name` or
                                                                      `destination_collection_id` must be provided.
                                                                      Defaults to None.
        destination_collection_id (typing.Optional[str], optional): The destination collection uuid  where data will be
                                                                    transferred to. Either `destination_collection_name`
                                                                    or destination_collection_id` must be provided.
                                                                    Defaults to None.
        label (typing.Optional[str], optional): The label of the transfer task. Defaults to None.
        sync_level (typing.Optional[int], optional): The sync level of the transfer task.
                                                     If not provided or set to None, the transfer will
                                                     transfer-overwrite any files with the same name that are in the
                                                     same directory in the destination collection.
                                                     If provided the level must be an integer in the 0-3 range, and it
                                                     controls what action is performed if there is already a file with
                                                     the same name in the same directory in the destination collection.
                                                     `0`: Transfer only the files that do not already exist at the
                                                          destination collection.
                                                     `1`: Transfer-overwrite same name, same directory files if their
                                                          size in the destination collection does not match their size
                                                          in the source collection.
                                                     `2`: Transfer-overwrite same name, same directory files if their
                                                          last modified timestamp in the destination collection is
                                                          older than the last modified timestamp in the
                                                          source collection.
                                                     `3`: Transfer-overwrite same name, same directory files if their
                                                           checksums in the source and destination collection do
                                                           not match.
                                                      Defaults to None.
        status_change_check_interval (str, optional): Time interval between status change checks for the transfer.
                                                      Accepted formats are "ss", "mm:ss", "hh:mm:ss".
                                                      Defaults to "00:01:00" meaning every minute.
        auto_cancel_if_inactive_wait_period (str, optional): Once the transfer gets an `INACTIVE` status what should be
                                                             the minimum time it should wait until cancelling the
                                                             transfer task. Accepted formats are "ss", "mm:ss",
                                                             "hh:mm:ss". Defaults to "00:00:00" that the moment it
                                                             detects inactivity if the task is still inactive in the
                                                             next `status_change_check_interval` it cancels it.

    Returns:
       typing.List[GlobusHTTPResponse]: If the transfer task ends with a `SUCCEEDED` status code, a list of the
                                        successfully transferred files will be returned. If the transfer task ends with
                                        a `FAILED` status code or gets auto-cancelled due to prolonged, a list of the
                                        transfer task events will be returned, to aid with the troubleshooting of any
                                        errors.

    Raises:
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on source collection name and/or source collection id, no source collection was found
        ValueError: Based on source collection name and/or source collection id, more than one source collection was
                    found
        ValueError: Based on destination collection name and/or collection id, no destination collection was found
        ValueError: Based on destination collection name and/or collection id, more than one destination collection was
                    found
        ex: Fail to get monitored collection list
        ValueError: Incorrect time format for `status_change_check_interval`
        ValueError: `status_change_check_interval` is less than 0 seconds
        ValueError: Incorrect time format for `auto_cancel_if_inactive_wait_period`
        ValueError: `auto_cancel_if_inactive_wait_period` is less than 0 seconds
        ex: Fail to load `item_list_filename` file
        ex: Fail to submit task

    """

    check_interval = status_change_check_interval.split(":")
    if len(check_interval) > 3:
        logger.error(
            'Incorrect status_change_check_interval argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
        )
        raise ValueError(
            'Incorrect status_change_check_interval argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
        )
    for i in check_interval:
        if int(i) < 0 or int(i) > 59:
            logger.error(
                """Invalid status_change_check_interval argument. It should follow
                the "ss" or "mm:ss" or "hh:mm:ss" time formats."""
            )
            raise ValueError(
                'Incorrect status_change_check_interval argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
            )
    if len(check_interval) == 1:
        check_interval = int(check_interval[0])
    elif len(check_interval) == 2:
        check_interval = int(check_interval[0]) * 60 + int(check_interval[1])
    else:
        check_interval = (
            int(check_interval[0]) * 60 + int(check_interval[1])
        ) * 60 + int(check_interval[2])
    if check_interval <= 0:
        logger.error(
            "The status_change_check_interval argument has to be more than 0 seconds."
        )
        raise ValueError(
            "The status_change_check_interval argument has to be more than 0 seconds."
        )

    inactive_interval = auto_cancel_if_inactive_wait_period.split(":")
    if len(inactive_interval) > 3:
        logger.error(
            'Incorrect auto_cancel_if_inactive_wait_period argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
        )
        raise ValueError(
            'Incorrect auto_cancel_if_inactive_wait_period argument. Use "ss" or "mm:ss" or "hh:mm:ss" time formats.'
        )
    for i in inactive_interval:
        if int(i) < 0 or int(i) > 59:
            logger.error(
                """Invalid auto_cancel_if_inactive_wait_period argument. It should follow
                the "ss" or "mm:ss" or "hh:mm:ss" time formats."""
            )
            raise ValueError(
                """Incorrect auto_cancel_if_inactive_wait_period argument.
                Use "ss" or "mm:ss" or "hh:mm:ss" time formats"""
            )
    if len(inactive_interval) == 1:
        inactive_interval = int(inactive_interval[0])
    elif len(inactive_interval) == 2:
        inactive_interval = int(inactive_interval[1]) * 60 + int(inactive_interval[0])
    else:
        inactive_interval = (
            int(inactive_interval[0]) * 60 + int(inactive_interval[1])
        ) * 60 + int(inactive_interval[2])
    if inactive_interval < 0:
        logger.error(
            "Invalid auto_cancel_if_inactive_wait_period argument, as it is less than 0 seconds."
        )
        raise ValueError(
            "Invalid auto_cancel_if_inactive_wait_period argument, as it is less than 0 seconds."
        )

    transfer_response = _submit_transfer(
        current_transfer_client=current_transfer_client,
        source_collection_name=source_collection_name,
        source_collection_id=source_collection_id,
        destination_collection_name=destination_collection_name,
        destination_collection_id=destination_collection_id,
        item_list_filename=item_list_filename,
        label=label,
        sync_level=sync_level,
    )

    task_id = transfer_response.get(key="task_id")

    time.sleep(check_interval)

    task_info = _get_task(
        current_transfer_client=current_transfer_client, task_id=task_id
    )

    inactivity_flag = False
    remaining_time_before_cancellation = inactive_interval
    while (
        task_info.get(key="status") != "SUCCEEDED"
        and task_info.get(key="status") != "FAILED"
    ):
        time.sleep(check_interval)
        task_info = _get_task(
            current_transfer_client=current_transfer_client, task_id=task_id
        )
        # Reset everything if the task returns to active mode
        if task_info.get(key="status") == "ACTIVE" and inactivity_flag is True:
            inactivity_flag = False
            remaining_time_before_cancellation = inactive_interval
            logger.warning("Transfer recovered from inactivity and it is now active.")

        # If task is inactive and it also was in a previous loop (because the inactivity_flag turned True),
        # now reduce the seconds of the remaining time before cancellation
        if task_info.get(key="status") == "INACTIVE" and inactivity_flag is True:
            remaining_time_before_cancellation = (
                remaining_time_before_cancellation - check_interval
            )

        # If there is no more remaining time, break the loop
        if (
            task_info.get(key="status") == "INACTIVE"
            and remaining_time_before_cancellation <= 0
        ):
            break

        # If it is the first time that the task turns inactive, turn the inactivity_flag to True
        if task_info.get(key="status") == "INACTIVE" and inactivity_flag is False:
            inactivity_flag = True
            logger.warning(
                f"""Transfer has turn to inactive mode. If it continues like this it will be canceled in
                    {remaining_time_before_cancellation} seconds."""
            )

    if inactivity_flag:
        logger.error("The transfer was cancelled due to prolonged inactivity.")
        _cancel_tasks(
            current_transfer_client=current_transfer_client,
            task_ids=task_id,
            message="Task cancelled due to prolonged inactivity",
        )
        list_of_events = _task_event_list(
            current_transfer_client=current_transfer_client,
            task_id=task_id,
        )
        return list_of_events
    elif task_info.get(key="status") == "FAILED":
        logger.error("The transfer failed due to an error.")
        list_of_events = _task_event_list(
            current_transfer_client=current_transfer_client,
            task_id=task_id,
        )
        return list_of_events
    else:
        list_of_transfers = _task_successful_transfers(
            current_transfer_client=current_transfer_client,
            task_id=task_id,
        )
        return list_of_transfers


def get_monitored_collection(
    confidential_client_id: str,
    confidential_client_secret: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Gets a collection from all collections that the confidential client can monitor.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        collection_name (typing.Optional[str], optional): The name of the collection. Either `collection_name` or `
                                                          collection id` must be provided. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid. Either `collection_name` or
                                                        `collection_id` must be provided. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of collections. Typically, the list has size of one, but it may
                                         return more than one if e.g. there are more than one collection with the
                                         same name.
    Raises:
        ex: Fail to get monitored collection info

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    list_of_monitored_endpoints = _get_monitored_collection(
        current_transfer_client=current_transfer_client,
        collection_name=collection_name,
        collection_id=collection_id,
    )

    output(list_of_monitored_endpoints, json_filename=json, yaml_filename=yaml)

    return list_of_monitored_endpoints


def _get_monitored_collection(
    current_transfer_client: TransferClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `get_monitored_collection`. Gets a collection from all collections that the
       confidential client can monitor.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        collection_name (typing.Optional[str], optional): The name of the collection. Either `collection_name` or
                                                          `collection id` must be provided.  Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid. Either `collection_name` or
                                                        `collection_id` must be provided. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of collections. Typically, the list has size of one, but it may return
                                         more than one if  e.g. there are more than one collection with the same name.

    Raises:
        ex: Fail to get monitored collection info

    """
    try:
        collections = list(
            current_transfer_client.endpoint_manager_monitored_endpoints()
        )

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
                    f"""Collections named: {collection_name} were found and collections with id {collection_id} were
                        found, but not a single one that is both named {collection_name} and with id {collection_id}.
                        Please provide either only the collection name or the collection id argument or provide both
                        but make sure that their pair corresponds to a single collection."""
                )
            elif len(collection) > 1:
                logger.warning(
                    f"""Multiple collection_name & collection_id matches were found. This should not be possible
                        since there should be a single collection with id {collection_id}.
                        Please investigate further."""
                )
            return collection
        elif collection_based_on_name is not None:
            collection = collection_based_on_name
            if len(collection) > 1:
                logger.warning(
                    f"""Multiple collections named {collection_name}, were found, please provide a
                        collection_id (a valid one) of the intended collection."""
                )
            return collection
        elif collection_based_on_id is not None:
            collection = collection_based_on_id
            if len(collection) > 1:
                logger.warning(
                    f"""Multiple collections with id {collection_id}, this should not be
                        possible since there should a single collection with id {collection_id}.
                        Please investigate further."""
                )
            return collection

    except Exception as ex:
        logger.exception("Failed to get monitored collection...", exc_info=ex)
        raise ex


def get_task(
    confidential_client_id: str,
    confidential_client_secret: str,
    task_id: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Gets a collection from all collections that the confidential client can monitor.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        task_id (str, required): The task uuid.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of getting a task. Uses standard HTTPS structure.

    Raises:
        ex: Fail to get task info

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    transfer_response = _get_task(
        current_transfer_client=current_transfer_client,
        task_id=task_id,
    )

    output(transfer_response, json_filename=json, yaml_filename=yaml)

    return transfer_response


def _get_task(
    current_transfer_client: TransferClient,
    task_id: str,
) -> GlobusHTTPResponse:
    """Private method used by `get_task`. Gets a collection from all collections that
       the confidential client can monitor.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        task_id (str, required): The task uuid.

    Returns:
        GlobusHTTPResponse: Globus API result of getting a task. Uses standard HTTPS structure.

    Raises:
        ex: Fail to get task info

    """
    try:
        transfer_response = current_transfer_client.endpoint_manager_get_task(task_id)
        logger.info(transfer_response)
        return transfer_response

    except Exception as ex:
        logger.exception("Failed to get task...", exc_info=ex)
        raise ex


def monitored_collection_list(
    confidential_client_id: str,
    confidential_client_secret: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Gets a list of all collections that the confidential client can monitor.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of all monitored collections.

    Raises:
        ex: Fail to get monitored collection list

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    list_of_monitored_endpoints = _monitored_collection_list(
        current_transfer_client=current_transfer_client,
    )

    output(list_of_monitored_endpoints, json_filename=json, yaml_filename=yaml)

    return list_of_monitored_endpoints


def _monitored_collection_list(
    current_transfer_client: TransferClient,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `monitored_collection_list`. Gets a list of all collections that the confidential client
       can monitor.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of all monitored collections.

    Raises:
        ex: Fail to get monitored collection list
    """
    try:
        list_of_monitored_endpoints = list(
            current_transfer_client.endpoint_manager_monitored_endpoints()
        )
        logger.info(list_of_monitored_endpoints)
        return list_of_monitored_endpoints

    except Exception as ex:
        logger.exception("Failed to get monitored collection list...", exc_info=ex)
        raise ex


def submit_transfer(
    confidential_client_id: str,
    confidential_client_secret: str,
    item_list_filename: str,
    source_collection_id: typing.Optional[str] = None,
    source_collection_name: typing.Optional[str] = None,
    destination_collection_id: typing.Optional[str] = None,
    destination_collection_name: typing.Optional[str] = None,
    label: typing.Optional[str] = None,
    sync_level: typing.Optional[int] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Globus transfer submission.
    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        item_list_filename (str, required): The filename of the item list file. It should be either a JSON or YAML file.
                                            It should contain a list of dictionaries.
                                            Each dictionary should have 2 keys `source_path` and `destination_path`,
                                            each containing the corresponding paths in the source and destination
                                            collection respectively.
                                            To transfer whole directories in a recursive manner, both paths should end
                                            with the character `/`.
        source_collection_name (typing.Optional[str], optional): The name of the source collection where data will be
                                                                 transferred from. Either `source_collection_name` or
                                                                 `source_collection_id` must be provided.
                                                                 Defaults to None.
        source_collection_id (typing.Optional[str], optional): The source collection uuid where data will be transferred
                                                               from. Either `source_collection_name` or
                                                               `source_collection_id` must be provided.
                                                               Defaults to None.
        destination_collection_name (typing.Optional[str], optional): The name of the destination collection where data
                                                                      will be transferred to. Either
                                                                      `destination_collection_name` or
                                                                      `destination_collection_id` must be provided.
                                                                      Defaults to None.
        destination_collection_id (typing.Optional[str], optional): The destination collection uuid  where data will be
                                                                    transferred to. Either `destination_collection_name`
                                                                    or destination_collection_id` must be provided.
                                                                    Defaults to None.
        label (typing.Optional[str], optional): The label of the transfer task. Defaults to None.
        sync_level (typing.Optional[int], optional): The sync level of the transfer task.
                                                     If not provided or set to None, the transfer will
                                                     transfer-overwrite any files with the same name that are in the
                                                     same directory in the destination collection.
                                                     If provided the level must be an integer in the 0-3 range, and it
                                                     controls what action is performed if there is already a file with
                                                     the same name in the same directory in the destination collection.
                                                     `0`: Transfer only the files that do not already exist at the
                                                          destination collection.
                                                     `1`: Transfer-overwrite same name, same directory files if their
                                                          size in the destination collection does not match their size
                                                          in the source collection.
                                                     `2`: Transfer-overwrite same name, same directory files if their
                                                          last modified timestamp in the destination collection is older
                                                          than the last modified timestamp in the source collection.
                                                     `3`: Transfer-overwrite same name, same directory files if their
                                                          checksums in the source and destination collection do
                                                          not match.
                                                      Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of submitting a transfer. Uses standard HTTPS structure.

    Raises:
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on source collection name and/or source collection id, no source collection was found
        ValueError: Based on source collection name and/or source collection id, more than one source collection was
                    found
        ValueError: Based on destination collection name and/or collection id, no destination collection was found
        ValueError: Based on destination collection name and/or collection id, more than one destination collection was
                    found
        ex: Fail to get monitored collection list
        ex: Fail to load `item_list_filename` file
        ex: Fail to submit task

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    transfer_response = _submit_transfer(
        current_transfer_client=current_transfer_client,
        item_list_filename=item_list_filename,
        source_collection_id=source_collection_id,
        source_collection_name=source_collection_name,
        destination_collection_id=destination_collection_id,
        destination_collection_name=destination_collection_name,
        label=label,
        sync_level=sync_level,
    )

    output(transfer_response, json_filename=json, yaml_filename=yaml)

    return transfer_response


def _submit_transfer(
    current_transfer_client: TransferClient,
    item_list_filename: str,
    source_collection_id: typing.Optional[str] = None,
    source_collection_name: typing.Optional[str] = None,
    destination_collection_id: typing.Optional[str] = None,
    destination_collection_name: typing.Optional[str] = None,
    label: typing.Optional[str] = None,
    sync_level: typing.Optional[int] = None,
) -> GlobusHTTPResponse:
    """Private method used by `submit_transfer`. Globus transfer submission.
    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        item_list_filename (str, required): The filename of the item list file. It should be either a JSON or YAML file.
                                            It should contain a list of dictionaries.
                                            Each dictionary should have 2 keys `source_path` and `destination_path`,
                                            each containing the corresponding paths in the source and destination
                                            collection respectively.
                                            To transfer whole directories in a recursive manner, both paths should end
                                            with the character `/`.
        source_collection_name (typing.Optional[str], optional): The name of the source collection where data will be
                                                                 transferred from. Either `source_collection_name` or
                                                                 `source_collection_id` must be provided.
                                                                 Defaults to None.
        source_collection_id (typing.Optional[str], optional): The source collection uuid where data will be transferred
                                                               from. Either `source_collection_name` or
                                                               `source_collection_id` must be provided.
                                                               Defaults to None.
        destination_collection_name (typing.Optional[str], optional): The name of the destination collection where data
                                                                      will be transferred to. Either
                                                                      `destination_collection_name` or
                                                                      `destination_collection_id` must be provided.
                                                                      Defaults to None.
        destination_collection_id (typing.Optional[str], optional): The destination collection uuid  where data will be
                                                                    transferred to. Either `destination_collection_name`
                                                                    or destination_collection_id` must be provided.
                                                                    Defaults to None.
        label (typing.Optional[str], optional): The label of the transfer task. Defaults to None.
        sync_level (typing.Optional[int], optional): The sync level of the transfer task.
                                                     If not provided or set to None, the transfer will
                                                     transfer-overwrite any files with the same name that are in the
                                                     same directory in the destination collection.
                                                     If provided the level must be an integer in the 0-3 range, and it
                                                     controls what action is performed if there is already a file with
                                                     the same name in the same directory in the destination collection.
                                                     `0`: Transfer only the files that do not already exist at the
                                                          destination collection.
                                                     `1`: Transfer-overwrite same name, same directory files if their
                                                          size in the destination collection does not match their size
                                                          in the source collection.
                                                     `2`: Transfer-overwrite same name, same directory files if their
                                                          last modified timestamp in the destination collection is older
                                                          than the last modified timestamp in the source collection.
                                                     `3`: Transfer-overwrite same name, same directory files if their
                                                          checksums in the source and destination collection do
                                                          not match.
                                                      Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of submitting a transfer. Uses standard HTTPS structure.

    Raises:
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on source collection name and/or source collection id, no source collection was found
        ValueError: Based on source collection name and/or source collection id, more than one source collection was
                    found
        ValueError: Based on destination collection name and/or collection id, no destination collection was found
        ValueError: Based on destination collection name and/or collection id, more than one destination collection was
                    found
        ex: Fail to get monitored collection list
        ex: Fail to load `item_list_filename` file
        ex: Fail to submit task

    """

    source_collection_candidate = _get_monitored_collection(
        current_transfer_client=current_transfer_client,
        collection_name=source_collection_name,
        collection_id=source_collection_id,
    )

    if len(source_collection_candidate) == 0:
        logger.error(
            f"""The source collection:{source_collection_name} provided in the
                `source_collection_name` argument does not exist."""
        )
        raise ValueError(
            f"""The source collection:{source_collection_name} provided in the
                `source_collection_name` argument does not exist."""
        )
    elif len(source_collection_candidate) > 1:
        logger.error(
            f"""For the `source_collection_name` argument, multiple collections found that are named:
                {source_collection_name}. Please use the `source_collection_id` argument "for
                disambiguation."""
        )
        raise ValueError(
            f"""For the `source_collection_name` argument, multiple collections found that are named:
                {source_collection_name}. Please use the `source_collection_id` argument "for
                disambiguation."""
        )
    else:
        source_collection = source_collection_candidate[0]["id"]

    destination_collection_candidate = _get_monitored_collection(
        current_transfer_client=current_transfer_client,
        collection_name=destination_collection_name,
        collection_id=destination_collection_id,
    )

    if len(destination_collection_candidate) == 0:
        logger.error(
            f"""The destination collection:{destination_collection_name} provided in the
                `destination_collection_name` argument does not exist."""
        )
        raise ValueError(
            f"""The destination collection:{destination_collection_name} provided in the
                `destination_collection_name` argument does not exist."""
        )
    elif len(destination_collection_candidate) > 1:
        logger.error(
            f"""For the `destination_collection_name` argument, multiple collections found that are named:
                {destination_collection_name}. Please use the `destination_collection_id` argument
                for disambiguation."""
        )
        raise ValueError(
            f"""For the `destination_collection_name` argument, multiple collections found that are named:
                {destination_collection_name}. Please use the `destination_collection_id` argument
                for disambiguation."""
        )
    else:
        destination_collection = destination_collection_candidate[0]["id"]

    try:
        if item_list_filename[-5:] == ".json" or item_list_filename[-5:] == ".JSON":
            list_of_items = json.load(open(item_list_filename))
        else:
            list_of_items = yaml.safe_load(open(item_list_filename))

    except Exception as ex:
        logger.exception(
            "Failed to load the list of items to be submitted for transfer...",
            exc_info=ex,
        )
        raise ex

    try:
        tdata = TransferData(
            current_transfer_client,
            source_collection,
            destination_collection,
            label=label,
            sync_level=sync_level,
        )
        for item in list_of_items:
            if item["source_path"][-1] == "/":
                tdata.add_item(
                    item["source_path"], item["destination_path"], recursive=True
                )
            else:
                tdata.add_item(item["source_path"], item["destination_path"])
        transfer_result = current_transfer_client.submit_transfer(tdata)
        logger.info(transfer_result)
        return transfer_result

    except Exception as ex:
        logger.exception("Failed to transfer data...", exc_info=ex)
        raise ex


def task_event_list(
    confidential_client_id: str,
    confidential_client_secret: str,
    task_id: str,
    filter_is_error: typing.Optional[bool] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Gets a list of task events for a task.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        task_id (str, required): The task uuid.
        filter_is_error (typing.Optional[bool], optional) Return only events that are errors. A value of "False"
                                                          (returning only non-errors) is not supported. If None all
                                                          events are returned. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of task events.

    Raises:
        ex: Fail to get task event list

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    list_of_events = _task_event_list(
        current_transfer_client=current_transfer_client,
        task_id=task_id,
        filter_is_error=filter_is_error,
    )

    output(list_of_events, json_filename=json, yaml_filename=yaml)

    return list_of_events


def _task_event_list(
    current_transfer_client: TransferClient,
    task_id: str,
    filter_is_error: typing.Optional[bool] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `_task_event_list`. Gets a list of task events for a task.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        task_id (str, required): The task uuid.
        filter_is_error (typing.Optional[bool], optional) Return only events that are errors. A value of "False"
                                                          (returning only non-errors) is not supported. If None all
                                                          events are returned. Defaults to None.
    Returns:
        typing.List[GlobusHTTPResponse]: A list of task events.

    Raises:
        ex: Fail to get task event list

    """
    try:
        list_of_events = list()
        for event in current_transfer_client.paginated.endpoint_manager_task_event_list(
            task_id=task_id, filter_is_error=filter_is_error
        ).items():
            list_of_events.append(event)
        logger.info(list_of_events)
        return list_of_events

    except Exception as ex:
        logger.exception("Failed collect a list of events...", exc_info=ex)
        raise ex


def task_list(
    confidential_client_id: str,
    confidential_client_secret: str,
    filter_status: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    filter_task_id: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    filter_owner_uuid: typing.Optional[str] = None,
    filter_owner_identity: typing.Optional[str] = None,
    filter_collection_id: typing.Optional[str] = None,
    filter_collection_name: typing.Optional[str] = None,
    filter_collection_use: typing.Optional[str] = None,
    filter_is_paused: typing.Optional[bool] = None,
    filter_completion_time: typing.Optional[
        typing.Union[str, typing.Tuple[str, str]]
    ] = None,
    filter_min_faults: typing.Optional[int] = None,
    filter_local_user: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Gets a list of tasks.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        filter_status (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): Return only tasks with any
                                                                                            of the specified statuses.
                                                                                            Note that in-progress tasks
                                                                                            will have status "ACTIVE" or
                                                                                            "INACTIVE", and completed
                                                                                            tasks will have status
                                                                                            "SUCCEEDED" or "FAILED".
                                                                                            Defaults to None.
        filter_task_id (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): Return only tasks with any
                                                                                             of the specified ids. If
                                                                                             any of the specified tasks
                                                                                             do not involve a collection
                                                                                             that the user has an
                                                                                             appropriate role for, a
                                                                                             PermissionDenied error will
                                                                                             be returned. This filter
                                                                                             can’t be combined with any
                                                                                             other filter. If another
                                                                                             filter is passed, a
                                                                                             BadRequest will be
                                                                                             returned.
                                                                                             (limit: 50 task IDs).
                                                                                             Defaults to None.
        filter_owner_uuid (typing.Optional[str], optional): The uuid of a Globus user. Limit results to tasks submitted
                                                            by the specified user, or linked to the specified user,
                                                            at submit time. Returns UserNotFound if the user does not
                                                            exist or has never used the Globus Transfer service. If no
                                                            tasks were submitted by this user to a collection that the
                                                            current user has an appropriate role on, an empty result
                                                            set will be returned. Unless filtering for running tasks
                                                            (i.e. `filter_status` is a subset of ("ACTIVE", "INACTIVE"),
                                                            `filter_collection_id` and/or `filter_collection_name` is
                                                            required when using filter_owner_uuid. Defaults to None.
        filter_owner_identity (typing.Optional[str], optional): The Globus identity of a user. Please provide Globus
                                                                identities that end in either "orcid.org" or
                                                                "globusid.org". Limit results to tasks submitted by the
                                                                specified user, or linked to the specified user, at
                                                                submit time. Returns UserNotFound if the user does not
                                                                exist or has never used the Globus Transfer service.
                                                                If no tasks were submitted by this user to a collection
                                                                that the current user has an appropriate role on, an
                                                                empty result set will be returned. Unless filtering for
                                                                running tasks (i.e. `filter_status` is a subset of
                                                                ("ACTIVE", "INACTIVE"), `filter_collection_id` and/or
                                                                `filter_collection_name` is required when using
                                                                `filter_owner_uuid`. Defaults to None.
        filter_collection_name (typing.Optional[str], optional): The name of the source collection where data will be
                                                                 transferred from. Either `filter_collection_name` or
                                                                 `filter_collection_id` must be provided.
                                                                 Defaults to None.
        filter_collection_id (typing.Optional[str], optional): The source collection uuid where data will be transferred
                                                               from. Either `filter_collection_name` or
                                                               `filter_collection_id` must be provided.
                                                               Defaults to None.
        filter_collection_use (typing.Optional[str], optional): In combination with `filter_collection_id` and/or
                                                                `filter_collection_name`, filter to tasks where the
                                                                collection was used specifically as the source or
                                                                destination of the transfer. Input should either
                                                                "source" or "destination". Defaults to None.
        filter_is_paused (typing.Optional[bool], optional): Return only tasks with the specified is_paused value.
                                                            Requires that filter_status is also passed and contains a
                                                            subset of "ACTIVE" and "INACTIVE". Completed tasks always
                                                            have is_paused equal to False and filtering on their paused
                                                            state is not useful and not supported. Note that pausing is
                                                            an async operation, and after a pause rule is inserted it
                                                            will take time before the is_paused flag is set on all
                                                            affected tasks. Tasks paused by id will have the is_paused
                                                            flag set immediately. Defaults to None.
        filter_completion_time (
            typing.Optional[typing.Union[str, typing.Tuple[str,str]]],
            optional): Start and end date-times separated by a comma, or provided as a tuple of strings or datetime
                       objects. Returns only completed tasks with completion_time in the specified range. Date strings
                       should be specified in one of the following ISO 8601 formats: "YYYY-MM-DDTHH:MM:SS",
                       "YYYY-MM-DDTHH:MM:SS+/-HH:MM", or "YYYY-MM-DDTHH:MM:SSZ". If no timezone is specified, UTC is
                       assumed. A space can be used between the date and time instead of T. A blank string may be used
                       for either the start or end (but not both) to indicate no limit on that side. If the end date is
                       blank, the filter will also include all active tasks, since they will complete some time in the
                       future. Defaults to None.
        filter_min_faults (typing.Optional[int], optional): Minimum number of cumulative faults, inclusive. Return only
                                                            tasks with faults >= N, where N is the filter value. Use
                                                            `filter_min_faults`=1 to find all tasks with at least one
                                                            fault. Note that many errors are not fatal and the task may
                                                            still be successful even if faults >= 1. Defaults to None.
        filter_local_user (typing.Optional[str], optional): A valid username for the target system running the endpoint
                                                            of the collection, as a utf8 encoded string. Requires that
                                                            `filter_collection_id` and/or `filter_collection_name`
                                                            is/are also set. Return only tasks that have successfully
                                                            fetched the local user from the collection, and match the
                                                            value of filter_local_user on the source or on the
                                                            destination. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of tasks.

    Raises:
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get task list

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    if filter_owner_identity is not None:
        current_auth_client = auth_client(
            confidential_client_id=confidential_client_id,
            confidential_client_secret=confidential_client_secret,
            scopes=[
                AuthScopes.openid,
                AuthScopes.profile,
                AuthScopes.email,
                AuthScopes.view_identity_set,
            ],
        )
    else:
        current_auth_client = None

    list_of_tasks = _task_list(
        current_transfer_client=current_transfer_client,
        current_auth_client=current_auth_client,
        filter_status=filter_status,
        filter_task_id=filter_task_id,
        filter_owner_uuid=filter_owner_uuid,
        filter_owner_identity=filter_owner_identity,
        filter_collection_id=filter_collection_id,
        filter_collection_name=filter_collection_name,
        filter_collection_use=filter_collection_use,
        filter_is_paused=filter_is_paused,
        filter_completion_time=filter_completion_time,
        filter_min_faults=filter_min_faults,
        filter_local_user=filter_local_user,
    )

    output(list_of_tasks, json_filename=json, yaml_filename=yaml)

    return list_of_tasks


def _task_list(
    current_transfer_client: TransferClient,
    current_auth_client: typing.Optional[AuthClient] = None,
    filter_status: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    filter_task_id: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
    filter_owner_uuid: typing.Optional[str] = None,
    filter_owner_identity: typing.Optional[str] = None,
    filter_collection_id: typing.Optional[str] = None,
    filter_collection_name: typing.Optional[str] = None,
    filter_collection_use: typing.Optional[str] = None,
    filter_is_paused: typing.Optional[bool] = None,
    filter_completion_time: typing.Optional[
        typing.Union[str, typing.Tuple[str, str]]
    ] = None,
    filter_min_faults: typing.Optional[int] = None,
    filter_local_user: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `task_list`. Gets a list of tasks.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
       filter_status (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): Return only tasks with any
                                                                                            of the specified statuses.
                                                                                            Note that in-progress tasks
                                                                                            will have status "ACTIVE" or
                                                                                            "INACTIVE", and completed
                                                                                            tasks will have status
                                                                                            "SUCCEEDED" or "FAILED".
                                                                                            Defaults to None.
        filter_task_id (typing.Optional[typing.Union[str, typing.Iterable[str]]], optional): Return only tasks with any
                                                                                             of the specified ids. If
                                                                                             any of the specified tasks
                                                                                             do not involve a collection
                                                                                             that the user has an
                                                                                             appropriate role for, a
                                                                                             PermissionDenied error will
                                                                                             be returned. This filter
                                                                                             can’t be combined with any
                                                                                             other filter. If another
                                                                                             filter is passed, a
                                                                                             BadRequest will be
                                                                                             returned.
                                                                                             (limit: 50 task IDs).
                                                                                             Defaults to None.
        filter_owner_uuid (typing.Optional[str], optional): The uuid of a Globus user. Limit results to tasks submitted
                                                            by the specified user, or linked to the specified user,
                                                            at submit time. Returns UserNotFound if the user does not
                                                            exist or has never used the Globus Transfer service. If no
                                                            tasks were submitted by this user to a collection that the
                                                            current user has an appropriate role on, an empty result
                                                            set will be returned. Unless filtering for running tasks
                                                            (i.e. `filter_status` is a subset of ("ACTIVE", "INACTIVE"),
                                                            `filter_collection_id` and/or `filter_collection_name` is
                                                            required when using filter_owner_uuid. Defaults to None.
        filter_owner_identity (typing.Optional[str], optional): The Globus identity of a user. Please provide Globus
                                                                identities that end in either "orcid.org" or
                                                                "globusid.org". Limit results to tasks submitted by the
                                                                specified user, or linked to the specified user, at
                                                                submit time. Returns UserNotFound if the user does not
                                                                exist or has never used the Globus Transfer service.
                                                                If no tasks were submitted by this user to a collection
                                                                that the current user has an appropriate role on, an
                                                                empty result set will be returned. Unless filtering for
                                                                running tasks (i.e. `filter_status` is a subset of
                                                                ("ACTIVE", "INACTIVE"), `filter_collection_id` and/or
                                                                `filter_collection_name` is required when using
                                                                `filter_owner_uuid`. Defaults to None.
        filter_collection_name (typing.Optional[str], optional): The name of the source collection where data will be
                                                                 transferred from. Either `filter_collection_name` or
                                                                 `filter_collection_id` must be provided.
                                                                 Defaults to None.
        filter_collection_id (typing.Optional[str], optional): The source collection uuid where data will be transferred
                                                               from. Either `filter_collection_name` or
                                                               `filter_collection_id` must be provided.
                                                               Defaults to None.
        filter_collection_use (typing.Optional[str], optional): In combination with `filter_collection_id` and/or
                                                                `filter_collection_name`, filter to tasks where the
                                                                collection was used specifically as the source or
                                                                destination of the transfer. Input should either
                                                                "source" or "destination". Defaults to None.
        filter_is_paused (typing.Optional[bool], optional): Return only tasks with the specified is_paused value.
                                                            Requires that filter_status is also passed and contains a
                                                            subset of "ACTIVE" and "INACTIVE". Completed tasks always
                                                            have is_paused equal to False and filtering on their paused
                                                            state is not useful and not supported. Note that pausing is
                                                            an async operation, and after a pause rule is inserted it
                                                            will take time before the is_paused flag is set on all
                                                            affected tasks. Tasks paused by id will have the is_paused
                                                            flag set immediately. Defaults to None.
        filter_completion_time (
            typing.Optional[typing.Union[str, typing.Tuple[str,str]]],
            optional): Start and end date-times separated by a comma, or provided as a tuple of strings or datetime
                       objects. Returns only completed tasks with completion_time in the specified range. Date strings
                       should be specified in one of the following ISO 8601 formats: "YYYY-MM-DDTHH:MM:SS",
                       "YYYY-MM-DDTHH:MM:SS+/-HH:MM", or "YYYY-MM-DDTHH:MM:SSZ". If no timezone is specified, UTC is
                       assumed. A space can be used between the date and time instead of T. A blank string may be used
                       for either the start or end (but not both) to indicate no limit on that side. If the end date is
                       blank, the filter will also include all active tasks, since they will complete some time in the
                       future. Defaults to None.
        filter_min_faults (typing.Optional[int], optional): Minimum number of cumulative faults, inclusive. Return only
                                                            tasks with faults >= N, where N is the filter value. Use
                                                            `filter_min_faults`=1 to find all tasks with at least one
                                                            fault. Note that many errors are not fatal and the task may
                                                            still be successful even if faults >= 1. Defaults to None.
        filter_local_user (typing.Optional[str], optional): A valid username for the target system running the endpoint
                                                            of the collection, as a utf8 encoded string. Requires that
                                                            `filter_collection_id` and/or `filter_collection_name`
                                                            is/are also set. Return only tasks that have successfully
                                                            fetched the local user from the collection, and match the
                                                            value of filter_local_user on the source or on the
                                                            destination. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of tasks.

    Raises:
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get task list

    """
    if filter_owner_identity is not None:
        if (
            (not filter_owner_identity.endswith("@orcid.org"))
            and (not filter_owner_identity.endswith("@globusid.org"))
            and filter_owner_uuid is None
        ):
            logger.error(
                """For the "filter_owner_identity" argument please provide either a valid user identity
                   (ending with either with @orcid.org or @globusid.org) or provide the `filter_owner_uuid`
                   by entering the user's uuid."""
            )
            raise ValueError(
                """For the "filter_owner_identity" argument please provide either a valid user identity
                   (ending with either with @orcid.org or @globusid.org) or provide the `filter_owner_uuid`
                   by entering the user's uuid."""
            )

        user_uuid = get_user_uuid(
            current_auth_client=current_auth_client,
            list_orcids=[
                filter_owner_identity,
            ],
        )[0]

        if filter_owner_uuid is not None and user_uuid != filter_owner_uuid:
            logger.error(
                f"""Provided user identity (argument `filter_owner_identity`) has uuid {user_uuid} that do not
                    match with the provided `filter_owner_uuid` argument which is {filter_owner_uuid}. Please
                    to disambiguate, provide as input either only one or the other or a `filter_owner_identity`
                    that corresponds to a user with uuid that matches the `filter_owner_uuid` argument."""
            )
            raise ValueError(
                f"""Provided user identity (argument `filter_owner_identity`) has uuid {user_uuid} that do
                    not match with the provided `filter_owner_uuid` argument which is {filter_owner_uuid}.
                    Please to disambiguate, provide as input either only one or the other or a
                    `filter_owner_identity` that corresponds to a user with uuid that matches the
                    `filter_owner_uuid` argument."""
            )

        filter_owner_uuid = user_uuid

    if filter_collection_id is not None or filter_collection_name is not None:
        collection = _get_monitored_collection(
            current_transfer_client=current_transfer_client,
            collection_name=filter_collection_name,
            collection_id=filter_collection_id,
        )

        if len(collection) == 0:
            logger.error(
                f"""The collection:{filter_collection_name} provided in the `filter_collection_name`
                    argument does not exist."""
            )
            raise ValueError(
                f"""The collection:{filter_collection_name} provided in the `filter_collection_name`
                    argument does not exist."""
            )
        elif len(collection) > 1:
            logger.error(
                f"""For the `filter_collection_name` argument, multiple collections found that are named:
                    {filter_collection_name}. Please use the `filter_collection_id` argument
                    for disambiguation."""
            )
            raise ValueError(
                f"""For the `filter_collection_name` argument, multiple collections found that are named:
                    {filter_collection_name}. Please use the `filter_collection_id` argument
                    for disambiguation."""
            )
        else:
            filter_endpoint = collection[0]["id"]
    else:
        filter_endpoint = None

    try:
        list_of_tasks = list()
        for task in current_transfer_client.paginated.endpoint_manager_task_list(
            filter_status=filter_status,
            filter_task_id=filter_task_id,
            filter_owner_id=filter_owner_uuid,
            filter_endpoint=filter_endpoint,
            filter_endpoint_use=filter_collection_use,
            filter_is_paused=filter_is_paused,
            filter_completion_time=filter_completion_time,
            filter_min_faults=filter_min_faults,
            filter_local_user=filter_local_user,
        ).items():
            list_of_tasks.append(task)
        logger.info(list_of_tasks)
        return list_of_tasks

    except Exception as ex:
        logger.exception("Failed collect a list of task ids...", exc_info=ex)
        raise ex


def task_successful_transfers(
    confidential_client_id: str,
    confidential_client_secret: str,
    task_id: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Gets a list of dictionaries each representing a successfully transferred file.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        task_id (str, required): The task uuid.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of dictionaries each representing a successfully transferred file.
                                         Each dictionary consists of 2 keys `source_path` and `destination_path`,
                                         each containing the corresponding paths.

    Raises:
        ex: Fail to get task successful transfers

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    list_of_transfers = _task_successful_transfers(
        current_transfer_client=current_transfer_client,
        task_id=task_id,
    )

    output(list_of_transfers, json_filename=json, yaml_filename=yaml)

    return list_of_transfers


def _task_successful_transfers(
    current_transfer_client: TransferClient,
    task_id: str,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `task_successful_transfers`. Gets a list of dictionaries each representing a
       successfully transferred file.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        task_id (str, required): The task uuid.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of dictionaries each representing a successfully transferred file. Each
                                         dictionary consists of 2 keys `source_path` and `destination_path`,
                                         each containing the corresponding paths.

    Raises:
        ex: Fail to get task successful transfers

    """
    try:
        list_of_transfers = list()
        for (
            successful_transfers
        ) in current_transfer_client.paginated.endpoint_manager_task_successful_transfers(
            task_id
        ).items():
            list_of_transfers.append(successful_transfers)
        logger.info(list_of_transfers)
        return list_of_transfers

    except Exception as ex:
        logger.exception("Failed collect task successful transfers...", exc_info=ex)
        raise ex
