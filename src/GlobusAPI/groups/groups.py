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

from globus_sdk import AuthClient, GroupsClient, GroupsManager
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import AuthScopes, GroupsScopes

import GlobusAPI

from ..logging.logging import dump, get_logger
from ..output.file_output import output
from .users import auth_client, get_user_uuid, get_users

logger = get_logger()


def groups_client(
    confidential_client_id: str,
    confidential_client_secret: str,
    scopes=GroupsScopes.all,
) -> GroupsClient:
    """Return a groups client object initialized with the given parameters.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        scopes (GroupsScopes, optional): The Globus Scopes for the groups client. Defaults to GroupsScopes.all .

    Returns:
        It returns a groups client object initialized with the given parameters.

    Raises:
        ex: Fail to create Authorizer
        ex: Fail to create Groups Authorizer

    """
    try:
        groups_authorizer = GlobusAPI.auth.authorizer.get_client_credentials_authorizer(
            confidential_client_id, confidential_client_secret, scopes
        )

    except Exception as ex:
        logger.exception("Failed to create authorizer...", exc_info=ex)
        raise ex

    try:
        current_groups_client = GroupsClient(authorizer=groups_authorizer)

        return current_groups_client

    except Exception as ex:
        logger.exception("Failed to create groups client...", exc_info=ex)
        raise ex


