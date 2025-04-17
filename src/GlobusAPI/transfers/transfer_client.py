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

from globus_sdk import TransferClient
from globus_sdk.scopes import TransferScopes

import GlobusAPI

from ..logging.logging import get_logger

logger = get_logger(stdout=True)


def transfer_client(
    confidential_client_id: str,
    confidential_client_secret: str,
    scopes: TransferScopes = TransferScopes.all,
) -> TransferClient:
    """Return a transfer client object initialized with the given parameters.

    Args:
        confidential_client_id (str, required): The uuid of the confidential client that you are using.
        confidential_client_secret (str, required): The secret of the confidential client.
        scopes (TransferScopes, optional): The Globus Scopes for the transfer client. Defaults to TransferScopes.all .

    Returns:
        It returns a transfer client object initialized with the given parameters.
    """

    try:
        transfer_authorizer = (
            GlobusAPI.auth.authorizer.get_client_credentials_authorizer(
                confidential_client_id, confidential_client_secret, scopes
            )
        )

    except Exception as ex:
        logger.exception("Failed to create authorizer...", exc_info=ex)
        raise ex

    try:
        current_transfer_client = TransferClient(authorizer=transfer_authorizer)

        return current_transfer_client

    except Exception as ex:
        logger.exception("Failed to create transfer client...", exc_info=ex)
        raise ex
