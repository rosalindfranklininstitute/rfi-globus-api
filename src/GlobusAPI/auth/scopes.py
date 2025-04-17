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

import typing

from globus_sdk._types import ScopeCollectionType
from globus_sdk.scopes import GCSCollectionScopeBuilder, GCSEndpointScopeBuilder

from ..logging.logging import get_logger

logger = get_logger()


def get_collections_scope(
    endpoint_id: str, collection_ids: typing.List[str]
) -> ScopeCollectionType:
    """Create a scope object with data access to the collections of an endpoint.

    Args:
        endpoint_id (str, required): String endpoint id for the collections.
        collection_ids (typing.List[str], required): List of string collection ids within the endpoint.

    Returns:
        A scope (ScopeCollectionType)
    """

    logger.info("Create scopes for accessing collection data...")
    logger.debug(f"  {endpoint_id=}")
    logger.debug(f"  {collection_ids=}")

    # Build scope to manage given endpoint collections
    scope = GCSEndpointScopeBuilder(endpoint_id).make_mutable("manage_collections")

    # Add a data access scope for each collection within the endpoint
    for collection_id in collection_ids:
        scope.add_dependency(GCSCollectionScopeBuilder(collection_id).data_access)

    return scope
