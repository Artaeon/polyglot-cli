"""Application context — holds all engines and session state."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from db.database import Database
from engines.builder import SentenceBuilderEngine
from engines.cia_drills import CIADrillEngine
from engines.cloze import ClozeEngine
from engines.cluster import ClusterEngine
from engines.conjugation import ConjugationEngine
from engines.gamification import GamificationEngine
from engines.palace import PalaceEngine
from engines.planner import PlannerEngine
from engines.quiz import QuizEngine
from engines.sentence import SentenceEngine
from engines.speed_learn import SpeedLearnEngine

if TYPE_CHECKING:
    from engines.adaptive import AdaptiveDifficultyEngine
    from engines.custom_vocab import CustomVocabEngine
    from engines.daily_challenge import DailyChallengeEngine
    from engines.statistics import StatisticsEngine

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Mutable session tracking."""

    start: float = 0
    words_learned: int = 0
    words_reviewed: int = 0
    languages: set = field(default_factory=set)


class AppContext:
    """Holds the database, all engines, and session state."""

    def __init__(self, db: Optional[Database] = None) -> None:
        self.db: Optional[Database] = db
        self.cluster_engine: Optional[ClusterEngine] = None
        self.quiz_engine: Optional[QuizEngine] = None
        self.palace_engine: Optional[PalaceEngine] = None
        self.planner: Optional[PlannerEngine] = None
        self.sentence_engine: Optional[SentenceEngine] = None
        self.gamification: Optional[GamificationEngine] = None
        self.cloze_engine: Optional[ClozeEngine] = None
        self.conjugation_engine: Optional[ConjugationEngine] = None
        self.builder_engine: Optional[SentenceBuilderEngine] = None
        self.speed_engine: Optional[SpeedLearnEngine] = None
        self.cia_engine: Optional[CIADrillEngine] = None
        self.daily_challenge_engine: Optional[DailyChallengeEngine] = None
        self.custom_vocab_engine: Optional[CustomVocabEngine] = None
        self.statistics_engine: Optional[StatisticsEngine] = None
        self.adaptive_engine: Optional[AdaptiveDifficultyEngine] = None

        self.session = SessionState()

    def init(self) -> None:
        """Initialize database and all engines."""
        logger.info("Initializing application")
        if self.db is None:
            self.db = Database()
        self.db.init_schema()

        self._init_core_engines()

        # Phase 2 engines (lazy — imported on demand)
        self._init_phase2_engines()
        logger.info("Application initialized")

    def _init_core_engines(self) -> None:
        """Initialize core engines used throughout the app."""
        self.cluster_engine = ClusterEngine(self.db)
        self.quiz_engine = QuizEngine(self.db, self.cluster_engine)
        self.palace_engine = PalaceEngine(self.db, self.cluster_engine)
        self.planner = PlannerEngine(self.db, self.cluster_engine)
        self.sentence_engine = SentenceEngine(self.db)
        self.gamification = GamificationEngine(self.db)
        self.cloze_engine = ClozeEngine(self.db, self.sentence_engine)
        self.conjugation_engine = ConjugationEngine(self.db)
        self.builder_engine = SentenceBuilderEngine(self.db, self.sentence_engine)
        self.speed_engine = SpeedLearnEngine(self.db, self.cluster_engine)
        self.cia_engine = CIADrillEngine(self.db, self.cluster_engine, self.quiz_engine)

    def _init_phase2_engines(self) -> None:
        """Initialize new Phase 2 engines."""
        from engines.daily_challenge import DailyChallengeEngine
        from engines.custom_vocab import CustomVocabEngine
        from engines.statistics import StatisticsEngine
        from engines.adaptive import AdaptiveDifficultyEngine

        self.daily_challenge_engine = DailyChallengeEngine(self.db, self.gamification)
        self.custom_vocab_engine = CustomVocabEngine(self.db)
        self.statistics_engine = StatisticsEngine(self.db)
        self.adaptive_engine = AdaptiveDifficultyEngine(self.db)

    def start_session(self) -> None:
        """Start tracking a learning session."""
        self.session = SessionState(start=time.time())

    def end_session(self, session_type: str = "mixed") -> None:
        """End and log a learning session."""
        if self.session.start == 0:
            return
        duration = int((time.time() - self.session.start) / 60)
        if duration > 0 or self.session.words_learned > 0 or self.session.words_reviewed > 0:
            self.db.log_session(
                session_type=session_type,
                duration=max(duration, 1),
                words_learned=self.session.words_learned,
                words_reviewed=self.session.words_reviewed,
                languages=list(self.session.languages),
            )
        self.session.start = 0
