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

from globus_sdk import ClientCredentialsAuthorizer, ConfidentialAppAuthClient
from globus_sdk._types import ScopeCollectionType
from globus_sdk.authorizers import GlobusAuthorizer

from ..logging.logging import get_logger

logger = get_logger()


def get_client_credentials_authorizer(
    client_id: str, client_secret: str, scopes: ScopeCollectionType
) -> GlobusAuthorizer:
    """Authenticate using Client credentials only. To use this method your client needs to be set up as an
     Administrator on your guest collection.

    Args:
        client_id (str, required): the uid of your Client.
        client_secret (str, required): the client secret.
        scopes (ScopeCollectionType, required): the scope must include the collection ID of the collection your
                                                administrator is on.

    Returns:
        An authorizer object (GlobusAuthorizer)
    """
    logger.info("Getting refresh tokens authorizer")
    logger.debug(f"  {client_id=}")

    client = ConfidentialAppAuthClient(client_id, client_secret)
    authorizer = ClientCredentialsAuthorizer(client, scopes=scopes)

    return authorizer
