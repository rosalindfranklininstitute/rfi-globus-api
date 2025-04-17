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

from ..groups.groups import (
    add_group_members,
    change_role_group_members,
    create_group,
    delete_group,
    get_group,
    group_list,
    groups_client,
    remove_group_members,
    set_group_members,
)
from ..logging.logging import dump_with_auto_obfuscation, get_logger

logger = get_logger(stdout=True)
LOGGING_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]


@click.command()
@click.option("--group-name", required=True, type=str, help="Globus group name.")
@click.option("--parent-id", default=None, type=str, help="Globus group parent id.")
@click.option("--description", default=None, type=str, help="Globus group description.")
@click.option(
    "--terms-and-conditions",
    default=None,
    type=str,
    help="Globus group terms and conditions.",
)
@click.option(
    "--policy-is-high-assurance",
    default=False,
    type=bool,
    help="Globus group policy if the group is high assurance.",
)
@click.option(
    "--policy-authentication-assurance-timeout",
    default=None,
    type=int,
    help="""Globus group policy. Maximum allowed seconds before a user must reauthenticate to access the group if is set
            to High Assurance. Defaults to 28800 (aka 8 hours) for HA groups.""",
)
@click.option(
    "--policy-group-visibility",
    default="private",
    type=str,
    help="""Globus group policy. Who can view the group, it can be either "authenticated": Any authenticated user, or
            "private": Only active/invited/pending members of the group.""",
)
@click.option(
    "--policy-group-members-visibility",
    default="members",
    type=str,
    help="""Globus group policy. Who can view group memberships, it can be either "members": All members of the group,
            or "managers": Only admins and managers.""",
)
@click.option(
    "--policy-join-requests",
    default=False,
    type=bool,
    help="Globus group policy. If true then users may request to join the group.",
)
@click.option(
    "--policy_signup_fields",
    default=None,
    type=str,
    help="""Globus group policy. Type with spaces between them, any additional signup fields apart from "First Name",
            "Last Name" and "Organisation", that the members will have to fill when they enter the group. Possible
            values are: "institution", "current_project_name", "address", "city", "state", "country", "address1",
            "address2", "zip", "phone", "department", "field_of_science".""",
)
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the creategroup response which is a dictionary output.",
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
def creategroup(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Create_group")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    assert (
        ctx.obj["policy_group_visibility"] == "private"
        or ctx.obj["policy_group_visibility"] == "authenticated"
    )
    assert (
        ctx.obj["policy_group_members_visibility"] == "members"
        or ctx.obj["policy_group_visibility"] == "managers"
    )
    if ctx.obj["policy_signup_fields"] is not None:
        ctx.obj["policy_signup_fields"] = list(
            set(ctx.obj["policy_signup_fields"].split(" "))
        )

    groups_response = create_group(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        group_name=ctx.obj["group_name"],
        parent_id=ctx.obj["parent_id"],
        description=ctx.obj["description"],
        terms_and_conditions=ctx.obj["terms_and_conditions"],
        policy_is_high_assurance=ctx.obj["policy_is_high_assurance"],
        policy_authentication_assurance_timeout=ctx.obj[
            "policy_authentication_assurance_timeout"
        ],
        policy_group_visibility=ctx.obj["policy_group_visibility"],
        policy_group_members_visibility=ctx.obj["policy_group_members_visibility"],
        policy_join_requests=ctx.obj["policy_join_requests"],
        policy_signup_fields=ctx.obj["policy_signup_fields"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{groups_response.get(key=parameters[i])}")


@click.command()
@click.option("--group-name", required=True, type=str, help="Globus group name.")
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the deletegroup response which is a dictionary output.",
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
def deletegroup(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Delete_Group")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    groups_response = delete_group(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        group_name=ctx.obj["group_name"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{groups_response.get(key=parameters[i])}")


@click.command()
@click.option("--group-name", required=True, type=str, help="Globus group name.")
@click.option(
    "--print-parameter",
    default=None,
    type=str,
    help="Print one parameter from the getgroup response which is a dictionary output.",
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
def getgroup(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Get_Group")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    groups_response = get_group(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        group_name=ctx.obj["group_name"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )

    if ctx.obj["print_parameter"] is not None:
        parameters = ctx.obj["print_parameter"].split(" ")
        for i in range(0, len(parameters)):
            click.echo(f"{groups_response.get(key=parameters[i])}")


@click.command()
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
def grouplist(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Group_List")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    group_list(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option("--group-name", required=True, type=str, help="Globus group name.")
@click.option(
    "--set-members",
    required=True,
    type=str,
    help="""Whitespace separated list of ORCIDs to set the group membership to. Users will be added and deleted to
            accomplish this.""",
)
@click.option(
    "--roles",
    default="member",
    type=str,
    help="""A single string without spaces to set all users as either "member", "manager", or "admin". Alternatively a
            whitespace separated list of roles that correspond to each ORCIDs. In the second case the number of roles
            must be as many as the ORCIDs.""",
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
def setgroupmembers(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Set_group_members")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    count_of_set_members = len(list(set(ctx.obj["set_members"].split(" "))))
    roles = ctx.obj["roles"].split(" ")
    if len(roles) == 1:
        assert roles[0] == "member" or roles[0] == "manager" or roles[0] == "admin"
        ctx.obj["roles"] = (roles[0] + " ") * (count_of_set_members - 1) + roles[0]
    else:
        assert len(roles) == count_of_set_members
        for role in roles:
            assert role == "member" or role == "manager" or role == "admin"

    set_group_members(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        group_name=ctx.obj["group_name"],
        set_members_list=ctx.obj["set_members"],
        roles=ctx.obj["roles"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option("--group-name", required=True, type=str, help="Globus group name.")
@click.option(
    "--add-members",
    required=True,
    type=str,
    help="Whitespace separated list of ORCIDs to add members to the group.",
)
@click.option(
    "--roles",
    default="member",
    type=str,
    help="""A single string without spaces to set all users as either "member", "manager", or "admin". Alternatively a
            whitespace separated list of roles that correspond to each ORCIDs. In the second case the number of roles
            must be as many as the ORCIDs.""",
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
def addgroupmembers(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Add_group_members")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    count_of_add_members = len(list(set(ctx.obj["add_members"].split(" "))))
    roles = ctx.obj["roles"].split(" ")
    if len(roles) == 1:
        assert roles[0] == "member" or roles[0] == "manager" or roles[0] == "admin"
        ctx.obj["roles"] = (roles[0] + " ") * (count_of_add_members - 1) + roles[0]
    else:
        assert len(roles) == count_of_add_members
        for role in roles:
            assert role == "member" or role == "manager" or role == "admin"

    add_group_members(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        group_name=ctx.obj["group_name"],
        add_members_list=ctx.obj["add_members"],
        roles=ctx.obj["roles"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option("--group-name", required=True, type=str, help="Globus group name.")
@click.option(
    "--members",
    required=True,
    type=str,
    help="Whitespace separated list of ORCIDs to change the membership roles of the group members.",
)
@click.option(
    "--roles",
    default="member",
    type=str,
    help="""A single string without spaces to set all users as either "member", "manager", or "admin". Alternatively a
            whitespace separated list of roles that correspond to each ORCIDs. In the second case the number of roles
            must be as many as the ORCIDs.""",
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
def changerolegroupmembers(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Add_group_members")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    count_of_members = len(list(set(ctx.obj["members"].split(" "))))
    roles = ctx.obj["roles"].split(" ")
    if len(roles) == 1:
        assert roles[0] == "member" or roles[0] == "manager" or roles[0] == "admin"
        ctx.obj["roles"] = (roles[0] + " ") * (count_of_members - 1) + roles[0]
    else:
        assert len(roles) == count_of_members
        for role in roles:
            assert role == "member" or role == "manager" or role == "admin"

    change_role_group_members(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        group_name=ctx.obj["group_name"],
        members_list=ctx.obj["members"],
        roles=ctx.obj["roles"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )


@click.command()
@click.option("--group-name", required=True, type=str, help="Globus group name.")
@click.option(
    "--remove-members",
    required=True,
    type=str,
    help="""Whitespace separated list of ORCIDs to remove users from the group.""",
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
def removegroupmembers(ctx, **kargs):
    logger.setLevel(LOGGING_LEVELS[min(len(LOGGING_LEVELS) - 1, kargs["verbose"])])
    logger.info("Remove_group_members")
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Debug the config passed to the program
    dump_with_auto_obfuscation(logger.debug, dict(ctx=ctx.obj), prefix="CONFIG")

    remove_group_members(
        confidential_client_id=ctx.obj["confidential_client_id"],
        confidential_client_secret=ctx.obj["confidential_client_secret"],
        group_name=ctx.obj["group_name"],
        remove_members_list=ctx.obj["remove_members"],
        json=ctx.obj["json"],
        yaml=ctx.obj["yaml"],
    )
