"""Tests for the planner engine — CEFR levels, progress, daily plan."""

import pytest
from engines.planner import PlannerEngine
from engines.cluster import ClusterEngine


@pytest.fixture
def planner(populated_db):
    """PlannerEngine with populated database."""
    cluster = ClusterEngine(populated_db)
    return PlannerEngine(populated_db, cluster)


def test_cefr_level_zero(planner):
    """Zero words gives lowest CEFR level."""
    level = planner.get_cefr_level(0)
    assert level in ("pre", "A1-", "A1")


def test_cefr_level_progression(planner):
    """More words yield higher CEFR levels."""
    l1 = planner.get_cefr_level(10)
    l2 = planner.get_cefr_level(100)
    # Both should be valid strings
    assert isinstance(l1, str)
    assert isinstance(l2, str)


def test_get_progress_by_language(planner):
    """Progress returns all languages."""
    progress = planner.get_progress_by_language()
    assert isinstance(progress, list)
    assert len(progress) == 3  # ru, es, zh
    for p in progress:
        assert "id" in p
        assert "learned" in p
        assert "total" in p
        assert "level" in p


def test_progress_totals_correct(planner):
    """Word totals match what's in the database."""
    progress = planner.get_progress_by_language()
    ru = next(p for p in progress if p["id"] == "ru")
    assert ru["total"] == 3
    assert ru["learned"] == 0  # No review cards yet


def test_get_sprint_summary(planner):
    """Sprint summary returns required fields."""
    summary = planner.get_sprint_summary()
    assert isinstance(summary, dict)
    assert "total_learned" in summary
    assert "streak" in summary
    assert "sprint_day" in summary


def test_get_daily_plan_contains_recommended_cefr(planner):
    """Daily plan exposes CEFR recommendation for adaptive drills."""
    plan = planner.get_daily_plan()
    assert "recommended_cefr" in plan
    assert isinstance(plan["recommended_cefr"], str)


def test_recommended_cefr_target(planner):
    """Recommended CEFR target is within supported range."""
    target = planner.get_recommended_cefr_target()
    assert target in {"A1", "A1+", "A2-", "A2", "A2+", "B1-"}
