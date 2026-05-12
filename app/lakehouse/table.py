import time
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class IcebergPartitionField(BaseModel):
    source_id: int
    field_id: int
    name: str
    transform: str = "identity"

class IcebergSchema(BaseModel):
    schema_id: int = 0
    fields: List[Dict[str, Any]] = Field(default_factory=list)

class IcebergTableMetadata(BaseModel):
    """Logical container anchoring Iceberg V2 metadata definitions."""
    format_version: int = 2
    table_uuid: str
    location: str
    
    last_sequence_number: int = 0
    last_updated_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    
    schemas: List[IcebergSchema] = Field(default_factory=list)
    current_schema_id: int = 0
    
    partition_specs: List[List[IcebergPartitionField]] = Field(default_factory=list)
    default_spec_id: int = 0
