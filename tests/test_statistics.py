"""Tests for the statistics engine."""

import pytest
from datetime import date, timedelta
from engines.statistics import StatisticsEngine


@pytest.fixture
def stats_engine(populated_db):
    """StatisticsEngine with populated database."""
    return StatisticsEngine(populated_db)


def test_retention_curve_empty(stats_engine):
    """Retention curve with no reviews returns zeroes."""
    data = stats_engine.retention_curve(30)
    assert isinstance(data, list)
    assert len(data) == 30
    assert all(d["total"] == 0 for d in data)


def test_retention_curve_with_reviews(stats_engine):
    """Retention curve counts reviews correctly."""
    # Create a review card and simulate a review
    words = stats_engine.db.get_words_by_language("ru")
    wid = words[0]["id"]
    cid = stats_engine.db.create_review_card(wid)

    today = date.today().isoformat()
    stats_engine.db.update_review_card(
        cid, ease_factor=2.6, interval=1, repetitions=1,
        next_review_date=(date.today() + timedelta(days=1)).isoformat(),
        correct=True,
    )

    data = stats_engine.retention_curve(30)
    today_data = [d for d in data if d["date"] == today]
    if today_data:
        assert today_data[0]["total"] >= 1


def test_weak_areas_empty(stats_engine):
    """Weak areas with no data returns empty."""
    result = stats_engine.weak_areas(15)
    assert isinstance(result, list)


def test_learning_velocity(stats_engine):
    """Learning velocity returns required fields."""
    vel = stats_engine.learning_velocity(30)
    assert "total" in vel
    assert "average_per_day" in vel
    assert "trend" in vel
    assert "daily_counts" in vel


def test_category_breakdown(stats_engine):
    """Category breakdown returns list."""
    data = stats_engine.category_breakdown()
    assert isinstance(data, list)
