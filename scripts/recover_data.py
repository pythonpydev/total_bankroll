"""
Recovery script: Restores data from MySQL binary logs.
Recovered from binlogs 250, 252, 253.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from src.total_bankroll import create_app
from src.total_bankroll.models import db, User, Sites, Assets, Deposits, Drawings, SiteHistory, AssetHistory, Currency
from datetime import datetime

app = create_app()

# --- Site names: from test_data.csv where IDs overlap, otherwise "Unknown" ---
# test_data.csv had: 5=Party Poker, 6=Gg, 7=Party Poker, 8=Party Poker,
#   9=888, 10=888, 11=888, 12=Party Poker, 13=Pokerstars, 14=Pokerstars, 15=Pokerstars
SITE_NAMES = {
    6: "Gg",
    7: "Party Poker",
    8: "Party Poker",
    13: "Pokerstars",
}

# test_data.csv had: 1=Silver Coins, 2=Crypto, 3=Gold, 4=Gold, 5=Crypto, 6=Crypto, 7=Silver Coins
ASSET_NAMES = {
    7: "Silver Coins",
    8: "Unknown Asset 8",
    9: "Unknown Asset 9",
    12: "Unknown Asset 12",
}

with app.app_context():
    print("=" * 60)
    print("DATABASE RECOVERY FROM BINARY LOGS")
    print("=" * 60)

    # Check current state
    existing_user = User.query.filter_by(email='ukpokerfan1@gmail.com').first()
    if existing_user:
        print(f"\n⚠️  User already exists (id={existing_user.id}). Skipping user creation.")
        user_id = existing_user.id
    else:
        # 1. Restore the user with the exact password hash from binlogs
        print("\n1. Restoring user account...")
        user = User(
            id=3,
            email='ukpokerfan1@gmail.com',
            password_hash='$argon2id$v=19$m=65536,t=3,p=4$bo1x7n2vVQqhdM7ZG4PQeg$21Ip9jAO4bD3aAnIdkT1UxRCgAPc21Dq/G1Y/npwf8o',
            active=True,
            created_at=datetime(2025, 8, 27, 6, 33, 49),
            last_login_at=datetime(2026, 2, 13, 13, 59, 42),
            fs_uniquifier='cec34c83515614a98aff4e15ad25c4ef93b08aa1137b1ff7',
            is_confirmed=True,
            confirmed_on=datetime(2025, 8, 27, 6, 34, 4),
            default_currency_code='GBP',
            otp_secret=None,
            otp_enabled=False,
            last_activity_date=None,
            streak_days=0,
        )
        db.session.add(user)
        db.session.flush()
        user_id = user.id
        print(f"   ✅ User restored: {user.email} (id={user_id})")
        print(f"   ✅ Password hash preserved — you can log in with your existing password")

    # 2. Create sites (referenced by site_history)
    print("\n2. Restoring sites...")
    sites_created = 0
    for site_id, name in sorted(SITE_NAMES.items()):
        existing = Sites.query.get(site_id)
        if existing:
            print(f"   ⚠️  Site {site_id} already exists: {existing.name}")
            continue
        site = Sites(id=site_id, name=name, user_id=user_id, display_order=0)
        db.session.add(site)
        sites_created += 1
        print(f"   ✅ Site {site_id}: {name}")
    print(f"   Created {sites_created} sites")

    # 3. Create assets (referenced by asset_history)
    print("\n3. Restoring assets...")
    assets_created = 0
    for asset_id, name in sorted(ASSET_NAMES.items()):
        existing = Assets.query.get(asset_id)
        if existing:
            print(f"   ⚠️  Asset {asset_id} already exists: {existing.name}")
            continue
        asset = Assets(id=asset_id, name=name, user_id=user_id, display_order=0)
        db.session.add(asset)
        assets_created += 1
        print(f"   ✅ Asset {asset_id}: {name}")
    print(f"   Created {assets_created} assets")

    db.session.flush()  # Flush so FK references work

    # 4. Restore deposits (from binlog 253)
    print("\n4. Restoring deposits...")
    deposits_data = [
        # id, date, amount, last_updated, currency, user_id
        (11, datetime(2026, 2, 13), 82.60, datetime(2026, 2, 13, 14, 1, 14), 'USD', user_id),
        (12, datetime(2026, 2, 13), 21.73, datetime(2026, 2, 13, 14, 1, 32), 'GBP', user_id),
    ]
    deposits_created = 0
    for dep_id, date, amount, last_updated, currency, uid in deposits_data:
        existing = Deposits.query.get(dep_id)
        if existing:
            print(f"   ⚠️  Deposit {dep_id} already exists")
            continue
        dep = Deposits(id=dep_id, date=date, amount=amount, last_updated=last_updated, currency=currency, user_id=uid)
        db.session.add(dep)
        deposits_created += 1
        print(f"   ✅ Deposit {dep_id}: {amount} {currency} on {date.date()}")
    print(f"   Created {deposits_created} deposits (IDs 1-10 were lost)")

    # 5. Restore drawings (from binlogs 252 + 253)
    print("\n5. Restoring drawings...")
    drawings_data = [
        (10, datetime(2026, 1, 8), 4.99, datetime(2026, 2, 13, 13, 9, 48), 'USD', user_id),
        (11, datetime(2026, 2, 13), 143.48, datetime(2026, 2, 13, 14, 1, 56), 'USD', user_id),
        (12, datetime(2026, 2, 13), 41.52, datetime(2026, 2, 13, 14, 2, 5), 'GBP', user_id),
    ]
    drawings_created = 0
    for drw_id, date, amount, last_updated, currency, uid in drawings_data:
        existing = Drawings.query.get(drw_id)
        if existing:
            print(f"   ⚠️  Drawing {drw_id} already exists")
            continue
        drw = Drawings(id=drw_id, date=date, amount=amount, last_updated=last_updated, currency=currency, user_id=uid)
        db.session.add(drw)
        drawings_created += 1
        print(f"   ✅ Drawing {drw_id}: {amount} {currency} on {date.date()}")
    print(f"   Created {drawings_created} drawings (IDs 1-9 were lost)")

    # 6. Restore site_history (from binlog 252)
    print("\n6. Restoring site history...")
    site_history_data = [
        (99, 6, 436.51, 'USD', datetime(2026, 2, 13, 10, 49, 0), user_id),
        (100, 7, 1.15, 'USD', datetime(2026, 2, 13, 10, 49, 23), user_id),
        (101, 8, 29.59, 'GBP', datetime(2026, 2, 13, 10, 49, 39), user_id),
        (102, 13, 51.45, 'USD', datetime(2026, 2, 13, 10, 50, 6), user_id),
    ]
    sh_created = 0
    for sh_id, site_id, amount, currency, recorded_at, uid in site_history_data:
        existing = SiteHistory.query.get(sh_id)
        if existing:
            print(f"   ⚠️  SiteHistory {sh_id} already exists")
            continue
        sh = SiteHistory(id=sh_id, site_id=site_id, amount=amount, currency=currency, recorded_at=recorded_at, user_id=uid)
        db.session.add(sh)
        sh_created += 1
        print(f"   ✅ SiteHistory {sh_id}: site {site_id} = {amount} {currency}")
    print(f"   Created {sh_created} site history records (IDs 1-98 were lost)")

    # 7. Restore asset_history (from binlog 252)
    print("\n7. Restoring asset history...")
    asset_history_data = [
        (20, 7, 1.80, 'GBP', datetime(2026, 2, 13, 12, 57, 17), user_id),
        (21, 8, 2.60, 'GBP', datetime(2026, 2, 13, 12, 58, 0), user_id),
        (22, 9, 4.37, 'GBP', datetime(2026, 2, 13, 12, 58, 29), user_id),
        (23, 12, 180.00, 'GBP', datetime(2026, 2, 13, 12, 58, 40), user_id),
    ]
    ah_created = 0
    for ah_id, asset_id, amount, currency, recorded_at, uid in asset_history_data:
        existing = AssetHistory.query.get(ah_id)
        if existing:
            print(f"   ⚠️  AssetHistory {ah_id} already exists")
            continue
        ah = AssetHistory(id=ah_id, asset_id=asset_id, amount=amount, currency=currency, recorded_at=recorded_at, user_id=uid)
        db.session.add(ah)
        ah_created += 1
        print(f"   ✅ AssetHistory {ah_id}: asset {asset_id} = {amount} {currency}")
    print(f"   Created {ah_created} asset history records (IDs 1-19 were lost)")

    # Commit everything
    try:
        db.session.commit()
        print("\n" + "=" * 60)
        print("✅ RECOVERY COMPLETE")
        print("=" * 60)
        print(f"""
WHAT WAS RECOVERED:
  • User account: ukpokerfan1@gmail.com (same password works)
  • {sites_created} sites: {', '.join(f'{v} (id={k})' for k,v in sorted(SITE_NAMES.items()))}
  • {assets_created} assets: {', '.join(f'{v} (id={k})' for k,v in sorted(ASSET_NAMES.items()))}
  • {deposits_created} deposits (IDs 11-12 only)
  • {drawings_created} drawings (IDs 10-12 only)
  • {sh_created} site history records (IDs 99-102 only)
  • {ah_created} asset history records (IDs 20-23 only)

WHAT WAS LOST (binary logs rotated out):
  • Deposits 1-10
  • Drawings 1-9
  • Site history 1-98 (all older balance snapshots)
  • Asset history 1-19 (all older value snapshots)
  • Any sites/assets NOT referenced in today's history
    (the 4 sites and 4 assets above are ones we KNOW existed)

NEXT STEPS:
  1. Log in with your existing password
  2. Rename 'Unknown Asset 8/9/12' to their real names
  3. Check if any sites/assets are missing and re-add them
  4. Re-enter any historical deposits/drawings you remember
""")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ RECOVERY FAILED: {e}")
        raise
