"""
Service Layer Package

This package contains all service layer components for the Total Bankroll application.
Services encapsulate business logic and provide a clean interface between routes and models.

Architecture:
    Routes (Presentation) → Services (Business Logic) → Models (Data)

Available Services:
    - BankrollService: Manages bankroll calculations and history
    - RecommendationService: Generates stake recommendations
    - AchievementService: Handles user achievements and badges
    - CurrencyService: Manages currency conversions and rates

Usage:
    from ..services import BankrollService
    
    service = BankrollService()
    total = service.calculate_total_bankroll(user_id=1)
"""

from .base import BaseService
from .bankroll_service import BankrollService
from .recommendation_service import RecommendationService
from .achievement_service import AchievementService
from .currency_service import CurrencyService

__all__ = [
    'BaseService',
    'BankrollService',
    'RecommendationService',
    'AchievementService',
    'CurrencyService',
]
