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

import datetime
import json
import typing

import yaml
from globus_sdk import (
    OnceTimerSchedule,
    RecurringTimerSchedule,
    TimersAPIError,
    TimersClient,
    TransferClient,
    TransferData,
    TransferTimer,
)
from globus_sdk._missing import MISSING, MissingType
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import Scope, TimersScopes, TransferScopes

import GlobusAPI

from ..logging.logging import get_logger
from ..output.file_output import output
from ..transfers.transfer_client import transfer_client
from ..transfers.transfer_methods import _get_monitored_collection
from ..utilities.utils import time_string_to_integer_seconds

logger = get_logger(stdout=True)

# The Timers service runs transfers on the client's behalf, so the `timer` scope must
# depend on the Transfer service's scope, or Globus will reject timer creation.
TIMERS_SCOPE = TimersScopes.timer.with_dependency(TransferScopes.all)


def timers_client(
    confidential_client_id: str,
    confidential_client_secret: str,
    scopes: typing.Union[str, Scope, typing.Iterable[typing.Union[str, Scope]]] = (
        TIMERS_SCOPE
    ),
) -> TimersClient:
    """Return a timers client object initialized with the given parameters.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        scopes (typing.Union[str,Scope,typing.Iterable[typing.Union[str,Scope]]], optional): The Globus Scopes for
                                                                                             the timers client.
                                                                                             Defaults to
                                                                                             `TIMERS_SCOPE`, which
                                                                                             depends on
                                                                                             `TransferScopes.all`.

    Returns:
        It returns a timers client object initialized with the given parameters.

    Raises:
        ex: Fail to create Authorizer
        ex: Fail to create Timers Client

    """
    try:
        timers_authorizer = GlobusAPI.auth.authorizer.get_client_credentials_authorizer(
            confidential_client_id, confidential_client_secret, scopes
        )

    except Exception as ex:
        logger.exception("Failed to create authorizer...", exc_info=ex)
        raise ex

    try:
        current_timers_client = TimersClient(authorizer=timers_authorizer)

        return current_timers_client

    except Exception as ex:
        logger.exception("Failed to create timers client...", exc_info=ex)
        raise ex


