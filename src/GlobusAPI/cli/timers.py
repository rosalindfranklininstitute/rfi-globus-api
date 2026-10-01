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

import logging

import click
from globus_sdk._missing import MISSING

from ..logging.logging import dump_with_auto_obfuscation, get_logger
from ..timers.timers import (
    create_timer,
    delete_timer,
    get_timer,
    pause_timer,
    resume_timer,
    timer_list,
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
def listtimers(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Timer_List")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    timer_list(
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
    "--timer-id",
    default=None,
    type=str,
    help="Globus API Timer ID. Either --timer-id or --timer-name must be provided, but not both.",
)
@click.option(
    "--timer-name",
    default=None,
    type=str,
    help="""Globus API Timer Name. Must match exactly one timer. Either --timer-id or --timer-name must be provided,
            but not both.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the gettimer response which is a dictionary output.",
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
def gettimer(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Get_Timer")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    timer_response = get_timer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        timer_id=ctx.obj["timer_id"],
        timer_name=ctx.obj["timer_name"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            # timer_response may be a plain dict (create_timer unwraps the "timer" key
            # from the GlobusHTTPResponse) or a GlobusHTTPResponse (get/delete return the
            # response directly); .get() called positionally works for both.
            click.echo(f"{timer_response.get(parameters[i])}")


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
    help="""Globus API Path to a JSON or YAML file with the list of items (files or directories) to be transferred by
            the timer.""",
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
@click.option("--name", default=None, type=str, help="A name for the timer.")
@click.option(
    "--interval",
    default=None,
    type=str,
    help="""The interval at which the timer recurs. Accepted formats "ss", "mm:ss", "hh:mm:ss". Either --interval or
            --run-at must be provided, but not both.""",
)
@click.option(
    "--start",
    default=None,
    type=str,
    help="""ISO 8601 datetime string for when a recurring timer should first run. Only used with --interval. If not
            provided, the timer starts immediately.""",
)
@click.option(
    "--stop-after-iterations",
    default=None,
    type=int,
    help="""Number of times a recurring timer should run before stopping. Only used with --interval. Mutually
            exclusive with --stop-at.""",
)
@click.option(
    "--stop-at",
    default=None,
    type=str,
    help="""ISO 8601 datetime string after which a recurring timer stops running. Only used with --interval. Mutually
            exclusive with --stop-after-iterations.""",
)
@click.option(
    "--run-at",
    default=None,
    type=str,
    help="""ISO 8601 datetime string for when a one-off timer should run. Either --interval or --run-at must be
            provided, but not both.""",
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
    "--replace",
    is_flag=True,
    default=False,
    help="""Make timer creation idempotent by --name: if exactly one existing timer already has this name, its
            name/schedule/transfer body are compared against the ones requested here. If they match, the existing
            timer is left alone and returned unchanged. If they differ, the existing timer is deleted before the
            new one is created. Requires --name.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the createtimer response which is a dictionary output.",
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
def createtimer(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Create_Timer")
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

    timer_response = create_timer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        item_list_filename=ctx.obj["item_list_filename"],
        source_collection_id=ctx.obj["source_collection_id"],
        source_collection_name=ctx.obj["source_collection_name"],
        destination_collection_id=ctx.obj["destination_collection_id"],
        destination_collection_name=ctx.obj["destination_collection_name"],
        name=ctx.obj["name"],
        interval=ctx.obj["interval"],
        start=ctx.obj["start"],
        stop_after_iterations=ctx.obj["stop_after_iterations"],
        stop_at=ctx.obj["stop_at"],
        run_at=ctx.obj["run_at"],
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
        replace=ctx.obj["replace"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            # timer_response may be a plain dict (create_timer unwraps the "timer" key
            # from the GlobusHTTPResponse) or a GlobusHTTPResponse (get/delete return the
            # response directly); .get() called positionally works for both.
            click.echo(f"{timer_response.get(parameters[i])}")


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
    "--timer-id",
    default=None,
    type=str,
    help="Globus API Timer ID. Either --timer-id or --timer-name must be provided, but not both.",
)
@click.option(
    "--timer-name",
    default=None,
    type=str,
    help="""Globus API Timer Name. Must match exactly one timer. Either --timer-id or --timer-name must be provided,
            but not both.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the deletetimer response which is a dictionary output.",
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
def deletetimer(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Delete_Timer")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    timer_response = delete_timer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        timer_id=ctx.obj["timer_id"],
        timer_name=ctx.obj["timer_name"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            # timer_response may be a plain dict (create_timer unwraps the "timer" key
            # from the GlobusHTTPResponse) or a GlobusHTTPResponse (get/delete return the
            # response directly); .get() called positionally works for both.
            click.echo(f"{timer_response.get(parameters[i])}")


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
    "--timer-id",
    default=None,
    type=str,
    help="Globus API Timer ID. Either --timer-id or --timer-name must be provided, but not both.",
)
@click.option(
    "--timer-name",
    default=None,
    type=str,
    help="""Globus API Timer Name. Must match exactly one timer. Either --timer-id or --timer-name must be provided,
            but not both.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the pausetimer response which is a dictionary output.",
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
def pausetimer(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Pause_Timer")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    timer_response = pause_timer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        timer_id=ctx.obj["timer_id"],
        timer_name=ctx.obj["timer_name"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{timer_response.get(parameters[i])}")


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
    "--timer-id",
    default=None,
    type=str,
    help="Globus API Timer ID. Either --timer-id or --timer-name must be provided, but not both.",
)
@click.option(
    "--timer-name",
    default=None,
    type=str,
    help="""Globus API Timer Name. Must match exactly one timer. Either --timer-id or --timer-name must be provided,
            but not both.""",
)
@click.option(
    "--update-credentials",
    default=None,
    type=str,
    help="""When true, replace the timer's refresh token using the credentials of this call. Can be used to
            resolve authorization errors, but could also introduce them if the new credentials lack a property of
            the ones they replace. If not supplied, the Timers service decides whether to replace credentials based
            on why the timer became inactive.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the resumetimer response which is a dictionary output.",
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
def resumetimer(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Resume_Timer")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["update_credentials"] is not None:
        ctx.obj["update_credentials"] = ctx.obj["update_credentials"] in (
            "True",
            "true",
        )

    timer_response = resume_timer(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        timer_id=ctx.obj["timer_id"],
        timer_name=ctx.obj["timer_name"],
        update_credentials=ctx.obj["update_credentials"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{timer_response.get(parameters[i])}")
