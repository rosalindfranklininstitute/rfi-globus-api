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
    complete_transfer,
    get_monitored_collection,
    get_task,
    monitored_collection_list,
    submit_transfer,
    task_event_list,
    task_list,
    task_successful_transfers,
)

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

    if ctx.obj["filter_task_id"] is not None:
        if len(ctx.obj["filter_task_id"].split(" ")) > 1:
            ctx.obj["filter_task_id"] = iter(ctx.obj["filter_task_id"].split(" "))

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

    if ctx.obj["filter_is_paused"] is not None:
        ctx.obj["filter_is_paused"] = (
            ctx.obj["filter_is_paused"] == "True"
            or ctx.obj["filter_is_paused"] == "true"
        )

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
    help="Globus API Path to a JSON or YAML file with the list of transfers to be submitted.",
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

    transfer_response = submit_transfer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        item_list_filename=ctx.obj["item_list_filename"],
        source_collection_id=ctx.obj["source_collection_id"],
        source_collection_name=ctx.obj["source_collection_name"],
        destination_collection_id=ctx.obj["destination_collection_id"],
        destination_collection_name=ctx.obj["destination_collection_name"],
        label=ctx.obj["label"],
        sync_level=ctx.obj["sync_level"],
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
    help="Globus API Path to a JSON or YAML file with the list of transfers to be submitted.",
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
    "--check-interval",
    default="00:01:00",
    type=str,
    help="""Globus API Transfer status check time interval. Accepted formats "ss", "mm:ss", "hh:mm:ss".
            Default is "00:01:00" seconds.""",
)
@click.option(
    "--autocancel-period",
    default="00:00:00",
    type=str,
    help="""Globus API Transfer Inactivity wait period before cancelling the task. Accepted formats "ss", "mm:ss",
           "hh:mm:ss". Default is "00:00:00" seconds.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the completetransfer response which is a dictionary output.",
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
def completetransfer(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Complete_Transfer")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    transfer_response = complete_transfer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        item_list_filename=ctx.obj["item_list_filename"],
        source_collection_id=ctx.obj["source_collection_id"],
        source_collection_name=ctx.obj["source_collection_name"],
        destination_collection_id=ctx.obj["destination_collection_id"],
        destination_collection_name=ctx.obj["destination_collection_name"],
        label=ctx.obj["label"],
        sync_level=ctx.obj["sync_level"],
        status_change_check_interval=ctx.obj["check_interval"],
        auto_cancel_if_inactive_wait_period=ctx.obj["autocancel_period"],
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
