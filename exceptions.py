"""Custom exceptions for PolyglotCLI."""

from __future__ import annotations


class PolyglotError(Exception):
    """Base exception for PolyglotCLI."""


class DataLoadError(PolyglotError):
    """Error loading data files."""


class NoDataError(PolyglotError):
    """No data available for the requested operation."""
