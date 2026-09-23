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

from globus_sdk.scopes import TransferScopes

import GlobusAPI
import GlobusAPI.timers as timers
import GlobusAPI.transfers as transfers

logger = GlobusAPI.logging.logging.get_logger(stdout=True)


class TestTimers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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

        cls.timer_response = timers.timers._create_timer(
            current_transfer_client=cls.transfer_client,
            current_timers_client=cls.timers_client,
            item_list_filename=cls.item_list_filename,
            source_collection_id=cls.source_collection_id,
            destination_collection_id=cls.destination_collection_id,
            name="Unit_Test_Timer",
            interval="01:00:00",
            start=cls.far_future,
            stop_after_iterations=1,
        )
        cls.timer_id = cls.timer_response["job_id"]

    def test_get_timers_client(self):
        self.assertIsNotNone(self.timers_client)

    def test_timer_list(self):
        list_of_timers = timers.timers._timer_list(
            current_timers_client=self.timers_client
        )
        timer_ids = [timer["job_id"] for timer in list_of_timers]
        self.assertIn(self.timer_id, timer_ids)

    def test_get_timer(self):
        timer_info = timers.timers._get_timer(
            current_timers_client=self.timers_client, timer_id=self.timer_id
        )
        self.assertEqual(timer_info["job_id"], self.timer_id)

    def test_get_timer_incorrect_id(self):
        with self.assertRaises(Exception):
            timers.timers._get_timer(
                current_timers_client=self.timers_client,
                timer_id=str(uuid.uuid4()),
            )

    def test_get_timer_by_name(self):
        unique_name = f"Unit_Test_Timer_By_Name_{uuid.uuid4()}"
        timer_response = timers.timers._create_timer(
            current_transfer_client=self.transfer_client,
            current_timers_client=self.timers_client,
            item_list_filename=self.item_list_filename,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            name=unique_name,
            run_at=self.far_future,
        )
        timer_id = timer_response["job_id"]

        try:
            timer_info = timers.timers._get_timer(
                current_timers_client=self.timers_client, timer_name=unique_name
            )
            self.assertEqual(timer_info["job_id"], timer_id)
        finally:
            timers.timers._delete_timer(
                current_timers_client=self.timers_client, timer_id=timer_id
            )

    def test_get_timer_requires_exactly_one_of_id_or_name(self):
        with self.assertRaises(ValueError):
            timers.timers._get_timer(current_timers_client=self.timers_client)
        with self.assertRaises(ValueError):
            timers.timers._get_timer(
                current_timers_client=self.timers_client,
                timer_id=self.timer_id,
                timer_name="Unit_Test_Timer",
            )

    def test_get_timer_by_name_no_match(self):
        with self.assertRaises(ValueError):
            timers.timers._get_timer(
                current_timers_client=self.timers_client,
                timer_name=f"Nonexistent_Timer_{uuid.uuid4()}",
            )

    def test_get_timer_by_name_multiple_matches(self):
        duplicate_name = f"Unit_Test_Timer_Duplicate_{uuid.uuid4()}"
        timer_ids = []
        try:
            for _ in range(2):
                timer_response = timers.timers._create_timer(
                    current_transfer_client=self.transfer_client,
                    current_timers_client=self.timers_client,
                    item_list_filename=self.item_list_filename,
                    source_collection_id=self.source_collection_id,
                    destination_collection_id=self.destination_collection_id,
                    name=duplicate_name,
                    run_at=self.far_future,
                )
                timer_ids.append(timer_response["job_id"])

            with self.assertRaises(ValueError):
                timers.timers._get_timer(
                    current_timers_client=self.timers_client,
                    timer_name=duplicate_name,
                )
        finally:
            for timer_id in timer_ids:
                timers.timers._delete_timer(
                    current_timers_client=self.timers_client, timer_id=timer_id
                )

    def test_delete_timer_by_name(self):
        unique_name = f"Unit_Test_Timer_Delete_By_Name_{uuid.uuid4()}"
        timer_response = timers.timers._create_timer(
            current_transfer_client=self.transfer_client,
            current_timers_client=self.timers_client,
            item_list_filename=self.item_list_filename,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            name=unique_name,
            run_at=self.far_future,
        )
        timer_id = timer_response["job_id"]

        delete_response = timers.timers._delete_timer(
            current_timers_client=self.timers_client, timer_name=unique_name
        )
        self.assertEqual(delete_response["job_id"], timer_id)
        self.assertTrue(delete_response["changed"])

    def test_create_timer_once(self):
        timer_response = timers.timers._create_timer(
            current_transfer_client=self.transfer_client,
            current_timers_client=self.timers_client,
            item_list_filename=self.item_list_filename,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            name="Unit_Test_Timer_Once",
            run_at=self.far_future,
        )
        try:
            self.assertIsNotNone(timer_response["job_id"])
            self.assertTrue(timer_response["changed"])
        finally:
            timers.timers._delete_timer(
                current_timers_client=self.timers_client,
                timer_id=timer_response["job_id"],
            )

    def test_create_timer_requires_a_schedule(self):
        with self.assertRaises(ValueError):
            timers.timers._create_timer(
                current_transfer_client=self.transfer_client,
                current_timers_client=self.timers_client,
                item_list_filename=self.item_list_filename,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
            )

    def test_create_timer_rejects_two_schedules(self):
        with self.assertRaises(ValueError):
            timers.timers._create_timer(
                current_transfer_client=self.transfer_client,
                current_timers_client=self.timers_client,
                item_list_filename=self.item_list_filename,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                interval="00:01:00",
                run_at=self.far_future,
            )

    def test_create_timer_replace_requires_name(self):
        with self.assertRaises(ValueError):
            timers.timers._create_timer(
                current_transfer_client=self.transfer_client,
                current_timers_client=self.timers_client,
                item_list_filename=self.item_list_filename,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                run_at=self.far_future,
                replace=True,
            )

    def test_create_timer_replace_creates_when_none_exists(self):
        unique_name = f"Unit_Test_Timer_Replace_New_{uuid.uuid4()}"
        timer_response = timers.timers._create_timer(
            current_transfer_client=self.transfer_client,
            current_timers_client=self.timers_client,
            item_list_filename=self.item_list_filename,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            name=unique_name,
            run_at=self.far_future,
            replace=True,
        )
        try:
            self.assertIsNotNone(timer_response["job_id"])
            self.assertTrue(timer_response["changed"])
        finally:
            timers.timers._delete_timer(
                current_timers_client=self.timers_client,
                timer_id=timer_response["job_id"],
            )

    def test_create_timer_replace_skips_when_unchanged(self):
        unique_name = f"Unit_Test_Timer_Replace_Unchanged_{uuid.uuid4()}"
        first_response = timers.timers._create_timer(
            current_transfer_client=self.transfer_client,
            current_timers_client=self.timers_client,
            item_list_filename=self.item_list_filename,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            name=unique_name,
            run_at=self.far_future,
        )
        first_job_id = first_response["job_id"]

        try:
            second_response = timers.timers._create_timer(
                current_transfer_client=self.transfer_client,
                current_timers_client=self.timers_client,
                item_list_filename=self.item_list_filename,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                name=unique_name,
                run_at=self.far_future,
                replace=True,
            )
            # Identical request, so the existing timer should be left alone and
            # returned unchanged rather than deleted and recreated.
            self.assertEqual(second_response["job_id"], first_job_id)
            self.assertFalse(second_response["changed"])
        finally:
            timers.timers._delete_timer(
                current_timers_client=self.timers_client, timer_id=first_job_id
            )

    def test_create_timer_replace_recreates_when_changed(self):
        unique_name = f"Unit_Test_Timer_Replace_Changed_{uuid.uuid4()}"
        other_far_future = (
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=366)
        ).isoformat()

        first_response = timers.timers._create_timer(
            current_transfer_client=self.transfer_client,
            current_timers_client=self.timers_client,
            item_list_filename=self.item_list_filename,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            name=unique_name,
            run_at=self.far_future,
        )
        job_ids = [first_response["job_id"]]

        try:
            second_response = timers.timers._create_timer(
                current_transfer_client=self.transfer_client,
                current_timers_client=self.timers_client,
                item_list_filename=self.item_list_filename,
                source_collection_id=self.source_collection_id,
                destination_collection_id=self.destination_collection_id,
                name=unique_name,
                run_at=other_far_future,
                replace=True,
            )
            job_ids.append(second_response["job_id"])
            self.assertNotEqual(second_response["job_id"], job_ids[0])
            self.assertTrue(second_response["changed"])

            old_timer_info = timers.timers._get_timer(
                current_timers_client=self.timers_client, timer_id=job_ids[0]
            )
            self.assertEqual(old_timer_info["status"], "delete_in_progress")
        finally:
            for job_id in job_ids:
                try:
                    timers.timers._delete_timer(
                        current_timers_client=self.timers_client, timer_id=job_id
                    )
                except Exception:
                    pass

    def test_create_timer_replace_rejects_multiple_matches(self):
        duplicate_name = f"Unit_Test_Timer_Replace_Duplicate_{uuid.uuid4()}"
        job_ids = []
        try:
            for _ in range(2):
                timer_response = timers.timers._create_timer(
                    current_transfer_client=self.transfer_client,
                    current_timers_client=self.timers_client,
                    item_list_filename=self.item_list_filename,
                    source_collection_id=self.source_collection_id,
                    destination_collection_id=self.destination_collection_id,
                    name=duplicate_name,
                    run_at=self.far_future,
                )
                job_ids.append(timer_response["job_id"])

            with self.assertRaises(ValueError):
                timers.timers._create_timer(
                    current_transfer_client=self.transfer_client,
                    current_timers_client=self.timers_client,
                    item_list_filename=self.item_list_filename,
                    source_collection_id=self.source_collection_id,
                    destination_collection_id=self.destination_collection_id,
                    name=duplicate_name,
                    run_at=self.far_future,
                    replace=True,
                )
        finally:
            for job_id in job_ids:
                timers.timers._delete_timer(
                    current_timers_client=self.timers_client, timer_id=job_id
                )

    def test_pause_and_resume_timer(self):
        timer_response = timers.timers._create_timer(
            current_transfer_client=self.transfer_client,
            current_timers_client=self.timers_client,
            item_list_filename=self.item_list_filename,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            name="Unit_Test_Timer_Pause_Resume",
            interval="01:00:00",
            start=self.far_future,
            stop_after_iterations=1,
        )
        timer_id = timer_response["job_id"]

        try:
            # pause_job/resume_job only return a confirmation message, not the
            # timer document, so the effect is verified via a follow-up get_timer.
            pause_response = timers.timers._pause_timer(
                current_timers_client=self.timers_client, timer_id=timer_id
            )
            self.assertTrue(pause_response["changed"])
            timer_info = timers.timers._get_timer(
                current_timers_client=self.timers_client, timer_id=timer_id
            )
            self.assertEqual(timer_info["status"], "inactive")

            # Pausing an already-inactive timer is a no-op.
            pause_again_response = timers.timers._pause_timer(
                current_timers_client=self.timers_client, timer_id=timer_id
            )
            self.assertFalse(pause_again_response["changed"])

            resume_response = timers.timers._resume_timer(
                current_timers_client=self.timers_client, timer_id=timer_id
            )
            self.assertTrue(resume_response["changed"])
            timer_info = timers.timers._get_timer(
                current_timers_client=self.timers_client, timer_id=timer_id
            )
            self.assertNotEqual(timer_info["status"], "inactive")

            # Resuming an already-active timer is a no-op.
            resume_again_response = timers.timers._resume_timer(
                current_timers_client=self.timers_client, timer_id=timer_id
            )
            self.assertFalse(resume_again_response["changed"])
        finally:
            timers.timers._delete_timer(
                current_timers_client=self.timers_client, timer_id=timer_id
            )

    def test_delete_timer(self):
        timer_response = timers.timers._create_timer(
            current_transfer_client=self.transfer_client,
            current_timers_client=self.timers_client,
            item_list_filename=self.item_list_filename,
            source_collection_id=self.source_collection_id,
            destination_collection_id=self.destination_collection_id,
            name="Unit_Test_Timer_To_Delete",
            run_at=self.far_future,
        )
        timer_id = timer_response["job_id"]

        delete_response = timers.timers._delete_timer(
            current_timers_client=self.timers_client, timer_id=timer_id
        )
        # Globus deletes timers asynchronously: deletion is only requested here, not
        # completed, so the timer still exists (in "delete_in_progress" status) rather
        # than immediately 404ing on a subsequent get.
        self.assertEqual(delete_response["status"], "delete_in_progress")
        self.assertTrue(delete_response["changed"])

        timer_info = timers.timers._get_timer(
            current_timers_client=self.timers_client, timer_id=timer_id
        )
        self.assertEqual(timer_info["status"], "delete_in_progress")

    def test_delete_timer_is_idempotent_for_unknown_id(self):
        delete_response = timers.timers._delete_timer(
            current_timers_client=self.timers_client, timer_id=str(uuid.uuid4())
        )
        self.assertFalse(delete_response["changed"])

    def test_delete_timer_is_idempotent_for_unknown_name(self):
        delete_response = timers.timers._delete_timer(
            current_timers_client=self.timers_client,
            timer_name=f"Nonexistent_Timer_{uuid.uuid4()}",
        )
        self.assertFalse(delete_response["changed"])

    @classmethod
    def tearDownClass(cls):
        timers.timers._delete_timer(
            current_timers_client=cls.timers_client, timer_id=cls.timer_id
        )
