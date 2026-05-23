# Import all models so Alembic autogenerate sees them all
from app.models.base import Base  # noqa: F401
from app.models.users import User, UserRole  # noqa: F401  # OAuthAccount added in 04-02
from app.models.parties import Party  # noqa: F401
from app.models.politicians import Politician, PoliticianPartyMembership, PoliticianLevel  # noqa: F401
from app.models.elections import Election, ElectionLevel  # noqa: F401
from app.models.promises import Promise, PromiseElectionLink, ModerationStatus, ResolvedStatus  # noqa: F401
from app.models.evidence import Evidence, EvidenceType  # noqa: F401
from app.models.votes import Vote, VoteHistory, VoteStatus  # noqa: F401
from app.models.stats_cache import StatsCache, AppSettings  # noqa: F401