def create_group(
    confidential_client_id: str,
    confidential_client_secret: str,
    group_name: str,
    parent_id: typing.Optional[str] = None,
    description: typing.Optional[str] = None,
    terms_and_conditions: typing.Optional[str] = None,
    policy_is_high_assurance: typing.Optional[bool] = False,
    policy_authentication_assurance_timeout: typing.Optional[int] = None,
    policy_group_visibility: typing.Optional[str] = "private",
    policy_group_members_visibility: typing.Optional[str] = "members",
    policy_join_requests: typing.Optional[bool] = False,
    policy_signup_fields: typing.Optional[typing.List[str]] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Creates a new Globus Group.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        group_name (str, required): The name for the new group.
        parent_id (typing.Optional[str], optional): The UUID of the parent group so that the new group to be a child of
                                                    this group. The confidential client creating this group must be an
                                                    admin of the parent group.
        description (typing.Optional[str], optional): A short description for the new group. Defaults to None.
        terms_and_conditions (typing.Optional[str], optional): The terms and conditions for group membership. It should
                                                               be <= 120000 characters. Defaults to None.
        policy_is_high_assurance (typing.Optional[bool], optional): Whether group is on the "High Assurance - HA" mode.
                                                                    Defaults to False.
        policy_authentication_assurance_timeout (typing.Optional[int], optional): Maximum allowed seconds before a user
                                                                                  must reauthenticate to access the
                                                                                  group if is set to High Assurance.
                                                                                  If None to 28800 seconds for
                                                                                  HA groups. Defaults to None.
        policy_group_visibility (typing.Optional[str], optional): Who can view the group. It should be either
                                                                  "authenticated" or "private". "authenticated" allows
                                                                  any Globus authenticated user to see the group.
                                                                  "private" allows only active/invited/pending members
                                                                  of the group to see the group. Defaults to "private".
        policy_group_members_visibility (typing.Optional[str], optional): Who can view the group's memberships. It
                                                                          should be either "members" or "managers".
                                                                          "members" all the group members can see the
                                                                          group memberships. "managers" only admins
                                                                          and managers can see the group memberships.
                                                                          Defaults to "members".
        policy_join_requests (typing.Optional[bool], optional): If True then users who can see the group but are not
                                                                members may be able to request to join the group.
                                                                Defaults to False.
        policy_signup_fields (typing.Optional[typing.List[str]], optional): List with the additional signup fields new
                                                                            members will be able to fill. It should be a
                                                                            list of strings which is a combinations of
                                                                            the following strings: "institution",
                                                                            "current_project_name", "address", "city",
                                                                            "state", "country", "address1", "address2",
                                                                            "zip", "phone", "department",
                                                                            "field_of_science". Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of creating a new group uses standard HTTPS structure.

    Raises:
        ex: Fail to create new group
        ex: Fail to list existing groups (to verify that there is not a group with the same name already)

    """
    current_groups_client = groups_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=GroupsScopes.all,
    )

    groups_response = _create_group(
        current_groups_client=current_groups_client,
        group_name=group_name,
        parent_id=parent_id,
        description=description,
        terms_and_conditions=terms_and_conditions,
        policy_is_high_assurance=policy_is_high_assurance,
        policy_authentication_assurance_timeout=policy_authentication_assurance_timeout,
        policy_group_visibility=policy_group_visibility,
        policy_group_members_visibility=policy_group_members_visibility,
        policy_join_requests=policy_join_requests,
        policy_signup_fields=policy_signup_fields,
    )

    output(groups_response, json_filename=json, yaml_filename=yaml)

    return groups_response


def _create_group(
    current_groups_client: GroupsClient,
    group_name: str,
    parent_id: typing.Optional[str] = None,
    description: typing.Optional[str] = None,
    terms_and_conditions: typing.Optional[str] = None,
    policy_is_high_assurance: typing.Optional[bool] = False,
    policy_authentication_assurance_timeout: typing.Optional[int] = None,
    policy_group_visibility: typing.Optional[str] = "private",
    policy_group_members_visibility: typing.Optional[str] = "members",
    policy_join_requests: typing.Optional[bool] = False,
    policy_signup_fields: typing.Optional[typing.List[str]] = None,
) -> typing.Union[GlobusHTTPResponse, typing.Dict[str, str]]:
    """Private method used by `create_group`. Creates a new Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        group_name (str, required): The name for the new group.
        parent_id (typing.Optional[str], optional): The UUID of the parent group so that the new group to be a child
                                                    of this group. The confidential client creating this group must
                                                    be an admin of the parent group.
        description (typing.Optional[str], optional): A short description for the new group. Defaults to None.
        terms_and_conditions (typing.Optional[str], optional): The terms and conditions for group membership. It should
                                                               be <= 120000 characters. Defaults to None.
        policy_is_high_assurance (typing.Optional[bool], optional): Whether group is on the "High Assurance - HA" mode.
                                                                    Defaults to False.
        policy_authentication_assurance_timeout (typing.Optional[int], optional): Maximum allowed seconds before a user
                                                                                  must reauthenticate to access the
                                                                                  group if is set to High Assurance.
                                                                                  If None to 28800 seconds for
                                                                                  HA groups. Defaults to None.
        policy_group_visibility (typing.Optional[str], optional): Who can view the group. It should be either
                                                                  "authenticated" or "private". "authenticated" allows
                                                                  any Globus authenticated user to see the group.
                                                                  "private" allows only active/invited/pending members
                                                                  of the group to see the group. Defaults to "private".
        policy_group_members_visibility (typing.Optional[str], optional): Who can view the group's memberships. It
                                                                          should be either "members" or "managers".
                                                                          "members" all the group members can see the
                                                                          group memberships. "managers" only admins and
                                                                          managers can see the group memberships.
                                                                          Defaults to "members".
        policy_join_requests (typing.Optional[bool], optional): If True then users who can see the group but are not
                                                                members may be able to request to join the group.
                                                                Defaults to False.
        policy_signup_fields (typing.Optional[typing.List[str]], optional): List with the additional signup fields new
                                                                            members will be able to fill. It should be a
                                                                            list of strings which is a combinations of
                                                                            the following strings: "institution",
                                                                            "current_project_name", "address", "city",
                                                                            "state", "country", "address1", "address2",
                                                                            "zip", "phone", "department",
                                                                            "field_of_science". Defaults to None.

    Returns:
        typing.Union[GlobusHTTPResponse, typing.Dict[str, str]]: Globus API result of creating a new group uses
                                                                 standard HTTPS structure.

    Raises:
        ex: Fail to create new group
        ex: Fail to list existing groups (to verify that there is not a group with the same name already)

    """

    group = get_group_from_name(current_groups_client, group_name)
    if not group:
        try:
            policies = {
                "is_high_assurance": policy_is_high_assurance,
                "authentication_assurance_timeout": policy_authentication_assurance_timeout,
                "group_visibility": policy_group_visibility,
                "group_members_visibility": policy_group_members_visibility,
                "join_requests": policy_join_requests,
                "signup_fields": policy_signup_fields,
            }
            group_info = {
                "name": group_name,
                "parent_id": parent_id,
                "description": description,
                "terms_and_conditions": terms_and_conditions,
                "policies": policies,
            }

            dump(logger.info, dict(group_info=group_info), prefix="GROUP")

            logger.info("Creating the group...")

            groups_result = current_groups_client.create_group(group_info)
            logger.info(f"Group {group_info['name']} created")
            logger.info("Retrieving the group...")
            group = get_group_from_name(current_groups_client, group_name)

            dump(logger.debug, dict(group=group), prefix="GROUP")

            assert group["name"] == group_name
            assert group["id"] is not None

            return groups_result

        except Exception as ex:
            logger.exception("Failed to create group...", exc_info=ex)
            raise ex

    else:
        logger.info(
            f"Group {group['id']}:{group['name']} already exists and was not created"
        )
        return {"name": "This group already exists", "id": "This group already exists"}


def set_group_members(
    confidential_client_id: str,
    confidential_client_secret: str,
    group_name: str,
    set_members_list: str,
    roles: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.Dict[str, GlobusHTTPResponse]:
    """Seting of members to a Globus Group.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        group_name (str, required): The name for the group to which memberships will be set.
        set_members_list (str, required): List of member(s) to set as members, any existing members not included in the
                                          `set_members_list` will be removed. It should be a list of
                                          identities/usernames that are separated with whitespace.
        roles (str, required): List of group role(s) for the corresponding members in the `set_members_list`. Each
                               member of the group should be either "member", "manager" or "admin". The list should have
                               the same size as the `set_members_list`. The roles per member should be separated
                               with whitespace.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.Dict[str, GlobusHTTPResponse]: Globus API result of setting group members uses standard HTTPS structure.

    Raises:
        ex: Fail to list existing groups
        ex: Fail to get users' properties
        ex: Fail to change group member roles
        ex: Fail to add new members
        ex: Fail to remove members
        AssertionError: The size of `set_members_list` list does not match the size of `roles` list
        AssertionError: Roles other than "member", "manager" or "admin" are specified in the `roles` list

    """
    current_groups_client = groups_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=GroupsScopes.all,
    )

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

    groups_response = _set_group_members(
        current_groups_client=current_groups_client,
        current_auth_client=current_auth_client,
        group_name=group_name,
        set_members_list=set_members_list,
        roles=roles,
    )

    output(groups_response, json_filename=json, yaml_filename=yaml)

    return groups_response


def _set_group_members(
    current_groups_client: GroupsClient,
    current_auth_client: AuthClient,
    group_name: str,
    set_members_list: str,
    roles: str,
) -> typing.Dict[str, GlobusHTTPResponse]:
    """Private method used by `set_group_member`. Setting of members to a Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        current_auth_client (AuthClient, required): Globus auth client.
        group_name (str, required): The name for the group to which memberships will be set.
        set_members_list (str, required): List of member(s) to set as members, any existing members not included in the
                                          `set_members_list` will be removed. It should be a list of
                                          identities/usernames that are separated with whitespace.
        roles (str, required): List of group role(s) for the corresponding members in the `set_members_list`. Each
                               member of the group should be either "member", "manager" or "admin". The list should have
                               the same size as the `set_members_list`. The roles per member should be separated
                               with whitespace.

    Returns:
        typing.Dict[str, GlobusHTTPResponse]: Globus API result of setting group members uses standard HTTPS structure.

    Raises:
        ex: Fail to list existing groups
        ex: Fail to get users' properties
        ex: Fail to change group member roles
        ex: Fail to add new members
        ex: Fail to remove members
        AssertionError: The size of `set_members_list` list does not match the size of `roles` list
        AssertionError: Roles other than "member", "manager" or "admin" are specified in the `roles` list
    """

    logger.info("Retrieving the group...")
    group = get_group_from_name(current_groups_client, group_name)
    set_members = list(set(set_members_list.split(" ")))
    roles = roles.split(" ")

    assert len(set_members) == len(roles)
    for role in roles:
        assert role == "member" or role == "manager" or role == "admin"

    set_members = [
        f"{user}@orcid.org" if not user.endswith("@orcid.org") else user
        for user in set_members
    ]
    globus_members = get_users(current_auth_client, set_members)
    globus_members_orcid = [
        globus_member["username"] for globus_member in globus_members
    ]

    missing_members = list()
    leftover_members = list()
    roles_for_leftover_members = list()
    for i in range(0, len(set_members)):
        if set_members[i] not in globus_members_orcid:
            missing_members.append(set_members[i])
        else:
            leftover_members.append(set_members[i])
            roles_for_leftover_members.append(roles[i])
    if len(missing_members) > 0:
        logger.error(
            f"""The following users do not have accounts on Globus: {missing_members}
                and were not added to the group."""
        )

    if len(leftover_members) == 0:
        logger.error(
            "All users provided do not have Globus accounts and so none user will be set."
        )
        return dict()

    logger.info("Getting uuids of desired group members...")
    set_members_uuids = get_user_uuid(current_auth_client, leftover_members)

    dump(logger.debug, dict(set_members_uuids=set_members_uuids))

    logger.info("Getting uuids of current group members...")
    current_group_uuids = get_group_members_uuid(current_groups_client, group_name)
    current_group_roles = get_group_members_role(current_groups_client, group_name)

    dump(logger.debug, dict(current_group_uuids=current_group_uuids))

    set_group_members_result = dict()

    # Add new users
    added_members_uuids = list()
    added_members_roles = list()
    for i in range(0, len(set_members_uuids)):
        if set_members_uuids[i] not in current_group_uuids:
            added_members_uuids.append(set_members_uuids[i])
            added_members_roles.append(roles_for_leftover_members[i])
        elif (
            roles_for_leftover_members[i]
            != current_group_roles[current_group_uuids.index(set_members_uuids[i])]
        ):
            try:
                logger.info(
                    f"""Changing the role of uuid [{set_members_uuids[i]}] from
                        [{current_group_roles[current_group_uuids.index(set_members_uuids[i])]}] to
                        [{roles_for_leftover_members[i]}]"""
                )
                GroupsManager(current_groups_client).remove_member(
                    group["id"], set_members_uuids[i]
                )
                set_group_members_result[
                    f"Changed_role_user_{set_members_uuids[i]}"
                ] = GroupsManager(current_groups_client).add_member(
                    group["id"],
                    set_members_uuids[i],
                    role=roles_for_leftover_members[i],
                )

            except Exception as ex:
                logger.exception(
                    "Failed to change the group members' roles...", exc_info=ex
                )
                raise ex

    try:
        dump(logger.debug, dict(add_members_uuids=added_members_uuids))

        for i in range(0, len(added_members_uuids)):
            logger.info(f"Adding uuid [{added_members_uuids[i]}]")
            set_group_members_result[
                f"Added_user_{added_members_uuids[i]}"
            ] = GroupsManager(current_groups_client).add_member(
                group["id"], added_members_uuids[i], role=added_members_roles[i]
            )

    except Exception as ex:
        logger.exception("Failed to add new group members...", exc_info=ex)
        raise ex

    # Remove unwanted users
    removed_members_uuids = [
        uuid for uuid in current_group_uuids if uuid not in set_members_uuids
    ]

    try:
        dump(logger.debug, dict(removed_members_uuids=removed_members_uuids))

        for uuid in removed_members_uuids:
            logger.info(f"Removing uuid [{uuid}]")
            set_group_members_result[f"Removed_user_{uuid}"] = GroupsManager(
                current_groups_client
            ).remove_member(group["id"], uuid)

    except Exception as ex:
        logger.exception("Failed to remove group members...", exc_info=ex)
        raise ex

    updated_group_uuids = get_group_members_uuid(current_groups_client, group_name)
    dump(logger.debug, dict(updated_group_uuids=updated_group_uuids))

    return set_group_members_result


def add_group_members(
    confidential_client_id: str,
    confidential_client_secret: str,
    group_name: str,
    add_members_list: str,
    roles: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.Dict[str, GlobusHTTPResponse]:
    """Addition of the members to a Globus Group.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        group_name (str, required): The name for the group to which memberships will be added.
        add_members_list (str, required): List of member(s) to be added in the group. It should be a list of
                                          identities/usernames that are separated with whitespace.
        roles (str, required): List of group role(s) for the corresponding members in the `add_members_list`. Each
                               member of the group should be either "member", "manager" or "admin". The list should have
                               the same size as the `add_members_list`. The roles per member should be separated
                               with whitespace.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.Dict[str, GlobusHTTPResponse]: Globus API result of adding new group members uses standard HTTPS
                                              structure.

    Raises:
        ex: Fail to list existing groups
        ex: Fail to get users' properties
        ex: Fail to add new members
        AssertionError: The size of `set_members_list` list does not match the size of `roles` list
        AssertionError: Roles other than "member", "manager" or "admin" are specified in the `roles` list

    """
    current_groups_client = groups_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=GroupsScopes.all,
    )

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

    groups_response = _add_group_members(
        current_groups_client=current_groups_client,
        current_auth_client=current_auth_client,
        group_name=group_name,
        add_members_list=add_members_list,
        roles=roles,
    )

    output(groups_response, json_filename=json, yaml_filename=yaml)

    return groups_response


def _add_group_members(
    current_groups_client: GroupsClient,
    current_auth_client: AuthClient,
    group_name: str,
    add_members_list: str,
    roles: str,
) -> typing.Dict[str, GlobusHTTPResponse]:
    """Private method used by `add_group_member`. Addition of members to a Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        current_auth_client (AuthClient, required): Globus auth client.
        group_name (str, required): The name for the group to which memberships will be added.
        add_members_list (str, required): List of member(s) to be added in the group. It should be a list of
                                          identities/usernames that are separated with whitespace.
        roles (str, required): List of group role(s) for the corresponding members in the `add_members_list`. Each
                               member of the group should be either "member", "manager" or "admin". The list should
                               have the same size as the `add_members_list`. The roles per member should be separated
                               with whitespace.

    Returns:
        typing.Dict[str, GlobusHTTPResponse]: Globus API result of adding new group members uses standard HTTPS
                                              structure.

    Raises:
        ex: Fail to list existing groups
        ex: Fail to get users' properties
        ex: Fail to add new members
        AssertionError: The size of `set_members_list` list does not match the size of `roles` list
        AssertionError: Roles other than "member", "manager" or "admin" are specified in the `roles` list

    """
    logger.info("Retrieving the group...")
    group = get_group_from_name(current_groups_client, group_name)
    add_members = list(set(add_members_list.split(" ")))
    roles = roles.split(" ")

    assert len(add_members) == len(roles)
    for role in roles:
        assert role == "member" or role == "manager" or role == "admin"

    add_members = [
        f"{user}@orcid.org" if not user.endswith("@orcid.org") else user
        for user in add_members
    ]
    logger.info(add_members)
    globus_members = get_users(current_auth_client, add_members)
    globus_members_orcid = [
        globus_member["username"] for globus_member in globus_members
    ]

    missing_members = list()
    leftover_members = list()
    roles_for_leftover_members = list()
    for i in range(0, len(add_members)):
        if add_members[i] not in globus_members_orcid:
            missing_members.append(add_members[i])
        else:
            leftover_members.append(add_members[i])
            roles_for_leftover_members.append(roles[i])
    if len(missing_members) > 0:
        logger.error(
            f"""The following users do not have accounts on Globus:
            {missing_members} and were not added to the group."""
        )

    if len(leftover_members) == 0:
        logger.error(
            "All users provided do not have Globus accounts and so none user will be added."
        )
        return dict()

    logger.info("Getting uuids of group members to be added...")
    added_members_uuids = get_user_uuid(current_auth_client, leftover_members)

    add_group_members_result = dict()
    try:
        for i in range(0, len(added_members_uuids)):
            add_group_members_result[
                f"Added_user_{added_members_uuids[i]}"
            ] = GroupsManager(current_groups_client).add_member(
                group["id"], added_members_uuids[i], role=roles_for_leftover_members[i]
            )

        logger.info(f"Added {added_members_uuids} to group {group_name}:{group['id']}")

    except Exception as ex:
        logger.exception("Failed to add group members...", exc_info=ex)
        raise ex

    return add_group_members_result


def change_role_group_members(
    confidential_client_id: str,
    confidential_client_secret: str,
    group_name: str,
    members_list: str,
    roles: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.Dict[str, GlobusHTTPResponse]:
    """Change of membership roles in a Globus Group.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        group_name (str, required): The name for the group to which memberships' roles will be changed.
        members_list (str, required): List of member(s) which their memberships roles will be changed. It should be a
                                      list of identities/usernames that are separated with whitespace.
        roles (str, required): List of group role(s) for the corresponding members in the `members_list`. Each member
                               of the group should be either "member", "manager" or "admin". The list should have the
                               same size as the `add_members_list`. The roles per member should be separated
                               with whitespace.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.Dict[str, GlobusHTTPResponse]: Globus API result of changing roles for group members uses standard HTTPS
                                              structure.

    Raises:
        ex: Fail to list existing groups
        ex: Fail to get users' properties
        ex: Fail to change group member roles
        AssertionError: The size of `set_members_list` list does not match the size of `roles` list
        AssertionError: Roles other than "member", "manager" or "admin" are specified in the `roles` list

    """

    current_groups_client = groups_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=GroupsScopes.all,
    )

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

    groups_response = _change_role_group_members(
        current_groups_client=current_groups_client,
        current_auth_client=current_auth_client,
        group_name=group_name,
        members_list=members_list,
        roles=roles,
    )

    output(groups_response, json_filename=json, yaml_filename=yaml)

    return groups_response


def _change_role_group_members(
    current_groups_client: GroupsClient,
    current_auth_client: AuthClient,
    group_name: str,
    members_list: str,
    roles: str,
) -> typing.Dict[str, GlobusHTTPResponse]:
    """Private method used by `change_role_group_members`. Changing membership roles in a Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        current_auth_client (AuthClient, required): Globus auth client.
        group_name (str, required): The name for the group to which memberships' roles will be changed.
        members_list (str, required): List of member(s) which their memberships roles will be changed. It should be a
                                      list of identities/usernames that are separated with whitespace.
        roles (str, required): List of group role(s) for the corresponding members in the `members_list`. Each member
                               of the group should be either "member", "manager" or "admin". The list should have the
                               same size as the `add_members_list`. The roles per member should be separated
                               with whitespace.

    Returns:
        typing.Dict[str, GlobusHTTPResponse]: Globus API result of changing roles for group members uses standard HTTPS
                                              structure.

    Raises:
        ex: Fail to list existing groups
        ex: Fail to get users' properties
        ex: Fail to change group member roles
        AssertionError: The size of `set_members_list` list does not match the size of `roles` list
        AssertionError: Roles other than "member", "manager" or "admin" are specified in the `roles` list

    """
    logger.info("Retrieving the group...")
    group = get_group_from_name(current_groups_client, group_name)
    members = list(set(members_list.split(" ")))
    roles = roles.split(" ")

    assert len(members) == len(roles)
    for role in roles:
        assert role == "member" or role == "manager" or role == "admin"

    members = [
        f"{user}@orcid.org" if not user.endswith("@orcid.org") else user
        for user in members
    ]
    globus_members = get_users(current_auth_client, members)
    globus_members_orcid = [
        globus_member["username"] for globus_member in globus_members
    ]

    missing_members = list()
    leftover_members = list()
    roles_for_leftover_members = list()
    for i in range(0, len(members)):
        if members[i] not in globus_members_orcid:
            missing_members.append(members[i])
        else:
            leftover_members.append(members[i])
            roles_for_leftover_members.append(roles[i])
    if len(missing_members) > 0:
        logger.error(
            f"""The following users do not have accounts on Globus:
                {missing_members} and thus they cannot be members of the group."""
        )

    if len(leftover_members) == 0:
        logger.error(
            "All users provided do not have Globus accounts and so there will be none role change."
        )
        return dict()

    logger.info(
        "Getting uuids of group members that will change their roles in the group..."
    )
    members_uuids = get_user_uuid(current_auth_client, leftover_members)

    logger.info("Getting uuids of current group members...")
    current_group_uuids = get_group_members_uuid(current_groups_client, group_name)
    current_group_roles = get_group_members_role(current_groups_client, group_name)

    group_members_result = dict()

    for i in range(0, len(members_uuids)):
        if members_uuids[i] not in current_group_uuids:
            logger.info(
                f"""User with uuid [{members_uuids[i]}] is not a member of the group,
                    and thus their role cannot be changed."""
            )
        else:
            if (
                roles_for_leftover_members[i]
                != current_group_roles[current_group_uuids.index(members_uuids[i])]
            ):
                try:
                    logger.info(
                        f"""Changing the role of user with uuid [{members_uuids[i]}] from
                            [{current_group_roles[current_group_uuids.index(members_uuids[i])]}] to
                            [{roles_for_leftover_members[i]}]"""
                    )
                    GroupsManager(current_groups_client).remove_member(
                        group["id"], members_uuids[i]
                    )
                    group_members_result[
                        f"Changed_role_user_{members_uuids[i]}"
                    ] = GroupsManager(current_groups_client).add_member(
                        group["id"],
                        members_uuids[i],
                        role=roles_for_leftover_members[i],
                    )

                except Exception as ex:
                    logger.exception(
                        "Failed to change the roles of group members...", exc_info=ex
                    )
                    raise ex
            else:
                logger.info(
                    f"""User with uuid [{members_uuids[i]}] has already the role of
                        [{roles_for_leftover_members[i]}], and so their role will not be changed."""
                )

    return group_members_result


def remove_group_members(
    confidential_client_id: str,
    confidential_client_secret: str,
    group_name: str,
    remove_members_list: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.Dict[str, GlobusHTTPResponse]:
    """Removal of member(s) in a Globus Group.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        group_name (str, required): The name for the group to which memberships will be removed.
        remove_members_list (str, required): List of member(s) to be removed from a group. It should be a list of
                                             identities/usernames that are separated with whitespace.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.Dict[str, GlobusHTTPResponse]: Globus API result of removing group members uses standard HTTPS structure.

    Raises:
        ex: Fail to list existing groups
        ex: Fail to get users' properties
        ex: Fail to remove members
        AssertionError: The size of `set_members_list` list does not match the size of `roles` list
        AssertionError: Roles other than "member", "manager" or "admin" are specified in the `roles` list

    """
    current_groups_client = groups_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=GroupsScopes.all,
    )

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

    groups_response = _remove_group_members(
        current_groups_client=current_groups_client,
        current_auth_client=current_auth_client,
        group_name=group_name,
        remove_members_list=remove_members_list,
    )

    output(groups_response, json_filename=json, yaml_filename=yaml)

    return groups_response


def _remove_group_members(
    current_groups_client: GroupsClient,
    current_auth_client: AuthClient,
    group_name: str,
    remove_members_list: str,
) -> typing.Dict[str, GlobusHTTPResponse]:
    """Private method used by `remove_group_members`. Removal of member(s) in a Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        current_auth_client (AuthClient, required): Globus auth client.
        group_name (str, required): The name for the group to which memberships will be removed.
        remove_members_list (str, required): List of member(s) to be removed from a group. It should be a list of
                                             identities/usernames that are separated with whitespace.

    Returns:
        typing.Dict[str, GlobusHTTPResponse]: Globus API result of removing group members uses standard HTTPS structure.

    Raises:
        ex: Fail to list existing groups
        ex: Fail to get users' properties
        ex: Fail to remove members
        AssertionError: The size of `set_members_list` list does not match the size of `roles` list
        AssertionError: Roles other than "member", "manager" or "admin" are specified in the `roles` list

    """
    remove_members = list(set(remove_members_list.split(" ")))
    remove_members = [
        f"{user}@orcid.org" if not user.endswith("@orcid.org") else user
        for user in remove_members
    ]

    group = get_group_from_name(current_groups_client, group_name)
    globus_members = get_users(current_auth_client, remove_members)
    globus_members_orcid = [
        globus_member["username"] for globus_member in globus_members
    ]

    missing_members = [
        member for member in remove_members if member not in globus_members_orcid
    ]
    if missing_members:
        logger.info(
            f"The following users do not have accounts on Globus: {missing_members}"
        )

    remove_group_members_result = dict()
    try:
        for member in globus_members:
            remove_group_members_result[f"Removed_user_{member['id']}"] = GroupsManager(
                current_groups_client
            ).remove_member(group["id"], member["id"])

        logger.info(f"Removed {remove_members} from group {group_name}:{group['id']}")

    except Exception as ex:
        logger.exception("Failed to remove group members...", exc_info=ex)
        raise ex

    return remove_group_members_result


def delete_group(
    confidential_client_id: str,
    confidential_client_secret: str,
    group_name: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Deletion of a Globus Group.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        group_name (str, required): The name for the group to be deleted.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of group deletion uses standard HTTPS structure.

    Raises:
        ex: Fail to delete the group
        ex: Fail to list existing groups
        ex: Fail to get users' properties

    """
    current_groups_client = groups_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=GroupsScopes.all,
    )

    groups_response = _delete_group(
        current_groups_client=current_groups_client,
        group_name=group_name,
    )

    output(groups_response, json_filename=json, yaml_filename=yaml)

    return groups_response


