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

import logging

import click
from globus_sdk._missing import MISSING

from ..logging.logging import dump_with_auto_obfuscation, get_logger
from ..transfers.acl_rules import (
    acl_rule_list,
    add_acl_rule,
    delete_acl_rule,
    get_acl_rule,
    update_acl_rule,
)
from ..transfers.transfer_methods import (
    cancel_tasks,
    complete_delete,
    complete_transfer,
    get_monitored_collection,
    get_task,
    monitored_collection_list,
    submit_delete,
    submit_transfer,
    task_event_list,
    task_list,
    task_successful_transfers,
)
from ..transfers.url_methods import get_url

logger = get_logger(stdout=True)
LOGGING_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option("--task-id", required=True, type=str, help="Globus API Task ID.")
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def successfultransfers(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Task_Successful_Transfers")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    task_successful_transfers(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        task_id=ctx.obj["task_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--filter-status",
    default=None,
    type=str,
    help='Globus API Filter Status like "ACTIVE", "INACTIVE", "SUCCEEDED" or "FAILED".',
)
@click.option(
    "--filter-task-id", default=None, type=str, help="Globus API Filter Task IDs."
)
@click.option(
    "--filter-owner-uuid",
    default=None,
    type=str,
    help="Globus API Filter based on the UUID of the Task Owner.",
)
@click.option(
    "--filter-owner-identity",
    default=None,
    type=str,
    help="""Globus API Filter based on the identity of the Task Owner. The identity should end either with "orcid.org"
            or "globusid.org".""",
)
@click.option(
    "--filter-collection-id",
    default=None,
    type=str,
    help="""Globus API Filter based on the UUID of the Collection. It will return the tasks where the collection is
            either source collection or the destination collection, unless specified by the filter-collection-use.""",
)
@click.option(
    "--filter-collection-name",
    default=None,
    type=str,
    help="""Globus API Filter based on the name of the Collection. It will return the tasks where the collection is
            either source collection or the destination collection, unless specifiedby the filter-collection-use.""",
)
@click.option(
    "--filter-collection-use",
    default=None,
    type=str,
    help="""Globus API Filter to specify the usage of the collection specified by the filter-collection-id and/or
            filter-collection-id. It can be either "source" or "destination". If provided along side
            filter-collection-id and/or filter-collection-id then it will return  the tasks where the collection is used
            as specified by filter-collection-use.""",
)
@click.option(
    "--filter-is-paused",
    default=None,
    type=str,
    help="Globus API Filter if is_paused value is True.",
)
@click.option(
    "--filter-completion-time",
    default=None,
    type=str,
    help="Globus API Filter Completion Time.",
)
@click.option(
    "--filter-min-faults",
    default=None,
    type=int,
    help="Globus API Filter Minimum number of cumulative faults, inclusive.",
)
@click.option(
    "--filter-local-user",
    default=None,
    type=str,
    help="Globus API Filter A valid username for the target system running the endpoint, as a utf8 encoded string.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def tasklist(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Task_list")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["filter_status"] is not None:
        if len(ctx.obj["filter_status"].split(" ")) > 1:
            ctx.obj["filter_status"] = iter(ctx.obj["filter_status"].split(" "))
    else:
        ctx.obj["filter_status"] = MISSING

    if ctx.obj["filter_task_id"] is not None:
        if len(ctx.obj["filter_task_id"].split(" ")) > 1:
            ctx.obj["filter_task_id"] = iter(ctx.obj["filter_task_id"].split(" "))
    else:
        ctx.obj["filter_task_id"] = MISSING

    if ctx.obj["filter_owner_uuid"] is None:
        ctx.obj["filter_owner_uuid"] = MISSING

    if ctx.obj["filter_owner_identity"] is None:
        ctx.obj["filter_owner_identity"] = MISSING

    if ctx.obj["filter_collection_use"] is None:
        ctx.obj["filter_collection_use"] = MISSING

    if ctx.obj["filter_completion_time"] is not None:
        try:
            assert len(ctx.obj["filter_completion_time"].split(" ")) < 3
        except Exception as ex:
            logger.exception(
                "Completion time filter should have at most 2 dates...", exc_info=ex
            )
            raise ex
        if len(ctx.obj["filter_completion_time"].split(" ")) > 1:
            ctx.obj["filter_completion_time"] = tuple(
                ctx.obj["filter_completion_time"].split(" ")
            )
    else:
        ctx.obj["filter_completion_time"] = MISSING

    if ctx.obj["filter_is_paused"] is not None:
        ctx.obj["filter_is_paused"] = (
            ctx.obj["filter_is_paused"] == "True"
            or ctx.obj["filter_is_paused"] == "true"
        )
    else:
        ctx.obj["filter_is_paused"] = MISSING

    if ctx.obj["filter_min_faults"] is None:
        ctx.obj["filter_min_faults"] = MISSING

    if ctx.obj["filter_local_user"] is None:
        ctx.obj["filter_local_user"] = MISSING

    task_list(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        filter_status=ctx.obj["filter_status"],
        filter_task_id=ctx.obj["filter_task_id"],
        filter_owner_uuid=ctx.obj["filter_owner_uuid"],
        filter_owner_identity=ctx.obj["filter_owner_identity"],
        filter_collection_id=ctx.obj["filter_collection_id"],
        filter_collection_name=ctx.obj["filter_collection_name"],
        filter_collection_use=ctx.obj["filter_collection_use"],
        filter_completion_time=ctx.obj["filter_completion_time"],
        filter_min_faults=ctx.obj["filter_min_faults"],
        filter_local_user=ctx.obj["filter_local_user"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option("--task-id", required=True, type=str, help="Globus API Task ID.")
@click.option(
    "--filter-is-error", default=None, type=str, help="Globus API Filter Endpoint."
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def taskeventlist(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Task_event_list")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["filter_is_error"] is not None:
        ctx.obj["filter_is_error"] = (
            ctx.obj["filter_is_error"] == "True" or ctx.obj["filter_is_error"] == "true"
        )
        if not ctx.obj["filter_is_error"]:
            ctx.obj["filter_is_error"] = None
            logger.info(
                """A value of False for the --filter-is-error option, (returning only non-errors) is not
                   supported. Events will not be filtered."""
            )
    else:
        ctx.obj["filter_is_error"] = MISSING

    task_event_list(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        task_id=ctx.obj["task_id"],
        filter_is_error=ctx.obj["filter_is_error"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--item-list-filename",
    required=True,
    type=str,
    help="""Globus API Path to a JSON or YAML file with the list of items (files or directories) to be submitted for
            transfer.""",
)
@click.option(
    "--filter-rule-list-filename",
    type=str,
    help="""Globus API Path to a JSON or YAML file with the list of transfer filter rules that will be used for the item
            transfer.""",
)
@click.option(
    "--source-collection-id",
    default=None,
    type=str,
    help="Globus API Source Collection UUID.",
)
@click.option(
    "--source-collection-name",
    default=None,
    type=str,
    help="Globus API Source Collection Name.",
)
@click.option(
    "--destination-collection-id",
    default=None,
    type=str,
    help="Globus API Destination Collection UUID.",
)
@click.option(
    "--destination-collection-name",
    default=None,
    type=str,
    help="Globus API Destination Collection Name.",
)
@click.option("--label", default=None, type=str, help="Globus API Transfer label.")
@click.option(
    "--sync-level", default=None, type=int, help="Globus API Transfer sync level."
)
@click.option(
    "--verify-checksum",
    default=None,
    type=str,
    help="Globus API Transfer verify checksum.",
)
@click.option(
    "--preserve-timestamp",
    default=None,
    type=str,
    help="Globus API Transfer preserve timestamp.",
)
@click.option(
    "--encrypt-data", default=None, type=str, help="Globus API Transfer encrypt data."
)
@click.option(
    "--skip-source-errors",
    default=None,
    type=str,
    help="Globus API Transfer skip source errors.",
)
@click.option(
    "--fail-on-quota-errors",
    default=None,
    type=str,
    help="Globus API Transfer fail on quota errors .",
)
@click.option(
    "--notify-on-succeeded",
    default=None,
    type=str,
    help="Globus API Transfer notify on succeeded.",
)
@click.option(
    "--notify-on-failed",
    default=None,
    type=str,
    help="Globus API Transfer notify on failed.",
)
@click.option(
    "--notify-on-inactive",
    default=None,
    type=str,
    help="Globus API Transfer notify on inactive.",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the submittransfer response which is a dictionary output.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def submittransfer(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Submit_Transfer")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["label"] is None:
        ctx.obj["label"] = MISSING

    if ctx.obj["sync_level"] is None:
        ctx.obj["sync_level"] = MISSING

    if ctx.obj["verify_checksum"] is not None:
        ctx.obj["verify_checksum"] = (
            ctx.obj["verify_checksum"] == "True" or ctx.obj["verify_checksum"] == "true"
        )
    else:
        ctx.obj["verify_checksum"] = MISSING

    if ctx.obj["preserve_timestamp"] is not None:
        ctx.obj["preserve_timestamp"] = (
            ctx.obj["preserve_timestamp"] == "True"
            or ctx.obj["preserve_timestamp"] == "true"
        )
    else:
        ctx.obj["preserve_timestamp"] = MISSING

    if ctx.obj["encrypt_data"] is not None:
        ctx.obj["encrypt_data"] = (
            ctx.obj["encrypt_data"] == "True" or ctx.obj["encrypt_data"] == "true"
        )
    else:
        ctx.obj["encrypt_data"] = MISSING

    if ctx.obj["skip_source_errors"] is not None:
        ctx.obj["skip_source_errors"] = (
            ctx.obj["skip_source_errors"] == "True"
            or ctx.obj["skip_source_errors"] == "true"
        )
    else:
        ctx.obj["skip_source_errors"] = MISSING

    if ctx.obj["fail_on_quota_errors"] is not None:
        ctx.obj["fail_on_quota_errors"] = (
            ctx.obj["fail_on_quota_errors"] == "True"
            or ctx.obj["fail_on_quota_errors"] == "true"
        )
    else:
        ctx.obj["fail_on_quota_errors"] = MISSING

    if ctx.obj["notify_on_succeeded"] is not None:
        ctx.obj["notify_on_succeeded"] = (
            ctx.obj["notify_on_succeeded"] == "True"
            or ctx.obj["notify_on_succeeded"] == "true"
        )
    else:
        ctx.obj["notify_on_succeeded"] = MISSING

    if ctx.obj["notify_on_failed"] is not None:
        ctx.obj["notify_on_failed"] = (
            ctx.obj["notify_on_failed"] == "True"
            or ctx.obj["notify_on_failed"] == "true"
        )
    else:
        ctx.obj["notify_on_failed"] = MISSING

    if ctx.obj["notify_on_inactive"] is not None:
        ctx.obj["notify_on_inactive"] = (
            ctx.obj["notify_on_inactive"] == "True"
            or ctx.obj["notify_on_inactive"] == "true"
        )
    else:
        ctx.obj["notify_on_inactive"] = MISSING

    transfer_response = submit_transfer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        item_list_filename=ctx.obj["item_list_filename"],
        filter_rule_list_filename=ctx.obj["filter_rule_list_filename"],
        source_collection_id=ctx.obj["source_collection_id"],
        source_collection_name=ctx.obj["source_collection_name"],
        destination_collection_id=ctx.obj["destination_collection_id"],
        destination_collection_name=ctx.obj["destination_collection_name"],
        label=ctx.obj["label"],
        sync_level=ctx.obj["sync_level"],
        verify_checksum=ctx.obj["verify_checksum"],
        preserve_timestamp=ctx.obj["preserve_timestamp"],
        encrypt_data=ctx.obj["encrypt_data"],
        skip_source_errors=ctx.obj["skip_source_errors"],
        fail_on_quota_errors=ctx.obj["fail_on_quota_errors"],
        notify_on_succeeded=ctx.obj["notify_on_succeeded"],
        notify_on_failed=ctx.obj["notify_on_failed"],
        notify_on_inactive=ctx.obj["notify_on_inactive"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{transfer_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--item-list-filename",
    required=True,
    type=str,
    help="""Globus API Path to a JSON or YAML file with the list of items (files or directories) to be submitted for
            transfer.""",
)
@click.option(
    "--collection-id",
    default=None,
    type=str,
    help="Globus API Source Collection UUID.",
)
@click.option(
    "--collection-name",
    default=None,
    type=str,
    help="Globus API Source Collection Name.",
)
@click.option("--label", default=None, type=str, help="Globus API Delete label.")
@click.option(
    "--recursive", default="True", type=str, help="Globus API Delete recursive."
)
@click.option(
    "--ignore-missing",
    default=None,
    type=str,
    help="Globus API Delete ignore missing.",
)
@click.option(
    "--interpret-globs",
    default=None,
    type=str,
    help="Globus API Delete interpret globs .",
)
@click.option(
    "--notify-on-succeeded",
    default=None,
    type=str,
    help="Globus API Delete notify on succeeded.",
)
@click.option(
    "--notify-on-failed",
    default=None,
    type=str,
    help="Globus API Delete  notify on failed.",
)
@click.option(
    "--notify-on-inactive",
    default=None,
    type=str,
    help="Globus API Delete notify on inactive.",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the submittransfer response which is a dictionary output.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def submitdelete(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Submit_Delete")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["label"] is None:
        ctx.obj["label"] = MISSING

    if ctx.obj["recursive"] is not None:
        ctx.obj["recursive"] = (
            ctx.obj["recursive"] == "True" or ctx.obj["recursive"] == "true"
        )
    else:
        ctx.obj["recursive"] = MISSING

    if ctx.obj["ignore_missing"] is not None:
        ctx.obj["ignore_missing"] = (
            ctx.obj["ignore_missing"] == "True" or ctx.obj["ignore_missing"] == "true"
        )
    else:
        ctx.obj["ignore_missing"] = MISSING

    if ctx.obj["interpret_globs"] is not None:
        ctx.obj["interpret_globs"] = (
            ctx.obj["interpret_globs"] == "True" or ctx.obj["interpret_globs"] == "true"
        )
    else:
        ctx.obj["interpret_globs"] = MISSING

    if ctx.obj["notify_on_succeeded"] is not None:
        ctx.obj["notify_on_succeeded"] = (
            ctx.obj["notify_on_succeeded"] == "True"
            or ctx.obj["notify_on_succeeded"] == "true"
        )
    else:
        ctx.obj["notify_on_succeeded"] = MISSING

    if ctx.obj["notify_on_failed"] is not None:
        ctx.obj["notify_on_failed"] = (
            ctx.obj["notify_on_failed"] == "True"
            or ctx.obj["notify_on_failed"] == "true"
        )
    else:
        ctx.obj["notify_on_failed"] = MISSING

    if ctx.obj["notify_on_inactive"] is not None:
        ctx.obj["notify_on_inactive"] = (
            ctx.obj["notify_on_inactive"] == "True"
            or ctx.obj["notify_on_inactive"] == "true"
        )
    else:
        ctx.obj["notify_on_inactive"] = MISSING

    deletion_response = submit_delete(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        item_list_filename=ctx.obj["item_list_filename"],
        collection_id=ctx.obj["collection_id"],
        collection_name=ctx.obj["collection_name"],
        label=ctx.obj["label"],
        recursive=ctx.obj["recursive"],
        ignore_missing=ctx.obj["ignore_missing"],
        interpret_globs=ctx.obj["interpret_globs"],
        notify_on_succeeded=ctx.obj["notify_on_succeeded"],
        notify_on_failed=ctx.obj["notify_on_failed"],
        notify_on_inactive=ctx.obj["notify_on_inactive"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{deletion_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--item-list-filename",
    required=True,
    type=str,
    help="""Globus API Path to a JSON or YAML file with the list of items (files or directories) to be submitted for
            transfer.""",
)
@click.option(
    "--filter-rule-list-filename",
    type=str,
    help="""Globus API Path to a JSON or YAML file with the list of transfer filter rules that will be used for the item
            transfer.""",
)
@click.option(
    "--source-collection-id",
    default=None,
    type=str,
    help="Globus API Source Collection UUID.",
)
@click.option(
    "--source-collection-name",
    default=None,
    type=str,
    help="Globus API Source Collection Name.",
)
@click.option(
    "--destination-collection-id",
    default=None,
    type=str,
    help="Globus API Destination Collection UUID.",
)
@click.option(
    "--destination-collection-name",
    default=None,
    type=str,
    help="Globus API Destination Collection Name.",
)
@click.option("--label", default=None, type=str, help="Globus API Transfer label.")
@click.option(
    "--sync-level", default=None, type=int, help="Globus API Transfer sync level."
)
@click.option(
    "--verify-checksum",
    default=None,
    type=str,
    help="Globus API Transfer verify checksum.",
)
@click.option(
    "--preserve-timestamp",
    default=None,
    type=str,
    help="Globus API Transfer preserve timestamp.",
)
@click.option(
    "--encrypt-data", default=None, type=str, help="Globus API Transfer encrypt data."
)
@click.option(
    "--skip-source-errors",
    default=None,
    type=str,
    help="Globus API Transfer skip source errors.",
)
@click.option(
    "--fail-on-quota-errors",
    default=None,
    type=str,
    help="Globus API Transfer fail on quota errors .",
)
@click.option(
    "--notify-on-succeeded",
    default=None,
    type=str,
    help="Globus API Transfer notify on succeeded.",
)
@click.option(
    "--notify-on-failed",
    default=None,
    type=str,
    help="Globus API Transfer notify on failed.",
)
@click.option(
    "--notify-on-inactive",
    default=None,
    type=str,
    help="Globus API Transfer notify on inactive.",
)
@click.option(
    "--check-interval",
    default="00:00:30",
    type=str,
    help="""Globus API Transfer status check time interval. Accepted formats "ss", "mm:ss", "hh:mm:ss".
            Default is "00:00:30" aka 30 seconds.""",
)
@click.option(
    "--autocancel-period",
    default="00:00:00",
    type=str,
    help="""Globus API Transfer Inactivity wait period before cancelling the task. Accepted formats "ss", "mm:ss",
           "hh:mm:ss". Default is "00:00:00" seconds.""",
)
@click.option(
    "--transfer-json",
    default=None,
    type=str,
    help="""Path to the JSON file that stores the command's list of successful transfers response and 
            the transfer's list of events.""",
)
@click.option(
    "--transfer-yaml",
    default=None,
    type=str,
    help="""Path to the YAML file that stores the command's list of successful transfers response and 
            the transfer's list of events.""",
)
@click.option(
    "--task-json",
    default=None,
    type=str,
    help="Path to the JSON file that stores the command's final transfer task response.",
)
@click.option(
    "--task-yaml",
    default=None,
    type=str,
    help="Path to the YAML file that stores the command's final transfer task response.",
)
@click.pass_context
def completetransfer(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Complete_Transfer")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["label"] is None:
        ctx.obj["label"] = MISSING

    if ctx.obj["sync_level"] is None:
        ctx.obj["sync_level"] = MISSING

    if ctx.obj["verify_checksum"] is not None:
        ctx.obj["verify_checksum"] = (
            ctx.obj["verify_checksum"] == "True" or ctx.obj["verify_checksum"] == "true"
        )
    else:
        ctx.obj["verify_checksum"] = MISSING

    if ctx.obj["preserve_timestamp"] is not None:
        ctx.obj["preserve_timestamp"] = (
            ctx.obj["preserve_timestamp"] == "True"
            or ctx.obj["preserve_timestamp"] == "true"
        )
    else:
        ctx.obj["preserve_timestamp"] = MISSING

    if ctx.obj["encrypt_data"] is not None:
        ctx.obj["encrypt_data"] = (
            ctx.obj["encrypt_data"] == "True" or ctx.obj["encrypt_data"] == "true"
        )
    else:
        ctx.obj["encrypt_data"] = MISSING

    if ctx.obj["skip_source_errors"] is not None:
        ctx.obj["skip_source_errors"] = (
            ctx.obj["skip_source_errors"] == "True"
            or ctx.obj["skip_source_errors"] == "true"
        )
    else:
        ctx.obj["skip_source_errors"] = MISSING

    if ctx.obj["fail_on_quota_errors"] is not None:
        ctx.obj["fail_on_quota_errors"] = (
            ctx.obj["fail_on_quota_errors"] == "True"
            or ctx.obj["fail_on_quota_errors"] == "true"
        )
    else:
        ctx.obj["fail_on_quota_errors"] = MISSING

    if ctx.obj["notify_on_succeeded"] is not None:
        ctx.obj["notify_on_succeeded"] = (
            ctx.obj["notify_on_succeeded"] == "True"
            or ctx.obj["notify_on_succeeded"] == "true"
        )
    else:
        ctx.obj["notify_on_succeeded"] = MISSING

    if ctx.obj["notify_on_failed"] is not None:
        ctx.obj["notify_on_failed"] = (
            ctx.obj["notify_on_failed"] == "True"
            or ctx.obj["notify_on_failed"] == "true"
        )
    else:
        ctx.obj["notify_on_failed"] = MISSING

    if ctx.obj["notify_on_inactive"] is not None:
        ctx.obj["notify_on_inactive"] = (
            ctx.obj["notify_on_inactive"] == "True"
            or ctx.obj["notify_on_inactive"] == "true"
        )
    else:
        ctx.obj["notify_on_inactive"] = MISSING

    complete_transfer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        item_list_filename=ctx.obj["item_list_filename"],
        filter_rule_list_filename=ctx.obj["filter_rule_list_filename"],
        source_collection_id=ctx.obj["source_collection_id"],
        source_collection_name=ctx.obj["source_collection_name"],
        destination_collection_id=ctx.obj["destination_collection_id"],
        destination_collection_name=ctx.obj["destination_collection_name"],
        label=ctx.obj["label"],
        sync_level=ctx.obj["sync_level"],
        verify_checksum=ctx.obj["verify_checksum"],
        preserve_timestamp=ctx.obj["preserve_timestamp"],
        encrypt_data=ctx.obj["encrypt_data"],
        skip_source_errors=ctx.obj["skip_source_errors"],
        fail_on_quota_errors=ctx.obj["fail_on_quota_errors"],
        notify_on_succeeded=ctx.obj["notify_on_succeeded"],
        notify_on_failed=ctx.obj["notify_on_failed"],
        notify_on_inactive=ctx.obj["notify_on_inactive"],
        status_change_check_interval=ctx.obj["check_interval"],
        auto_cancel_if_inactive_wait_period=ctx.obj["autocancel_period"],
        transfer_json=ctx.obj["transfer_json"],
        transfer_yaml=ctx.obj["transfer_yaml"],
        task_json=ctx.obj["task_json"],
        task_yaml=ctx.obj["task_yaml"],
    )


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--item-list-filename",
    required=True,
    type=str,
    help="""Globus API Path to a JSON or YAML file with the list of items (files or directories) to be submitted for
            transfer.""",
)
@click.option(
    "--collection-id",
    default=None,
    type=str,
    help="Globus API Source Collection UUID.",
)
@click.option(
    "--collection-name",
    default=None,
    type=str,
    help="Globus API Source Collection Name.",
)
@click.option("--label", default=None, type=str, help="Globus API Delete label.")
@click.option(
    "--recursive", default=True, type=str, help="Globus API Delete recursive."
)
@click.option(
    "--ignore-missing",
    default=None,
    type=str,
    help="Globus API Delete ignore missing.",
)
@click.option(
    "--interpret-globs",
    default=None,
    type=str,
    help="Globus API Delete interpret globs .",
)
@click.option(
    "--notify-on-succeeded",
    default=None,
    type=str,
    help="Globus API Delete notify on succeeded.",
)
@click.option(
    "--notify-on-failed",
    default=None,
    type=str,
    help="Globus API Delete  notify on failed.",
)
@click.option(
    "--notify-on-inactive",
    default=None,
    type=str,
    help="Globus API Delete notify on inactive.",
)
@click.option(
    "--check-interval",
    default="00:00:30",
    type=str,
    help="""Globus API Delete status check time interval. Accepted formats "ss", "mm:ss", "hh:mm:ss".
            Default is "00:00:30" aka 30 seconds.""",
)
@click.option(
    "--autocancel-period",
    default="00:00:00",
    type=str,
    help="""Globus API Delete Inactivity wait period before cancelling the task. Accepted formats "ss", "mm:ss",
           "hh:mm:ss". Default is "00:00:00" seconds.""",
)
@click.option(
    "--delete-json",
    default=None,
    type=str,
    help="""Path to the JSON file that stores the command's list of successful deletions response and 
            the deletion's list of events.""",
)
@click.option(
    "--delete-yaml",
    default=None,
    type=str,
    help="""Path to the YAML file that stores the command's list of successful deletions response and 
            the deletion's list of events.""",
)
@click.option(
    "--task-json",
    default=None,
    type=str,
    help="Path to the JSON file that stores the command's final deletion task response.",
)
@click.option(
    "--task-yaml",
    default=None,
    type=str,
    help="Path to the YAML file that stores the command's final deletion task response.",
)
@click.pass_context
def completedelete(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Complete_Delete")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["label"] is None:
        ctx.obj["label"] = MISSING

    if ctx.obj["recursive"] is not None:
        ctx.obj["recursive"] = (
            ctx.obj["recursive"] == "True" or ctx.obj["recursive"] == "true"
        )
    else:
        ctx.obj["recursive"] = MISSING

    if ctx.obj["ignore_missing"] is not None:
        ctx.obj["ignore_missing"] = (
            ctx.obj["ignore_missing"] == "True" or ctx.obj["ignore_missing"] == "true"
        )
    else:
        ctx.obj["ignore_missing"] = MISSING

    if ctx.obj["interpret_globs"] is not None:
        ctx.obj["interpret_globs"] = (
            ctx.obj["interpret_globs"] == "True" or ctx.obj["interpret_globs"] == "true"
        )
    else:
        ctx.obj["interpret_globs"] = MISSING

    if ctx.obj["notify_on_succeeded"] is not None:
        ctx.obj["notify_on_succeeded"] = (
            ctx.obj["notify_on_succeeded"] == "True"
            or ctx.obj["notify_on_succeeded"] == "true"
        )
    else:
        ctx.obj["notify_on_succeeded"] = MISSING

    if ctx.obj["notify_on_failed"] is not None:
        ctx.obj["notify_on_failed"] = (
            ctx.obj["notify_on_failed"] == "True"
            or ctx.obj["notify_on_failed"] == "true"
        )
    else:
        ctx.obj["notify_on_failed"] = MISSING

    if ctx.obj["notify_on_inactive"] is not None:
        ctx.obj["notify_on_inactive"] = (
            ctx.obj["notify_on_inactive"] == "True"
            or ctx.obj["notify_on_inactive"] == "true"
        )
    else:
        ctx.obj["notify_on_inactive"] = MISSING

    complete_delete(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        item_list_filename=ctx.obj["item_list_filename"],
        collection_id=ctx.obj["collection_id"],
        collection_name=ctx.obj["collection_name"],
        label=ctx.obj["label"],
        recursive=ctx.obj["recursive"],
        ignore_missing=ctx.obj["ignore_missing"],
        interpret_globs=ctx.obj["interpret_globs"],
        notify_on_succeeded=ctx.obj["notify_on_succeeded"],
        notify_on_failed=ctx.obj["notify_on_failed"],
        notify_on_inactive=ctx.obj["notify_on_inactive"],
        status_change_check_interval=ctx.obj["check_interval"],
        auto_cancel_if_inactive_wait_period=ctx.obj["autocancel_period"],
        delete_json=ctx.obj["delete_json"],
        delete_yaml=ctx.obj["delete_yaml"],
        task_json=ctx.obj["task_json"],
        task_yaml=ctx.obj["task_yaml"],
    )


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option("--task-ids", required=True, type=str, help="Globus API Task IDs.")
@click.option(
    "--message", default="Tasks Cancellation", type=str, help="Globus API Message."
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="""Print one parameter from the canceltasks response which is a dictionary output.""",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def canceltasks(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Cancel_Tasks")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    transfer_response = cancel_tasks(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        task_ids=ctx.obj["task_ids"],
        message=ctx.obj["message"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{transfer_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option("--task-id", required=True, type=str, help="Globus API Task IDs.")
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the gettask response which is a dictionary output.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def gettask(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Get_Task")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    transfer_info = get_task(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        task_id=ctx.obj["task_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{transfer_info.get(key=parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--collection-name", default=None, type=str, help="Globus Mapped Collection name."
)
@click.option(
    "--collection-id", default=None, type=str, help="Globus Mapped Collection ID."
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def aclrulelist(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("ACL_List")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    acl_rule_list(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--collection-name", default=None, type=str, help="Globus Mapped Collection name."
)
@click.option(
    "--collection-id", default=None, type=str, help="Globus Mapped Collection ID."
)
@click.option(
    "--user-identity", default=None, type=str, help="Globus API user identity."
)
@click.option(
    "--principal",
    default=None,
    type=str,
    help="""Globus API Principal. The UUID of a user's or
                                                             group's identity.""",
)
@click.option("--path", default=None, type=str, help="Globus API Permission Path.")
@click.option(
    "--permissions",
    default=None,
    type=str,
    help='Globus API Permissions, either "r" or "rw".',
)
@click.option("--rule-id", default=None, type=str, help="Globus API Rule ID.")
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the getaclrule response which is a dictionary output.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def getaclrule(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Get_ACL_Rule")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    acl_info = get_acl_rule(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        user_identity=ctx.obj["user_identity"],
        principal=ctx.obj["principal"],
        path=ctx.obj["path"],
        permissions=ctx.obj["permissions"],
        rule_id=ctx.obj["rule_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if len(acl_info) > 1:
        click.echo(
            "Multiple ACL rules found. You may want to use the --rule-id argument for disambiguation."
        )
        if ctx.obj["print_parameter"] is not None:
            click.echo(
                "Multiple ACL rules found. The --print_parameter will not be displayed."
            )
    else:
        if ctx.obj["print_parameter"] is not None:
            parameters = ctx.obj["print_parameter"].split(" ")
            for i in range(0, len(parameters)):
                click.echo(f"{acl_info.get(key=parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--collection-name", default=None, type=str, help="Globus Mapped Collection name."
)
@click.option(
    "--collection-id", default=None, type=str, help="Globus Mapped Collection ID."
)
@click.option(
    "--user-identity", default=None, type=str, help="Globus API user identity."
)
@click.option(
    "--principal-type",
    default="identity",
    type=str,
    help='Globus API Principal Type. It can be "identity" or "group".',
)
@click.option(
    "--principal",
    default=None,
    type=str,
    help="Globus API Principal. The UUID of a user's or group's identity.",
)
@click.option(
    "--path",
    default="/",
    type=str,
    help='Globus API Permission Path. Default is "/" which is is the root.',
)
@click.option(
    "--permissions",
    default="r",
    type=str,
    help='Globus API Permissions, either "r" for read-only or "rw" for read & write. Default is "rw".',
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the addaclrule response which is a dictionary output.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def addaclrule(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Add_ACL_Rule")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    acl_info = add_acl_rule(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        user_identity=ctx.obj["user_identity"],
        principal_type=ctx.obj["principal_type"],
        principal=ctx.obj["principal"],
        path=ctx.obj["path"],
        permissions=ctx.obj["permissions"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{acl_info.get(key=parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--collection-name", default=None, type=str, help="Globus Mapped Collection name."
)
@click.option(
    "--collection-id", default=None, type=str, help="Globus Mapped Collection ID."
)
@click.option(
    "--user-identity", default=None, type=str, help="Globus API user identity."
)
@click.option(
    "--principal",
    default=None,
    type=str,
    help="Globus API Principal. The UUID of a user's or group's identity.",
)
@click.option("--path", default=None, type=str, help="Globus API Permission Path.")
@click.option(
    "--permissions",
    default=None,
    type=str,
    help='Globus API Permissions, either "r" or "rw".',
)
@click.option("--rule-id", default=None, type=str, help="Globus API Rule ID.")
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the deleteaclrule response which is a dictionary output.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def deleteaclrule(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Delete_ACL_Rule")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    acl_info = delete_acl_rule(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        user_identity=ctx.obj["user_identity"],
        principal=ctx.obj["principal"],
        path=ctx.obj["path"],
        permissions=ctx.obj["permissions"],
        rule_id=ctx.obj["rule_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{acl_info.get(key=parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--new-permissions", type=str, help='Globus API Permissions, either "r" or "rw".'
)
@click.option(
    "--collection-name", default=None, type=str, help="Globus Mapped Collection name."
)
@click.option(
    "--collection-id", default=None, type=str, help="Globus Mapped Collection ID."
)
@click.option(
    "--user-identity", default=None, type=str, help="Globus API user identity."
)
@click.option(
    "--principal",
    default=None,
    type=str,
    help="""Globus API Principal. The UUID of a user's or
                                                             group's identity.""",
)
@click.option("--path", default=None, type=str, help="Globus API Permission Path.")
@click.option(
    "--permissions",
    default=None,
    type=str,
    help='Globus API Permissions, either "r" or "rw".',
)
@click.option("--rule-id", default=None, type=str, help="Globus API Rule ID.")
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the updateaclrule response which is a dictionary output.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def updateaclrule(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Update_ACL_Rule")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    acl_info = update_acl_rule(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        new_permissions=ctx.obj["new_permissions"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        user_identity=ctx.obj["user_identity"],
        principal=ctx.obj["principal"],
        path=ctx.obj["path"],
        permissions=ctx.obj["permissions"],
        rule_id=ctx.obj["rule_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{acl_info.get(key=parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--collection-name", type=str, default=None, help="Globus guest collection name."
)
@click.option(
    "--collection-id", type=str, default=None, help="Globus guest collection id."
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the getmonitoredcollection response which is a dictionary output.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def getmonitoredcollection(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Get_monitored_collection")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    transfer_response = get_monitored_collection(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )
    if len(transfer_response) > 1:
        click.echo(
            "Multiple collections found. You may want to use the --collection-id argument for disambiguation."
        )
        if ctx.obj["print_parameter"] is not None:
            click.echo(
                "Multiple collections found. The --print_parameter will not be displayed."
            )
    else:
        if ctx.obj["print_parameter"] is not None:
            parameters = ctx.obj["print_parameter"].split(" ")
            for i in range(0, len(parameters)):
                click.echo(f"{transfer_response[0].get(parameters[i])}")


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def monitoredcollectionlist(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Monitored_collection_list")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    monitored_collection_list(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    type=int,
    help="""Verbose output. Use multiple times for more output. -v for INFO, -vv for DEBUG. If you use it three or more
            times, then the verbose output would be equal of using it only 2 times e.g. -vvv for DEBUG, -vvvv for
            DEBUG, etc.""",
)
@click.option(
    "--collection-id",
    default=None,
    type=str,
    help="Globus API Collection UUID.",
)
@click.option(
    "--collection-name",
    default=None,
    type=str,
    help="Globus API Collection Name.",
)
@click.option("--path", default="/", type=str, help="Globus API Permission Path.")
@click.option(
    "--print-url",
    is_flag=True,
    help="Print the URL based on the provided collection and path. Type True or False.",
)
@click.option(
    "--json",
    default=None,
    type=str,
    help="Path to a JSON file to store the command's output response.",
)
@click.option(
    "--yaml",
    default=None,
    type=str,
    help="Path to a YAML file to store the command's output response.",
)
@click.pass_context
def geturl(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Get_URL")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    url = get_url(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        path=ctx.obj["path"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_url"]:
        click.echo(f"{url}")
