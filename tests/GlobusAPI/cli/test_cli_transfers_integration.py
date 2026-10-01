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

import json
import os
import time
import unittest

import yaml
from click.testing import CliRunner
from globus_sdk.scopes import AuthScopes, TransferScopes

import GlobusAPI
import GlobusAPI.cli.transfers as GlobusAPI_cli
import GlobusAPI.collections as collections
import GlobusAPI.groups as groups
import GlobusAPI.transfers as transfers
from GlobusAPI.__main__ import cli

logger = GlobusAPI.logging.logging.get_logger(stdout=True)
SUCCESSFUL_EXIT_CODE = 0


class TestCliTransfers(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.endpoint_id = os.environ["GLOBUSAPI_ENDPOINT_ID"]
        cls.source_collection_id = os.environ["GLOBUSAPI_SOURCE_COLLECTION_ID"]
        cls.source_collection_name = os.environ["GLOBUSAPI_SOURCE_COLLECTION_NAME"]
        cls.destination_collection_id = os.environ[
            "GLOBUSAPI_DESTINATION_COLLECTION_ID"
        ]
        cls.destination_collection_name = os.environ[
            "GLOBUSAPI_DESTINATION_COLLECTION_NAME"
        ]
        cls.transfer_item_list_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/data/transfer_list.json"
        )
        cls.filter_rule_list_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/data/filter_rule_list.json"
        )
        cls.delete_item_list_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/data/delete_list.json"
        )
        cls.wait_period_for_transfers = int(
            os.environ["GLOBUSAPI_WAIT_PERIOD_FOR_TRANSFERS"]
        )
        cls.transfer_client = transfers.transfer_client.transfer_client(
            cls.confidential_client_id,
            cls.confidential_client_secret,
            TransferScopes.all,
        )

        cls.transfer_response = transfers.transfer_methods._submit_transfer(
            current_transfer_client=cls.transfer_client,
            source_collection_id=cls.source_collection_id,
            destination_collection_id=cls.destination_collection_id,
            item_list_filename=cls.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=None,
        )

        cls.task_id = cls.transfer_response.get(key="task_id")

        time.sleep(cls.wait_period_for_transfers)

        cls.task_info = transfers.transfer_methods._get_task(
            current_transfer_client=cls.transfer_client, task_id=cls.task_id
        )

        while cls.task_info.get(key="status") != "SUCCEEDED":
            time.sleep(cls.wait_period_for_transfers)
            cls.task_info = transfers.transfer_methods._get_task(
                current_transfer_client=cls.transfer_client, task_id=cls.task_id
            )

        # Transfer commands
        cli.add_command(GlobusAPI_cli.successfultransfers)
        cli.add_command(GlobusAPI_cli.submittransfer)
        cli.add_command(GlobusAPI_cli.submitdelete)
        cli.add_command(GlobusAPI_cli.canceltasks)
        cli.add_command(GlobusAPI_cli.gettask)
        cli.add_command(GlobusAPI_cli.tasklist)
        cli.add_command(GlobusAPI_cli.taskeventlist)
        cli.add_command(GlobusAPI_cli.completetransfer)
        cli.add_command(GlobusAPI_cli.completedelete)
        cli.add_command(GlobusAPI_cli.getmonitoredcollection)
        cli.add_command(GlobusAPI_cli.monitoredcollectionlist)

        cls.runner = CliRunner()

    def test_cli_cancel_tasks(self):
        logger.info("Start cancel task test ...")
        submit_transfer_result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "submittransfer",
                "--source-collection-id",
                self.source_collection_id,
                "--destination-collection-id",
                self.destination_collection_id,
                "--item-list-filename",
                self.transfer_item_list_filename,
                "--label",
                "Unit_Test_Transfer",
                "--print-parameter",
                "task_id",
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
                "canceltasks",
                "--task-ids",
                str(submit_transfer_result.output)[-37:-1],
                "--message",
                "Cancel_Tasks",
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_get_task(self):
        logger.info("Start get task test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "gettask",
                "--task-id",
                self.task_id,
                "--print-parameter",
                "status",
                "-v",
            ],
        )

        self.assertEqual("SUCCEEDED", str(result.output)[-10:-1])
        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_get_task_with_output_json(self):
        logger.info("Start get task test with output json...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "gettask",
                "--task-id",
                self.task_id,
                "--print-parameter",
                "status",
                "--json",
                "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.json",
                "-v",
            ],
        )

        self.assertTrue(
            os.path.isfile(
                "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.json"
            )
        )
        with open("/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.json") as f:
            output = json.load(f)
        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_get_task_with_output_yaml(self):
        logger.info("Start get task test with output yaml...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "gettask",
                "--task-id",
                self.task_id,
                "--print-parameter",
                "status",
                "--yaml",
                "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.yaml",
                "-v",
            ],
        )

        self.assertTrue(
            os.path.isfile(
                "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.yaml"
            )
        )
        with open("/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.yaml") as f:
            output = yaml.safe_load(f)
        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_submit_transfer(self):
        logger.info("Start submit transfer test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "submittransfer",
                "--source-collection-id",
                self.source_collection_id,
                "--source-collection-name",
                self.source_collection_name,
                "--destination-collection-id",
                self.destination_collection_id,
                "--destination-collection-name",
                self.destination_collection_name,
                "--item-list-filename",
                self.transfer_item_list_filename,
                "--filter-rule-list-filename",
                self.filter_rule_list_filename,
                "--label",
                "Unit_Test_Transfer",
                "--verify-checksum",
                "True",
                "--preserve-timestamp",
                "True",
                "--encrypt-data",
                "False",
                "--skip-source-errors",
                "False",
                "--fail-on-quota-errors",
                "True",
                "--notify-on-succeeded",
                "False",
                "--notify-on-failed",
                "True",
                "--notify-on-inactive",
                "True",
                "--print-parameter",
                "task_id",
                "-v",
            ],
        )

        task_id = str(result.output)[-37:-1]

        time.sleep(self.wait_period_for_transfers)

        task_info_result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "gettask",
                "--task-id",
                task_id,
                "--print-parameter",
                "status",
                "-v",
            ],
        )

        status = str(task_info_result.output)[-10:-1]

        while status != "SUCCEEDED":
            time.sleep(self.wait_period_for_transfers)
            task_info_result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "gettask",
                    "--task-id",
                    task_id,
                    "--print-parameter",
                    "status",
                    "-v",
                ],
            )
            status = str(task_info_result.output)[-10:-1]

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_submit_delete(self):
        logger.info("Start submit delete test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "completetransfer",
                "--item-list-filename",
                self.transfer_item_list_filename,
                "--filter-rule-list-filename",
                self.filter_rule_list_filename,
                "--source-collection-id",
                self.source_collection_id,
                "--source-collection-name",
                self.source_collection_name,
                "--destination-collection-id",
                self.destination_collection_id,
                "--destination-collection-name",
                self.destination_collection_name,
                "--label",
                "Unit_Test_Transfer",
                "--verify-checksum",
                "True",
                "--preserve-timestamp",
                "True",
                "--encrypt-data",
                "False",
                "--skip-source-errors",
                "False",
                "--fail-on-quota-errors",
                "True",
                "--notify-on-succeeded",
                "False",
                "--notify-on-failed",
                "True",
                "--notify-on-inactive",
                "True",
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
                "submitdelete",
                "--collection-id",
                self.destination_collection_id,
                "--collection-name",
                self.destination_collection_name,
                "--item-list-filename",
                self.delete_item_list_filename,
                "--label",
                "Unit_Test_Delete",
                "--recursive",
                "True",
                "--ignore-missing",
                "False",
                "--interpret-globs",
                "False",
                "--notify-on-succeeded",
                "False",
                "--notify-on-failed",
                "True",
                "--notify-on-inactive",
                "True",
                "--print-parameter",
                "task_id",
                "-v",
            ],
        )

        task_id = str(result.output)[-37:-1]

        time.sleep(self.wait_period_for_transfers)

        task_info_result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "gettask",
                "--task-id",
                task_id,
                "--print-parameter",
                "status",
                "-v",
            ],
        )

        status = str(task_info_result.output)[-10:-1]

        while status != "SUCCEEDED":
            time.sleep(self.wait_period_for_transfers)
            task_info_result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "gettask",
                    "--task-id",
                    task_id,
                    "--print-parameter",
                    "status",
                    "-v",
                ],
            )
            status = str(task_info_result.output)[-10:-1]

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_complete_transfer(self):
        logger.info("Start complete transfer test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "completetransfer",
                "--item-list-filename",
                self.transfer_item_list_filename,
                "--filter-rule-list-filename",
                self.filter_rule_list_filename,
                "--source-collection-id",
                self.source_collection_id,
                "--source-collection-name",
                self.source_collection_name,
                "--destination-collection-id",
                self.destination_collection_id,
                "--destination-collection-name",
                self.destination_collection_name,
                "--label",
                "Unit_Test_Transfer",
                "--verify-checksum",
                "True",
                "--preserve-timestamp",
                "True",
                "--encrypt-data",
                "False",
                "--skip-source-errors",
                "False",
                "--fail-on-quota-errors",
                "True",
                "--notify-on-succeeded",
                "False",
                "--notify-on-failed",
                "True",
                "--notify-on-inactive",
                "True",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_complete_transfer_with_output_json_and_yaml(self):
        logger.info("Start complete transfer test with json and yaml output...")

        transfer_json_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/clicompletetransferinfo.json"
        )
        transfer_yaml_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/clicompletetransferinfo.yaml"
        )
        task_json_filename = "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/clicompletetransfertaskinfo.json"
        task_yaml_filename = "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/clicompletetransfertaskinfo.yaml"

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "completetransfer",
                "--item-list-filename",
                self.transfer_item_list_filename,
                "--source-collection-id",
                self.source_collection_id,
                "--destination-collection-id",
                self.destination_collection_id,
                "--label",
                "Unit_Test_Transfer",
                "--transfer-json",
                transfer_json_filename,
                "--transfer-yaml",
                transfer_yaml_filename,
                "--task-json",
                task_json_filename,
                "--task-yaml",
                task_yaml_filename,
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

        self.assertTrue(os.path.isfile(transfer_json_filename))
        self.assertTrue(os.path.isfile(transfer_yaml_filename))
        self.assertTrue(os.path.isfile(task_json_filename))
        self.assertTrue(os.path.isfile(task_yaml_filename))

        expected_transfer_keys = {
            "successful_transfers",
            "base_url",
            "event_list",
            "status",
        }
        with open(transfer_json_filename) as f:
            transfer_json_content = json.load(f)
        with open(transfer_yaml_filename) as f:
            transfer_yaml_content = yaml.safe_load(f)
        for content in (transfer_json_content, transfer_yaml_content):
            self.assertEqual(set(content.keys()), expected_transfer_keys)

        with open(task_json_filename) as f:
            task_json_content = json.load(f)
        with open(task_yaml_filename) as f:
            task_yaml_content = yaml.safe_load(f)
        for content in (task_json_content, task_yaml_content):
            self.assertIn("task_id", content)
            self.assertIn("status", content)

    def test_cli_complete_delete(self):
        logger.info("Start complete delete test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "completetransfer",
                "--item-list-filename",
                self.transfer_item_list_filename,
                "--filter-rule-list-filename",
                self.filter_rule_list_filename,
                "--source-collection-id",
                self.source_collection_id,
                "--source-collection-name",
                self.source_collection_name,
                "--destination-collection-id",
                self.destination_collection_id,
                "--destination-collection-name",
                self.destination_collection_name,
                "--label",
                "Unit_Test_Transfer",
                "--verify-checksum",
                "True",
                "--preserve-timestamp",
                "True",
                "--encrypt-data",
                "False",
                "--skip-source-errors",
                "False",
                "--fail-on-quota-errors",
                "True",
                "--notify-on-succeeded",
                "False",
                "--notify-on-failed",
                "True",
                "--notify-on-inactive",
                "True",
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
                "completedelete",
                "--collection-id",
                self.destination_collection_id,
                "--collection-name",
                self.destination_collection_name,
                "--item-list-filename",
                self.delete_item_list_filename,
                "--label",
                "Unit_Test_Delete",
                "--recursive",
                "True",
                "--ignore-missing",
                "False",
                "--interpret-globs",
                "False",
                "--notify-on-succeeded",
                "False",
                "--notify-on-failed",
                "True",
                "--notify-on-inactive",
                "True",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_complete_delete_with_output_json_and_yaml(self):
        logger.info("Start complete delete test with json and yaml output...")

        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "completetransfer",
                "--item-list-filename",
                self.transfer_item_list_filename,
                "--source-collection-id",
                self.source_collection_id,
                "--destination-collection-id",
                self.destination_collection_id,
                "--label",
                "Unit_Test_Transfer",
                "-v",
            ],
        )

        delete_json_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/clicompletedeleteinfo.json"
        )
        delete_yaml_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/clicompletedeleteinfo.yaml"
        )
        task_json_filename = "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/clicompletedeletetaskinfo.json"
        task_yaml_filename = "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/clicompletedeletetaskinfo.yaml"

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "completedelete",
                "--collection-id",
                self.destination_collection_id,
                "--item-list-filename",
                self.delete_item_list_filename,
                "--label",
                "Unit_Test_Delete",
                "--delete-json",
                delete_json_filename,
                "--delete-yaml",
                delete_yaml_filename,
                "--task-json",
                task_json_filename,
                "--task-yaml",
                task_yaml_filename,
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

        self.assertTrue(os.path.isfile(delete_json_filename))
        self.assertTrue(os.path.isfile(delete_yaml_filename))
        self.assertTrue(os.path.isfile(task_json_filename))
        self.assertTrue(os.path.isfile(task_yaml_filename))

        expected_delete_keys = {"successful_deletions", "event_list", "status"}
        with open(delete_json_filename) as f:
            delete_json_content = json.load(f)
        with open(delete_yaml_filename) as f:
            delete_yaml_content = yaml.safe_load(f)
        for content in (delete_json_content, delete_yaml_content):
            self.assertEqual(set(content.keys()), expected_delete_keys)

        with open(task_json_filename) as f:
            task_json_content = json.load(f)
        with open(task_yaml_filename) as f:
            task_yaml_content = yaml.safe_load(f)
        for content in (task_json_content, task_yaml_content):
            self.assertIn("task_id", content)
            self.assertIn("status", content)

    def test_cli_successful_transfer(self):
        logger.info("Start successful transfer test ...")

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "successfultransfers",
                "--task-id",
                self.task_id,
                "-v",
            ],
        )
        logger.info(result)
        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_task_list(self):
        logger.info("Start task list test ...")

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "tasklist",
                "--filter-status",
                "SUCCEEDED",
                "--filter-collection-id",
                self.source_collection_id,
                "-v",
            ],
        )

        logger.info(result)
        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_task_event_list(self):
        logger.info("Start task event list test ...")

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "taskeventlist",
                "--task-id",
                self.task_id,
                "--filter-is-error",
                "True",
                "-v",
            ],
        )

        logger.info(result)
        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_get_monitored_collection(self):
        logger.info("Start get monitored collection test ...")

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "getmonitoredcollection",
                "--collection-name",
                self.source_collection_name,
                "--collection-id",
                self.source_collection_id,
                "--print-parameter",
                "id",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_monitored_collection_list(self):
        logger.info("Start monitored collection list test ...")

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "monitoredcollectionlist",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))


class TestCliACLRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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
        logger.info(cls.user_uuid)

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=cls.transfer_client,
            current_auth_client=cls.auth_client,
            collection_name=cls.guest_collection_name,
            user_identity=cls.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )
        logger.info(
            transfers.acl_rules._get_acl_rule(
                current_transfer_client=cls.transfer_client,
                current_auth_client=cls.auth_client,
                collection_name=cls.guest_collection_name,
                user_identity=cls.user_identity,
                path="/",
                permissions="r",
            )
        )

        # ACL Rule commands
        cli.add_command(GlobusAPI_cli.aclrulelist)
        cli.add_command(GlobusAPI_cli.getaclrule)
        cli.add_command(GlobusAPI_cli.addaclrule)
        cli.add_command(GlobusAPI_cli.deleteaclrule)
        cli.add_command(GlobusAPI_cli.updateaclrule)

        cls.runner = CliRunner()

    def test_cli_add_acl_rule(self):
        logger.info("Start add acl rule test ...")
        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "deleteaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "--print-parameter",
                "request_id",
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
                "addaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "--print-parameter",
                "request_id",
                "-v",
            ],
        )

        self.assertIn('"code": "Created"', result.output)

        result2 = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "getaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "-v",
            ],
        )

        self.assertIn(
            f"'path': '/', 'permissions': 'r', 'principal': '{self.user_uuid}'",
            result2.output,
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_delete_acl_rule(self):
        logger.info("Start delete acl rule test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "deleteaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "--print-parameter",
                "request_id",
                "-v",
            ],
        )

        self.assertIn('"code": "Deleted"', result.output)

        result2 = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "getaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "-v",
            ],
        )

        self.assertNotIn(
            f"'path': '/', 'permissions': 'r', 'principal': '{self.user_uuid}'",
            result2.output,
        )

        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "addaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "--print-parameter",
                "request_id",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_update_acl_rule(self):
        logger.info("Start update acl rule test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "updateaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--new-permissions",
                "rw",
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "--print-parameter",
                "request_id",
                "-v",
            ],
        )

        self.assertIn('"code": "Updated"', result.output)

        result2 = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "getaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "-v",
            ],
        )

        self.assertIn(
            f"'path': '/', 'permissions': 'rw', 'principal': '{self.user_uuid}'",
            result2.output,
        )

        self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "updateaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--new-permissions",
                "r",
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "rw",
                "--print-parameter",
                "request_id",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_get_acl_rule(self):
        logger.info("Start get acl rule test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "getaclrule",
                "--collection-name",
                self.guest_collection_name,
                "--user-identity",
                self.user_identity,
                "--path",
                "/",
                "--permissions",
                "r",
                "-v",
            ],
        )

        self.assertIn(
            f"'path': '/', 'permissions': 'r', 'principal': '{self.user_uuid}'",
            result.output,
        )
        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    def test_cli_acl_rule_list(self):
        logger.info("Start acl rule list test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "aclrulelist",
                "--collection-name",
                self.guest_collection_name,
                "-v",
            ],
        )

        self.assertIn(
            f"'path': '/', 'permissions': 'r', 'principal': '{self.user_uuid}'",
            result.output,
        )
        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))

    @classmethod
    def tearDownClass(cls):
        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=cls.transfer_client,
            current_auth_client=cls.auth_client,
            collection_name=cls.guest_collection_name,
            user_identity=cls.user_identity,
            path="/",
            permissions="r",
        )
        collections.guest._delete_guest_collection(
            cls.gcs_client, cls.guest_collection_name
        )


class TestCliURL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.collection_id = os.environ["GLOBUSAPI_SOURCE_COLLECTION_ID"]
        cls.collection_name = os.environ["GLOBUSAPI_SOURCE_COLLECTION_NAME"]

        item_list_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/data/transfer_list.json"
        )
        try:
            if item_list_filename[-5:] == ".json" or item_list_filename[-5:] == ".JSON":
                cls.item_list = json.load(open(item_list_filename))
            else:
                cls.item_list = yaml.safe_load(open(item_list_filename))
        except Exception as ex:
            logger.exception(
                "Failed to load the list of items to be submitted for transfer...",
                exc_info=ex,
            )
            raise ex

        # URL commands
        cli.add_command(GlobusAPI_cli.geturl)

        cls.runner = CliRunner()

    def test_cli_get_url(self):
        logger.info("Start get url test ...")

        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "geturl",
                "--collection-name",
                self.collection_name,
                "--collection-id",
                self.collection_id,
                "--path",
                self.item_list[0]["source_path"],
                "--print-url",
                "-v",
            ],
        )

        self.assertEqual(SUCCESSFUL_EXIT_CODE, result.exit_code)
        self.assertIn("SystemExit(0)", str(result.exc_info))
