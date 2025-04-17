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

from globus_sdk import AuthClient, GCSClient
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import AuthScopes

from ..groups.users import auth_client, get_user_uuid
from ..logging.logging import get_logger
from ..output.file_output import output
from .utils import gcs_client, get_collection

logger = get_logger()


def create_role(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal_type: str = "identity",
    principal: typing.Optional[str] = None,
    role: str = "activity_manager",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Gives to a group or to a user, a role on a Globus collection.
       The role could be: "adminsitrator", "activtivty_monitor", "activity_monitor" or "access_manager"

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        collection_name (typing.Optional[str], optional): The name of the collection that the role will be added to.
                                                          It is required to give either the `collection_name` or
                                                          `collection_id`. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection the role will be added to.
                                                        It is required to give either the `collection_name` or
                                                        `collection_id`.Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user. Please provide Globus
                                                        identities that end in either "orcid.org" or "globusid.org".
                                                        To use this option  you must give a principal_type for the
                                                        users, either "identity" or "group". Defaults to None.
        principal_type (str, optional): The type of principal being given the role either "identity"
                                        or "group". This must be given if user identity is given.
                                        Defaults to "identity".
        principal (typing.Optional[str], optional): The globus uuid of the user or group. This can be given instead of
                                                    user_identity and principal_type. Defaults to None.
        role (str, optional): Globus role on collections either "administrator", "activity_manager",
                              "activity_monitor" or "access_manager". Defaults to "activity_manager".
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of adding a role to the Globus collection uses standard HTTPS structure.

    Raises:
        ValueError: user_identity and principal_type were provided but principal_type was not "identity"
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get collection info
        ex: Fail to get role list
        ex: Fail to create role

    """
    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
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

    gcs_response = _create_role(
        current_gcs_client=current_gcs_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal_type=principal_type,
        principal=principal,
        role=role,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _create_role(
    current_gcs_client: GCSClient,
    current_auth_client: AuthClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal_type: str = "identity",
    principal: typing.Optional[str] = None,
    role: str = "activity_manager",
) -> GlobusHTTPResponse:
    """Private method used by `create_role`. Creates the role on the collection with validation steps.
    Args:
        current_gcs_client (GCSClient, required): Globus connect server client.
        current_auth_client (AuthClient, required): Globus Authentication Client.
        collection_name (typing.Optional[str], optional): The name of the collection that the role will be added to.
                                                          Either `collection_name` or `collection id` must be provided.
                                                          Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection the role will be added to.
                                                        Either `collection_name` or `collection_id` must be provided.
                                                        Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user to whom the role will be given.
                                                        Please provide Globus identities that end in either "orcid.org"
                                                        or "globusid.org". To use this option if you provide a
                                                        `principal_type` argument this must be "identity". Either
                                                        `user_identity` or both `principal_type` and `principal`
                                                        must be provided. Defaults to None.
        principal_type (str, optional): The type of principal being given the role either "identity"
                                        or "group". Either `user_identity` or both `principal_type`
                                        and `principal` must be provided. Defaults to "identity".
        principal (typing.Optional[str], optional): The globus uuid of the user or group to whom the role will be given.
                                                    Either `user_identity` or both `principal_type` and `principal`
                                                    must be provided. Defaults to None.
        role (str, optional): Globus roles on collections either "administrator", "activity_manager",
                              "activity_monitor" or "access_manager". Defaults to "activity_manager".

    Returns:
        GlobusHTTPResponse: Globus API result of adding a role to the Globus collection uses standard HTTPS structure.

    Raises:
        ValueError: user_identity and principal_type were provided but principal_type was not "identity"
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get collection info
        ex: Fail to get role list
        ex: Fail to create role

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
                """Please provide either a valid user_identity (ending with
                   either with @orcid.org or @globusid.org) or provide a user's uuid
                   (aka its principal)."""
            )
            raise ValueError(
                """Please provide either a valid user_identity (ending with
                   either with @orcid.org or @globusid.org) or provide a user's uuid
                   (aka its principal)."""
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

    check_role = _get_role(
        current_gcs_client=current_gcs_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        principal=principal,
        role=role,
        role_id=None,
    )

    if len(check_role) == 1:
        logger.error(f"Error: Role already exists: {check_role}.")
        raise ValueError(f"Error: Role already exists: {check_role}.")
    elif len(check_role) > 1:
        logger.error(
            f"""Multiple roles found based on this input {check_role}. Please provide more specific input
                to discern if this role does not already exist so it can then be created."""
        )
        raise ValueError(
            f"""Multiple roles found based on this input {check_role}. Please provide more specific
                input to discern if this role does not already exist so it can then be created."""
        )

    collection = get_collection(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        collection_id=collection_id,
    )

    if len(collection) == 0:
        logger.error(
            f"""Error: No collection found based on the collection_name {collection_name} and the
                collection_id {collection_id}."""
        )
        raise ValueError(
            f"""Error: No collection found based on the collection_name {collection_name} and the
                collection_id {collection_id}."""
        )
    elif len(collection) > 1:
        logger.error(f"Error: Multiple collections found {collection}.")
        raise ValueError(f"Error: Multiple collections found {collection}.")

    try:
        if principal_type == "identity":
            role_data = {
                "DATA_TYPE": "role#1.0.0",
                "principal": f"urn:globus:auth:identity:{principal}",
                "collection": collection[0]["id"],
                "role": role,
            }
        elif principal_type == "group":
            role_data = {
                "DATA_TYPE": "role#1.0.0",
                "principal": f"urn:globus:groups:id:{principal}",
                "collection": collection[0]["id"],
                "role": role,
            }
        else:
            logger.error('Error: principal_type is neither "identity" nor "group".')
            raise ValueError('Error: principal_type is neither "identity" nor "group".')

        role_result = current_gcs_client.create_role(role_data)
        logger.info(role_result)
        return role_result

    except Exception as ex:
        logger.exception("Failed to create role...", exc_info=ex)
        raise ex


def delete_role(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    role: typing.Optional[str] = None,
    role_id: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Deletes role from the collection with verification checks

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        collection_name (typing.Optional[str], optional): The name of the collection that the role will be removed from.
                                                          It is required to give either the `collection_name` or
                                                          `collection_id`. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection the role will be removed
                                                        from. It is required to give either the `collection_name` or
                                                        `collection_id`. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user. Please provide Globus
                                                        identities that end in either "orcid.org" or "globusid.org".
                                                        Can be used with role title instead of using principal.
                                                        Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group. Can be used instead of
                                                    user_identity and role. Defaults to None.
        role (typing.Optional[str], optional): Globus roles on collections either "administrator", "activity_manager",
                                               "activity_monitor" or "access_manager". Defaults to None.
        role_id: the role uuid. This must be given if there is more than one entry for a user on that role.
                                Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of deleting a role to the Globus collection uses standard HTTPS
                            structure.

    Raises:
        ValueError: user_identity and principal_type were provided but principal_type was not "identity"
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get collection info
        ex: Fail to get role list
        ex: Fail to delete role

    """
    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
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

    gcs_response = _delete_role(
        current_gcs_client=current_gcs_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal=principal,
        role=role,
        role_id=role_id,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _delete_role(
    current_gcs_client: GCSClient,
    current_auth_client: AuthClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    role: typing.Optional[str] = None,
    role_id: typing.Optional[str] = None,
) -> GlobusHTTPResponse:
    """Private method used by `delete_role`. Deletes role from the collection with verification checks.

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client.
        current_auth_client (AuthClient, required): Globus Authentication Client.
        collection_name (typing.Optional[str], optional): The name of the collection that the role will be removed from.
                                                          If a `collection_name` is not given, a `collection_id` must
                                                          be provided. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection the role will be removed
                                                        from. If a `collection_id` is not provided, then a
                                                        `collection_name` must be given. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user. Please provide Globus
                                                        identities that end in either "orcid.org" or "globusid.org".
                                                        Can be used with role title instead of using principal.
                                                        Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group. Can be used instead of
                                                    `user_identity` and `role`. If both `user_identity` and `principal`
                                                    are supplied they must agree. Defaults to None.
        role (typing.Optional[str], optional): Globus roles on collections either `administrator`, `activity_manager`,
                                               `activity_monitor` or `access_manager. Defaults to None.
        role_id (typing.Optional[str], optional): The role uuid. This is to disambiguate the exact role if there is more
                                                  than one role for a principal/user on that collection.
                                                  Defaults to None.

    Returns:
        GlobusHTTPResponse: Globus API result of deleting a role to the Globus collection uses standard HTTPS structure.

    Raises:
        ValueError: user_identity and principal_type were provided but principal_type was not "identity"
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get collection info
        ex: Fail to get role list
        ValueError: ACL rule was not found
        ValueError: More than one ACL rule was found
        ex: Fail to delete role

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

    check_role = _get_role(
        current_gcs_client=current_gcs_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        principal=principal,
        role=role,
        role_id=role_id,
    )

    if len(check_role) == 0:
        logger.error("Error: Role does not exist.")
        raise ValueError("Error: Role does not exist.")
    elif len(check_role) > 1:
        logger.error(
            f"""Multiple roles found based on this input {check_role}. Please provide more specific
                input to discern which role to delete."""
        )
        raise ValueError(
            f"""Multiple roles found based on this input {check_role}. Please provide more specific
                input to discern which role to delete."""
        )
    try:
        role_result = current_gcs_client.delete_role(check_role[0]["id"])
        logger.info(role_result)
        return role_result

    except Exception as ex:
        logger.exception("Failed to delete role...", exc_info=ex)
        raise ex


def get_role(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    role: typing.Optional[str] = None,
    role_id: typing.Optional[str] = None,
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Checks that a role id is present in the list of roles on a collection from either the: `user_identity` or
       `role_id` or `principal` and returns infp about this role.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        collection_name (typing.Optional[str], optional): The name of the collection to search for the role.
                                                          It is required to give either the `collection_name` or
                                                          `collection_id`.  Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection to search for the role.
                                                        It is required to give either the `collection_name` or
                                                        `collection_id`. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user. Please provide Globus
                                                        identities that end in either "orcid.org" or "globusid.org".
                                                        If you want to reference a group and not a user, please use the
                                                        `principal_type` option (input "group") and the `principal`
                                                        option (uuid of the group). You can use these 2 options of
                                                        course, if you want to add a user for whom you do not know
                                                        their Globus identity. Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group. Can be used instead of
                                                    `user_identity`. If both are used. they must agree.
                                                    Defaults to None.
        role (typing.Optional[str], optional): Globus roles on collections either `administrator`, `activity_manager`,
                                               `activity_monitor` or `access_manager. To be used in conjunction with
                                               either `user_identity` or `role` Defaults to None.
        role_id (typing.Optional[str], optional): The role uuid. This is to disambiguate the exact role if there is more
                                                  than one role for a principal/user on that collection.
                                                  Defaults to None.
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: role details within a one element list. If no role is found
                                         it returns an empty list.

    Raises:
        ValueError: user_identity and principal_type were provided but principal_type was not "identity"
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get collection info
        ex: Fail to get role list
        ex: Fail to get role info

    """
    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
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

    gcs_response = _get_role(
        current_gcs_client=current_gcs_client,
        current_auth_client=current_auth_client,
        collection_name=collection_name,
        collection_id=collection_id,
        user_identity=user_identity,
        principal=principal,
        role=role,
        role_id=role_id,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _get_role(
    current_gcs_client: GCSClient,
    current_auth_client: AuthClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    user_identity: typing.Optional[str] = None,
    principal: typing.Optional[str] = None,
    role: typing.Optional[str] = None,
    role_id: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `get_role`. Checks that a role id is present in the list of roles on a collection
       from either the: `user_identity` or `role_id` or `principal`, and returns infp about this role.

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client.
        current_auth_client (AuthClient, required): Globus Authentication Client.
        collection_name (typing.Optional[str], optional): The name of the collection to search for the role.
                                                          Either the `collection_name` or the `collection_id`
                                                          can be provided. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection to search for the role.
                                                        Either the `collection_name` or the `collection_id`
                                                        can be provided. Defaults to None.
        user_identity (typing.Optional[str], optional): The Globus identity of the user. Please provide Globus
                                                        identities that end in either "orcid.org" or "globusid.org".
                                                        Can be used instead of `principal`. If both are used they
                                                        must agree. Defaults to None.
        principal (typing.Optional[str], optional): The globus uuid of the user or group. Can be used instead of
                                                   `user_identity`. If both are used. they must agree. Defaults to None.
        role (typing.Optional[str], optional): Globus roles on collections either "administrator", "activity_manager",
                                               "activity_monitor" or "access_manager". To be used in conjunction with
                                               either `user_identity` or `role` Defaults to None.
        role_id (typing.Optional[str], optional): The role uuid. This is to disambiguate the exact role if there is more
                                                  than one role for a principal/user on that collection.
                                                  Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: role details within a one element list. If no role is found
                                         it returns an empty list.

    Raises:
        ValueError: user_identity and principal_type were provided but principal_type was not "identity"
        ValueError: user_identity's domain is neither @orcid.org nor @globusid.org
        ex: Fail to get users' properties
        ValueError: user_identity and principal were provided but user_identity's principal is not matching the input
                    principal
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get collection info
        ex: Fail to get role list
        ex: Fail to get role info

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
                """Please provide either a valid user_identity (ending with either with @orcid.org
                   or @globusid.org) or provide a user's uuid (aka its principal)."""
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
                f"""Provided user_identity has uuid {user_uuid} that do not match with the
                    provided principal {principal}. Please to disambiguate, provide as input either
                    only one or the other or a user_identity with uuid that matches the principal."""
            )

        principal = user_uuid

    output_role = list()
    if role_id is None:
        list_of_roles = _role_list(
            current_gcs_client=current_gcs_client,
            collection_name=collection_name,
            collection_id=collection_id,
        )

        matching_roles = None
        if principal is not None:
            matching_roles = list()
            for currect_role in list_of_roles:
                if principal in currect_role["principal"]:
                    matching_roles.append(currect_role)

        matching_roles2 = None
        if role is not None:
            matching_roles2 = list()
            if principal is not None:
                for currect_role in matching_roles:
                    if role == currect_role["role"]:
                        matching_roles2.append(currect_role)
                if len(matching_roles2) == 0:
                    logger.error(
                        f"No role found with principal: {principal} and with {role} role"
                    )
                elif len(matching_roles2) > 1:
                    logger.warning(
                        f"""Multiple roles found with principal: {principal} and with {role} role.
                            This should not be possible, as a principal can only have 1 role of the
                            same type in the same collection. Investigate further."""
                    )
                    output_role = matching_roles2
                else:
                    output_role = matching_roles2
            else:
                for currect_role in list_of_roles:
                    if role == currect_role["role"]:
                        matching_roles2.append(currect_role)
                if len(matching_roles2) == 0:
                    logger.error(
                        f"""No role found with title {role}.
                            Maybe provide the principal if it is known for disambiguation."""
                    )
                elif len(matching_roles2) > 1:
                    logger.warning(
                        f"""Multiple roles found with title {role}.
                            Please also provide a principal for disambiguation."""
                    )
                    output_role = matching_roles2
                else:
                    output_role = matching_roles2

        if matching_roles2 is None and matching_roles is None:
            logger.error(
                "If the role_id is not provided then either the principal or the role title should be."
            )
            raise ValueError(
                """If the role_id is not provided then either the principal or the role title
                   should be."""
            )
        elif matching_roles2 is None:
            if len(matching_roles) == 0:
                logger.error(
                    f"""No role found with principal {principal}.
                        Maybe provide the role title if it is known for disambiguation."""
                )
            elif len(matching_roles) > 0:
                logger.warning(
                    f"""Multiple roles found with principal {principal}.
                        Please also provide a role title for disambiguation."""
                )
                output_role = matching_roles
            else:
                output_role = matching_roles

    else:
        try:
            output_role.append(
                current_gcs_client.get_role(role_id, {"include": "all_roles"})
            )
        except Exception as ex:
            logger.exception("Failed to get role info...", exc_info=ex)
            raise ex

    logger.info(output_role)
    return output_role


def role_list(
    confidential_client_id: str,
    confidential_client_secret: str,
    endpoint_id: str,
    mapped_collection_id: str,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    include: typing.Optional[str] = "all_roles",
    json: typing.Optional[str] = None,
    yaml: typing.Optional[str] = None,
) -> typing.List[GlobusHTTPResponse]:
    """Returns a list of roles on a collection

    Args:

        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        endpoint_id (str, required): The endpoint where your confidential client is mapped.
        mapped_collection_id (str, required): The mapped collection that the collection sits on.
        collection_name (typing.Optional[str], optional): The name of the collection to retrieve the role list from.
                                                          It is required to give either the `collection_name` or
                                                          `collection_id`. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection to search for the role.
                                                        It is required to give either the `collection_name` or
                                                        `collection_id`. Defaults to None.
        include (typing.Optional[str], optional): Elect to return or not information about all roles.
                                                  To do this the input must be "all_roles". To not do this input None.
                                                  Defaults to "all_roles".
        json (typing.Optional[str], optional): output a json. Defaults to None.
        yaml (typing.Optional[str], optional): output a yaml. Defaults to None.

    Returns:
        typing.List[GlobusHTTPResponse]: Returns a list of roles associated with the collection

    Raises:
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get collection info
        ex: Fail to get role list

    """
    current_gcs_client = gcs_client(
        confidential_client_id=confidential_client_id,
        confidential_client_secret=confidential_client_secret,
        endpoint_id=endpoint_id,
        collection_ids=[
            mapped_collection_id,
        ],
    )

    gcs_response = _role_list(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        collection_id=collection_id,
        include=include,
    )

    output(gcs_response, json_filename=json, yaml_filename=yaml)

    return gcs_response


def _role_list(
    current_gcs_client: GCSClient,
    collection_name: typing.Optional[str] = None,
    collection_id: typing.Optional[str] = None,
    include: typing.Optional[str] = "all_roles",
) -> typing.List[GlobusHTTPResponse]:
    """Private method used by `role_list`. Returns a list of roles on a collection.

    Args:
        current_gcs_client (GCSClient, required): Globus connect server client.
        collection_name (typing.Optional[str], optional): The name of the collection to retrieve the role list from.
                                                          It is required to give either the `collection_name` or
                                                          `collection_id`. Defaults to None.
        collection_id (typing.Optional[str], optional): The collection id of the collection to search for the role.
                                                        It is required to give either the `collection_name` or
                                                        `collection_id`. Defaults to None.
        include (typing.Optional[str], optional): Elect to return or not information about all roles.
                                                  To do this the input must be "all_roles". To not do this input None.
                                                  Defaults to "all_roles".

    Returns:
        typing.List[GlobusHTTPResponse]: Returns a list of roles associated with the collection

    Raises:
        ValueError: Based on collection name and/or collection id, no collection was found
        ValueError: Based on collection name and/or collection id, more than one collection was found
        ex: Fail to get collection info
        ex: Fail to get role list

    """
    collection = get_collection(
        current_gcs_client=current_gcs_client,
        collection_name=collection_name,
        collection_id=collection_id,
    )

    if len(collection) == 0:
        logger.error(
            f"""Error: No collection found based on the collection_name {collection_name} and the
                collection_id {collection_id}."""
        )
        raise ValueError(
            f"""Error: No collection found based on the collection_name {collection_name} and the
                collection_id {collection_id}."""
        )
    elif len(collection) > 1:
        logger.error(
            f"Error: Multiple collections found {collection}. Provide collection_id to be precise."
        )
        raise ValueError(
            f"Error: Multiple collections found {collection}. Provide collection_id to be precise."
        )

    try:
        list_of_roles = list()
        for role in current_gcs_client.paginated.get_role_list(
            collection_id=collection[0]["id"], include=include
        ).items():
            list_of_roles.append(role)
        logger.info(list_of_roles)
        return list_of_roles

    except Exception as ex:
        logger.exception("Failed to get list of roles...", exc_info=ex)
        raise ex
