import time
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class DataManifest(BaseModel):
    """Central ledger anchoring file provenance within the Medallion layers."""
    
    layer: str = Field(..., description="bronze, silver, gold")
    table_name: str
    
    partition_key: str = "1970-01-01"
    snapshot_ts: float = Field(default_factory=time.time)
    
    schema_version: str = "1.0.0"
    record_count: int = 0
    
    source_feed: str = "unknown"
    lineage_parent_ids: list[str] = Field(default_factory=list)
    
    is_incremental: bool = False
    
    audit_checksum: Optional[str] = None
