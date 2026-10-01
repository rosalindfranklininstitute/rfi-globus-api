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

import validators
import yaml
from globus_sdk._missing import MISSING, MissingType
from globus_sdk.scopes import AuthScopes, TransferScopes

import GlobusAPI
import GlobusAPI.collections as collections
import GlobusAPI.groups as groups
import GlobusAPI.output as output
import GlobusAPI.transfers as transfers

logger = GlobusAPI.logging.logging.get_logger(stdout=True)


class TestTransfers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
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
        cls.filter_rule_list_filename_incorrect_method = "/usr/local/GlobusAPI/tests/GlobusAPI/data/filter_rule_list_incorrect_method.json"
        cls.filter_rule_list_filename_incorrect_type = "/usr/local/GlobusAPI/tests/GlobusAPI/data/filter_rule_list_incorrect_type.json"
        cls.delete_item_list_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/data/delete_list.json"
        )
        cls.non_existing_collection_name = os.environ[
            "GLOBUSAPI_NON_EXISTING_COLLECTION_NAME"
        ]
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
            sync_level=MISSING,
        )

        cls.task_id = cls.transfer_response.get(key="task_id")

        time.sleep(cls.wait_period_for_transfers)

        cls.task_info = transfers.transfer_methods._get_task(
            current_transfer_client=cls.transfer_client, task_id=cls.task_id
        )

        while (
            cls.task_info.get(key="status") != "SUCCEEDED"
            and cls.task_info.get(key="status") != "FAILED"
        ):
            time.sleep(cls.wait_period_for_transfers)
            cls.task_info = transfers.transfer_methods._get_task(
                current_transfer_client=cls.transfer_client, task_id=cls.task_id
            )

    def test_successful_transfer(self):
        logger.info("Start test successful transfers smoke test...")

        transfers.transfer_methods._task_successful_transfers(
            current_transfer_client=self.transfer_client,
            task_id=self.task_id,
        )

    def test_successful_transfer_incorrect_task_id(self):
        logger.info("Start test successful transfers incorrect task_id...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._task_successful_transfers(
                current_transfer_client=self.transfer_client,
                task_id=None,
            )

    def test_successful_transfer_incorrect_transfer_client(self):
        logger.info("Start test successful transfers incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._task_successful_transfers(
                current_transfer_client=None,
                task_id=self.task_id,
            )

    def test_get_task_id(self):
        logger.info("Start test get task_id smoke test...")

        transfers.transfer_methods._get_task(
            current_transfer_client=self.transfer_client,
            task_id=self.task_id,
        )

    def test_get_task_id_incorrect_transfer_client(self):
        logger.info("Start test get task_id incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._get_task(
                current_transfer_client=None,
                task_id=self.task_id,
            )

    def test_get_task_id_incorrect_task_id(self):
        logger.info("Start test get task_id incorrect task_id...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._get_task(
                current_transfer_client=self.transfer_client,
                task_id=None,
            )

    def test_submit_transfer_incorrect_client(self):
        logger.info("Start test submit transfer incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=None,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_source_collection_id(self):
        logger.info("Start test submit transfer incorrect source collection id...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=None,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_source_collection_name(self):
        logger.info("Start test submit transfer incorrect source collection name...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_name=None,
                destination_collection_name=self.destination_collection_name,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_destination_collection_id(self):
        logger.info("Start test submit transfer incorrect destination collection id...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=None,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_destination_collection_name(self):
        logger.info(
            "Start test submit transfer incorrect destination collection name..."
        )

        with self.assertRaises(ValueError):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_name=self.source_collection_name,
                destination_collection_name=None,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_item_list_filename(self):
        logger.info("Start test submit transfer incorrect item list filename...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename="None",
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_filter_rule_list_filename(self):
        logger.info("Start test submit transfer incorrect filter rule list filename...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                filter_rule_list_filename="None",
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_method_in_filter_rule(self):
        logger.info("Start test submit transfer incorrect method in filter rule...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                filter_rule_list_filename=self.filter_rule_list_filename_incorrect_method,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_type_in_filter_rule(self):
        logger.info("Start test submit transfer incorrect method in filter rule...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                filter_rule_list_filename=self.filter_rule_list_filename_incorrect_type,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_submit_transfer_incorrect_sync_level(self):
        logger.info("Start test submit transfer incorrect sync level...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._submit_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=4,
            )

    def test_submit_transfer(self):
        logger.info("Start test submit transfer...")

        transfer_response = transfers.transfer_methods._submit_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            item_list_filename=self.transfer_item_list_filename,
            filter_rule_list_filename=self.filter_rule_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
        )
        self.task_id = transfer_response.get(key="task_id")
        self.task_info = transfers.transfer_methods._get_task(
            current_transfer_client=self.transfer_client, task_id=self.task_id
        )
        while (
            self.task_info.get(key="status") != "SUCCEEDED"
            and self.task_info.get(key="status") != "FAILED"
        ):
            time.sleep(self.wait_period_for_transfers)
            self.task_info = transfers.transfer_methods._get_task(
                current_transfer_client=self.transfer_client, task_id=self.task_id
            )
        self.assertTrue(self.task_info.get(key="status") == "SUCCEEDED")

    def test_submit_transfer_using_solely_monitored_collection_names(self):
        logger.info(
            "Start test submit transfer using solely monitored collection names..."
        )

        transfer_response = transfers.transfer_methods._submit_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_name=self.source_collection_name,
            destination_collection_name=self.destination_collection_name,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
        )
        self.task_id = transfer_response.get(key="task_id")
        self.task_info = transfers.transfer_methods._get_task(
            current_transfer_client=self.transfer_client, task_id=self.task_id
        )
        while (
            self.task_info.get(key="status") != "SUCCEEDED"
            and self.task_info.get(key="status") != "FAILED"
        ):
            time.sleep(self.wait_period_for_transfers)
            self.task_info = transfers.transfer_methods._get_task(
                current_transfer_client=self.transfer_client, task_id=self.task_id
            )
        self.assertTrue(self.task_info.get(key="status") == "SUCCEEDED")

    def test_submit_delete_incorrect_client(self):
        logger.info("Start test submit delete incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._submit_delete(
                current_transfer_client=None,
                collection_id=self.destination_collection_id,
                item_list_filename=self.delete_item_list_filename,
                label="Unit_Test_Delete",
            )

    def test_submit_delete_incorrect_collection_id(self):
        logger.info("Start test submit delete incorrect collection id...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._submit_delete(
                current_transfer_client=self.transfer_client,
                collection_id=None,
                item_list_filename=self.delete_item_list_filename,
                label="Unit_Test_Delete",
            )

    def test_submit_delete_incorrect_collection_name(self):
        logger.info("Start test submit delete incorrect collection name...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._submit_delete(
                current_transfer_client=self.transfer_client,
                collection_name=None,
                item_list_filename=self.delete_item_list_filename,
                label="Unit_Test_Delete",
            )

    def test_submit_delete_incorrect_item_list_filename(self):
        logger.info("Start test submit delete incorrect item list filename...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._submit_delete(
                current_transfer_client=self.transfer_client,
                collection_id=self.destination_collection_id,
                item_list_filename="None",
                label="Unit_Test_Delete",
            )

    def test_submit_delete(self):
        logger.info("Start test submit delete...")

        transfers.transfer_methods._complete_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
        )
        deletion_response = transfers.transfer_methods._submit_delete(
            current_transfer_client=self.transfer_client,
            collection_id=self.destination_collection_id,
            item_list_filename=self.delete_item_list_filename,
            label="Unit_Test_Delete",
        )
        self.task_id = deletion_response.get(key="task_id")
        self.task_info = transfers.transfer_methods._get_task(
            current_transfer_client=self.transfer_client, task_id=self.task_id
        )
        while (
            self.task_info.get(key="status") != "SUCCEEDED"
            and self.task_info.get(key="status") != "FAILED"
        ):
            time.sleep(self.wait_period_for_transfers)
            self.task_info = transfers.transfer_methods._get_task(
                current_transfer_client=self.transfer_client, task_id=self.task_id
            )
        self.assertTrue(self.task_info.get(key="status") == "SUCCEEDED")

    def test_submit_delete_using_solely_monitored_collection_names(self):
        logger.info(
            "Start test submit delete using solely monitored collection names..."
        )

        transfers.transfer_methods._complete_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_name=self.source_collection_name,
            destination_collection_name=self.destination_collection_name,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
        )
        deletion_response = transfers.transfer_methods._submit_delete(
            current_transfer_client=self.transfer_client,
            collection_name=self.destination_collection_name,
            item_list_filename=self.delete_item_list_filename,
            label="Unit_Test_Delete",
        )
        self.task_id = deletion_response.get(key="task_id")
        self.task_info = transfers.transfer_methods._get_task(
            current_transfer_client=self.transfer_client, task_id=self.task_id
        )
        while (
            self.task_info.get(key="status") != "SUCCEEDED"
            and self.task_info.get(key="status") != "FAILED"
        ):
            time.sleep(self.wait_period_for_transfers)
            self.task_info = transfers.transfer_methods._get_task(
                current_transfer_client=self.transfer_client, task_id=self.task_id
            )
        self.assertTrue(self.task_info.get(key="status") == "SUCCEEDED")

    def test_complete_transfer_incorrect_client(self):
        logger.info("Start test complete transfer incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=None,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_source_collection_id(self):
        logger.info("Start test complete transfer incorrect source collection id...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=None,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_source_collection_name(self):
        logger.info("Start test complete transfer incorrect source collection name...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_name=None,
                destination_collection_name=self.destination_collection_name,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_destination_collection_id(self):
        logger.info(
            "Start test complete transfer incorrect destination collection id..."
        )

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=None,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_destination_collection_name(self):
        logger.info(
            "Start test complete transfer incorrect destination collection name..."
        )

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_name=self.source_collection_name,
                destination_collection_name=None,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_item_list_filename(self):
        logger.info("Start test complete transfer incorrect item list filename...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename="None",
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_filter_rule_list_filename(self):
        logger.info(
            "Start test complete transfer incorrect filter rule list filename..."
        )

        with self.assertRaises(Exception):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                filter_rule_list_filename="None",
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_method_in_filter_rule(self):
        logger.info("Start test complete transfer incorrect method in filter rule...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                filter_rule_list_filename=self.filter_rule_list_filename_incorrect_method,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_type_in_filter_rule(self):
        logger.info("Start test complete transfer incorrect method in filter rule...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                filter_rule_list_filename=self.filter_rule_list_filename_incorrect_type,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
            )

    def test_complete_transfer_incorrect_sync_level(self):
        logger.info("Start test complete transfer incorrect sync level...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=4,
            )

    def test_complete_transfer_incorrect_status_change_check_interval(self):
        logger.info(
            "Start test complete transfer incorrect status change check interval..."
        )

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
                status_change_check_interval="-1",
                auto_cancel_if_inactive_wait_period="00:00:00",
            )

    def test_complete_transfer_incorrect_auto_cancel_if_inactive_wait_period(self):
        logger.info(
            "Start test complete transfer incorrect auto cancel if inactive wait period..."
        )

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_transfer(
                current_transfer_client=self.transfer_client,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                item_list_filename=self.transfer_item_list_filename,
                label="Unit_Test_Transfer",
                sync_level=MISSING,
                status_change_check_interval="00:01:00",
                auto_cancel_if_inactive_wait_period="-1",
            )

    def test_complete_transfer(self):
        logger.info("Start test complete transfer...")

        transfers.transfer_methods._complete_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            item_list_filename=self.transfer_item_list_filename,
            filter_rule_list_filename=self.filter_rule_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
        )

    def test_complete_transfer_using_solely_monitored_collection_names(self):
        logger.info(
            "Start test complete transfer using solely monitored collection names..."
        )

        print(f"Source collection name: {self.source_collection_name}")
        print(f"Destination collection name: {self.destination_collection_name}")

        transfers.transfer_methods._complete_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_name=self.source_collection_name,
            destination_collection_name=self.destination_collection_name,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
        )

    def test_complete_transfer_with_output_json_and_yaml(self):
        logger.info("Start test complete transfer with json and yaml output...")

        transfer_json_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/completetransferinfo.json"
        )
        transfer_yaml_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/completetransferinfo.yaml"
        )
        task_json_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/completetransfertaskinfo.json"
        )
        task_yaml_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/completetransfertaskinfo.yaml"
        )

        (
            transfer_list,
            event_list,
            status,
            url,
        ) = transfers.transfer_methods.complete_transfer(
            confidential_client_id=self.confidential_client_id,
            confidential_client_secret=self.confidential_client_secret,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
            transfer_json=transfer_json_filename,
            transfer_yaml=transfer_yaml_filename,
            task_json=task_json_filename,
            task_yaml=task_yaml_filename,
        )

        self.assertTrue(os.path.isfile(transfer_json_filename))
        self.assertTrue(os.path.isfile(transfer_yaml_filename))
        self.assertTrue(os.path.isfile(task_json_filename))
        self.assertTrue(os.path.isfile(task_yaml_filename))

        with open(transfer_json_filename) as f:
            transfer_json_content = json.load(f)
        with open(transfer_yaml_filename) as f:
            transfer_yaml_content = yaml.safe_load(f)

        expected_transfer_keys = {
            "successful_transfers",
            "base_url",
            "event_list",
            "status",
        }
        for content in (transfer_json_content, transfer_yaml_content):
            self.assertEqual(set(content.keys()), expected_transfer_keys)
            self.assertEqual(content["status"], status)
            self.assertEqual(content["base_url"], url)
            self.assertEqual(len(content["successful_transfers"]), len(transfer_list))
            self.assertEqual(len(content["event_list"]), len(event_list))

        with open(task_json_filename) as f:
            task_json_content = json.load(f)
        with open(task_yaml_filename) as f:
            task_yaml_content = yaml.safe_load(f)

        for content in (task_json_content, task_yaml_content):
            self.assertIn("task_id", content)
            self.assertIn("status", content)
            self.assertTrue(len(content["task_id"]) > 0)
            self.assertEqual(content["status"], status)

    def test_complete_delete_incorrect_client(self):
        logger.info("Start test complete delete incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._complete_delete(
                current_transfer_client=None,
                collection_id=self.destination_collection_id,
                item_list_filename=self.delete_item_list_filename,
                label="Unit_Test_Deleter",
            )

    def test_complete_delete_incorrect_destination_collection_id(self):
        logger.info("Start test complete delete incorrect destination collection id...")

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_delete(
                current_transfer_client=self.transfer_client,
                collection_id=None,
                item_list_filename=self.delete_item_list_filename,
                label="Unit_Test_Delete",
            )

    def test_complete_delete_incorrect_destination_collection_name(self):
        logger.info(
            "Start test complete delete incorrect destination collection name..."
        )

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_delete(
                current_transfer_client=self.transfer_client,
                collection_name=None,
                item_list_filename=self.delete_item_list_filename,
                label="Unit_Test_Delete",
            )

    def test_complete_delete_incorrect_item_list_filename(self):
        logger.info("Start test complete delete incorrect item list filename...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._complete_delete(
                current_transfer_client=self.transfer_client,
                collection_id=self.destination_collection_id,
                item_list_filename="None",
                label="Unit_Test_Delete",
            )

    def test_complete_delete_incorrect_status_change_check_interval(self):
        logger.info(
            "Start test complete delete incorrect status change check interval..."
        )

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_delete(
                current_transfer_client=self.transfer_client,
                collection_id=self.destination_collection_id,
                item_list_filename=self.delete_item_list_filename,
                label="Unit_Test_Delete",
                status_change_check_interval="-1",
                auto_cancel_if_inactive_wait_period="00:00:00",
            )

    def test_complete_delete_incorrect_auto_cancel_if_inactive_wait_period(self):
        logger.info(
            "Start test complete delete incorrect auto cancel if inactive wait period..."
        )

        with self.assertRaises(ValueError):
            transfers.transfer_methods._complete_delete(
                current_transfer_client=self.transfer_client,
                collection_id=self.destination_collection_id,
                item_list_filename=self.delete_item_list_filename,
                label="Unit_Test_Delete",
                status_change_check_interval="00:01:00",
                auto_cancel_if_inactive_wait_period="-1",
            )

    def test_complete_delete(self):
        logger.info("Start test complete delete...")

        transfers.transfer_methods._complete_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
        )
        transfers.transfer_methods._complete_delete(
            current_transfer_client=self.transfer_client,
            collection_id=self.destination_collection_id,
            item_list_filename=self.delete_item_list_filename,
            label="Unit_Test_Delete",
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
        )

    def test_complete_delete_with_output_json_and_yaml(self):
        logger.info("Start test complete delete with json and yaml output...")

        transfers.transfer_methods._complete_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
        )

        delete_json_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/completedeleteinfo.json"
        )
        delete_yaml_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/completedeleteinfo.yaml"
        )
        task_json_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/completedeletetaskinfo.json"
        )
        task_yaml_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/completedeletetaskinfo.yaml"
        )

        deletion_list, event_list, status = transfers.transfer_methods.complete_delete(
            confidential_client_id=self.confidential_client_id,
            confidential_client_secret=self.confidential_client_secret,
            collection_id=self.destination_collection_id,
            item_list_filename=self.delete_item_list_filename,
            label="Unit_Test_Delete",
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
            delete_json=delete_json_filename,
            delete_yaml=delete_yaml_filename,
            task_json=task_json_filename,
            task_yaml=task_yaml_filename,
        )

        self.assertTrue(os.path.isfile(delete_json_filename))
        self.assertTrue(os.path.isfile(delete_yaml_filename))
        self.assertTrue(os.path.isfile(task_json_filename))
        self.assertTrue(os.path.isfile(task_yaml_filename))

        with open(delete_json_filename) as f:
            delete_json_content = json.load(f)
        with open(delete_yaml_filename) as f:
            delete_yaml_content = yaml.safe_load(f)

        expected_delete_keys = {"successful_deletions", "event_list", "status"}
        for content in (delete_json_content, delete_yaml_content):
            self.assertEqual(set(content.keys()), expected_delete_keys)
            self.assertEqual(content["status"], status)
            self.assertEqual(len(content["successful_deletions"]), len(deletion_list))
            self.assertEqual(len(content["event_list"]), len(event_list))

        with open(task_json_filename) as f:
            task_json_content = json.load(f)
        with open(task_yaml_filename) as f:
            task_yaml_content = yaml.safe_load(f)

        for content in (task_json_content, task_yaml_content):
            self.assertIn("task_id", content)
            self.assertIn("status", content)
            self.assertTrue(len(content["task_id"]) > 0)
            self.assertEqual(content["status"], status)

    def test_complete_delete_using_solely_monitored_collection_names(self):
        logger.info(
            "Start test complete delete using solely monitored collection names..."
        )

        print(f"Collection name: {self.destination_collection_name}")

        transfers.transfer_methods._complete_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_name=self.source_collection_name,
            destination_collection_name=self.destination_collection_name,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
        )
        transfers.transfer_methods._complete_delete(
            current_transfer_client=self.transfer_client,
            collection_name=self.destination_collection_name,
            item_list_filename=self.delete_item_list_filename,
            label="Unit_Test_Delete",
            status_change_check_interval="00:01:00",
            auto_cancel_if_inactive_wait_period="00:00:00",
        )

    def test_get_task_with_output_json(self):
        logger.info("Start test get task with json output...")
        transfer_response = transfers.transfer_methods._get_task(
            current_transfer_client=self.transfer_client, task_id=self.task_id
        )
        output.file_output.output(
            transfer_response,
            json_filename="/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.json",
        )
        self.assertTrue(
            os.path.isfile(
                "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.json"
            )
        )
        with open("/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.json") as f:
            fl = json.load(f)

        self.assertEqual(transfer_response.data, fl)

    def test_get_task_with_output_yaml(self):
        logger.info("Start test get task with yaml output...")
        transfer_response = transfers.transfer_methods._get_task(
            current_transfer_client=self.transfer_client, task_id=self.task_id
        )
        output.file_output.output(
            transfer_response,
            yaml_filename="/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.yaml",
        )
        self.assertTrue(
            os.path.isfile(
                "/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.yaml"
            )
        )
        with open("/usr/local/GlobusAPI/tests/GlobusAPI/outputs/gettaskinfo.yaml") as f:
            fl = yaml.safe_load(f)

        self.assertEqual(transfer_response.data, fl)

    def test_cancel_tasks(self):
        logger.info("Start test cancel tasks...")

        transfer_response = transfers.transfer_methods._submit_transfer(
            current_transfer_client=self.transfer_client,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            item_list_filename=self.transfer_item_list_filename,
            label="Unit_Test_Transfer",
            sync_level=MISSING,
        )
        self.task_id = transfer_response.get(key="task_id")
        transfers.transfer_methods._cancel_tasks(
            current_transfer_client=self.transfer_client,
            task_ids=self.task_id,
            message="Cancel_Tasks",
        )

    def test_cancel_tasks_incorrect_transfer_client(self):
        logger.info("Start test cancel tasks incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._cancel_tasks(
                current_transfer_client=None,
                task_ids=self.task_id,
                message="Cancel_Tasks",
            )

    def test_cancel_tasks_incorrect_task_id(self):
        logger.info("Start test cancel tasks incorrect task_id...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._cancel_tasks(
                current_transfer_client=self.transfer_client,
                task_ids="None",
                message="Cancel_Tasks",
            )

    def test_task_list(self):
        logger.info("Start test get task_list smoke test...")

        transfers.transfer_methods._task_list(
            current_transfer_client=self.transfer_client,
            filter_status="SUCCEEDED",
            filter_collection_id=self.source_collection_id,
        )

    def test_task_list_incorrect_transfer_client(self):
        logger.info("Start test task_list incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._task_list(
                current_transfer_client=None,
                filter_status="SUCCEEDED",
                filter_collection_id=self.source_collection_id,
            )

    def test_task_list_collection_id_not_provided(self):
        logger.info(
            'Start test task_list when filter status is "SUCCEEDED" and no filter collection id is given...'
        )

        with self.assertRaises(Exception):
            transfers.transfer_methods._task_list(
                current_transfer_client=self.transfer_client,
                filter_status="SUCCEEDED",
            )

    def test_task_event_list(self):
        logger.info("Start test get task_event_list smoke test...")

        transfers.transfer_methods._task_event_list(
            current_transfer_client=self.transfer_client,
            task_id=self.task_id,
            filter_is_error=True,
        )

    def test_task_event_list_incorrect_transfer_client(self):
        logger.info("Start test get task_event_list incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._task_event_list(
                current_transfer_client=None,
                task_id=self.task_id,
            )

    def test_task_event_list_incorrect_task_id(self):
        logger.info("Start test get task_event_list incorrect task_id...")

        with self.assertRaises(Exception):
            transfers.transfer_methods._task_event_list(
                current_transfer_client=self.transfer_client,
                task_id=None,
            )

    def test_get_monitored_collection(self):
        logger.info("Start test get monitored collection...")
        collection = transfers.transfer_methods._get_monitored_collection(
            current_transfer_client=self.transfer_client,
            collection_name=self.source_collection_name,
            collection_id=None,
        )
        self.assertEqual(collection[0]["display_name"], self.source_collection_name)

        # check that we return none when a collection is not found
        collection_name = self.non_existing_collection_name
        false_collection = transfers.transfer_methods._get_monitored_collection(
            current_transfer_client=self.transfer_client,
            collection_name=collection_name,
            collection_id=None,
        )
        self.assertEqual(len(false_collection), 0)

    def test_monitored_collection_list(self):
        logger.info("Start test monitored collection list...")
        collection_list = transfers.transfer_methods._monitored_collection_list(
            current_transfer_client=self.transfer_client
        )
        collection_name = [
            collection
            for collection in collection_list
            if collection["display_name"] == self.source_collection_name
        ]
        self.assertEqual(
            collection_name[0]["display_name"], self.source_collection_name
        )

    @classmethod
    def tearDownClass(cls) -> None:
        for fn in os.listdir("/usr/local/GlobusAPI/tests/GlobusAPI/outputs"):
            os.remove(f"/usr/local/GlobusAPI/tests/GlobusAPI/outputs/{fn}")
        os.rmdir("/usr/local/GlobusAPI/tests/GlobusAPI/outputs")


