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

from globus_sdk import AuthClient
from globus_sdk._types import ScopeCollectionType
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import AuthScopes

import GlobusAPI

from ..logging.logging import get_logger

logger = get_logger()


def auth_client(
    confidential_client_id: str,
    confidential_client_secret: str,
    scopes: typing.Optional[ScopeCollectionType] = None,
) -> AuthClient:
    """Return an auth client object initialized with the given parameters

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        scopes (typing.Optional[ScopeCollectionType], optional): The Globus Scopes for the
                                                                 auth client.
                                                                 Defaults to a list: [
                                                                 AuthScopes.openid,
                                                                 AuthScopes.profile,
                                                                 AuthScopes.email,
                                                                 AuthScopes.view_identity_set
                                                                 ].

    Returns:
        It returns an auth client object initialized with the given parameters.

    Raises:
        ex: Fail to create authorizer
        ex: Fail to create auth client

    """
    if scopes is None:
        scopes = [
            AuthScopes.openid,
            AuthScopes.profile,
            AuthScopes.email,
            AuthScopes.view_identity_set,
        ]
    try:
        auth_authorizer = GlobusAPI.auth.authorizer.get_client_credentials_authorizer(
            confidential_client_id, confidential_client_secret, scopes
        )

    except Exception as ex:
        logger.exception("Failed to create authorizer...", exc_info=ex)
        raise ex

    try:
        current_auth_client = AuthClient(authorizer=auth_authorizer)
        logger.info("Auth client created ")

        return current_auth_client

    except Exception as ex:
        logger.exception("Failed to create auth client...", exc_info=ex)
        raise ex


def get_users(
    current_auth_client: AuthClient, list_orcids: typing.List[str]
) -> typing.List[GlobusHTTPResponse]:
    """Return a list of dictionaries each with info about a user of the corresponding ORCID
       from the list of provided ORCIDs.

    Args:
        current_auth_client (AuthClient, required): AuthClient
        list_orcids (typing.List[str], required): list of ORCIDs in the form ["0000-0000-0000-0000@orcid.org"]

    Returns:
        typing.List[GlobusHTTPResponse]: A list of dictionaries each with info about a user of the corresponding ORCID
                                         from the list of provided ORCIDs.

    Raises:
        ex: Fail to get users' properties

    """
    try:
        response = current_auth_client.get_identities(usernames=list_orcids)

        return response["identities"]

    except Exception as ex:
        logger.exception("Failed to get users' properties...", exc_info=ex)
        raise ex


def get_user_uuid(
    current_auth_client: AuthClient, list_orcids: typing.List[str]
) -> typing.List[str]:
    """Return a list of users' uuids based the provided list of ORCIDs.

    Args:
        current_auth_client (AuthClient, required): AuthClient
        list_orcids (typing.List[str], required): list of ORCIDs in the form ["0000-0000-0000-0000@orcid.org"]

    Returns:
        typing.List[str]: A list of users' uuids based the provided list of ORCIDs.

    Raises:
        ex: Fail to get users' properties

    """
    try:
        users = get_users(current_auth_client, list_orcids)
        return [user["id"] for user in users]

    except Exception as ex:
        logger.exception("Failed to get users' properties...", exc_info=ex)
        raise ex


def get_user_emails(
    current_auth_client: AuthClient, list_orcids: typing.List[str]
) -> typing.List[str]:
    """Return a list of users' email addresses based the provided list of ORCIDs.

    Args:
        current_auth_client (AuthClient, required): AuthClient
        list_orcids (typing.List[str], required): list of ORCIDs in the form ["0000-0000-0000-0000@orcid.org"]

    Returns:
        typing.List[str]: A list of users' email addresses based the provided list of ORCIDs.

    Raises:
        ex: Fail to get users' properties

    """
    try:
        users = get_users(current_auth_client, list_orcids)
        return [user["email"] for user in users]

    except Exception as ex:
        logger.exception("Failed to get users' properties...", exc_info=ex)
        raise ex