def timer_list(
    confidential_client_id: str,
    confidential_client_secret: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Get the list of timers owned by the confidential client.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of timers.

    Raises:
        ex: Fail to list timers

    """
    current_timers_client = timers_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
    )

    list_of_timers = _timer_list(current_timers_client=current_timers_client)

    output(list_of_timers, json_filename=json, yaml_filename=yaml)

    return list_of_timers


def _timer_list(
    current_timers_client: TimersClient,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `timer_list`. Get the list of timers owned by the confidential client.

    Args:
        current_timers_client (TimersClient, required): Globus Timers Client.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of timers.

    Raises:
        ex: Fail to list timers

    """
    try:
        list_of_timers = current_timers_client.list_jobs()["jobs"]
        logger.info(list_of_timers)
        return list_of_timers

    except Exception as ex:
        logger.exception("Failed to get timer list...", exc_info=ex)
        raise ex


def _resolve_timer_id(
    current_timers_client: TimersClient,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
) -> str:
    """Resolve a timer's uuid from either a `timer_id` or a `timer_name`. Exactly one of the two must be provided;
       when `timer_name` is used, exactly one timer must match that name.

    Args:
        current_timers_client (TimersClient, required): Globus Timers Client.
        timer_id (typing.Optional[str], optional): The uuid of the timer. Defaults to None.
        timer_name (typing.Optional[str], optional): The name of the timer. Defaults to None.

    Returns:
        str: The uuid of the timer.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, no timer was found
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to list timers

    """
    if (timer_id is None) == (timer_name is None):
        logger.error(
            "Please provide exactly one of the `timer_id` or `timer_name` arguments."
        )
        raise ValueError(
            "Please provide exactly one of the `timer_id` or `timer_name` arguments."
        )

    if timer_id is not None:
        return timer_id

    matching_timers = [
        timer
        for timer in _timer_list(current_timers_client=current_timers_client)
        if timer["name"] == timer_name
    ]

    if len(matching_timers) == 0:
        logger.error(f"No timer found with the name:{timer_name}.")
        raise ValueError(f"No timer found with the name:{timer_name}.")
    elif len(matching_timers) > 1:
        logger.error(
            f"""Multiple timers found with the name:{timer_name}. Please use the
                `timer_id` argument for disambiguation."""
        )
        raise ValueError(
            f"""Multiple timers found with the name:{timer_name}. Please use the
                `timer_id` argument for disambiguation."""
        )
    else:
        return matching_timers[0]["job_id"]


def _normalize_for_diff(value: typing.Any) -> typing.Any:
    """Recursively normalize a value for equality comparison, so that differences which are not meaningful do not
       cause a false positive diff. Strips `MISSING` sentinel entries out of dicts (unset fields are omitted from
       both the API's stored representation and a freshly-built payload) and parses ISO 8601 datetime strings into
       `datetime.datetime` objects (so equivalent datetimes compare equal regardless of string formatting, e.g.
       trailing `Z` vs `+00:00`).

    Args:
        value (typing.Any, required): The value to normalize. May be a dict, list, or scalar.

    Returns:
        typing.Any: The normalized value.

    """
    if isinstance(value, dict):
        return {
            key: _normalize_for_diff(item)
            for key, item in value.items()
            if item is not MISSING
        }
    if isinstance(value, list):
        return [_normalize_for_diff(item) for item in value]
    if isinstance(value, str):
        try:
            # The Timers API truncates (not rounds) datetimes to whole seconds when
            # storing them, so a freshly-built value with microseconds would otherwise
            # never compare equal to the stored one.
            return datetime.datetime.fromisoformat(
                value.replace("Z", "+00:00")
            ).replace(microsecond=0)
        except ValueError:
            return value
    return value


def _find_existing_timer_by_name(
    current_timers_client: TimersClient,
    name: str,
) -> typing.Optional[GlobusHTTPResponse]:
    """Find the single existing timer with the given name, if any.

    Args:
        current_timers_client (TimersClient, required): Globus Timers Client.
        name (str, required): The name to search for.

    Returns:
        typing.Optional[GlobusHTTPResponse]: The matching timer, or None if no timer has this name.

    Raises:
        ValueError: More than one timer was found with the given `name`
        ex: Fail to list timers

    """
    matching_timers = [
        timer
        for timer in _timer_list(current_timers_client=current_timers_client)
        if timer["name"] == name
    ]

    if len(matching_timers) > 1:
        logger.error(
            f"""Multiple timers found with the name:{name}. Cannot determine which one to
                replace."""
        )
        raise ValueError(
            f"""Multiple timers found with the name:{name}. Cannot determine which one to
                replace."""
        )

    return matching_timers[0] if matching_timers else None


def _timer_matches(
    existing_timer: GlobusHTTPResponse,
    name: typing.Optional[str],
    schedule: typing.Union[RecurringTimerSchedule, OnceTimerSchedule],
    tdata: TransferData,
) -> bool:
    """Compare an existing timer against the name/schedule/transfer body that would be submitted to (re)create it.

    Args:
        existing_timer (GlobusHTTPResponse, required): The existing timer, as returned by `list_jobs`/`get_job`.
        name (typing.Optional[str], required): The desired timer name.
        schedule (typing.Union[RecurringTimerSchedule, OnceTimerSchedule], required): The desired schedule.
        tdata (TransferData, required): The desired transfer body.

    Returns:
        bool: True if the existing timer already matches the desired name, schedule and transfer body.

    """
    existing_body = existing_timer.get("callback_body", {}).get("body", {})

    return (
        existing_timer.get("name") == name
        and _normalize_for_diff(existing_timer.get("schedule", {}))
        == _normalize_for_diff(dict(schedule))
        and _normalize_for_diff(existing_body) == _normalize_for_diff(dict(tdata))
    )


def get_timer(
    confidential_client_id: str,
    confidential_client_secret: str,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Get the info of a timer based on its uuid or name.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        timer_id (typing.Optional[str], optional): The uuid of the timer. Either `timer_id` or `timer_name` must be
                                                    provided, but not both. Defaults to None.
        timer_name (typing.Optional[str], optional): The name of the timer. Must match exactly one timer. Either
                                                      `timer_id` or `timer_name` must be provided, but not both.
                                                      Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of getting the timer info. Uses standard HTTPS structure.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, no timer was found
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to get timer info

    """
    current_timers_client = timers_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
    )

    timer_response = _get_timer(
        current_timers_client=current_timers_client,
        timer_id=timer_id,
        timer_name=timer_name,
    )

    output(timer_response, json_filename=json, yaml_filename=yaml)

    return timer_response


def _get_timer(
    current_timers_client: TimersClient,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Private method used by `get_timer`. Get the info of a timer based on its uuid or name.

    Args: see `get_timer`, but `current_timers_client` replaces the confidential client credentials.

    Returns:
        GlobusHTTPResponse: Globus API result of getting the timer info. Uses standard HTTPS structure.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, no timer was found
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to get timer info

    """
    resolved_timer_id = _resolve_timer_id(
        current_timers_client=current_timers_client,
        timer_id=timer_id,
        timer_name=timer_name,
    )

    try:
        timer_response = current_timers_client.get_job(resolved_timer_id)
        logger.info(timer_response)
        return timer_response

    except Exception as ex:
        logger.exception("Failed to get timer info...", exc_info=ex)
        raise ex


def delete_timer(
    confidential_client_id: str,
    confidential_client_secret: str,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Deletes a timer based on its uuid or name.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        timer_id (typing.Optional[str], optional): The uuid of the timer to be deleted. Either `timer_id` or
                                                    `timer_name` must be provided, but not both. Defaults to None.
        timer_name (typing.Optional[str], optional): The name of the timer to be deleted. Must match exactly one
                                                      timer. Either `timer_id` or `timer_name` must be provided, but
                                                      not both. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of deleting the timer, with an added `changed` boolean key: false if
                            the timer was already absent (deletion is idempotent), true otherwise. Uses standard
                            HTTPS structure.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to delete timer

    """
    current_timers_client = timers_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
    )

    timer_response = _delete_timer(
        current_timers_client=current_timers_client,
        timer_id=timer_id,
        timer_name=timer_name,
    )

    output(timer_response, json_filename=json, yaml_filename=yaml)

    return timer_response


def _delete_timer(
    current_timers_client: TimersClient,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Private method used by `delete_timer`. Deletes a timer based on its uuid or name. Idempotent: if the timer is
       already absent, this is a no-op rather than an error.

    Args: see `delete_timer`, but `current_timers_client` replaces the confidential client credentials.

    Returns:
        GlobusHTTPResponse: Globus API result of deleting the timer, with an added `changed` boolean key: false if
                            the timer was already absent, true otherwise. Uses standard HTTPS structure.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to delete timer

    """
    if (timer_id is None) == (timer_name is None):
        logger.error(
            "Please provide exactly one of the `timer_id` or `timer_name` arguments."
        )
        raise ValueError(
            "Please provide exactly one of the `timer_id` or `timer_name` arguments."
        )

    if timer_name is not None:
        existing_timer = _find_existing_timer_by_name(
            current_timers_client=current_timers_client, name=timer_name
        )
        if existing_timer is None:
            logger.info(f"No timer found with the name:{timer_name}; already absent.")
            return {"name": timer_name, "changed": False}
        timer_id = existing_timer["job_id"]

    try:
        timer_response = current_timers_client.delete_job(timer_id)
        result = dict(timer_response.data)
        result["changed"] = True
        logger.info(result)
        return result

    except TimersAPIError as ex:
        if ex.http_status == 404:
            logger.info(f"Timer job_id:{timer_id} already absent.")
            return {"job_id": timer_id, "changed": False}
        logger.exception("Failed to delete timer...", exc_info=ex)
        raise ex

    except Exception as ex:
        logger.exception("Failed to delete timer...", exc_info=ex)
        raise ex


def pause_timer(
    confidential_client_id: str,
    confidential_client_secret: str,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Pauses a timer based on its uuid or name, preventing it from running until resumed.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        timer_id (typing.Optional[str], optional): The uuid of the timer to be paused. Either `timer_id` or
                                                    `timer_name` must be provided, but not both. Defaults to None.
        timer_name (typing.Optional[str], optional): The name of the timer to be paused. Must match exactly one
                                                      timer. Either `timer_id` or `timer_name` must be provided, but
                                                      not both. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of pausing the timer, with an added `changed` boolean key: false if
                            the timer was already inactive (pausing is idempotent), true otherwise. Uses standard
                            HTTPS structure.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, no timer was found
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to pause timer

    """
    current_timers_client = timers_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
    )

    timer_response = _pause_timer(
        current_timers_client=current_timers_client,
        timer_id=timer_id,
        timer_name=timer_name,
    )

    output(timer_response, json_filename=json, yaml_filename=yaml)

    return timer_response


def _pause_timer(
    current_timers_client: TimersClient,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Private method used by `pause_timer`. Pauses a timer based on its uuid or name, preventing it from running
       until resumed. Idempotent: if the timer is already inactive, this is a no-op rather than pausing again.

    Args: see `pause_timer`, but `current_timers_client` replaces the confidential client credentials.

    Returns:
        GlobusHTTPResponse: Globus API result of pausing the timer, with an added `changed` boolean key: false if
                            the timer was already inactive, true otherwise. Uses standard HTTPS structure.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, no timer was found
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to pause timer

    """
    resolved_timer_id = _resolve_timer_id(
        current_timers_client=current_timers_client,
        timer_id=timer_id,
        timer_name=timer_name,
    )

    try:
        current_status = current_timers_client.get_job(resolved_timer_id).get("status")
        if current_status == "inactive":
            logger.info(
                f"Timer job_id:{resolved_timer_id} is already inactive; nothing to pause."
            )
            return {"job_id": resolved_timer_id, "status": "inactive", "changed": False}

        timer_response = current_timers_client.pause_job(resolved_timer_id)
        result = dict(timer_response.data)
        result["changed"] = True
        logger.info(result)
        return result

    except Exception as ex:
        logger.exception("Failed to pause timer...", exc_info=ex)
        raise ex


def resume_timer(
    confidential_client_id: str,
    confidential_client_secret: str,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
    update_credentials: typing.Optional[bool] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Resumes a paused timer based on its uuid or name.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        timer_id (typing.Optional[str], optional): The uuid of the timer to be resumed. Either `timer_id` or
                                                    `timer_name` must be provided, but not both. Defaults to None.
        timer_name (typing.Optional[str], optional): The name of the timer to be resumed. Must match exactly one
                                                      timer. Either `timer_id` or `timer_name` must be provided, but
                                                      not both. Defaults to None.
        update_credentials (typing.Optional[bool], optional): When true, replace the timer's refresh token using
                                                               the credentials of this call. Can be used to resolve
                                                               authorization errors, but could also introduce them if
                                                               the new credentials lack a property of the ones they
                                                               replace. If not supplied, the Timers service decides
                                                               whether to replace credentials based on why the timer
                                                               became inactive. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of resuming the timer, with an added `changed` boolean key: false if
                            the timer was not inactive (resuming is idempotent), true otherwise. Uses standard
                            HTTPS structure.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, no timer was found
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to resume timer

    """
    current_timers_client = timers_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
    )

    timer_response = _resume_timer(
        current_timers_client=current_timers_client,
        timer_id=timer_id,
        timer_name=timer_name,
        update_credentials=update_credentials,
    )

    output(timer_response, json_filename=json, yaml_filename=yaml)

    return timer_response


def _resume_timer(
    current_timers_client: TimersClient,
    timer_id: typing.Optional[str] = None,
    timer_name: typing.Optional[str] = None,
    update_credentials: typing.Optional[bool] = None,
) -> GlobusHTTPResponse:
    """Private method used by `resume_timer`. Resumes a paused timer based on its uuid or name. Idempotent: if the
       timer is not inactive, this is a no-op rather than resuming again.

    Args: see `resume_timer`, but `current_timers_client` replaces the confidential client credentials.

    Returns:
        GlobusHTTPResponse: Globus API result of resuming the timer, with an added `changed` boolean key: false if
                            the timer was not inactive, true otherwise. Uses standard HTTPS structure.

    Raises:
        ValueError: Neither or both of `timer_id` and `timer_name` were provided
        ValueError: Based on `timer_name`, no timer was found
        ValueError: Based on `timer_name`, more than one timer was found
        ex: Fail to resume timer

    """
    resolved_timer_id = _resolve_timer_id(
        current_timers_client=current_timers_client,
        timer_id=timer_id,
        timer_name=timer_name,
    )

    try:
        current_status = current_timers_client.get_job(resolved_timer_id).get("status")
        if current_status != "inactive":
            logger.info(
                f"""Timer job_id:{resolved_timer_id} is not inactive
                    (status:{current_status}); nothing to resume."""
            )
            return {
                "job_id": resolved_timer_id,
                "status": current_status,
                "changed": False,
            }

        timer_response = current_timers_client.resume_job(
            resolved_timer_id, update_credentials=update_credentials
        )
        result = dict(timer_response.data)
        result["changed"] = True
        logger.info(result)
        return result

    except Exception as ex:
        logger.exception("Failed to resume timer...", exc_info=ex)
        raise ex


def create_timer(
    confidential_client_id: str,
    confidential_client_secret: str,
    item_list_filename: str,
    source_collection_id: typing.Optional[str] = None,
    source_collection_name: typing.Optional[str] = None,
    destination_collection_id: typing.Optional[str] = None,
    destination_collection_name: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
    interval: typing.Optional[str] = None,
    start: typing.Optional[str] = None,
    stop_after_iterations: typing.Optional[int] = None,
    stop_at: typing.Optional[str] = None,
    run_at: typing.Optional[str] = None,
    label: typing.Union[str, MissingType] = MISSING,
    sync_level: typing.Union[
        int, typing.Literal["exists", "size", "mtime", "checksum"], MissingType
    ] = MISSING,
    verify_checksum: typing.Union[bool, MissingType] = MISSING,
    preserve_timestamp: typing.Union[bool, MissingType] = MISSING,
    encrypt_data: typing.Union[bool, MissingType] = MISSING,
    skip_source_errors: typing.Union[bool, MissingType] = MISSING,
    fail_on_quota_errors: typing.Union[bool, MissingType] = MISSING,
    notify_on_succeeded: typing.Union[bool, MissingType] = MISSING,
    notify_on_failed: typing.Union[bool, MissingType] = MISSING,
    notify_on_inactive: typing.Union[bool, MissingType] = MISSING,
    replace: bool = False,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Creates a Globus timer that runs a transfer task, either once or on a recurring schedule.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        item_list_filename (str, required): The filename of the item list file. It should be either a JSON or YAML
                                            file. It should contain a list of dictionaries. Each dictionary should
                                            have 2 keys `source_path` and `destination_path`, each containing the
                                            corresponding paths in the source and destination collection
                                            respectively. To transfer whole directories in a recursive manner, both
                                            paths should end with the character `/`.
        source_collection_name (typing.Optional[str], optional): The name of the source collection where data will be
                                                                 transferred from. Either `source_collection_name` or
                                                                 `source_collection_id` must be provided.
                                                                 Defaults to None.
        source_collection_id (typing.Optional[str], optional): The source collection uuid where data will be
                                                               transferred from. Either `source_collection_name` or
                                                               `source_collection_id` must be provided.
                                                               Defaults to None.
        destination_collection_name (typing.Optional[str], optional): The name of the destination collection where
                                                                      data will be transferred to. Either
                                                                      `destination_collection_name` or
                                                                      `destination_collection_id` must be provided.
                                                                      Defaults to None.
        destination_collection_id (typing.Optional[str], optional): The destination collection uuid where data will
                                                                    be transferred to. Either
                                                                    `destination_collection_name` or
                                                                    `destination_collection_id` must be provided.
                                                                    Defaults to None.
        name (typing.Optional[str], optional): A name for the timer. Defaults to None.
        interval (typing.Optional[str], optional): The interval at which the timer recurs. Accepted formats "ss",
                                                    "mm:ss", "hh:mm:ss". Either `interval` or `run_at` must be
                                                    provided, but not both.
        start (typing.Optional[str], optional): ISO 8601 datetime string for when the recurring timer should first
                                                 run. Only used with `interval`. If not provided, the timer starts
                                                 immediately. Defaults to None.
        stop_after_iterations (typing.Optional[int], optional): Number of times the recurring timer should run
                                                                 before stopping. Only used with `interval`. Mutually
                                                                 exclusive with `stop_at`. Defaults to None, meaning
                                                                 the timer runs indefinitely.
        stop_at (typing.Optional[str], optional): ISO 8601 datetime string after which the recurring timer stops
                                                   running. Only used with `interval`. Mutually exclusive with
                                                   `stop_after_iterations`. Defaults to None, meaning the timer runs
                                                   indefinitely.
        run_at (typing.Optional[str], optional): ISO 8601 datetime string for when a one-off timer should run.
                                                  Either `interval` or `run_at` must be provided, but not both.
        label (typing.Union[str, MissingType], optional): The label of the transfer tasks submitted by the timer.
                                                           Defaults to MISSING.
        sync_level (
            typing.Union[
                int,
                typing.Literal['exists', 'size', 'mtime', 'checksum'],
                MissingType,
            ],
            optional): The sync level of the transfer tasks submitted by the timer. Defaults to MISSING.
        verify_checksum (typing.Union[bool, MissingType], optional): When true, after transfer verify that the
                                                                     source and destination file checksums match.
                                                                     Defaults to MISSING.
        preserve_timestamp (typing.Union[bool, MissingType], optional): When true, Globus Transfer will attempt to
                                                                        set file timestamps on the destination to
                                                                        match those on the origin. Defaults to
                                                                        MISSING.
        encrypt_data (typing.Union[bool, MissingType], optional): When true, all files will be TLS-protected during
                                                                  transfer. Defaults to MISSING.
        skip_source_errors (typing.Union[bool, MissingType], optional): When true, source permission denied and file
                                                                        not found errors from the source endpoint
                                                                        will cause the offending path to be skipped.
                                                                        Defaults to MISSING.
        fail_on_quota_errors (typing.Union[bool, MissingType], optional): When true, quota exceeded errors will
                                                                          cause the task to fail. Defaults to
                                                                          MISSING.
        notify_on_succeeded (typing.Union[bool, MissingType], optional): Send a notification email when a submitted
                                                                         transfer completes with a status of
                                                                         SUCCEEDED. Defaults to MISSING.
        notify_on_failed (typing.Union[bool, MissingType], optional): Send a notification email when a submitted
                                                                      transfer completes with a status of FAILED.
                                                                      Defaults to MISSING.
        notify_on_inactive (typing.Union[bool, MissingType], optional): Send a notification email when a submitted
                                                                        transfer changes status to INACTIVE.
                                                                        Defaults to MISSING.
        replace (bool, optional): When true, makes timer creation idempotent by `name`: if exactly one existing
                                  timer already has this `name`, its name/schedule/transfer body are compared
                                  against the ones requested here. If they match, the existing timer is left alone
                                  and returned unchanged. If they differ, the existing timer is deleted before the
                                  new one is created. Requires `name` to be provided. Defaults to False.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of creating a timer, or the existing timer unchanged if `replace` is
                            true and it already matches the request. Includes an added `changed` boolean key: false
                            only when `replace` skipped an already-matching timer, true otherwise. Uses standard
                            HTTPS structure.

    Raises:
        ValueError: Neither or both of `interval` and `run_at` were provided
        ValueError: Both `stop_after_iterations` and `stop_at` were provided
        ValueError: Based on source collection name and/or source collection id, no source collection was found
        ValueError: Based on source collection name and/or source collection id, more than one source collection
                    was found
        ValueError: Based on destination collection name and/or collection id, no destination collection was found
        ValueError: Based on destination collection name and/or collection id, more than one destination collection
                    was found
        ValueError: `replace` is true but `name` was not provided
        ValueError: `replace` is true and more than one existing timer was found with the given `name`
        ex: Fail to get monitored collection list
        ex: Fail to load `item_list_filename` file
        ex: Fail to create timer

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    current_timers_client = timers_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
    )

    timer_response = _create_timer(
        current_transfer_client=current_transfer_client,
        current_timers_client=current_timers_client,
        item_list_filename=item_list_filename,
        source_collection_id=source_collection_id,
        source_collection_name=source_collection_name,
        destination_collection_id=destination_collection_id,
        destination_collection_name=destination_collection_name,
        name=name,
        interval=interval,
        start=start,
        stop_after_iterations=stop_after_iterations,
        stop_at=stop_at,
        run_at=run_at,
        label=label,
        sync_level=sync_level,
        verify_checksum=verify_checksum,
        preserve_timestamp=preserve_timestamp,
        encrypt_data=encrypt_data,
        skip_source_errors=skip_source_errors,
        fail_on_quota_errors=fail_on_quota_errors,
        notify_on_succeeded=notify_on_succeeded,
        notify_on_failed=notify_on_failed,
        notify_on_inactive=notify_on_inactive,
        replace=replace,
    )

    output(timer_response, json_filename=json, yaml_filename=yaml)

    return timer_response


def _create_timer(
    current_transfer_client: TransferClient,
    current_timers_client: TimersClient,
    item_list_filename: str,
    source_collection_id: typing.Optional[str] = None,
    source_collection_name: typing.Optional[str] = None,
    destination_collection_id: typing.Optional[str] = None,
    destination_collection_name: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
    interval: typing.Optional[str] = None,
    start: typing.Optional[str] = None,
    stop_after_iterations: typing.Optional[int] = None,
    stop_at: typing.Optional[str] = None,
    run_at: typing.Optional[str] = None,
    label: typing.Union[str, MissingType] = MISSING,
    sync_level: typing.Union[
        int, typing.Literal["exists", "size", "mtime", "checksum"], MissingType
    ] = MISSING,
    verify_checksum: typing.Union[bool, MissingType] = MISSING,
    preserve_timestamp: typing.Union[bool, MissingType] = MISSING,
    encrypt_data: typing.Union[bool, MissingType] = MISSING,
    skip_source_errors: typing.Union[bool, MissingType] = MISSING,
    fail_on_quota_errors: typing.Union[bool, MissingType] = MISSING,
    notify_on_succeeded: typing.Union[bool, MissingType] = MISSING,
    notify_on_failed: typing.Union[bool, MissingType] = MISSING,
    notify_on_inactive: typing.Union[bool, MissingType] = MISSING,
    replace: bool = False,
) -> GlobusHTTPResponse:
    """Private method used by `create_timer`. Creates a Globus timer that runs a transfer task, either once or on a
       recurring schedule.

    Args: see `create_timer`, but `current_transfer_client` and `current_timers_client` replace the confidential
          client credentials.

    Returns:
        GlobusHTTPResponse: Globus API result of creating a timer, or the existing timer unchanged if `replace` is
                            true and it already matches the request. Includes an added `changed` boolean key: false
                            only when `replace` skipped an already-matching timer, true otherwise. Uses standard
                            HTTPS structure.

    Raises:
        ValueError: Neither or both of `interval` and `run_at` were provided
        ValueError: Both `stop_after_iterations` and `stop_at` were provided
        ValueError: Based on source collection name and/or source collection id, no source collection was found
        ValueError: Based on source collection name and/or source collection id, more than one source collection
                    was found
        ValueError: Based on destination collection name and/or collection id, no destination collection was found
        ValueError: Based on destination collection name and/or collection id, more than one destination collection
                    was found
        ValueError: `replace` is true but `name` was not provided
        ValueError: `replace` is true and more than one existing timer was found with the given `name`
        ex: Fail to get monitored collection list
        ex: Fail to load `item_list_filename` file
        ex: Fail to create timer

    """
    if replace and name is None:
        logger.error(
            "The `replace` option requires `name` to look up any existing timer."
        )
        raise ValueError(
            "The `replace` option requires `name` to look up any existing timer."
        )

    if (interval is None) == (run_at is None):
        logger.error(
            "Please provide exactly one of the `interval` or `run_at` arguments."
        )
        raise ValueError(
            "Please provide exactly one of the `interval` or `run_at` arguments."
        )

    if stop_after_iterations is not None and stop_at is not None:
        logger.error(
            """Please provide at most one of the `stop_after_iterations` or `stop_at`
               arguments."""
        )
        raise ValueError(
            """Please provide at most one of the `stop_after_iterations` or `stop_at`
               arguments."""
        )

    if interval is not None:
        end = MISSING
        if stop_after_iterations is not None:
            # The live Timers API rejects the field name `iterations` that the
            # globus_sdk 4.8.0 docstrings document; it expects the count under `count`
            # while keeping the `condition` value as `"iterations"`.
            end = {"condition": "iterations", "count": stop_after_iterations}
        elif stop_at is not None:
            end = {"condition": "time", "datetime": stop_at}

        schedule = RecurringTimerSchedule(
            interval_seconds=time_string_to_integer_seconds(interval),
            start=start if start is not None else MISSING,
            end=end,
        )
    else:
        schedule = OnceTimerSchedule(datetime=run_at)

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
                {source_collection_name}. Please use the `source_collection_id` argument for
                disambiguation."""
        )
        raise ValueError(
            f"""For the `source_collection_name` argument, multiple collections found that are named:
                {source_collection_name}. Please use the `source_collection_id` argument for
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
            source_collection,
            destination_collection,
            label=label,
            sync_level=sync_level,
            verify_checksum=verify_checksum,
            preserve_timestamp=preserve_timestamp,
            encrypt_data=encrypt_data,
            skip_source_errors=skip_source_errors,
            fail_on_quota_errors=fail_on_quota_errors,
            notify_on_succeeded=notify_on_succeeded,
            notify_on_failed=notify_on_failed,
            notify_on_inactive=notify_on_inactive,
        )
        for item in list_of_items:
            if item["source_path"][-1] == "/":
                tdata.add_item(
                    item["source_path"], item["destination_path"], recursive=True
                )
            else:
                tdata.add_item(item["source_path"], item["destination_path"])

        if replace:
            existing_timer = _find_existing_timer_by_name(
                current_timers_client=current_timers_client, name=name
            )

            if existing_timer is not None:
                if _timer_matches(
                    existing_timer=existing_timer,
                    name=name,
                    schedule=schedule,
                    tdata=tdata,
                ):
                    logger.info(
                        f"""Timer '{name}' already matches the requested configuration;
                            skipping replace."""
                    )
                    existing_timer["changed"] = False
                    return existing_timer

                logger.info(
                    f"""Timer '{name}' differs from the requested configuration; deleting
                        job_id:{existing_timer['job_id']} before recreating it."""
                )
                current_timers_client.delete_job(existing_timer["job_id"])
            else:
                logger.info(
                    f"No existing timer found with name '{name}'; creating a new one."
                )

        timer = TransferTimer(
            name=name if name is not None else MISSING,
            schedule=schedule,
            body=tdata,
        )
        timer_result = current_timers_client.create_timer(timer)["timer"]
        timer_result["changed"] = True
        logger.info(timer_result)
        return timer_result

    except Exception as ex:
        logger.exception("Failed to create timer...", exc_info=ex)
        raise ex
