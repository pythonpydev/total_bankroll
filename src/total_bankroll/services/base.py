"""
Base Service Class

This module provides the base class for all service layer components.
The service layer encapsulates business logic and provides a clean interface
between the presentation layer (routes) and the data layer (models).

Service Layer Pattern Benefits:
- Separation of Concerns: Business logic separate from presentation
- Reusability: Services can be used by multiple routes or other services
- Testability: Easier to unit test business logic in isolation
- Maintainability: Changes to business logic don't require route changes

Usage:
    from .base import BaseService
    
    class MyService(BaseService):
        def my_business_logic(self):
            # Business logic here
            pass
"""

from typing import Optional, Any, Dict, List
from flask import current_app
from ..models import db


class BaseService:
    """
    Base class for all service layer components.
    
    Provides common functionality for database operations, logging,
    and error handling that all services can inherit.
    """
    
    def __init__(self):
        """Initialize the service."""
        self.db = db
        self.logger = current_app.logger if current_app else None
    
    def _log_info(self, message: str) -> None:
        """Log an info message."""
        if self.logger:
            self.logger.info(f"[{self.__class__.__name__}] {message}")
    
    def _log_error(self, message: str) -> None:
        """Log an error message."""
        if self.logger:
            self.logger.error(f"[{self.__class__.__name__}] {message}")
    
    def _log_debug(self, message: str) -> None:
        """Log a debug message."""
        if self.logger:
            self.logger.debug(f"[{self.__class__.__name__}] {message}")
    
    def commit(self) -> bool:
        """
        Commit database changes.
        
        Returns:
            bool: True if commit successful, False otherwise
        """
        try:
            self.db.session.commit()
            return True
        except Exception as e:
            self._log_error(f"Commit failed: {str(e)}")
            self.db.session.rollback()
            return False
    
    def rollback(self) -> None:
        """Rollback database changes."""
        self.db.session.rollback()
        self._log_debug("Database transaction rolled back")
    
    def add(self, instance: Any) -> None:
        """
        Add an instance to the database session.
        
        Args:
            instance: Model instance to add
        """
        self.db.session.add(instance)
        self._log_debug(f"Added {instance.__class__.__name__} to session")
    
    def delete(self, instance: Any) -> None:
        """
        Delete an instance from the database.
        
        Args:
            instance: Model instance to delete
        """
        self.db.session.delete(instance)
        self._log_debug(f"Marked {instance.__class__.__name__} for deletion")
    
    def flush(self) -> None:
        """Flush pending changes to the database."""
        self.db.session.flush()
        self._log_debug("Flushed database session")
