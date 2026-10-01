"""
   Copyright [2026] [Rosalind Franklin Institute]

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

import datetime
import os
import unittest
import uuid

from click.testing import CliRunner
from globus_sdk.scopes import TransferScopes

import GlobusAPI
import GlobusAPI.cli.timers as GlobusAPI_cli
import GlobusAPI.timers as timers
import GlobusAPI.transfers as transfers
from GlobusAPI.__main__ import cli

logger = GlobusAPI.logging.logging.get_logger(stdout=True)
SUCCESSFUL_EXIT_CODE = 0


class TestCliTimers(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.source_collection_id = os.environ["GLOBUSAPI_SOURCE_COLLECTION_ID"]
        cls.destination_collection_id = os.environ[
            "GLOBUSAPI_DESTINATION_COLLECTION_ID"
        ]
        cls.item_list_filename = (
            "/usr/local/GlobusAPI/tests/GlobusAPI/data/transfer_list.json"
        )
        # Scheduled far enough in the future that the timer never actually fires during
        # the test run, so the tests do not depend on a real transfer completing.
        cls.far_future = (
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
        ).isoformat()

        cls.timers_client = timers.timers.timers_client(
            confidential_client_id=cls.confidential_client_id,
            confidential_client_secret=cls.confidential_client_secret,
        )
        cls.transfer_client = transfers.transfer_client.transfer_client(
            cls.confidential_client_id,
            cls.confidential_client_secret,
            TransferScopes.all,
        )

        # Timer commands
        cli.add_command(GlobusAPI_cli.listtimers)
        cli.add_command(GlobusAPI_cli.gettimer)
        cli.add_command(GlobusAPI_cli.createtimer)
        cli.add_command(GlobusAPI_cli.deletetimer)
        cli.add_command(GlobusAPI_cli.pausetimer)
        cli.add_command(GlobusAPI_cli.resumetimer)

        cls.runner = CliRunner()

    def test_cli_create_and_delete_timer(self):
        logger.info("Start create/delete timer test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createtimer",
                "--item-list-filename",
                self.item_list_filename,
                "--source-collection-id",
                self.source_collection_id,
                "--destination-collection-id",
                self.destination_collection_id,
                "--name",
                "Unit_Test_Cli_Timer",
                "--run-at",
                self.far_future,
                "--print-parameter",
                "job_id changed",
                "-v",
            ],
        )

        self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
        create_output_lines = result.output.strip().splitlines()
        timer_id = create_output_lines[-2]
        self.assertEqual(create_output_lines[-1], "True")

        try:
            result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "gettimer",
                    "--timer-id",
                    timer_id,
                    "--print-parameter",
                    "job_id",
                    "-v",
                ],
            )
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            self.assertIn(timer_id, result.output)

            result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "deletetimer",
                    "--timer-id",
                    timer_id,
                    "--print-parameter",
                    "changed",
                    "-v",
                ],
            )
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            self.assertEqual(result.output.strip().splitlines()[-1], "True")
        finally:
            try:
                timers.timers._delete_timer(
                    current_timers_client=self.timers_client, timer_id=timer_id
                )
            except Exception:
                pass

    def test_cli_pause_and_resume_timer(self):
        logger.info("Start pause/resume timer test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createtimer",
                "--item-list-filename",
                self.item_list_filename,
                "--source-collection-id",
                self.source_collection_id,
                "--destination-collection-id",
                self.destination_collection_id,
                "--name",
                "Unit_Test_Cli_Timer_Pause_Resume",
                "--interval",
                "01:00:00",
                "--start",
                self.far_future,
                "--stop-after-iterations",
                "1",
                "--print-parameter",
                "job_id",
                "-v",
            ],
        )
        self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
        timer_id = result.output.strip().splitlines()[-1]

        try:
            result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "pausetimer",
                    "--timer-id",
                    timer_id,
                    "--print-parameter",
                    "changed",
                    "-v",
                ],
            )
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            self.assertEqual(result.output.strip().splitlines()[-1], "True")

            # pausetimer only returns a confirmation message, not the timer
            # document, so the effect is verified via a follow-up gettimer.
            result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "gettimer",
                    "--timer-id",
                    timer_id,
                    "--print-parameter",
                    "status",
                    "-v",
                ],
            )
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            self.assertIn("inactive", result.output)

            # Pausing an already-inactive timer is a no-op.
            result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "pausetimer",
                    "--timer-id",
                    timer_id,
                    "--print-parameter",
                    "changed",
                    "-v",
                ],
            )
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            self.assertEqual(result.output.strip().splitlines()[-1], "False")

            result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "resumetimer",
                    "--timer-id",
                    timer_id,
                    "--print-parameter",
                    "changed",
                    "-v",
                ],
            )
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            self.assertEqual(result.output.strip().splitlines()[-1], "True")
        finally:
            try:
                timers.timers._delete_timer(
                    current_timers_client=self.timers_client, timer_id=timer_id
                )
            except Exception:
                pass

    def test_cli_get_and_delete_timer_by_name(self):
        logger.info("Start get/delete timer by name test ...")
        unique_name = f"Unit_Test_Cli_Timer_By_Name_{uuid.uuid4()}"
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "createtimer",
                "--item-list-filename",
                self.item_list_filename,
                "--source-collection-id",
                self.source_collection_id,
                "--destination-collection-id",
                self.destination_collection_id,
                "--name",
                unique_name,
                "--run-at",
                self.far_future,
                "--print-parameter",
                "job_id",
                "-v",
            ],
        )
        self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
        timer_id = result.output.strip().splitlines()[-1]

        try:
            result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "gettimer",
                    "--timer-name",
                    unique_name,
                    "--print-parameter",
                    "job_id",
                    "-v",
                ],
            )
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            self.assertIn(timer_id, result.output)

            result = self.runner.invoke(
                cli,
                [
                    "--confidential-client-id",
                    self.confidential_client_id,
                    "--confidential-client-secret",
                    self.confidential_client_secret,
                    "deletetimer",
                    "--timer-name",
                    unique_name,
                    "--print-parameter",
                    "changed",
                    "-v",
                ],
            )
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            self.assertEqual(result.output.strip().splitlines()[-1], "True")
        finally:
            try:
                timers.timers._delete_timer(
                    current_timers_client=self.timers_client, timer_id=timer_id
                )
            except Exception:
                pass

    def test_cli_createtimer_replace_is_idempotent(self):
        logger.info("Start createtimer --replace test ...")
        unique_name = f"Unit_Test_Cli_Timer_Replace_{uuid.uuid4()}"
        create_args = [
            "--confidential-client-id",
            self.confidential_client_id,
            "--confidential-client-secret",
            self.confidential_client_secret,
            "createtimer",
            "--item-list-filename",
            self.item_list_filename,
            "--source-collection-id",
            self.source_collection_id,
            "--destination-collection-id",
            self.destination_collection_id,
            "--name",
            unique_name,
            "--run-at",
            self.far_future,
            "--replace",
            "--print-parameter",
            "job_id changed",
            "-v",
        ]

        result = self.runner.invoke(cli, create_args)
        self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
        first_output_lines = result.output.strip().splitlines()
        first_timer_id = first_output_lines[-2]
        self.assertEqual(first_output_lines[-1], "True")

        try:
            # Identical request: the existing timer should be left alone and its
            # job_id returned unchanged, rather than deleted and recreated.
            result = self.runner.invoke(cli, create_args)
            self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
            second_output_lines = result.output.strip().splitlines()
            second_timer_id = second_output_lines[-2]
            self.assertEqual(second_timer_id, first_timer_id)
            self.assertEqual(second_output_lines[-1], "False")
        finally:
            try:
                timers.timers._delete_timer(
                    current_timers_client=self.timers_client, timer_id=first_timer_id
                )
            except Exception:
                pass

    def test_cli_list_timers(self):
        logger.info("Start list timers test ...")
        result = self.runner.invoke(
            cli,
            [
                "--confidential-client-id",
                self.confidential_client_id,
                "--confidential-client-secret",
                self.confidential_client_secret,
                "listtimers",
                "-v",
            ],
        )
        self.assertEqual(result.exit_code, SUCCESSFUL_EXIT_CODE)