class TestACLRules(unittest.TestCase):
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

    def test_add_acl_rule_with_collection_name_and_user_identity(self):
        logger.info(
            "Start test add acl rule using collection_name and user_identity..."
        )

        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        result = transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Created")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            rule_id=result["access_id"],
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "r")

    def test_add_acl_rule_with_collection_id_and_principal(self):
        logger.info("Start test add acl rule using collection_id and principal...")

        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        result = transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            principal_type="identity",
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Created")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            rule_id=result["access_id"],
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "r")

    def test_add_acl_rule_with_collection_name_and_principal(self):
        logger.info("Start test add acl rule using collection_name and principal...")

        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        result = transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            principal_type="identity",
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Created")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            rule_id=result["access_id"],
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "r")

    def test_add_acl_rule_with_collection_id_and_user_identity(self):
        logger.info("Start test add acl rule using collection_id and user_identity...")

        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        result = transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Created")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            rule_id=result["access_id"],
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "r")

    def test_add_acl_rule_incorrect_transfer_client(self):
        logger.info("Start test add acl rule with incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._add_acl_rule(
                current_transfer_client=None,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                principal_type="identity",
                path="/",
                permissions="r",
            )

    def test_add_acl_rule_incorrect_auth_client(self):
        logger.info("Start test add acl rule with incorrect auth client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._add_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=None,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                principal_type="identity",
                path="/",
                permissions="r",
            )

    def test_add_acl_rule_incorrect_collection_name_and_id(self):
        logger.info("Start test add acl rule with incorrect collection name and id...")

        with self.assertRaises(ValueError):
            transfers.acl_rules._add_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=None,
                collection_id=None,
                user_identity=self.user_identity,
                principal_type="identity",
                path="/",
                permissions="r",
            )

    def test_add_acl_rule_incorrect_user_identity_and_principal(self):
        logger.info(
            "Start test add acl rule with incorrect user_identity and principal..."
        )

        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        with self.assertRaises(Exception):
            transfers.acl_rules._add_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=None,
                principal=None,
                principal_type="identity",
                path="/",
                permissions="r",
            )

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_add_acl_rule_incorrect_principal_type(self):
        logger.info("Start test add acl rule with incorrect principal type...")

        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        with self.assertRaises(Exception):
            transfers.acl_rules._add_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                principal=self.user_uuid,
                principal_type="None",
                path="/",
                permissions="r",
            )

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_add_acl_rule_incorrect_path(self):
        logger.info("Start test add acl rule with incorrect path...")

        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        with self.assertRaises(Exception):
            transfers.acl_rules._add_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                principal_type="identity",
                path=None,
                permissions="r",
            )

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_add_acl_rule_incorrect_permissions(self):
        logger.info("Start test add acl rule with incorrect permissions...")

        transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        with self.assertRaises(Exception):
            transfers.acl_rules._add_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                principal_type="identity",
                path="/",
                permissions=None,
            )

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_delete_acl_rule_with_collection_name_user_identity_path_and_permissions(
        self,
    ):
        logger.info(
            "Start test delete acl rule using collection_name, user_identity, path and permissions..."
        )

        result = transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Deleted")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 0)

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_delete_acl_rule_with_collection_id_principal_path_and_permissions(self):
        logger.info(
            "Start test delete acl rule using collection_id, principal, path and permissions ..."
        )

        result = transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Deleted")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 0)

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_delete_acl_rule_with_collection_name_principal_path_and_permission(self):
        logger.info(
            "Start test delete acl rule using collection_name, principal, path and permissions..."
        )

        result = transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Deleted")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 0)

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_delete_acl_rule_with_collection_id_user_identity_path_and_permission(self):
        logger.info(
            "Start test delete acl rule using collection_id, user_identity, path and permissions..."
        )

        result = transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Deleted")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 0)

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_delete_acl_rule_with_collection_name_and_rule_id(self):
        logger.info("Start test delete acl rule using collection name and rule id...")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )[0]

        result = transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            rule_id=rule["id"],
        )

        self.assertEqual(result["code"], "Deleted")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 0)

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_delete_acl_rule_with_collection_id_and_rule_id(self):
        logger.info("Start test delete acl rule using collection id and rule id...")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )[0]

        result = transfers.acl_rules._delete_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            rule_id=rule["id"],
        )

        self.assertEqual(result["code"], "Deleted")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 0)

        transfers.acl_rules._add_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            path="/",
            permissions="r",
        )

    def test_delete_acl_rule_incorrect_transfer_client(self):
        logger.info("Start test delete acl rule with incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._delete_acl_rule(
                current_transfer_client=None,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_delete_acl_rule_incorrect_auth_client(self):
        logger.info("Start test delete acl rule with incorrect auth client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._delete_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=None,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_delete_acl_rule_incorrect_collection_name_and_id(self):
        logger.info(
            "Start test delete acl rule with incorrect collection name and id..."
        )

        with self.assertRaises(ValueError):
            transfers.acl_rules._delete_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=None,
                collection_id=None,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_delete_acl_rule_incorrect_user_identity_principal_path_permissions_and_rule_id(
        self,
    ):
        logger.info(
            "Start test delete acl rule with incorrect user_identity, principal, path, permissions and rule_id..."
        )

        with self.assertRaises(ValueError):
            transfers.acl_rules._delete_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=None,
                principal=None,
                path=None,
                permissions=None,
                rule_id=None,
            )

    def test_update_acl_rule_with_collection_name_user_identity_path_and_permissions(
        self,
    ):
        logger.info(
            "Start test update acl rule using collection_name, user_identity, path and permissions..."
        )

        result = transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="rw",
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Updated")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="rw",
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "rw")

        transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="r",
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="rw",
        )

    def test_update_acl_rule_with_collection_id_principal_path_and_permissions(self):
        logger.info(
            "Start test update acl rule using collection_id, principal, path and permissions ..."
        )

        result = transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="rw",
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Updated")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="rw",
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "rw")

        transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="r",
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            path="/",
            permissions="rw",
        )

    def test_update_acl_rule_with_collection_name_principal_path_and_permission(self):
        logger.info(
            "Start test update acl rule using collection_name, principal, path and permissions..."
        )

        result = transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="rw",
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Updated")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="rw",
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "rw")

        transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="r",
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            path="/",
            permissions="rw",
        )

    def test_update_acl_rule_with_collection_id_user_identity_path_and_permission(self):
        logger.info(
            "Start test update acl rule using collection_id, user_identity, path and permissions..."
        )

        result = transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="rw",
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )

        self.assertEqual(result["code"], "Updated")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="rw",
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "rw")

        transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="r",
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            path="/",
            permissions="rw",
        )

    def test_update_acl_rule_with_collection_name_and_rule_id(self):
        logger.info("Start test update acl rule using collection name and rule id...")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )[0]

        result = transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="rw",
            collection_name=self.guest_collection_name,
            rule_id=rule["id"],
        )

        self.assertEqual(result["code"], "Updated")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="rw",
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "rw")

        transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="r",
            collection_name=self.guest_collection_name,
            rule_id=rule["id"],
        )

    def test_update_acl_rule_with_collection_id_and_rule_id(self):
        logger.info("Start test update acl rule using collection id and rule id...")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )[0]

        result = transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="rw",
            collection_id=self.guest_collection["id"],
            rule_id=rule["id"],
        )

        self.assertEqual(result["code"], "Updated")

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            permissions="rw",
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
        )[0]

        self.assertEqual(rule["principal"], self.user_uuid)
        self.assertEqual(rule["path"], "/")
        self.assertEqual(rule["permissions"], "rw")

        transfers.acl_rules._update_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            new_permissions="r",
            collection_id=self.guest_collection["id"],
            rule_id=rule["id"],
        )

    def test_update_acl_rule_incorrect_transfer_client(self):
        logger.info("Start test update acl rule with incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._update_acl_rule(
                current_transfer_client=None,
                current_auth_client=self.auth_client,
                new_permissions="rw",
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_update_acl_rule_incorrect_auth_client(self):
        logger.info("Start test update acl rule with incorrect auth client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._update_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=None,
                new_permissions="rw",
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_update_acl_rule_incorrect_collection_name_and_id(self):
        logger.info(
            "Start test update acl rule with incorrect collection name and id..."
        )

        with self.assertRaises(ValueError):
            transfers.acl_rules._update_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                new_permissions="rw",
                collection_name=None,
                collection_id=None,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_update_acl_rule_incorrect_user_identity_principal_path_permissions_and_rule_id(
        self,
    ):
        logger.info(
            "Start test update acl rule with incorrect user_identity, principal, path, permissions and rule_id..."
        )

        with self.assertRaises(ValueError):
            transfers.acl_rules._update_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                new_permissions="rw",
                collection_name=self.guest_collection_name,
                user_identity=None,
                principal=None,
                path=None,
                permissions=None,
                rule_id=None,
            )

    def test_update_acl_rule_incorrect_new_permissions(self):
        logger.info("Start test update acl rule with incorrect new_permissions...")

        with self.assertRaises(Exception):
            transfers.acl_rules._update_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                new_permissions="None",
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_get_acl_rule_with_collection_name_user_identity_path_and_permissions(self):
        logger.info(
            "Start test get acl rule using collection_name, user_identity, path and permissions..."
        )

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule[0]["principal"], self.user_uuid)
        self.assertEqual(rule[0]["path"], "/")
        self.assertEqual(rule[0]["permissions"], "r")

    def test_get_acl_rule_with_collection_id_principal_and_path_and_permission(self):
        logger.info(
            "Start test get acl rule using collection_id, principal, path and permissions..."
        )

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule[0]["principal"], self.user_uuid)
        self.assertEqual(rule[0]["path"], "/")
        self.assertEqual(rule[0]["permissions"], "r")

    def test_get_acl_rule_with_collection_name_principal_path_and_permission(self):
        logger.info(
            "Start test get acl rule using collection_name, principal, path and permissions..."
        )

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule[0]["principal"], self.user_uuid)
        self.assertEqual(rule[0]["path"], "/")
        self.assertEqual(rule[0]["permissions"], "r")

    def test_get_acl_rule_with_collection_id_user_identity_path_and_permission(self):
        logger.info(
            "Start test get acl rule using collection_id, user_identity, path and permissions..."
        )

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule[0]["principal"], self.user_uuid)
        self.assertEqual(rule[0]["path"], "/")
        self.assertEqual(rule[0]["permissions"], "r")

    def test_get_acl_rule_with_collection_name_and_rule_id(self):
        logger.info("Start test get acl rule using collection name and rule id...")

        grule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )[0]

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            rule_id=grule["id"],
        )
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule[0]["principal"], self.user_uuid)
        self.assertEqual(rule[0]["path"], "/")
        self.assertEqual(rule[0]["permissions"], "r")

    def test_get_acl_rule_with_collection_id_and_rule_id(self):
        logger.info("Start test get acl rule using collection id and rule id...")

        grule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            path="/",
            permissions="r",
        )[0]

        rule = transfers.acl_rules._get_acl_rule(
            current_transfer_client=self.transfer_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            rule_id=grule["id"],
        )
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule[0]["principal"], self.user_uuid)
        self.assertEqual(rule[0]["path"], "/")
        self.assertEqual(rule[0]["permissions"], "r")

    def test_get_acl_rule_incorrect_transfer_client(self):
        logger.info("Start test get acl rule with incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._get_acl_rule(
                current_transfer_client=None,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_get_acl_rule_incorrect_auth_client(self):
        logger.info("Start test get acl rule with incorrect auth client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._get_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=None,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_get_acl_rule_incorrect_collection_name_and_id(self):
        logger.info("Start test get acl rule with incorrect collection name and id...")

        with self.assertRaises(ValueError):
            transfers.acl_rules._get_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=None,
                collection_id=None,
                user_identity=self.user_identity,
                path="/",
                permissions="r",
            )

    def test_get_acl_rule_incorrect_user_identity_and_principal_path_permissions_and_rule_id(
        self,
    ):
        logger.info(
            "Start test get acl rule with incorrect user_identity, principal, path, permissions and rule_id..."
        )

        with self.assertRaises(ValueError):
            transfers.acl_rules._get_acl_rule(
                current_transfer_client=self.transfer_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=None,
                principal=None,
                path=None,
                permissions=None,
                rule_id=None,
            )

    def test_get_acl_rule_list_with_collection_name(self):
        logger.info("Start test get acl rule list using collection_name...")

        rule_list = transfers.acl_rules._acl_rule_list(
            current_transfer_client=self.transfer_client,
            collection_name=self.guest_collection_name,
        )
        self.assertEqual(len(rule_list), 3)

    def test_get_acl_rule_list_with_collection_id(self):
        logger.info("Start test get acl rule list using collection_id...")

        rule_list = transfers.acl_rules._acl_rule_list(
            current_transfer_client=self.transfer_client,
            collection_id=self.guest_collection["id"],
        )
        self.assertEqual(len(rule_list), 3)

    def test_get_acl_rule_list_incorrect_transfer_client(self):
        logger.info("Start test get acl rule list with incorrect transfer client...")

        with self.assertRaises(Exception):
            transfers.acl_rules._acl_rule_list(
                current_transfer_client=None,
                collection_name=self.guest_collection_name,
            )

    def test_get_acl_rule_list_incorrect_collection_name_and_id(self):
        logger.info(
            "Start test get acl rule list with incorrect collection_name and collection_id..."
        )

        with self.assertRaises(ValueError):
            transfers.acl_rules._acl_rule_list(
                current_transfer_client=self.transfer_client,
                collection_name=None,
                collection_id=None,
            )

    @classmethod
    def tearDownClass(cls) -> None:
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


class TestURL(unittest.TestCase):
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

        cls.non_existing_collection_name = os.environ[
            "GLOBUSAPI_NON_EXISTING_COLLECTION_NAME"
        ]

        cls.transfer_client = transfers.transfer_client.transfer_client(
            cls.confidential_client_id,
            cls.confidential_client_secret,
            TransferScopes.all,
        )

    def test_get_url(self):
        logger.info("Start test get url smoke test...")

        url1 = transfers.url_methods._get_url(
            current_transfer_client=self.transfer_client,
            collection_id=self.collection_id,
            path=self.item_list[0]["source_path"],
        )
        self.assertTrue(validators.url(url1))

        url2 = transfers.url_methods._get_url(
            current_transfer_client=self.transfer_client,
            collection_name=self.collection_name,
            path=self.item_list[0]["source_path"],
        )
        self.assertTrue(validators.url(url2))

        self.assertEqual(url1, url2)

    def test_get_url_incorrect_transfer_client(self):
        logger.info("Start test get url incorrect task_id...")

        with self.assertRaises(Exception):
            transfers.url_methods._get_url(
                current_transfer_client=None,
                collection_id=self.collection_id,
                path=self.item_list[0]["source_path"],
            )

    def test_get_url_incorrect_collection_id(self):
        logger.info("Start test get url incorrect collection_id...")

        with self.assertRaises(Exception):
            transfers.url_methods._get_url(
                current_transfer_client=self.transfer_client,
                collection_id=None,
                path=self.item_list[0]["source_path"],
            )

    def test_get_url_incorrect_collection_name(self):
        logger.info("Start test get url incorrect collection_name...")

        with self.assertRaises(Exception):
            transfers.url_methods._get_url(
                current_transfer_client=self.transfer_client,
                collection_name=self.non_existing_collection_name,
                path=self.item_list[0]["source_path"],
            )

    def test_get_url_incorrect_path(self):
        logger.info("Start test get url incorrect path...")

        with self.assertRaises(Exception):
            transfers.url_methods._get_url(
                current_transfer_client=self.transfer_client,
                collection_id=self.collection_id,
                path="None",
            )
