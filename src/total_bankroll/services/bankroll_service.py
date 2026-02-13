"""
Bankroll Service

Handles all bankroll-related business logic including:
- Total bankroll calculation
- Site and asset balance management
- Deposit and withdrawal tracking
- Bankroll history
- Profit/loss calculations

This service encapsulates the core financial logic of the application.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import func
from .base import BaseService
from ..models import (
    User, Sites, Assets, Deposits, Drawings,
    SiteHistory, AssetHistory, Currency, db
)
from ..extensions import cache


class BankrollService(BaseService):
    """
    Service for managing bankroll operations.
    
    This service handles all calculations and operations related to
    a user's total bankroll, including sites, assets, deposits, and withdrawals.
    """
    
    def __init__(self):
        """Initialize the BankrollService."""
        super().__init__()
    
    def _invalidate_cache(self, user_id: int):
        """
        Invalidate cached bankroll data for a user.
        
        Called after any mutation (add/update/delete) to ensure fresh data.
        
        Args:
            user_id: The user's ID
        """
        cache.delete(f'bankroll_total_{user_id}')
        cache.delete(f'bankroll_breakdown_{user_id}')
        self._log_debug(f"Invalidated bankroll cache for user {user_id}")
    
    def calculate_total_bankroll(self, user_id: int, currency_code: str = 'USD') -> Decimal:
        """
        Calculate the total bankroll for a user in the specified currency.
        
        Cached for 5 minutes to improve dashboard performance.
        
        Args:
            user_id: The user's ID
            currency_code: Currency code for the result (default: USD)
        
        Returns:
            Decimal: Total bankroll amount
        
        Example:
            >>> service = BankrollService()
            >>> total = service.calculate_total_bankroll(user_id=1)
            >>> print(f"Total: ${total}")
        """
        # Check cache first
        cache_key = f'bankroll_total_{user_id}'
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        self._log_debug(f"Calculating total bankroll for user {user_id}")
        
        data = self.get_bankroll_breakdown(user_id)
        result = data['total_bankroll']
        
        # Cache the result
        cache.set(cache_key, result, timeout=300)
        return result
    
    def get_bankroll_breakdown(self, user_id: int) -> Dict[str, Decimal]:
        """
        Get complete bankroll breakdown for a user.
        
        Calculates all key financial metrics with a single, efficient database query.
        Uses conditional aggregation to sum up different types of records
        (poker sites, assets, deposits, withdrawals) in one pass.
        
        Args:
            user_id: The user's ID
        
        Returns:
            Dictionary containing:
                - current_poker_total: Current poker site balances
                - previous_poker_total: Previous poker site balances
                - current_asset_total: Current asset values
                - previous_asset_total: Previous asset values
                - total_deposits: Total deposits made
                - total_withdrawals: Total withdrawals made
                - total_bankroll: Total current bankroll
                - total_profit: Total profit/loss
        
        Example:
            >>> service = BankrollService()
            >>> data = service.get_bankroll_breakdown(user_id=1)
            >>> print(f"Profit: ${data['total_profit']}")
        """
        # Check cache first
        cache_key = f'bankroll_breakdown_{user_id}'
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        self._log_debug(f"Getting bankroll breakdown for user {user_id}")
        
        # Subquery to rank site history records for each site
        site_history_ranked = db.session.query(
            SiteHistory,
            func.row_number().over(
                partition_by=SiteHistory.site_id,
                order_by=SiteHistory.recorded_at.desc()
            ).label('rn')
        ).filter(SiteHistory.user_id == user_id).subquery()

        # Subquery to rank asset history records for each asset
        asset_history_ranked = db.session.query(
            AssetHistory,
            func.row_number().over(
                partition_by=AssetHistory.asset_id,
                order_by=AssetHistory.recorded_at.desc()
            ).label('rn')
        ).filter(AssetHistory.user_id == user_id).subquery()

        # Calculate current and previous poker totals
        current_poker_total = db.session.query(
            func.sum(site_history_ranked.c.amount / Currency.rate)
        ).select_from(site_history_ranked)\
            .join(Currency, site_history_ranked.c.currency == Currency.code)\
            .filter(site_history_ranked.c.rn == 1).scalar() or Decimal('0.0')
        
        previous_poker_total = db.session.query(
            func.sum(site_history_ranked.c.amount / Currency.rate)
        ).select_from(site_history_ranked)\
            .join(Currency, site_history_ranked.c.currency == Currency.code)\
            .filter(site_history_ranked.c.rn == 2).scalar() or Decimal('0.0')
        
        # Calculate current and previous asset totals
        current_asset_total = db.session.query(
            func.sum(asset_history_ranked.c.amount / Currency.rate)
        ).select_from(asset_history_ranked)\
            .join(Currency, asset_history_ranked.c.currency == Currency.code)\
            .filter(asset_history_ranked.c.rn == 1).scalar() or Decimal('0.0')
        
        previous_asset_total = db.session.query(
            func.sum(asset_history_ranked.c.amount / Currency.rate)
        ).select_from(asset_history_ranked)\
            .join(Currency, asset_history_ranked.c.currency == Currency.code)\
            .filter(asset_history_ranked.c.rn == 2).scalar() or Decimal('0.0')

        # Calculate deposit and withdrawal totals
        total_deposits = db.session.query(
            func.sum(Deposits.amount / Currency.rate)
        ).join(Currency, Deposits.currency == Currency.code)\
            .filter(Deposits.user_id == user_id)\
            .scalar() or Decimal('0.0')

        total_withdrawals = db.session.query(
            func.sum(Drawings.amount / Currency.rate)
        ).join(Currency, Drawings.currency == Currency.code)\
            .filter(Drawings.user_id == user_id)\
            .scalar() or Decimal('0.0')

        # Calculate derived metrics
        total_bankroll = current_poker_total + current_asset_total
        total_profit = total_bankroll - total_deposits + total_withdrawals

        result = {
            'current_poker_total': current_poker_total,
            'previous_poker_total': previous_poker_total,
            'current_asset_total': current_asset_total,
            'previous_asset_total': previous_asset_total,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_bankroll': total_bankroll,
            'total_profit': total_profit,
        }
        
        # Cache the result
        cache.set(cache_key, result, timeout=300)
        return result
    
    def get_site_balances(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all site balances for a user with their current values.
        
        Args:
            user_id: The user's ID
        
        Returns:
            List of dictionaries containing site information and balances
        
        Example:
            >>> service = BankrollService()
            >>> balances = service.get_site_balances(user_id=1)
            >>> for site in balances:
            ...     print(f"{site['name']}: ${site['balance']}")
        """
        self._log_debug(f"Getting site balances for user {user_id}")
        
        # Get sites with their latest history entry
        sites = db.session.query(Sites).filter(Sites.user_id == user_id)\
            .order_by(Sites.display_order).all()
        
        result = []
        for site in sites:
            # Get latest history entry for this site
            latest_history = db.session.query(SiteHistory)\
                .filter(SiteHistory.site_id == site.id)\
                .order_by(SiteHistory.recorded_at.desc())\
                .first()
            
            if latest_history:
                # Convert to USD
                currency_rate = db.session.query(Currency.rate)\
                    .filter(Currency.code == latest_history.currency)\
                    .scalar() or Decimal('1.0')
                
                balance_usd = latest_history.amount / currency_rate
                
                result.append({
                    'id': site.id,
                    'name': site.name,
                    'balance': balance_usd,
                    'currency': latest_history.currency,
                    'original_amount': latest_history.amount,
                    'last_updated': latest_history.recorded_at,
                })
        
        return result
    
    def get_asset_values(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all asset values for a user with their current values.
        
        Args:
            user_id: The user's ID
        
        Returns:
            List of dictionaries containing asset information and values
        """
        self._log_debug(f"Getting asset values for user {user_id}")
        
        # Get assets with their latest history entry
        assets = db.session.query(Assets).filter(Assets.user_id == user_id)\
            .order_by(Assets.display_order).all()
        
        result = []
        for asset in assets:
            # Get latest history entry for this asset
            latest_history = db.session.query(AssetHistory)\
                .filter(AssetHistory.asset_id == asset.id)\
                .order_by(AssetHistory.recorded_at.desc())\
                .first()
            
            if latest_history:
                # Convert to USD
                currency_rate = db.session.query(Currency.rate)\
                    .filter(Currency.code == latest_history.currency)\
                    .scalar() or Decimal('1.0')
                
                value_usd = latest_history.amount / currency_rate
                
                result.append({
                    'id': asset.id,
                    'name': asset.name,
                    'value': value_usd,
                    'currency': latest_history.currency,
                    'original_amount': latest_history.amount,
                    'last_updated': latest_history.recorded_at,
                })
        
        return result
    
    def calculate_profit(self, user_id: int, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> Decimal:
        """
        Calculate profit/loss for a user over a date range.
        
        Formula: Profit = (Current Bankroll + Total Withdrawals) - Total Deposits
        
        Args:
            user_id: The user's ID
            start_date: Start date for calculation (optional)
            end_date: End date for calculation (optional)
        
        Returns:
            Decimal: Profit amount (negative for loss)
        """
        self._log_debug(f"Calculating profit for user {user_id}")
        
        data = self.get_bankroll_breakdown(user_id)
        return data['total_profit']
    
    def add_site(self, user_id: int, site_data: Dict[str, Any]) -> Optional[Sites]:
        """
        Add a new poker site for a user.
        
        Args:
            user_id: The user's ID
            site_data: Dictionary with 'name' and optional 'display_order'
        
        Returns:
            Sites: The created site object, or None if failed
        """
        self._log_info(f"Adding site for user {user_id}: {site_data.get('name')}")
        
        try:
            # Get next display order if not specified
            if 'display_order' not in site_data:
                max_order = db.session.query(func.max(Sites.display_order))\
                    .filter(Sites.user_id == user_id).scalar() or 0
                site_data['display_order'] = max_order + 1
            
            site = Sites(
                name=site_data['name'],
                user_id=user_id,
                display_order=site_data['display_order']
            )
            
            self.add(site)
            if self.commit():
                self._invalidate_cache(user_id)
                return site
            return None
        except Exception as e:
            self._log_error(f"Failed to add site: {str(e)}")
            self.rollback()
            return None
    
    def update_site(self, site_id: int, site_data: Dict[str, Any]) -> bool:
        """
        Update a poker site's information.
        
        Args:
            site_id: The site's ID
            site_data: Dictionary with fields to update ('name', 'display_order')
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._log_info(f"Updating site {site_id}")
        
        try:
            site = db.session.query(Sites).filter(Sites.id == site_id).first()
            if not site:
                self._log_error(f"Site {site_id} not found")
                return False
            
            if 'name' in site_data:
                site.name = site_data['name']
            if 'display_order' in site_data:
                site.display_order = site_data['display_order']
            
            if self.commit():
                self._invalidate_cache(site.user_id)
                return True
            return False
        except Exception as e:
            self._log_error(f"Failed to update site: {str(e)}")
            self.rollback()
            return False
    
    def delete_site(self, site_id: int) -> bool:
        """
        Delete a poker site and its history.
        
        Args:
            site_id: The site's ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._log_info(f"Deleting site {site_id}")
        
        try:
            site = db.session.query(Sites).filter(Sites.id == site_id).first()
            if not site:
                self._log_error(f"Site {site_id} not found")
                return False
            
            user_id = site.user_id
            
            # Delete associated history first
            db.session.query(SiteHistory)\
                .filter(SiteHistory.site_id == site_id).delete()
            
            # Delete the site
            self.delete(site)
            if self.commit():
                self._invalidate_cache(user_id)
                return True
            return False
        except Exception as e:
            self._log_error(f"Failed to delete site: {str(e)}")
            self.rollback()
            return False
    
    def add_asset(self, user_id: int, asset_data: Dict[str, Any]) -> Optional[Assets]:
        """
        Add a new asset for a user.
        
        Args:
            user_id: The user's ID
            asset_data: Dictionary with 'name' and optional 'display_order'
        
        Returns:
            Assets: The created asset object, or None if failed
        """
        self._log_info(f"Adding asset for user {user_id}: {asset_data.get('name')}")
        
        try:
            # Get next display order if not specified
            if 'display_order' not in asset_data:
                max_order = db.session.query(func.max(Assets.display_order))\
                    .filter(Assets.user_id == user_id).scalar() or 0
                asset_data['display_order'] = max_order + 1
            
            asset = Assets(
                name=asset_data['name'],
                user_id=user_id,
                display_order=asset_data['display_order']
            )
            
            self.add(asset)
            if self.commit():
                self._invalidate_cache(user_id)
                return asset
            return None
        except Exception as e:
            self._log_error(f"Failed to add asset: {str(e)}")
            self.rollback()
            return None
    
    def update_asset(self, asset_id: int, asset_data: Dict[str, Any]) -> bool:
        """
        Update an asset's information.
        
        Args:
            asset_id: The asset's ID
            asset_data: Dictionary with fields to update ('name', 'display_order')
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._log_info(f"Updating asset {asset_id}")
        
        try:
            asset = db.session.query(Assets).filter(Assets.id == asset_id).first()
            if not asset:
                self._log_error(f"Asset {asset_id} not found")
                return False
            
            if 'name' in asset_data:
                asset.name = asset_data['name']
            if 'display_order' in asset_data:
                asset.display_order = asset_data['display_order']
            
            if self.commit():
                self._invalidate_cache(asset.user_id)
                return True
            return False
        except Exception as e:
            self._log_error(f"Failed to update asset: {str(e)}")
            self.rollback()
            return False
    
    def delete_asset(self, asset_id: int) -> bool:
        """
        Delete an asset and its history.
        
        Args:
            asset_id: The asset's ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._log_info(f"Deleting asset {asset_id}")
        
        try:
            asset = db.session.query(Assets).filter(Assets.id == asset_id).first()
            if not asset:
                self._log_error(f"Asset {asset_id} not found")
                return False
            
            user_id = asset.user_id
            
            # Delete associated history first
            db.session.query(AssetHistory)\
                .filter(AssetHistory.asset_id == asset_id).delete()
            
            # Delete the asset
            self.delete(asset)
            if self.commit():
                self._invalidate_cache(user_id)
                return True
            return False
        except Exception as e:
            self._log_error(f"Failed to delete asset: {str(e)}")
            self.rollback()
            return False
    
    def record_deposit(self, user_id: int, amount: Decimal, 
                      currency: str, date: datetime) -> bool:
        """
        Record a deposit transaction.
        
        Args:
            user_id: The user's ID
            amount: Deposit amount
            currency: Currency code
            date: Transaction date
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._log_info(f"Recording deposit for user {user_id}: {amount} {currency}")
        
        try:
            deposit = Deposits(
                user_id=user_id,
                amount=amount,
                currency=currency,
                date=date,
                last_updated=datetime.now(UTC)
            )
            
            self.add(deposit)
            if self.commit():
                self._invalidate_cache(user_id)
                return True
            return False
        except Exception as e:
            self._log_error(f"Failed to record deposit: {str(e)}")
            self.rollback()
            return False
    
    def record_withdrawal(self, user_id: int, amount: Decimal,
                         currency: str, date: datetime) -> bool:
        """
        Record a withdrawal transaction.
        
        Args:
            user_id: The user's ID
            amount: Withdrawal amount
            currency: Currency code
            date: Transaction date
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._log_info(f"Recording withdrawal for user {user_id}: {amount} {currency}")
        
        try:
            withdrawal = Drawings(
                user_id=user_id,
                amount=amount,
                currency=currency,
                date=date,
                last_updated=datetime.now(UTC)
            )
            
            self.add(withdrawal)
            if self.commit():
                self._invalidate_cache(user_id)
                return True
            return False
        except Exception as e:
            self._log_error(f"Failed to record withdrawal: {str(e)}")
            self.rollback()
            return False
