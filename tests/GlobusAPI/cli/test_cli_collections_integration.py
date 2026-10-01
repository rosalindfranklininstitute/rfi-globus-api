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

from click.testing import CliRunner
from globus_sdk.scopes import AuthScopes, TransferScopes

import GlobusAPI
import GlobusAPI.cli.collections as GlobusAPI_cli
import GlobusAPI.collections as collections
import GlobusAPI.groups as groups
import GlobusAPI.transfers as transfers
from GlobusAPI.__main__ import cli

logger = GlobusAPI.logging.logging.get_logger(stdout=True)
SUCCESSFUL_EXIT_CODE = 0


class TestCliGuestCollections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.endpoint_id = os.environ["GLOBUSAPI_ENDPOINT_ID"]
        cls.mapped_collection_id = os.environ["GLOBUSAPI_MAPPED_COLLECTION_ID"]
        cls.guest_collection_name = os.environ["GLOBUSAPI_TESTING_COLLECTION_NAME"]
        cls.guest_collection2_name = os.environ["GLOBUSAPI_TESTING_COLLECTION2_NAME"]
        cls.base_path = os.environ["GLOBUSAPI_TESTING_COLLECTION_BASEPATH"]

        cls.transfer_client = transfers.transfer_client.transfer_client(
            confidential_client_id=cls.confidential_client_id,
            confidential_client_secret=cls.confidential_client_secret,
            scopes=TransferScopes.all,
        )
        cls.endpoint = cls.transfer_client.get_endpoint(cls.endpoint_id)
        cls.gcs_client = collections.utils.gcs_client(
            confidential_client_id=cls.confidential_client_id,
            confidential_client_secret=cls.confidential_client_secret,
            endpoint_id=cls.endpoint_id,
            collection_ids=[
                cls.mapped_collection_id,
            ],
        )

        collections.guest._create_guest_collection(
            current_gcs_client=cls.gcs_client,
            collection_name=cls.guest_collection_name,
            mapped_collection_id=cls.mapped_collection_id,
            base_path=cls.base_path,
        )

        # Guest Collections commands
        cli.add_command(GlobusAPI_cli.createguestcollection)
        cli.add_command(GlobusAPI_cli.deleteguestcollection)
        cli.add_command(GlobusAPI_cli.updateguestcollection)
        cli.add_command(GlobusAPI_cli.getguestcollection)
        cli.add_command(GlobusAPI_cli.guestcollectionlist)

        cls.runner = CliRunner()

    def test_cli_create_guest_collection(self):
        logger.info("Start create guest collection test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "deleteguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "-v",
            ],
        )

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--base-path",
                self.base_path,
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_delete_guest_collection(self):
        logger.info("Start delete guest collection test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--base-path",
                self.base_path,
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "deleteguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_update_guest_collection(self):
        logger.info("Start update guest collection test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--base-path",
                self.base_path,
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        result1 = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "updateguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--new-collection-name",
                self.guest_collection2_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "-v",
            ],
        )

        result2 = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "updateguestcollection",
                "--collection-name",
                self.guest_collection2_name,
                "--new-collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "-v",
            ],
        )

        self.assertEqual(0, result1.exit_code)
        self.assertIn("SystemExit(0)", str(result1.exc_info))
        self.assertEqual(0, result2.exit_code)
        self.assertIn("SystemExit(0)", str(result2.exc_info))

    def test_cli_get_guest_collection(self):
        logger.info("Start get guest collection test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--base-path",
                self.base_path,
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "getguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--filter",
                "guest_collections",
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_guest_collection_list(self):
        logger.info("Start guest collection list test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createguestcollection",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--base-path",
                self.base_path,
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "guestcollectionlist",
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--filter",
                "guest_collections",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    @classmethod
    def tearDownClass(cls) -> None:
        collections.guest._delete_guest_collection(
            cls.gcs_client, cls.guest_collection_name
        )
        collections.guest._delete_guest_collection(
            cls.gcs_client, cls.guest_collection2_name
        )


class TestCliRoles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.endpoint_id = os.environ["GLOBUSAPI_ENDPOINT_ID"]
        cls.mapped_collection_id = os.environ["GLOBUSAPI_MAPPED_COLLECTION_ID"]
        cls.guest_collection_name = os.environ["GLOBUSAPI_TESTING_COLLECTION_NAME"]
        cls.base_path = os.environ["GLOBUSAPI_TESTING_COLLECTION_BASEPATH"]
        cls.testing_user_identity = os.environ["GLOBUSAPI_TESTING_USER_IDENTITY"]

        cls.transfer_client = transfers.transfer_client.transfer_client(
            confidential_client_id=cls.confidential_client_id,
            confidential_client_secret=cls.confidential_client_secret,
            scopes=TransferScopes.all,
        )
        cls.endpoint = cls.transfer_client.get_endpoint(cls.endpoint_id)
        cls.gcs_client = collections.utils.gcs_client(
            confidential_client_id=cls.confidential_client_id,
            confidential_client_secret=cls.confidential_client_secret,
            endpoint_id=cls.endpoint_id,
            collection_ids=[
                cls.mapped_collection_id,
            ],
        )

        cls.auth_client = groups.users.auth_client(
            confidential_client_id=cls.confidential_client_id,
            confidential_client_secret=cls.confidential_client_secret,
            scopes=[
                AuthScopes.openid,
                AuthScopes.profile,
                AuthScopes.email,
                AuthScopes.view_identity_set,
            ],
        )

        collections.guest._create_guest_collection(
            current_gcs_client=cls.gcs_client,
            collection_name=cls.guest_collection_name,
            mapped_collection_id=cls.mapped_collection_id,
            base_path=cls.base_path,
        )

        cls.guest_collection = collections.utils.get_collection(
            current_gcs_client=cls.gcs_client,
            collection_name=cls.guest_collection_name,
            collection_id=None,
            filter_to_help="guest_collections",
        )[0]
        logger.info(cls.guest_collection)

        cls.user_identity = cls.testing_user_identity
        cls.user_uuid = groups.users.get_user_uuid(
            current_auth_client=cls.auth_client,
            list_orcids=[
                cls.user_identity,
            ],
        )[0]

        collections.roles._create_role(
            current_gcs_client=cls.gcs_client,
            current_auth_client=cls.auth_client,
            collection_name=cls.guest_collection_name,
            user_identity=cls.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )
        logger.info(
            collections.roles._get_role(
                current_gcs_client=cls.gcs_client,
                current_auth_client=cls.auth_client,
                collection_name=cls.guest_collection_name,
                user_identity=cls.user_identity,
                role="activity_monitor",
            )
        )

        # Guest Collections commands
        cli.add_command(GlobusAPI_cli.createrole)
        cli.add_command(GlobusAPI_cli.deleterole)
        cli.add_command(GlobusAPI_cli.getrole)
        cli.add_command(GlobusAPI_cli.rolelist)

        cls.runner = CliRunner()

    def test_cli_create_role(self):
        logger.info("Start create role test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "deleterole",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--user-identity",
                self.user_identity,
                "--role",
                "activity_monitor",
                "-v",
            ],
        )

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createrole",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--user-identity",
                self.user_identity,
                "--role",
                "activity_monitor",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_delete_role(self):
        logger.info("Start delete role test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "deleterole",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--user-identity",
                self.user_identity,
                "--role",
                "activity_monitor",
                "-v",
            ],
        )

        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createrole",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--user-identity",
                self.user_identity,
                "--role",
                "activity_monitor",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_get_role(self):
        logger.info("Start get role test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "getrole",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "--user-identity",
                self.user_identity,
                "--role",
                "activity_monitor",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_guest_collection_list(self):
        logger.info("Start guest collection list test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "rolelist",
                "--collection-name",
                self.guest_collection_name,
                "--endpoint-id",
                self.endpoint_id,
                "--mapped-collection-id",
                self.mapped_collection_id,
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    @classmethod
    def tearDownClass(cls) -> None:
        collections.roles._delete_role(
            current_gcs_client=cls.gcs_client,
            current_auth_client=cls.auth_client,
            collection_name=cls.guest_collection_name,
            user_identity=cls.user_identity,
            role="activity_monitor",
        )
        collections.guest._delete_guest_collection(
            cls.gcs_client, cls.guest_collection_name
        )
