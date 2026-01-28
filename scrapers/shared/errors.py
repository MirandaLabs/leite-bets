"""Custom exceptions for scrapers."""


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class CollectorError(ScraperError):
    """Exception raised during data collection."""
    pass


class ParserError(ScraperError):
    """Exception raised during data parsing."""
    pass
