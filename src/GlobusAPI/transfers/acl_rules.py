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

from globus_sdk import AuthClient, TransferClient
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import AuthScopes, TransferScopes

from ..groups.users import auth_client, get_user_uuid
from ..logging.logging import get_logger
from ..output.file_output import output
from .transfer_client import transfer_client
from .transfer_methods import _get_monitored_collection

logger = get_logger(stdout=True)


def acl_rule_list(
    confidential_client_id: str = None,
    confidential_client_secret: str = None,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Get the list of ACL rules on a collection
    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        collection_name (typing.Optional[str], optional): The name of the collection for which to get the list of ACL
                                                          rules. It is required to give either the `collection_name` or
                                                          `collection_id`. Defaults to None.
        collection_id (typing.Optional[str], optional): The uuid of the collection for which to get the list of ACL
                                                        rules. It is required to give either the `collection_name` or
                                                        `collection_id`. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: a list of ACL rules on a collection.

    Raises:
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
    )

    list_of_acl_rules = _acl_rule_list(
        current_transfer_client=current_transfer_client,
        collection_name=collection_name,
        collection_id=collection_id,
    )

    output(list_of_acl_rules, json_filename=json, yaml_filename=yaml)

    return list_of_acl_rules


def _acl_rule_list(
    current_transfer_client: TransferClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `acl_rule_list`. Get the list of ACL rules on a collection
    Args:

        current_transfer_client (TransferClient, required): Globus Transfer Client.
        collection_name (typing.Optional[str], optional): The name of the collection for which to get the list of ACL
                                                          rules. It is required to give either the `collection_name` or
                                                          `collection_id`. Defaults to None.
        collection_id (typing.Optional[str], optional): The uuid of the collection for which to get the list of ACL
                                                        rules. It is required to give either the `collection_name` or
                                                        `collection_id`. Defaults to None.

    Returns:
        typing.List[typing.Mapping]: a list of ACL rules on a collection.

    Raises:
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list

    """

    collection = _get_monitored_collection(
        current_transfer_client=current_transfer_client,
        collection_name=collection_name,
        collection_id=collection_id,
    )

    if len(collection) == 0:
        logger.error(
            f"""Error: No collection found based on the collection_name {collection_name}
                and the collection_id {collection_id}."""
        )
        raise ValueError(
            f"""Error: No collection found based on the collection_name {collection_name}
                and the collection_id {collection_id}."""
        )
    elif len(collection) > 1:
        logger.error(
            f"Error: Multiple collections found {collection}. Provide collection_id to be precise."
        )
        raise ValueError(
            f"Error: Multiple collections found {collection}. Provide collection_id to be precise."
        )

    try:
        list_of_acl_rules = list(
            current_transfer_client.endpoint_manager_acl_list(collection[0]["id"])
        )

        logger.info(list_of_acl_rules)
        return list_of_acl_rules

    except Exception as ex:
        logger.exception("Failed collect a list of acl rules...", exc_info=ex)
        raise ex


def add_acl_rule(
    confidential_client_id: str = None,
    confidential_client_secret: str = None,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal_type: str = "identity",
    principal: typing.Optional[str] = None,
    path: str = "/",
    permissions: str = "r",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Creates an ACL rule allowing a group or an identity to read-only or read & write on a path on a collection.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        collection_name (typing.Optional[str], optional): The name of the collection that the ACL rule will be added to.
                                                          Either `collection_name` or `collection id` must be provided.
                                                          Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection the ACL rule will be
                                                        added to. Either `collection_name` or `collection_id` must be
                                                        provided. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user to whom the ACL rule will be
                                                        given. Please provide Globus identities that end in either
                                                        "orcid.org" or "globusid.org". To use this option if you
                                                        provide a principal_type argument this must be "identity".
                                                        Either `user_identity` or both `principal_type` and `principal`
                                                        must be provided. Defaults to None.
        principal_type (str, optional): The type of principal that will receive the ACL rule. Either
                                        "identity" or "group". Either `user_identity` or both
                                        `principal_type` and `principal` must be provided.
                                        Defaults to "identity".
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the ACL rule will be
                                                    given. Either `user_identity` or both `principal_type` and
                                                    `principal` must be provided. Defaults to None.
        path (str, optional): Path within the collection where the ACL rule will apply. Defaults to `/`.
        permissions (str, optional): Permissions of the ACL rule. Either `r` for read-only or `rw` for read & write
                                     must be provided. Defaults to `r`.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of adding an ACL rule to the Globus collection.
                            Uses standard HTTPS structure.

    Raises:
        ValueError: user_identity and principal_type were provided but principal_type was not "identity"
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list
        ex: Fail to add ACL rule

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
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

    acl_response = _add_acl_rule(
        current_transfer_client=current_transfer_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal_type=principal_type,
        principal=principal,
        path=path,
        permissions=permissions,
    )

    output(acl_response, json_filename=json, yaml_filename=yaml)

    return acl_response


def _add_acl_rule(
    current_transfer_client: TransferClient = None,
    current_auth_client: AuthClient = None,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal_type: str = "identity",
    principal: typing.Optional[str] = None,
    path: str = "/",
    permissions: str = "r",
) -> GlobusHTTPResponse:
    """Private method used by `add_acl_rule`. Creates an ACL rule on the collection with validation steps
    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        current_auth_client (AuthClient, required): Globus Authentication Client.
        collection_name (typing.Optional[str], optional): The name of the collection that the ACL rule will be added to.
                                                          Either `collection_name` or `collection id` must be provided.
                                                          Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection the ACL rule will be
                                                        added to. Either `collection_name` or `collection_id` must be
                                                        provided. Defaults to None.
        user_identity (str, optional): The Globus identity of the user to whom the ACL permission will
                                       be given. Please provide Globus identities that end in either
                                       "orcid.org" or "globusid.org". To use this option if you provide
                                       a principal_type argument this must be "identity". Either
                                       `user_identity` or both `principal_type` and `principal`
                                       must be provided. Defaults to "identity".
        principal_type (typing.Optional[str], optional): The type of principal that will receive the ACL rule. Either
                                                         "identity" or "group". Either `user_identity` or both
                                                         `principal_type` and `principal` must be provided.
                                                         Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the ACL rule will be
                                                    given. Either `user_identity` or both `principal_type` and
                                                    `principal` must be provided. Defaults to None.
        path (str, optional): Path within the collection where the ACL rule will apply. Defaults to `/`.
        permissions (str, optional): Permissions of the ACL rule. Either `r` for read-only or `rw` for read & write
                                     must be provided. Defaults to `r`.

    Returns:
        GlobusHTTPResponse: Globus API result of adding an ACL rule to the Globus collection.
                            Uses standard HTTPS structure.

    Raises:
        ValueError: user_identity and principal_type were provided but principal_type was not "identity"
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list
        ex: Fail to add ACL rule

    """
    if user_identity is not None:
        if principal_type != "identity":
            logger.error(
                'If the user_identity argument is provided, the principal type must be "identity".'
            )
            raise ValueError(
                'If the user_identity argument is provided, the principal type must be "identity".'
            )

        if (
            (not user_identity.endswith("@orcid.org"))
            and (not user_identity.endswith("@globusid.org"))
            and principal is None
        ):
            logger.error(
                """Please provide either a valid user_identity (ending with either with @orcid.org or
                   @globusid.org) or provide a user's uuid (aka its principal)."""
            )
            raise ValueError(
                """Please provide either a valid user_identity (ending with either with @orcid.org or
                   @globusid.org) or provide a user's uuid (aka its principal)."""
            )

        user_uuid = get_user_uuid(
            current_auth_client=current_auth_client,
            list_orcids=[
                user_identity,
            ],
        )[0]

        if principal is not None and user_uuid != principal:
            logger.error(
                f"""Provided user_identity has uuid {user_uuid} that do not match with the provided
                    principal {principal}. Please to disambiguate, provide as input either only one or the
                    other or a user_identity with uuid that matches the principal."""
            )
            raise ValueError(
                f"""Provided user_identity has uuid {user_uuid} that do not match with the provided
                    principal {principal}. Please to disambiguate, provide as input either only one or the
                    other or a user_identity with uuid that matches the principal."""
            )

        principal = user_uuid

    check_rule = _get_acl_rule(
        current_transfer_client=current_transfer_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal=principal,
        path=path,
        permissions=permissions,
        rule_id=None,
    )

    if len(check_rule) == 1:
        logger.error(f"Error: ACL rule already exists: {check_rule}.")
        raise ValueError(f"Error: ACL rule already exists: {check_rule}.")
    elif len(check_rule) > 1:
        logger.error(
            f"""Multiple ACL rules found based on this input {check_rule}. Please provide more specific
                input to discern if this ACL rule does not already exist so it can then be created."""
        )
        raise ValueError(
            f"""Multiple ACL rules found based on this input {check_rule}. Please provide more specific
                input to discern if this ACL rule does not already exist so it can then be created."""
        )

    collection = _get_monitored_collection(
        current_transfer_client=current_transfer_client,
        collection_name=collection_name,
        collection_id=collection_id,
    )

    if len(collection) == 0:
        logger.error(
            f"""Error: No collection found based on the collection_name {collection_name}
                and the collection_id {collection_id}."""
        )
        raise ValueError(
            f"""Error: No collection found based on the collection_name {collection_name}
                and the collection_id {collection_id}."""
        )
    elif len(collection) > 1:
        logger.error(f"Error: Multiple collections found {collection}.")
        raise ValueError(f"Error: Multiple collections found {collection}.")

    try:
        rule_data = {
            "DATA_TYPE": "access",
            "principal_type": principal_type,
            "principal": principal,
            "path": path,
            "permissions": permissions,
        }

        acl_rule_result = current_transfer_client.add_endpoint_acl_rule(
            collection[0]["id"], rule_data
        )
        logger.info(acl_rule_result)
        return acl_rule_result

    except Exception as ex:
        logger.exception("Failed to add acl rule...", exc_info=ex)
        raise ex


