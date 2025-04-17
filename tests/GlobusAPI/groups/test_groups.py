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

from globus_sdk.scopes import AuthScopes, GroupsScopes

import GlobusAPI
import GlobusAPI.groups as groups

logger = GlobusAPI.logging.logging.get_logger(stdout=True)


class TestGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.testing_group_name = os.environ["GLOBUSAPI_TESTING_GROUP_NAME"]
        cls.non_existing_group_name = os.environ["GLOBUSAPI_NON_EXISTING_GROUP_NAME"]

        cls.groups_client = groups.groups.groups_client(
            confidential_client_id=cls.confidential_client_id,
            confidential_client_secret=cls.confidential_client_secret,
            scopes=GroupsScopes.all,
        )
        cls.group_name = cls.testing_group_name

        groups.groups._create_group(
            current_groups_client=cls.groups_client,
            group_name=cls.group_name,
            parent_id=None,
            description="Testing group",
        )
        cls.group = groups.groups.get_group_from_name(cls.groups_client, cls.group_name)

    def test_get_groups_client(self):
        self.assertIsNot(self.groups_client, None)

    def test_create_group(self):
        groups.groups._delete_group(self.groups_client, self.group_name)

        logger.info("Creating group...")
        groups.groups._create_group(
            current_groups_client=self.groups_client,
            group_name=self.group_name,
            parent_id=None,
            description="Testing group",
        )

        retrieve_group = groups.groups.get_group_from_name(
            self.groups_client, self.group_name
        )

        self.assertEqual(retrieve_group["name"], self.group_name)
        self.assertIsNotNone(retrieve_group["id"])

    def test_get_not_a_group_from_name(self):
        not_a_group = groups.groups.get_group_from_name(
            self.groups_client, self.non_existing_group_name
        )
        self.assertIsNone(not_a_group)

    def test_delete_group(self):
        logger.info("Deleting group ..")
        groups.groups._delete_group(self.groups_client, self.group_name)
        group = groups.groups.get_group_from_name(self.groups_client, self.group_name)
        self.assertIsNone(group)
        groups.groups._create_group(
            current_groups_client=self.groups_client,
            group_name=self.group_name,
            parent_id=None,
            description="Testing group",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        groups.groups._delete_group(cls.groups_client, cls.group_name)


class TestUserGroupsOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.testing_user_identity = os.environ["GLOBUSAPI_TESTING_USER_IDENTITY"]
        cls.testing_user_identity2 = os.environ["GLOBUSAPI_TESTING_USER_IDENTITY2"]
        cls.testing_group_name = os.environ["GLOBUSAPI_TESTING_GROUP_NAME"]
        cls.non_existing_orcid_identity = os.environ[
            "GLOBUSAPI_NON_EXISTING_ORCID_IDENTITY"
        ]
        cls.scopes = [GroupsScopes.all]

        cls.groups_client = groups.groups.groups_client(
            confidential_client_id=cls.confidential_client_id,
            confidential_client_secret=cls.confidential_client_secret,
            scopes=cls.scopes,
        )

        cls.group_name = cls.testing_group_name

        cls.auth_client = groups.users.auth_client(
            confidential_client_id=os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"],
            confidential_client_secret=os.environ[
                "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
            ],
            scopes=cls.scopes,
        )

        groups.groups._create_group(
            current_groups_client=cls.groups_client,
            group_name=cls.group_name,
            parent_id=None,
            description="Testing group creation",
        )
        cls.group = groups.groups.get_group_from_name(cls.groups_client, cls.group_name)

    def test_add_users_to_groups(self):
        logger.info("Adding members...")
        members = f"{self.testing_user_identity} {self.testing_user_identity2}"
        roles = "member member"

        groups.groups._add_group_members(
            current_groups_client=self.groups_client,
            current_auth_client=self.auth_client,
            group_name=self.group_name,
            add_members_list=members,
            roles=roles,
        )
        added_members = self.groups_client.get_group(
            self.group["id"], include=["memberships"]
        )

        member_uuid = groups.users.get_user_uuid(self.auth_client, members)
        added_member_uuid = groups.groups.get_group_members_uuid(
            self.groups_client, self.group_name
        )

        for uuid in member_uuid:
            with self.subTest(uuid=uuid):
                self.assertIn(uuid, added_member_uuid)
                for added_member in added_members["memberships"]:
                    with self.subTest(added_member=added_member):
                        if added_member["identity_id"] == uuid:
                            self.assertEqual(added_member["status"], "active")
                            self.assertRegex(
                                added_member["identity_id"],
                                "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                            )

    def test_change_role_of_users_to_groups(self):
        logger.info("Changing role members...")
        members = f"{self.testing_user_identity} {self.testing_user_identity2}"
        roles = "manager manager"

        groups.groups._change_role_group_members(
            current_groups_client=self.groups_client,
            current_auth_client=self.auth_client,
            group_name=self.group_name,
            members_list=members,
            roles=roles,
        )
        changed_role_members = self.groups_client.get_group(
            self.group["id"], include=["memberships"]
        )

        member_uuid = groups.users.get_user_uuid(self.auth_client, members)
        roles = list(set(roles.split(" ")))
        added_member_uuid = groups.groups.get_group_members_uuid(
            self.groups_client, self.group_name
        )

        for i in range(0, len(member_uuid)):
            uuid = member_uuid[i]
            role = roles[i]
            with self.subTest(uuid=uuid, role=role):
                self.assertIn(uuid, added_member_uuid)
                for changed_role_member in changed_role_members["memberships"]:
                    with self.subTest(added_member=changed_role_member):
                        if changed_role_member["identity_id"] == uuid:
                            self.assertEqual(changed_role_member["role"], role)
                            self.assertEqual(changed_role_member["status"], "active")
                            self.assertRegex(
                                changed_role_member["identity_id"],
                                "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                            )

    def test_remove_users_from_groups(self):
        logger.info("Removing members...")
        members = f"{self.testing_user_identity} {self.testing_user_identity2}"

        groups.groups._remove_group_members(
            current_groups_client=self.groups_client,
            current_auth_client=self.auth_client,
            group_name=self.group_name,
            remove_members_list=members,
        )
        removed_members = self.groups_client.get_group(
            self.group["id"], include=["memberships"]
        )
        logger.info(removed_members)
        member_uuid = groups.users.get_user_uuid(self.auth_client, members)
        for uuid in member_uuid:
            for removed_member in removed_members["memberships"]:
                if removed_member["identity_id"] == uuid:
                    self.assertEqual(removed_member["status"], "removed")

    def test_add_user_who_does_not_exist_in_globus(self):
        logger.info("Adding members...")

        groups.groups._add_group_members(
            current_groups_client=self.groups_client,
            current_auth_client=self.auth_client,
            group_name=self.group_name,
            add_members_list=self.non_existing_orcid_identity,
            roles="member",
        )
        added_members = self.groups_client.get_group(
            self.group["id"], include=["memberships"]
        )
        usernames = [member["username"] for member in added_members["memberships"]]

        self.assertNotIn(self.non_existing_orcid_identity, usernames)

    def test_get_group(self):
        logger.info("Get group info...")
        group_info = groups.groups._get_group(
            current_groups_client=self.groups_client, group_name=self.group_name
        )
        self.assertEqual(group_info["name"], self.group_name)
        self.assertIsNotNone(group_info["id"])

    def test_group_list(self):
        logger.info("Get list of existing groups...")
        list_of_groups = groups.groups._group_list(
            current_groups_client=self.groups_client
        )
        self.assertIsNotNone(list_of_groups[0]["id"])

    @classmethod
    def tearDownClass(cls) -> None:
        groups.groups._delete_group(cls.groups_client, cls.group_name)


class TestUsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.testing_user_identity = os.environ["GLOBUSAPI_TESTING_USER_IDENTITY"]
        cls.testing_user_name = os.environ["GLOBUSAPI_TESTING_USER_NAME"]
        cls.testing_user_identity2 = os.environ["GLOBUSAPI_TESTING_USER_IDENTITY2"]
        cls.testing_user_name2 = os.environ["GLOBUSAPI_TESTING_USER_NAME2"]
        cls.email_address_domain = os.environ[
            "GLOBUSAPI_ORGANISATION_EMAIL_ADDRESS_DOMAIN"
        ]
        cls.incorrect_orcid_identity = os.environ["GLOBUSAPI_INCORRECT_ORCID_IDENTITY"]
        cls.scopes = [AuthScopes.openid]

        cls.auth_client = groups.users.auth_client(
            confidential_client_id=os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"],
            confidential_client_secret=os.environ[
                "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
            ],
            scopes=cls.scopes,
        )
        cls.orcids = [cls.testing_user_identity, cls.testing_user_identity2]

    def test_get_users(self):
        users = groups.users.get_users(self.auth_client, list_orcids=self.orcids)

        for user in users:
            with self.subTest(user=user):
                self.assertIn(
                    user["name"], [self.testing_user_name, self.testing_user_name2]
                )

        not_orcids = [
            self.incorrect_orcid_identity,
        ]
        not_users = groups.users.get_users(self.auth_client, list_orcids=not_orcids)
        self.assertEqual(len(not_users), 0)

    def test_get_users_uuids(self):
        uuids = groups.users.get_user_uuid(self.auth_client, list_orcids=self.orcids)
        for uuid in uuids:
            with self.subTest(uuid=uuid):
                self.assertRegex(
                    uuid,
                    "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                )

    def test_get_user_emails(self):
        emails = groups.users.get_user_emails(self.auth_client, list_orcids=self.orcids)
        for email in emails:
            with self.subTest(email=email):
                self.assertIn(f"@{self.email_address_domain}", email)
