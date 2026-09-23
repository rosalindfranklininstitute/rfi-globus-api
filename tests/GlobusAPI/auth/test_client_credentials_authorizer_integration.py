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

import os
import unittest

from globus_sdk import ClientCredentialsAuthorizer
from globus_sdk.scopes import AuthScopes, GroupsScopes, TransferScopes

from GlobusAPI.auth.authorizer import get_client_credentials_authorizer
from GlobusAPI.auth.scopes import get_collections_scope
from GlobusAPI.logging.logging import get_logger

logger = get_logger(stdout=True)


class TestClientCredentialsAuthorizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.endpoint_id = os.environ["GLOBUSAPI_ENDPOINT_ID"]
        cls.mapped_collection_id = os.environ["GLOBUSAPI_MAPPED_COLLECTION_ID"]

    def test_client_credentials_authorizer(self):
        logger.info("Start client credentials authorizer test ...")
        scopes = get_collections_scope(
            endpoint_id=self.endpoint_id,
            collection_ids=[
                self.mapped_collection_id,
            ],
        )

        authorizer = get_client_credentials_authorizer(
            client_id=self.confidential_client_id,
            client_secret=self.confidential_client_secret,
            scopes=scopes,
        )
        self.assertIsInstance(authorizer, ClientCredentialsAuthorizer)

    def test_client_credentials_authorizer_against_scopes(self):
        logger.info("Start client credentials authorizer test against scopes...")
        groups_authorizer = get_client_credentials_authorizer(
            client_id=self.confidential_client_id,
            client_secret=self.confidential_client_secret,
            scopes=GroupsScopes.all,
        )

        transfer_authorizer = get_client_credentials_authorizer(
            client_id=self.confidential_client_id,
            client_secret=self.confidential_client_secret,
            scopes=TransferScopes.all,
        )

        authscopes_authorizer = get_client_credentials_authorizer(
            client_id=self.confidential_client_id,
            client_secret=self.confidential_client_secret,
            scopes=AuthScopes.openid,
        )

        logger.info(
            f"transfer_authorizer.access_token: {transfer_authorizer.access_token}"
        )
        logger.info(f"groups_authorizer.access_token: {groups_authorizer.access_token}")
        logger.info(
            f"authscopes_authorizer.access_token: {authscopes_authorizer.access_token}"
        )

        # Multiscope
        scopes = [GroupsScopes.all, TransferScopes.all]

        self.assertRaises(
            ValueError,
            get_client_credentials_authorizer,
            self.confidential_client_id,
            self.confidential_client_secret,
            scopes,
        )