def _delete_group(
    current_groups_client: GroupsClient,
    group_name: str,
) -> typing.Union[GlobusHTTPResponse, typing.Dict[str, str]]:
    """Private method used by `delete_group`. Deletion of a Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        group_name (str, required): The name for the group to be deleted.

    Returns:
        typing.Union[GlobusHTTPResponse, typing.Dict[str, str]]: Globus API result of group deletion uses standard
                                                                 HTTPS structure.

    Raises:
        ex: Fail to delete the group
        ex: Fail to list existing groups
        ex: Fail to get users' properties

    """
    logger.info("Deleting the group...")
    group = get_group_from_name(current_groups_client, group_name)
    if group:
        try:
            delete_group_result = current_groups_client.delete_group(
                group["id"],
            )
            logger.info(f"Group {group['name']}  has been deleted")
            return delete_group_result

        except Exception as ex:
            logger.exception("Failed to delete group...", exc_info=ex)
            raise ex
    else:
        logger.info(
            f"Group {group['id']}:{group['name']} does not exist and was not deleted"
        )
        return {"name": "This group already exists", "id": "This group already exists"}


def get_group(
    confidential_client_id: str,
    confidential_client_secret: str,
    group_name: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Get of Globus Group Info.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        group_name (str, required): The name for the group for which to retrieve information.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of getting group information uses standard HTTPS structure.

    Raises:
        ex: Fail to get group info

    """
    current_groups_client = groups_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=GroupsScopes.all,
    )

    groups_response = _get_group(
        current_groups_client=current_groups_client,
        group_name=group_name,
    )

    output(groups_response, json_filename=json, yaml_filename=yaml)

    return groups_response


def _get_group(
    current_groups_client: GroupsClient,
    group_name: str,
) -> GlobusHTTPResponse:
    """Private method used by `get_group`. Get of Globus Group Info.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        group_name (str, required): The name for the group for which to retrieve information.

    Returns:
        GlobusHTTPResponse: Globus API result of getting group information uses standard HTTPS structure.

    Raises:
        ex: Fail to get group info

    """
    try:
        logger.info("Getting group info...")
        group = get_group_from_name(current_groups_client, group_name)
        groups_result = current_groups_client.get_group(
            group["id"], include=["memberships"]
        )

        return groups_result

    except Exception as ex:
        logger.exception("Failed to get group...", exc_info=ex)
        raise ex


def group_list(
    confidential_client_id: str,
    confidential_client_secret: str,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Get of list of Globus Groups.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of groups. Each element of the list is a dictionary regarding a group.

    Raises:
        ex: Fail to list groups

    """
    current_groups_client = groups_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=GroupsScopes.all,
    )

    groups_response = _group_list(
        current_groups_client=current_groups_client,
    )

    output(groups_response, json_filename=json, yaml_filename=yaml)

    return groups_response


