"""Universal projection record (SHADOW v2): the immutable, append-only observation every engine writes."""
from nfl_edge.projection.record import (  # noqa: F401
    ProjectionRecord, SCHEMA_VERSION, PROSPECTIVE_FROZEN, HISTORICAL_RESEARCH, record_id, content_hash,
    SUPPORT_STATES,
)
from nfl_edge.projection.store import ProjectionStore, ProjectionConflict, read_projections  # noqa: F401