def get_acl_rule(
    confidential_client_id: str,
    confidential_client_secret: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    permissions: typing.Optional[str] = None,
    rule_id: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Gets the info of an ACL rule that allows a group or an identity to read-only or read & write on a path on a
       collection.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        collection_name (typing.Optional[str], optional): The name of the collection where the ACL rule is applied.
                                                          Either `collection_name` or `collection id` must be provided.
                                                          Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection where the ACL rule is
                                                        applied. Either `collection_name` or `collection_id` must be
                                                        provided. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user to whom the ACL rule gives
                                                        permissions. Please provide Globus identities that end in either
                                                        "orcid.org" or "globusid.org". To use this option if you provide
                                                        a principal_type argument this must be "identity". Either
                                                        `user_identity` or both `principal_type` and `principal` must be
                                                        provided. Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the ACL rule gives
                                                    permissions. Either `user_identity` or both `principal_type` and
                                                    `principal` must be provided. Defaults to None.
        path (typing.Optional[str], optional): Path within the collection where the ACL rule gives permissions. Please
                                               provide this argument, if there are multiple ACL rules for the provided
                                               principle/user on the provided collection. Defaults to None.
        permissions (typing.Optional[str], optional): The type of permissions of the ACL rule. Either `r` for read-only
                                                      or `rw` for read & write must be provided. Please provide this
                                                      argument, if there are multiple ACL rules for the provided
                                                      principle/user on the provided collection. Defaults to None.
        rule_id: The ACL rule uuid. This is to disambiguate the exact ACL rule if is more than one ACL rule for a
                 principal/user on the provided collection. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: ACL rule details within a one element list. If no ACL rule is found
                                         it returns an empty list.

    Raises:
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: At least one of the three (`principal`, `path`, `permissions`) should be provided, or more.
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list
        ex. Fail to get ACL rule info

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
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

    acl_response = _get_acl_rule(
        current_transfer_client=current_transfer_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal=principal,
        path=path,
        permissions=permissions,
        rule_id=rule_id,
    )

    output(acl_response, json_filename=json, yaml_filename=yaml)

    return acl_response


def _get_acl_rule(
    current_transfer_client: TransferClient,
    current_auth_client: AuthClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    permissions: typing.Optional[str] = None,
    rule_id: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `get_acl_rule`. Gets the info of an ACL rule that allows a group or an identity to
       read-only or read & write on a path on a collection.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        current_auth_client (AuthClient, required): Globus Authentication Client.
        collection_name (typing.Optional[str], optional): The name of the collection where the ACL rule is applied.
                                                          Either `collection_name` or `collection id` must be provided.
                                                          Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection where the ACL rule is
                                                        applied. Either `collection_name` or `collection_id` must be
                                                        provided. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user to whom the ACL rule gives
                                                        permissions. Please provide Globus identities that end in
                                                        either "orcid.org" or "globusid.org". To use this option if
                                                        you provide a principal_type argument this must be "identity".
                                                        Either `user_identity` or both `principal_type` and `principal`
                                                        must be provided. Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the ACL rule gives
                                                    permissions. Either `user_identity` or both `principal_type` and
                                                    `principal` must be provided. Defaults to None.
        path (typing.Optional[str], optional): Path within the collection where the ACL rule gives permissions. Please
                                               provide this argument, if there are multiple ACL rules for the provided
                                               principle/user on the provided collection. Defaults to None.
        permissions (typing.Optional[str], optional): The type of permissions of the ACL rule. Either `r` for read-only
                                                      or `rw` for read & write must be provided. Please provide this
                                                      argument, if there are multiple ACL rules for the provided
                                                      principle/user on the provided collection. Defaults to None.
        rule_id: The ACL rule uuid. This is to disambiguate the exact ACL rule if is more than one ACL rule for a
                 principal/user on the provided collection. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: ACL rule details within a one element list. If no ACL rule is found
                                         it returns an empty list.

    Raises:
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: At least one of the three (`principal`, `path`, `permissions`) should be provided, or more.
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list
        ex. Fail to get ACL rule info

    """
    if user_identity is not None:
        if (
            (not user_identity.endswith("@orcid.org"))
            and (not user_identity.endswith("@globusid.org"))
            and principal is None
        ):
            logger.error(
                """Please provide either a valid user_identity (ending with either with @orcid.org or
                   @globusid.org) or provide a user's uuid (aka its principal)."""
            )
            raise ValueError(
                """Please provide either a valid user_identity (ending with either with @orcid.org or
                   @globusid.org) or provide a user's uuid (aka its principal)."""
            )

        user_uuid = get_user_uuid(
            current_auth_client=current_auth_client,
            list_orcids=[
                user_identity,
            ],
        )[0]

        if principal is not None and user_uuid != principal:
            logger.error(
                f"""Provided user_identity has uuid {user_uuid} that do not match with the provided
                    principal {principal}. Please to disambiguate, provide as input either only one or the
                    other or a user_identity with uuid that matches the principal."""
            )
            raise ValueError(
                f"""Provided user_identity has uuid {user_uuid} that do not match with the provided
                    principal {principal}. Please to disambiguate, provide as input either only one or
                    the other or a user_identity with uuid that matches the principal."""
            )

        principal = user_uuid

    output_rule = list()
    if rule_id is None:
        list_of_rules = _acl_rule_list(
            current_transfer_client=current_transfer_client,
            collection_name=collection_name,
            collection_id=collection_id,
        )

        matching_rules_principal = None
        if principal is not None:
            matching_rules_principal = list()
            for currect_rule in list_of_rules:
                if principal in currect_rule["principal"]:
                    matching_rules_principal.append(currect_rule)

        matching_rules_path = None
        if path is not None:
            matching_rules_path = list()
            for currect_rule in list_of_rules:
                if path in currect_rule["path"]:
                    matching_rules_path.append(currect_rule)

        matching_rules_permissions = None
        if permissions is not None:
            matching_rules_permissions = list()
            for currect_rule in list_of_rules:
                if path in currect_rule["path"]:
                    matching_rules_permissions.append(currect_rule)

        if principal is None and path is None and permissions is None:
            logger.error(
                """If the rule_id is not provided then either the principal or the path or the
                   permissions should be given or any combination of the three."""
            )
            raise ValueError(
                """If the rule_id is not provided then either the principal or the path or the
                   permissions should be given or any combination of the three."""
            )
        elif principal is not None and path is None and permissions is None:
            output_rule = matching_rules_principal
        elif principal is None and path is not None and permissions is None:
            output_rule = matching_rules_path
        elif principal is None and path is None and permissions is not None:
            output_rule = matching_rules_permissions
        elif principal is not None and path is not None and permissions is None:
            matching_rules2 = list()
            for currect_rule in matching_rules_principal:
                if path == currect_rule["path"]:
                    matching_rules2.append(currect_rule)
            if len(matching_rules2) == 0:
                logger.error(
                    f"No ACL rule found with principal: {principal} and with {path} path"
                )
            elif len(matching_rules2) > 1:
                logger.warning(
                    f"""Multiple ACL rules found with principal: {principal} and with {path} path.
                        This should not be possible, as a principal can only have 1 ACL rule per path in
                        the same collection. Investigate further."""
                )
                output_rule = matching_rules2
            else:
                output_rule = matching_rules2
        elif principal is not None and path is None and permissions is not None:
            matching_rules2 = list()
            for currect_rule in matching_rules_principal:
                if permissions == currect_rule["permissions"]:
                    matching_rules2.append(currect_rule)
            if len(matching_rules2) == 0:
                logger.error(
                    f"No ACL rule found with principal: {principal} and with {permissions} permission"
                )
            elif len(matching_rules2) > 1:
                logger.warning(
                    f"""Multiple ACL rules found with principal: {principal} and with "{permissions}" permissions.
                        This should happen if the {principal} principal has "{permissions}" permissions on
                        different paths in the same collections."""
                )
                output_rule = matching_rules2
            else:
                output_rule = matching_rules2
        elif principal is None and path is not None and permissions is not None:
            matching_rules2 = list()
            for currect_rule in matching_rules_path:
                if permissions == currect_rule["permissions"]:
                    matching_rules2.append(currect_rule)
            if len(matching_rules2) == 0:
                logger.error(
                    f'No ACL rule found specifically for path: {path} and with "{permissions}" permissions.'
                )
            elif len(matching_rules2) > 1:
                logger.warning(
                    f"""Multiple ACL rules found specifically for path: {path} and with "{permissions}"
                        permissions. This should happen if the multiple principals (aka users or groups), have
                        "{permissions}" permissions on the path: {path}."""
                )
                output_rule = matching_rules2
            else:
                output_rule = matching_rules2
        else:
            matching_rules2 = list()
            for currect_rule in matching_rules_principal:
                if path == currect_rule["path"]:
                    matching_rules2.append(currect_rule)
            matching_rules3 = list()
            for currect_rule in matching_rules2:
                if permissions == currect_rule["permissions"]:
                    matching_rules3.append(currect_rule)
            if len(matching_rules3) == 0:
                logger.error(
                    f"""No ACL rule found with principal: {principal}, for path: {path} and with
                                "{permissions}" permissions."""
                )
            elif len(matching_rules3) > 1:
                logger.warning(
                    f"""Multiple ACL rules found specifically ith principal: {principal}, for path:
                        {path} and with "{permissions}" permissions. This should not be possible, as a principal
                        can only have 1 rule per path in the same collection. Investigate further."""
                )
                output_rule = matching_rules3
            else:
                output_rule = matching_rules3
    else:
        collection = _get_monitored_collection(
            current_transfer_client=current_transfer_client,
            collection_name=collection_name,
            collection_id=collection_id,
        )

        if len(collection) == 0:
            logger.error(
                f"""Error: No collection found based on the collection_name {collection_name}
                    and the collection_id {collection_id}."""
            )
            raise ValueError(
                f"""No collection found based on the collection_name {collection_name}
                    and the collection_id {collection_id}."""
            )
        elif len(collection) > 1:
            logger.error(
                f"""Error: Multiple collections found {collection}.
                    Provide collection_id to be precise."""
            )
            raise ValueError(
                f"""Error: Multiple collections found {collection}. Provide collection_id
                    to be precise."""
            )
        try:
            output_rule.append(
                current_transfer_client.get_endpoint_acl_rule(
                    collection[0]["id"], rule_id
                )
            )

        except Exception as ex:
            logger.exception("Failed to get acl rule...", exc_info=ex)
            raise ex

    logger.info(output_rule)
    return output_rule


def delete_acl_rule(
    confidential_client_id: str,
    confidential_client_secret: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    permissions: typing.Optional[str] = None,
    rule_id: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Deletes an ACL rule that allowed a group or an identity to read-only or read & write on a path on a collection.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        collection_name (typing.Optional[str], optional): The name of the collection where the ACL rule to be deleted
                                                          is applied. Either `collection_name` or `collection id` must
                                                          be provided.  Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection where the ACL rule to be
                                                        deleted is applied. Either `collection_name` or `collection_id`
                                                        must be provided. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user to whom the ACL rule will be
                                                        removed. Please provide Globus identities that end in either
                                                        "orcid.org" or "globusid.org". To use this option if you provide
                                                        a principal_type argument this must be "identity". Either
                                                        `user_identity` or both `principal_type` and `principal` must be
                                                        provided. Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the ACL rule will be
                                                    deleted. Either `user_identity` or both `principal_type` and
                                                    `principal` must be provided. Defaults to None.
        path (typing.Optional[str], optional): Path within the collection where the ACL rule to be deleted applies.
                                               Please provide this argument, if there are multiple ACL rules for the
                                               provided principle/user on the provided collection. Defaults to None.
        permissions (typing.Optional[str], optional): Permissions of the ACL rule to be deleted. Either `r` for
                                                      read-only or `rw` for read & write must be provided. Please
                                                      provide this argument, if there are multiple ACL rules for the
                                                      provided principle/user on the provided collection.
                                                      Defaults to None.
        rule_id: The ACL rule uuid. This is to disambiguate the exact ACL rule if is more than one ACL rule for a
                 principal/user on the provided collection. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of deleting an ACL rule to the Globus collection.
                            Uses standard HTTPS structure.

    Raises:
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: At least one of the three (`principal`, `path`, `permissions`) should be provided, or more.
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list
        ex: Fail to get ACL rule info
        ex. Fail to delete ACL rule

    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
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

    acl_response = _delete_acl_rule(
        current_transfer_client=current_transfer_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal=principal,
        path=path,
        permissions=permissions,
        rule_id=rule_id,
    )

    output(acl_response, json_filename=json, yaml_filename=yaml)

    return acl_response


def _delete_acl_rule(
    current_transfer_client: TransferClient,
    current_auth_client: AuthClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    permissions: typing.Optional[str] = None,
    rule_id: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Private method used by `delete_acl_rule`. Deletes an ACL rule that allowed a group or an identity to read-only
       or read & write on a path on a collection.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        current_auth_client (AuthClient, required): Globus Authentication Client.
        collection_name (typing.Optional[str], optional): The name of the collection where the ACL rule to be deleted
                                                          is applied. Either `collection_name` or `collection id` must
                                                          be provided.  Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection where the ACL rule to be
                                                        deleted is applied. Either `collection_name` or `collection_id`
                                                        must be provided. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user to whom the ACL rule will be
                                                        removed. Please provide Globus identities that end in either
                                                        "orcid.org" or "globusid.org". To use this option if you
                                                        provide a principal_type argument this must be "identity".
                                                        Either `user_identity` or both `principal_type` and `principal`
                                                        must be provided. Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the ACL rule will be
                                                    deleted. Either `user_identity` or both `principal_type` and
                                                    `principal` must be provided. Defaults to None.
        path (typing.Optional[str], optional): Path within the collection where the ACL rule to be deleted applies.
                                               Please provide this argument, if there are multiple ACL rules for the
                                               provided principle/user on the provided collection. Defaults to None.
        permissions (typing.Optional[str], optional): Permissions of the ACL rule to be deleted. Either `r` for
                                                      read-only or `rw` for read & write must be provided. Please
                                                      provide this argument, if there are multiple ACL rules for the
                                                      provided principle/user on the provided collection.
                                                      Defaults to None.
        rule_id: The ACL rule uuid. This is to disambiguate the exact ACL rule if is more than one ACL rule for a
                 principal/user on the provided collection. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of deleting an ACL rule to the Globus collection.
                            Uses standard HTTPS structure.

    Raises:
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: At least one of the three (`principal`, `path`, `permissions`) should be provided, or more.
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list
        ex: Fail to get ACL rule info
        ValueError: ACL rule was not found
        ValueError: More than one ACL rule was found
        ex. Fail to delete ACL rule

    """
    if user_identity is not None:
        if (
            (not user_identity.endswith("@orcid.org"))
            and (not user_identity.endswith("@globusid.org"))
            and principal is None
        ):
            logger.error(
                """Please provide either a valid user_identity (ending with either with @orcid.org or
                   @globusid.org) or provide a user's uuid (aka its principal)."""
            )
            raise ValueError(
                """Please provide either a valid user_identity (ending with either with @orcid.org or
                   @globusid.org) or provide a user's uuid (aka its principal)."""
            )

        user_uuid = get_user_uuid(
            current_auth_client=current_auth_client,
            list_orcids=[
                user_identity,
            ],
        )[0]

        if principal is not None and user_uuid != principal:
            logger.error(
                f"""Provided user_identity has uuid {user_uuid} that do not match with the provided
                    principal {principal}. Please to disambiguate, provide as input either only one or the
                    other or a user_identity with uuid that matches the principal."""
            )
            raise ValueError(
                f"""Provided user_identity has uuid {user_uuid} that do not match with the provided
                    principal {principal}. Please to disambiguate, provide as input either only one or the
                    other or a user_identity with uuid that matches the principal."""
            )

        principal = user_uuid

    check_rule = _get_acl_rule(
        current_transfer_client=current_transfer_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal=principal,
        path=path,
        permissions=permissions,
        rule_id=rule_id,
    )

    if len(check_rule) == 0:
        logger.error("Error: ACL rule does not exist.")
        raise ValueError("Error: ACL rule does not exist.")
    elif len(check_rule) > 1:
        logger.error(
            f"""Multiple ACL rules found based on this input {check_rule}. Please provide more specific
                input to discern if this ACL rule does not already exist so it can then be created."""
        )
        raise ValueError(
            f"""Multiple ACL rules found based on this input {check_rule}. Please provide more specific
                input to discern if this ACL rule does not already exist so it can then be created."""
        )

    collection = _get_monitored_collection(
        current_transfer_client=current_transfer_client,
        collection_name=collection_name,
        collection_id=collection_id,
    )

    if len(collection) == 0:
        logger.error(
            f"""Error: No collection found based on the collection_name {collection_name}
                and the collection_id {collection_id}."""
        )
        raise ValueError(
            f"""Error: No collection found based on the collection_name {collection_name}
                and the collection_id {collection_id}."""
        )
    elif len(collection) > 1:
        logger.error(f"Error: Multiple collections found {collection}.")
        raise ValueError(f"Error: Multiple collections found {collection}.")

    try:
        acl_rule_result = current_transfer_client.delete_endpoint_acl_rule(
            collection[0]["id"], check_rule[0]["id"]
        )
        logger.info(acl_rule_result)
        return acl_rule_result

    except Exception as ex:
        logger.exception("Failed to delete acl rule...", exc_info=ex)
        raise ex


def update_acl_rule(
    confidential_client_id: str,
    confidential_client_secret: str,
    new_permissions: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    permissions: typing.Optional[str] = None,
    rule_id: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Updates an ACL rule to allow a group or an identity to read-only or read & write on a path on a collection.
       Only the permissions can be updated. To change the path or the user/group associated with a rule, the rule needs
       to be deleted and then be re-added.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        new_permissions (str, optional): New permissions of the updated ACL rule. Either `r` for
                                         read-only or `rw` for read & write must be provided. Please provide this
                                         argument, if there are multiple ACL rules for the provided principle/user on
                                         the provided collection. Defaults to None.
        collection_name (typing.Optional[str], optional): The name of the collection where the ACL rule to be updated is
                                                          applied. Either `collection_name` or `collection id` must be
                                                          provided.  Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection where the ACL rule to be
                                                        updated is applied. Either `collection_name` or `collection_id`
                                                        must be provided. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user to whom the ACL rule will be
                                                        updated. Please provide Globus identities that end in either
                                                        "orcid.org" or "globusid.org". To use this option if you provide
                                                        a principal_type argument this must be "identity". Either
                                                        `user_identity` or both `principal_type` and `principal` must be
                                                        provided. Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the ACL rule will be
                                                    updated. Either `user_identity` or both `principal_type` and
                                                    `principal` must be provided. Defaults to None.
        path (typing.Optional[str], optional): Path within the collection where the ACL rule to be updated applies.
                                               Please provide this argument, if there are multiple ACL rules for the
                                               provided principle/user on the provided collection. Defaults to None.
        permissions (typing.Optional[str], optional): Previous permissions of the ACL rule to be updated. Either `r`
                                                      for read-only or `rw` for read & write must be provided. Please
                                                      provide this argument, if there are multiple ACL rules for the
                                                      provided principle/user on the provided collection.
                                                      Defaults to None.
        rule_id: The ACL rule uuid. This is to disambiguate the exact ACL rule if is more than one ACL rule for a
                 principal/user on the provided collection. Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of deleting an ACL rule to the Globus collection.
                            Uses standard HTTPS structure.

    Raises:
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: At least one of the three (`principal`, `path`, `permissions`) should be provided, or more.
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list
        ex: Fail to get ACL rule info
        ValueError: ACL rule was not found
        ValueError: More than one ACL rule was found
        ex. Fail to update ACL rule
    """
    current_transfer_client = transfer_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        scopes=TransferScopes.all,
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

    acl_response = _update_acl_rule(
        current_transfer_client=current_transfer_client,
        current_auth_client=current_auth_client,
        new_permissions=new_permissions,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal=principal,
        path=path,
        permissions=permissions,
        rule_id=rule_id,
    )

    output(acl_response, json_filename=json, yaml_filename=yaml)

    return acl_response


def _update_acl_rule(
    current_transfer_client: TransferClient,
    current_auth_client: AuthClient,
    new_permissions: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    permissions: typing.Optional[str] = None,
    rule_id: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Private method used by `update_acl_rule`. Updates an ACL rule to allow a group or an identity to read-only or
       read & write on a path on a collection. Only the permissions can be updated. To change the path or the
       user/group assosiated with a rule, the rule needs to be deleted and then be re-added.

    Args:
        current_transfer_client (TransferClient, required): Globus Transfer Client.
        current_auth_client (AuthClient, required): Globus Authentication Client.
        new_permissions (str, required): New permissions of the updated ACL rule. Either `r` for read-only or `rw` for
                                         read & write must be provided. Please provide this argument, if there are
                                         multiple ACL rules for the provided principle/user on the provided collection.
                                         Defaults to None.
        collection_name (typing.Optional[str], optional): The name of the collection where the ACL rule to be updated is
                                                          applied. Either `collection_name` or `collection id` must be
                                                          provided.  Defaults to None.
        collection_id (typing.Optional[str], optional): The collection uuid of the collection where the ACL rule to be
                                                        updated is applied. Either `collection_name` or `collection_id`
                                                        must be provided. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user to whom the ACL rule will be
                                                        updated. Please provide Globus identities that end in either
                                                        "orcid.org" or "globusid.org". To use this option if you
                                                        provide a principal_type argument this must be "identity".
                                                        Either `user_identity` or both `principal_type` and `principal`
                                                        must be provided. Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the ACL rule will be
                                                    updated. Either `user_identity` or both `principal_type` and
                                                    `principal` must be provided. Defaults to None.
        path (typing.Optional[str], optional): Path within the collection where the ACL rule to be updated applies.
                                               Please provide this argument, if there are multiple ACL rules for the
                                               provided principle/user on the provided collection. Defaults to None.
        permissions (typing.Optional[str], optional): Previous permissions of the ACL rule to be updated. Either `r`
                                                      for read-only or `rw` for read & write must be provided. Please
                                                      provide this argument, if there are multiple ACL rules for the
                                                      provided principle/user on the provided collection.
                                                      Defaults to None.
        rule_id: The ACL rule uuid. This is to disambiguate the exact ACL rule if is more than one ACL rule for a
                 principal/user on the provided collection. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of deleting an ACL rule to the Globus collection.
                            Uses standard HTTPS structure.

    Raises:
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: At least one of the three (`principal`, `path`, `permissions`) should be provided, or more.
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get monitored collection list
        ex: Fail to get ACL rule list
        ex: Fail to get ACL rule info
        ValueError: ACL rule was not found
        ValueError: More than one ACL rule was found
        ex. Fail to update ACL rule

    """
    if rule_id is None:
        if user_identity is not None:
            if (
                (not user_identity.endswith("@orcid.org"))
                and (not user_identity.endswith("@globusid.org"))
                and principal is None
            ):
                logger.error(
                    """Please provide either a valid user_identity (ending with either with @orcid.org or
                       @globusid.org) or provide a user's uuid (aka its principal)."""
                )
                raise ValueError(
                    """Please provide either a valid user_identity (ending with either with @orcid.org or
                       @globusid.org) or provide a user's uuid (aka its principal)."""
                )

            user_uuid = get_user_uuid(
                current_auth_client=current_auth_client,
                list_orcids=[
                    user_identity,
                ],
            )[0]

            if principal is not None and user_uuid != principal:
                logger.error(
                    f"""Provided user_identity has uuid {user_uuid} that do not match with the provided
                        principal {principal}. Please to disambiguate, provide as input either only one or
                        the other or a user_identity with uuid that matches the principal."""
                )
                raise ValueError(
                    f"""Provided user_identity has uuid {user_uuid} that do not match with the provided
                        principal {principal}. Please to disambiguate, provide as input either only one or
                        the other or a user_identity with uuid that matches the principal."""
                )

            principal = user_uuid

        check_rule = _get_acl_rule(
            current_transfer_client=current_transfer_client,
            current_auth_client=current_auth_client,
            collection_name=collection_name,
            collection_id=collection_id,
            user_identity=user_identity,
            principal=principal,
            path=path,
            permissions=permissions,
        )

        if len(check_rule) == 0:
            logger.error("Error: ACL rule does not exist.")
            raise ValueError("Error: ACL rule does not exist.")
        elif len(check_rule) > 1:
            logger.error(
                f"""Multiple ACL rules found based on this input {check_rule}. Please provide more specific
                    input to discern if this ACL rule does not already exist so it can then be created."""
            )
            raise ValueError(
                f"""Multiple ACL rules found based on this input {check_rule}. Please provide more
                    specific input to discern if this ACL rule does not already exist so it can then
                    be created."""
            )

        collection = _get_monitored_collection(
            current_transfer_client=current_transfer_client,
            collection_name=collection_name,
            collection_id=collection_id,
        )

        if len(collection) == 0:
            logger.error(
                f"""Error: No collection found based on the collection_name {collection_name}
                    and the collection_id {collection_id}."""
            )
            raise ValueError(
                f"""Error: No collection found based on the collection_name {collection_name}
                    and the collection_id {collection_id}."""
            )
        elif len(collection) > 1:
            logger.error(f"Error: Multiple collections found {collection}.")
            raise ValueError(f"Error: Multiple collections found {collection}.")

        if principal is None:
            principal = check_rule[0]["principal"]
        if path is None:
            path = check_rule[0]["path"]

        try:
            rule_data = {
                "DATA_TYPE": "access",
                "principal": principal,
                "path": path,
                "permissions": new_permissions,
            }

            acl_rule_result = current_transfer_client.update_endpoint_acl_rule(
                collection[0]["id"], check_rule[0]["id"], rule_data
            )
        except Exception as ex:
            logger.exception("Failed to update acl rule...", exc_info=ex)
            raise ex

    else:
        collection = _get_monitored_collection(
            current_transfer_client=current_transfer_client,
            collection_name=collection_name,
            collection_id=collection_id,
        )

        if len(collection) == 0:
            logger.error(
                f"""Error: No collection found based on the collection_name {collection_name}
                    and the collection_id {collection_id}."""
            )
            raise ValueError(
                f"""Error: No collection found based on the collection_name {collection_name}
                    and the collection_id {collection_id}."""
            )
        elif len(collection) > 1:
            logger.error(f"Error: Multiple collections found {collection}.")
            raise ValueError(f"Error: Multiple collections found {collection}.")

        try:
            rule_data = {"DATA_TYPE": "access", "permissions": new_permissions}

            acl_rule_result = current_transfer_client.update_endpoint_acl_rule(
                collection[0]["id"], rule_id, rule_data
            )

        except Exception as ex:
            logger.exception("Failed to update acl rule...", exc_info=ex)
            raise ex

    logger.info(acl_rule_result)
    return acl_rule_result
