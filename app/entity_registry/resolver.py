from typing import Optional, Dict
from uuid import UUID
from app.core.identity.generator import IdentityCore
from app.schemas.base import ProviderSource

class EntityResolver:
    """Definitive operational clearinghouse managing object convergence logic."""
    
    def __init__(self):
        self._internal_crosswalk: Dict[str, UUID] = {}

    def resolve_player(self, external_id: str, source: ProviderSource) -> UUID:
        """Determines final stable pointer for any inbound provider data snippet."""
        key = f"{source.value}:{external_id}"
        if key not in self._internal_crosswalk:
            # Generate absolute deterministic internal anchor
            self._internal_crosswalk[key] = IdentityCore.generate_player_uuid(external_id, source)
        return self._internal_crosswalk[key]

    def register_alias(self, canonical_uuid: UUID, alias_id: str, alias_source: ProviderSource):
        """Forces binding between multiple source IDs mapping them into same internal cluster."""
        key = f"{alias_source.value}:{alias_id}"
        self._internal_crosswalk[key] = canonical_uuid
