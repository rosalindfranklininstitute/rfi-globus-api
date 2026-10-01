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
from globus_sdk.scopes import GroupsScopes

import GlobusAPI
import GlobusAPI.cli.groups as GlobusAPI_cli
import GlobusAPI.groups as groups
from GlobusAPI.__main__ import cli

logger = GlobusAPI.logging.logging.get_logger(stdout=True)
SUCCESSFUL_EXIT_CODE = 0


class TestCliGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.testing_user_identity = os.environ["GLOBUSAPI_TESTING_USER_IDENTITY"]
        cls.testing_user_identity2 = os.environ["GLOBUSAPI_TESTING_USER_IDENTITY2"]

        cls.groups_client = groups.groups.groups_client(
            cls.confidential_client_id, cls.confidential_client_secret, GroupsScopes.all
        )

        cls.group_name = "TestingGroup_Unittests"

        groups.groups._create_group(
            current_groups_client=cls.groups_client,
            group_name=cls.group_name,
            parent_id=None,
            description="Testing group creation",
        )
        retrieve_group = groups.groups.get_group_from_name(
            cls.groups_client, cls.group_name
        )
        cls.group_id = retrieve_group["id"]

        # Group commands
        cli.add_command(GlobusAPI_cli.creategroup)
        cli.add_command(GlobusAPI_cli.deletegroup)
        cli.add_command(GlobusAPI_cli.getgroup)
        cli.add_command(GlobusAPI_cli.grouplist)
        cli.add_command(GlobusAPI_cli.setgroupmembers)
        cli.add_command(GlobusAPI_cli.addgroupmembers)
        cli.add_command(GlobusAPI_cli.changerolegroupmembers)
        cli.add_command(GlobusAPI_cli.removegroupmembers)

        cls.runner = CliRunner()

    def test_cli_create_group(self):
        logger.info("Start create group test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "deletegroup",
                "--group-name",
                self.group_name,
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
                "creategroup",
                "--group-name",
                self.group_name,
                "--description",
                "Testing group creation",
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_get_group(self):
        logger.info("Start get group test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "creategroup",
                "--group-name",
                self.group_name,
                "--description",
                "Testing group creation",
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
                "getgroup",
                "--group-name",
                self.group_name,
                "--print-parameter",
                "id" "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_group_list(self):
        logger.info("Start group list test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "creategroup",
                "--group-name",
                self.group_name,
                "--description",
                "Testing group creation",
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
                "grouplist",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_add_group_members(self):
        logger.info("Start add group members test ...")

        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "creategroup",
                "--group-name",
                self.group_name,
                "--description",
                "Testing group creation",
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
                "addgroupmembers",
                "--group-name",
                self.group_name,
                "--add-members",
                self.testing_user_identity,
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_set_group_members(self):
        logger.info("Start set group members test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "creategroup",
                "--group-name",
                self.group_name,
                "--description",
                "Testing group creation",
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
                "setgroupmembers",
                "--group-name",
                self.group_name,
                "--set-members",
                self.testing_user_identity2,
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
                "setgroupmembers",
                "--group-name",
                self.group_name,
                "--set-members",
                self.testing_user_identity,
                "-v",
            ],
        )

        self.assertEqual(0, result1.exit_code)
        self.assertIn("SystemExit(0)", str(result1.exc_info))
        self.assertEqual(0, result2.exit_code)
        self.assertIn("SystemExit(0)", str(result2.exc_info))

    def test_cli_change_role_group_members(self):
        logger.info("Start change role group members test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "creategroup",
                "--group-name",
                self.group_name,
                "--description",
                "Testing group creation",
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
                "setgroupmembers",
                "--group-name",
                self.group_name,
                "--set-members",
                self.testing_user_identity,
                "--roles",
                "member",
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
                "changerolegroupmembers",
                "--group-name",
                self.group_name,
                "--members",
                self.testing_user_identity,
                "--roles",
                "manager",
                "-v",
            ],
        )

        self.assertEqual(0, result1.exit_code)
        self.assertIn("SystemExit(0)", str(result1.exc_info))
        self.assertEqual(0, result2.exit_code)
        self.assertIn("SystemExit(0)", str(result2.exc_info))

    def test_cli_remove_group_members(self):
        logger.info("Start remove group members test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "creategroup",
                "--group-name",
                self.group_name,
                "--description",
                "Testing group creation",
                "--print-parameter",
                "id",
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
                "addgroupmembers",
                "--group-name",
                self.group_name,
                "--add-members",
                self.testing_user_identity2,
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
                "removegroupmembers",
                "--group-name",
                self.group_name,
                "--remove-members",
                self.testing_user_identity2,
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_delete_group(self):
        logger.info("Start delete group test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "creategroup",
                "--group-name",
                self.group_name,
                "--description",
                "Testing group creation",
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
                "deletegroup",
                "--group-name",
                self.group_name,
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    @classmethod
    def tearDownClass(cls) -> None:
        groups.groups._delete_group(cls.groups_client, cls.group_name)
