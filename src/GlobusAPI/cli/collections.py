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

from ..collections.guest import (
    create_guest_collection,
    delete_guest_collection,
    get_guest_collection,
    guest_collection_list,
    update_guest_collection,
)
from ..collections.roles import create_role, delete_role, get_role, role_list
from ..logging.logging import dump_with_auto_obfuscation, get_logger

logger = get_logger(stdout=True)
LOGGING_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]


@click.command()
@click.option(
    "--collection-name", required=True, type=str, help="Globus guest collection name."
)
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
)
@click.option(
    "--base-path", default="/", type=str, help="Globus base path of guest collection."
)
@click.option(
    "--wait-period",
    default="00:00:30",
    type=str,
    help="""Globus wait period after a collection is created to ensure that command's execution has been concluded in
            the Globus servers.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the createguestcollection response which is a dictionary output.",
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
@click.pass_context
def createguestcollection(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Create_guest_collection")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    gcs_response = create_guest_collection(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        collection_name=ctx.obj["collection_name"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        base_path=ctx.obj["base_path"],
        wait_period=ctx.obj["wait_period"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{gcs_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
)
@click.option(
    "--collection-name", default=None, type=str, help="Globus guest collection name."
)
@click.option(
    "--collection-id", default=None, type=str, help="Globus guest collection id."
)
@click.option(
    "--wait-period",
    default="00:00:30",
    type=str,
    help="""Globus wait period after a collection is deleted to ensure that command's execution has been concluded in
            the Globus servers.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the deleteguestcollection response which is a dictionary output.",
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
@click.pass_context
def deleteguestcollection(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Delete_guest_collection")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    gcs_response = delete_guest_collection(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        wait_period=ctx.obj["wait_period"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{gcs_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
)
@click.option(
    "--collection-name", default=None, type=str, help="Globus guest collection name."
)
@click.option(
    "--collection-id", default=None, type=str, help="Globus guest collection id."
)
@click.option(
    "--new-collection-name",
    default=None,
    type=str,
    help="Globus new guest collection name.",
)
@click.option(
    "--public",
    default=None,
    type=str,
    help="Globus Make the guest collection public or not.",
)
@click.option(
    "--wait-period",
    default="00:00:30",
    type=str,
    help="""Globus wait period after a collection is deleted to ensure that command's execution has been concluded in
            the Globus servers.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the updateguestcollection response which is a dictionary output.",
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
@click.pass_context
def updateguestcollection(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Update_guest_collection")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["public"] is not None:
        ctx.obj["public"] = ctx.obj["public"] == "True" or ctx.obj["public"] == "true"

    gcs_response = update_guest_collection(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        new_collection_name=ctx.obj["new_collection_name"],
        public=ctx.obj["public"],
        wait_period=ctx.obj["wait_period"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{gcs_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
)
@click.option(
    "--collection-name", type=str, default=None, help="Globus guest collection name."
)
@click.option(
    "--collection-id", type=str, default=None, help="Globus guest collection id."
)
@click.option(
    "--filter",
    default=None,
    type=str,
    help="""Globus filter collections, input a whitespace separated list of any of the following "mapped_collections",
            "guest_collections", "managed_by_me", "created_by_me", to filter which collections will be returned.""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the getguestcollection response which is a dictionary output.",
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
@click.pass_context
def getguestcollection(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Get_guest_collection")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["filter"] is not None:
        if len(ctx.obj["filter"].split(" ")) > 1:
            ctx.obj["filter"] = iter(ctx.obj["filter"].split(" "))

    gcs_response = get_guest_collection(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        filter_to_help=ctx.obj["filter"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )
    if len(gcs_response) > 1:
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
                click.echo(f"{gcs_response[0].get(parameters[i])}")


@click.command()
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
)
@click.option(
    "--filter",
    default=None,
    type=str,
    help="""Globus filter collections, input a whitespace separated list of any of the following "mapped_collections",
            "guest_collections", "managed_by_me", "created_by_me", to filter which collections will be returned.""",
)
@click.option(
    "--include",
    default=None,
    type=str,
    help="Globus Names of additional documents to include in the response.",
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
@click.pass_context
def guestcollectionlist(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Guest_collection_list")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    if ctx.obj["filter"] is not None:
        if len(ctx.obj["filter"].split(" ")) > 1:
            ctx.obj["filter"] = iter(ctx.obj["filter"].split(" "))

    if ctx.obj["include"] is not None:
        if len(ctx.obj["include"].split(" ")) > 1:
            ctx.obj["include"] = iter(ctx.obj["include"].split(" "))

    guest_collection_list(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        filter_to_help=ctx.obj["filter"],
        include=ctx.obj["include"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
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
    "--role",
    default=None,
    type=str,
    help="""Globus API Role ID i.e. "owner", "administrator", "access_manager", "activity_manager",
            "activity_monitor".""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the createrole response which is a dictionary output.",
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
@click.pass_context
def createrole(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Create_role")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    gcs_response = create_role(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        user_identity=ctx.obj["user_identity"],
        principal_type=ctx.obj["principal_type"],
        principal=ctx.obj["principal"],
        role=ctx.obj["role"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{gcs_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
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
@click.option(
    "--role",
    default=None,
    type=str,
    help="""Globus API Role ID i.e. "owner", "administrator", "access_manager", "activity_manager",
            "activity_monitor".""",
)
@click.option("--role-id", default=None, type=str, help="Globus API Role ID")
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the deleterole response which is a dictionary output.",
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
@click.pass_context
def deleterole(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Delete_role")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    gcs_response = delete_role(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        user_identity=ctx.obj["user_identity"],
        principal=ctx.obj["principal"],
        role=ctx.obj["role"],
        role_id=ctx.obj["role_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{gcs_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
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
@click.option(
    "--role",
    default=None,
    type=str,
    help="""Globus API Role ID i.e. "owner", "administrator", "access_manager", "activity_manager",
            "activity_monitor".""",
)
@click.option("--role-id", default=None, type=str, help="Globus API Role ID")
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the getrole response which is a dictionary output.",
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
@click.pass_context
def getrole(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Get_role")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    gcs_response = get_role(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        user_identity=ctx.obj["user_identity"],
        principal=ctx.obj["principal"],
        role=ctx.obj["role"],
        role_id=ctx.obj["role_id"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if len(gcs_response) > 1:
        click.echo(
            "Multiple roles found. You may want to use the --role-id argument for disambiguation."
        )
        if ctx.obj["print_parameter"] is not None:
            click.echo(
                "Multiple roles found. The --print_parameter will not be displayed."
            )
    else:
        if ctx.obj["print_parameter"] is not None:
            parameters = ctx.obj["print_parameter"].split(" ")
            for i in range(0, len(parameters)):
                click.echo(f"{gcs_response.get(key=parameters[i])}")


@click.command()
@click.option(
    "--endpoint-id",
    required=True,
    type=str,
    help="Globus Endpoint ID of the mapped collection.",
)
@click.option(
    "--mapped-collection-id",
    required=True,
    type=str,
    help="Globus Mapped Collection ID.",
)
@click.option(
    "--collection-name", default=None, type=str, help="Globus Mapped Collection name."
)
@click.option(
    "--collection-id", default=None, type=str, help="Globus Mapped Collection ID."
)
@click.option(
    "--include",
    default=None,
    type=str,
    help="""Elect to return or not info for all roles. Pass “all_roles” to do this. To not do this, do not use this
            argument.""",
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
@click.pass_context
def rolelist(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Role_list")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    gcs_response = role_list(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        endpoint_id=ctx.obj["endpoint_id"],
        mapped_collection_id=ctx.obj["mapped_collection_id"],
        collection_name=ctx.obj["collection_name"],
        collection_id=ctx.obj["collection_id"],
        include=ctx.obj["include"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )
