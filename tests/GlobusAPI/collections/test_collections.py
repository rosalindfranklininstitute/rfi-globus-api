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

from globus_sdk import GCSClient
from globus_sdk.scopes import AuthScopes, TransferScopes

import GlobusAPI
import GlobusAPI.collections as collections
import GlobusAPI.groups as groups
import GlobusAPI.transfers as transfers

logger = GlobusAPI.logging.logging.get_logger(stdout=True)


class TestCollectionUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage_gateway_name = os.environ["GLOBUSAPI_STORAGE_GATEWAY_NAME"]
        cls.confidential_client_id = os.environ["GLOBUSAPI_CONFIDENTIAL_CLIENT_ID"]
        cls.confidential_client_secret = os.environ[
            "GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET"
        ]
        cls.endpoint_id = os.environ["GLOBUSAPI_ENDPOINT_ID"]
        cls.mapped_collection_id = os.environ["GLOBUSAPI_MAPPED_COLLECTION_ID"]
        cls.guest_collection_name = os.environ["GLOBUSAPI_TESTING_COLLECTION_NAME"]
        cls.base_path = os.environ["GLOBUSAPI_TESTING_COLLECTION_BASEPATH"]
        cls.non_existing_storage_gateway = os.environ[
            "GLOBUSAPI_NON_EXISTING_STORAGE_GATEWAY"
        ]
        cls.non_existing_collection_name = os.environ[
            "GLOBUSAPI_NON_EXISTING_COLLECTION_NAME"
        ]

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

    def test_gcs_client(self):
        self.assertIsInstance(self.gcs_client, GCSClient)

    def test_get_storage_gateway_from_name(self):
        storage_gateway = collections.utils.get_storage_gateway_by_name(
            current_gcs_client=self.gcs_client,
            gateway_name=self.storage_gateway_name,
        )
        self.assertEqual(storage_gateway[0]["display_name"], self.storage_gateway_name)

        # test outcome when does not exist
        gateway_name = self.non_existing_storage_gateway
        storage_gateway = collections.utils.get_storage_gateway_by_name(
            current_gcs_client=self.gcs_client, gateway_name=gateway_name
        )
        self.assertEqual(storage_gateway, [])

    def test_get_collection_from_name(self):
        collection = collections.utils.get_collection_from_name(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
        )
        self.assertEqual(collection[0]["display_name"], self.guest_collection_name)

        # check that we return none when a collection is not found
        collection_name = self.non_existing_collection_name
        false_collection = collections.utils.get_collection_from_name(
            current_gcs_client=self.gcs_client,
            collection_name=collection_name,
        )
        self.assertEqual(len(false_collection), 0)

    def test_get_collection(self):
        collection = collections.utils.get_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            collection_id=None,
        )
        self.assertEqual(collection[0]["display_name"], self.guest_collection_name)

        # check that we return none when a collection is not found
        guest_collection_name = self.non_existing_collection_name
        false_collection = collections.utils.get_collection(
            current_gcs_client=self.gcs_client,
            collection_name=guest_collection_name,
            collection_id=None,
        )
        self.assertEqual(len(false_collection), 0)

    def test_get_collection_list(self):
        collection_list = collections.guest.get_collection_list(
            current_gcs_client=self.gcs_client,
            mapped_collection_id=self.mapped_collection_id,
        )
        collection_name = [
            collection
            for collection in collection_list
            if collection["display_name"] == self.guest_collection_name
        ]
        self.assertEqual(collection_name[0]["display_name"], self.guest_collection_name)

    @classmethod
    def tearDownClass(cls) -> None:
        collections.guest._delete_guest_collection(
            cls.gcs_client, cls.guest_collection_name
        )


class TestCollectionGuestCollection(unittest.TestCase):
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

    def test_collection(self):
        # create a guest collection for the mapped collection that
        collections.guest._create_guest_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            mapped_collection_id=self.mapped_collection_id,
            base_path=self.base_path,
        )
        guest_collection = collections.utils.get_collection_from_name(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            filter_to_help="guest_collections",
        )
        self.assertEqual(
            guest_collection[0]["display_name"], self.guest_collection_name
        )
        self.assertEqual(
            guest_collection[0]["mapped_collection_id"], self.mapped_collection_id
        )

    def test_delete_guest_collection(self):
        collections.guest._create_guest_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            mapped_collection_id=self.mapped_collection_id,
            base_path=self.base_path,
        )
        # delete collection
        collections.guest._delete_guest_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
        )
        # check it no longer exists
        guest_collection = collections.utils.get_collection_from_name(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            filter_to_help="guest_collections",
        )
        self.assertEqual(len(guest_collection), 0)
        # recreate the guest collection for further testing
        collections.guest._create_guest_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            mapped_collection_id=self.mapped_collection_id,
            base_path=self.base_path,
        )

    def test_update_guest_collection(self):
        collections.guest._create_guest_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            mapped_collection_id=self.mapped_collection_id,
            base_path=self.base_path,
        )

        guest_collection = collections.utils.get_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            collection_id=None,
            filter_to_help="guest_collections",
        )
        self.assertEqual(
            guest_collection[0]["display_name"], self.guest_collection_name
        )
        # update collection with new display name
        collections.guest._update_guest_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            new_collection_name=self.guest_collection2_name,
            public=False,
        )

        # check if it is now it has a new display name
        guest_collection = collections.utils.get_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection2_name,
            collection_id=None,
            filter_to_help="guest_collections",
        )
        self.assertEqual(
            guest_collection[0]["display_name"], self.guest_collection2_name
        )
        # update collection to undo the change
        collections.guest._update_guest_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection2_name,
            new_collection_name=self.guest_collection_name,
            public=False,
        )

        # check if it is now the base path changed
        guest_collection = collections.utils.get_collection(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
            collection_id=None,
            filter_to_help="guest_collections",
        )
        self.assertEqual(
            guest_collection[0]["display_name"], self.guest_collection_name
        )

    @classmethod
    def tearDownClass(cls) -> None:
        collections.guest._delete_guest_collection(
            cls.gcs_client, cls.guest_collection_name
        )
        collections.guest._delete_guest_collection(
            cls.gcs_client, cls.guest_collection2_name
        )
        # If more tests are to be performed around collection creation/deletion and or role creation/deletion
        # A cooldown period is required so Globus does not get overloaded and shows this error
        # "Bearer", 403, "permission_denied", "None of your identities have been granted a role to access this resource"


class TestCollectionRoles(unittest.TestCase):
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

    def test_create_role_with_collection_name_and_user_identity(self):
        logger.info("Start test create role using collection_name and user_identity...")

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        role = collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

        self.assertEqual(role["role"], "activity_monitor")

    def test_create_role_with_collection_id_and_principal(self):
        logger.info("Start test create role using collection_id and principal...")

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        role = collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            principal_type="identity",
            role="activity_monitor",
        )

        self.assertEqual(role["role"], "activity_monitor")

    def test_create_role_with_collection_name_and_principal(self):
        logger.info("Start test create role using collection_name and principal...")

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        role = collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            principal_type="identity",
            role="activity_monitor",
        )

        self.assertEqual(role["role"], "activity_monitor")

    def test_create_role_with_collection_id_and_user_identity(self):
        logger.info("Start test create role using collection_id and user_identity...")

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        role = collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

        self.assertEqual(role["role"], "activity_monitor")

    def test_create_role_incorrect_gcs_client(self):
        logger.info("Start test create role with incorrect gcs client...")

        with self.assertRaises(Exception):
            collections.roles._create_role(
                current_gcs_client=None,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                principal_type="identity",
                role="activity_monitor",
            )

    def test_create_role_incorrect_auth_client(self):
        logger.info("Start test create role with incorrect auth client...")

        with self.assertRaises(Exception):
            collections.roles._create_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=None,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                principal_type="identity",
                role="activity_monitor",
            )

    def test_create_role_incorrect_collection_name_and_id(self):
        logger.info("Start test create role with incorrect collection name and id...")

        with self.assertRaises(ValueError):
            collections.roles._create_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=self.auth_client,
                collection_name=None,
                collection_id=None,
                user_identity=self.user_identity,
                principal_type="identity",
                role="activity_monitor",
            )

    def test_create_role_incorrect_user_identity_and_principal(self):
        logger.info(
            "Start test create role with incorrect user_identity and principal..."
        )

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        with self.assertRaises(Exception):
            collections.roles._create_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=None,
                principal=None,
                principal_type="identity",
                role="activity_monitor",
            )

        collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

    def test_create_role_incorrect_principal_type(self):
        logger.info("Start test create role with incorrect principal type...")

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        with self.assertRaises(ValueError):
            collections.roles._create_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                principal=self.user_uuid,
                principal_type="None",
                role="activity_monitor",
            )

        collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

    def test_create_role_incorrect_role(self):
        logger.info("Start test create role with incorrect role...")

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        with self.assertRaises(Exception):
            collections.roles._create_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                principal_type="identity",
                role=None,
            )

        collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

    def test_delete_role_with_collection_name_user_identity_and_role_title(self):
        logger.info(
            "Start test delete role using collection_name, user_identity and role title..."
        )

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 0)

        collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

    def test_delete_role_with_collection_id_principal_and_role_title(self):
        logger.info(
            "Start test delete role using collection_id, principal and role title..."
        )

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            role="activity_monitor",
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 0)

        collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

    def test_delete_role_with_collection_name_principal_and_role_title(self):
        logger.info(
            "Start test delete role using collection_name, principal and role title..."
        )

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            role="activity_monitor",
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 0)

        collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

    def test_delete_role_with_collection_id_user_identity_and_role_title(self):
        logger.info(
            "Start test delete role using collection_id, user_identity and role title..."
        )

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            role="activity_monitor",
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 0)

        collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

    def test_delete_role_with_role_id(self):
        logger.info("Start test delete role using role id...")

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )[0]

        collections.roles._delete_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            role_id=role["id"],
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 0)

        collections.roles._create_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            principal_type="identity",
            role="activity_monitor",
        )

    def test_delete_role_incorrect_gcs_client(self):
        logger.info("Start test delete role with incorrect gcs client...")

        with self.assertRaises(Exception):
            collections.roles._delete_role(
                current_gcs_client=None,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                role="activity_monitor",
            )

    def test_delete_role_incorrect_auth_client(self):
        logger.info("Start test delete role with incorrect auth client...")

        with self.assertRaises(Exception):
            collections.roles._delete_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=None,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                role="activity_monitor",
            )

    def test_delete_role_incorrect_collection_name_and_id(self):
        logger.info("Start test delete role with incorrect collection name and id...")

        with self.assertRaises(ValueError):
            collections.roles._delete_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=self.auth_client,
                collection_name=None,
                collection_id=None,
                user_identity=self.user_identity,
                role="activity_monitor",
            )

    def test_delete_role_incorrect_user_identity_and_principal_role_title_and_id(self):
        logger.info(
            "Start test delete role with incorrect user_identity, principal, role title and id..."
        )

        with self.assertRaises(ValueError):
            collections.roles._delete_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=None,
                principal=None,
                role=None,
                role_id=None,
            )

    def test_get_role_with_collection_name_user_identity_and_role_title(self):
        logger.info(
            "Start test get role using collection_name, user_identity and role title..."
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 1)
        self.assertEqual(role[0]["role"], "activity_monitor")

    def test_get_role_with_collection_id_principal_and_role_title(self):
        logger.info(
            "Start test get role using collection_id, principal and role title..."
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            principal=self.user_uuid,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 1)
        self.assertEqual(role[0]["role"], "activity_monitor")

    def test_get_role_with_collection_name_principal_and_role_title(self):
        logger.info(
            "Start test get role using collection_name, principal and role title..."
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            principal=self.user_uuid,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 1)
        self.assertEqual(role[0]["role"], "activity_monitor")

    def test_get_role_with_collection_id_user_identity_and_role_title(self):
        logger.info(
            "Start test get role using collection_id, user_identity and role title..."
        )

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_id=self.guest_collection["id"],
            user_identity=self.user_identity,
            role="activity_monitor",
        )
        self.assertEqual(len(role), 1)
        self.assertEqual(role[0]["role"], "activity_monitor")

    def test_get_role_with_role_id(self):
        logger.info("Start test get role using role id...")

        grole = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            collection_name=self.guest_collection_name,
            user_identity=self.user_identity,
            role="activity_monitor",
        )[0]

        role = collections.roles._get_role(
            current_gcs_client=self.gcs_client,
            current_auth_client=self.auth_client,
            role_id=grole["id"],
        )
        self.assertEqual(len(role), 1)
        self.assertEqual(role[0]["role"], "activity_monitor")

    def test_get_role_incorrect_gcs_client(self):
        logger.info("Start test get role with incorrect gcs client...")

        with self.assertRaises(Exception):
            collections.roles._get_role(
                current_gcs_client=None,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                role="activity_monitor",
            )

    def test_get_role_incorrect_auth_client(self):
        logger.info("Start test get role with incorrect auth client...")

        with self.assertRaises(Exception):
            collections.roles._get_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=None,
                collection_name=self.guest_collection_name,
                user_identity=self.user_identity,
                role="activity_monitor",
            )

    def test_get_role_incorrect_collection_name_and_id(self):
        logger.info("Start test get role with incorrect collection name and id...")

        with self.assertRaises(ValueError):
            collections.roles._get_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=self.auth_client,
                collection_name=None,
                collection_id=None,
                user_identity=self.user_identity,
                role="activity_monitor",
            )

    def test_get_role_incorrect_user_identity_and_principal_role_title_and_id(self):
        logger.info(
            "Start test get role with incorrect user_identity, principal, role title and id..."
        )

        with self.assertRaises(ValueError):
            collections.roles._get_role(
                current_gcs_client=self.gcs_client,
                current_auth_client=self.auth_client,
                collection_name=self.guest_collection_name,
                user_identity=None,
                principal=None,
                role=None,
                role_id=None,
            )

    def test_role_list_with_collection_name(self):
        logger.info("Start test get role list using collection_name...")

        role_list = collections.roles._role_list(
            current_gcs_client=self.gcs_client,
            collection_name=self.guest_collection_name,
        )
        self.assertEqual(len(role_list), 2)

    def test_role_list_with_collection_id(self):
        logger.info("Start test get role list using collection_id...")

        role_list = collections.roles._role_list(
            current_gcs_client=self.gcs_client,
            collection_id=self.guest_collection["id"],
        )
        self.assertEqual(len(role_list), 2)

    def test_role_list_incorrect_gcs_client(self):
        logger.info("Start test get role list with incorrect gcs client...")

        with self.assertRaises(Exception):
            collections.roles._role_list(
                current_gcs_client=None,
                collection_name=self.guest_collection_name,
            )

    def test_role_list_incorrect_collection_name_and_id(self):
        logger.info(
            "Start test get role list with incorrect collection_name and collection_id..."
        )

        with self.assertRaises(ValueError):
            collections.roles._role_list(
                current_gcs_client=self.gcs_client,
                collection_name=None,
                collection_id=None,
            )

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