def _group_list(
    current_groups_client: typing.Optional[GroupsClient] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `group_list`. Get of list of Globus Groups.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.

    Returns:
        typing.List[GlobusHTTPResponse]: A list of groups. Each element of the list is a dictionary regarding a group.

    Raises:
        ex: Fail to list groups

    """
    try:
        logger.info("Getting group info...")

        list_of_groups = list()
        for group in current_groups_client.get_my_groups():
            list_of_groups.append(group)
        logger.info(list_of_groups)
        return list_of_groups

    except Exception as ex:
        logger.exception("Failed to get group list...", exc_info=ex)
        raise ex


def get_group_from_name(
    current_groups_client: GroupsClient, group_name: str
) -> GlobusHTTPResponse:
    """Get a Globus Group info based on the provided name.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        group_name (str, required): The name for the group for which to retrieve information.

    Returns:
        GlobusHTTPResponse: Globus API result of getting group information uses standard HTTPS structure.

    Raises:
        ex: Fail to list groups

    """

    try:
        for group in current_groups_client.get_my_groups():
            if group_name == group["name"]:
                return group

        logger.error(f"Group :{group_name} does not exists")

    except Exception as ex:
        logger.exception("Failed to get group list...", exc_info=ex)
        raise ex


def get_group_members_uuid(
    current_groups_client: GroupsClient, group_name: str
) -> typing.List[str]:
    """Get uuids of members of a Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        group_name (str, required): The name for the group for which to retrieve the uuids of its members.

    Returns:
        typing.List[str]: A list of uuids.

    Raises:
        ex: Fail to get group info

    """

    try:
        group = get_group_from_name(current_groups_client, group_name)
        group_members = current_groups_client.get_group(
            group["id"], include=["memberships"]
        )

        return [member["identity_id"] for member in group_members["memberships"]]

    except Exception as ex:
        logger.exception("Failed to get group info...", exc_info=ex)
        raise ex


def get_group_members_role(
    current_groups_client: GroupsClient, group_name: str
) -> typing.List[str]:
    """Get roles of members of a Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        group_name (str, required): The name for the group for which to retrieve the roles of its members.

    Returns:
        typing.List[str]: A list of group roles.

    Raises:
        ex: Fail to get group info

    """

    try:
        group = get_group_from_name(current_groups_client, group_name)
        group_members = current_groups_client.get_group(
            group["id"], include=["memberships"]
        )

        return [member["role"] for member in group_members["memberships"]]

    except Exception as ex:
        logger.exception("Failed to get group info...", exc_info=ex)
        raise ex


def get_group_members_orcid(
    current_groups_client: GroupsClient, group_name
) -> typing.List[str]:
    """Get usernames/orcid of members of a Globus Group.

    Args:
        current_groups_client (GroupsClient, required): Globus groups client.
        group_name (str, required): The name for the group for which to retrieve the usernames/orcids of its members.

    Returns:
        typing.List[str]: A list of group usernames/orcids.

    Raises:
        ex: Fail to get group info

    """
    try:
        group = get_group_from_name(current_groups_client, group_name)
        group_members = current_groups_client.get_group(
            group["id"], include=["memberships"]
        )
        return [member["username"] for member in group_members["memberships"]]

    except Exception as ex:
        logger.exception("Failed to get group info...", exc_info=ex)
        raise ex
