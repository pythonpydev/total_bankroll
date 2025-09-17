from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_file, jsonify, flash
from flask_security import current_user, login_required
from ..extensions import db
from ..models import Sites, Assets, Drawings, Deposits, SiteHistory, AssetHistory, Currency
import csv
import io
from datetime import datetime, UTC

common_bp = Blueprint('common', __name__)

@common_bp.app_context_processor
def inject_current_year():
    """Injects the current year into all templates."""
    return {'current_year': datetime.now(UTC).year}

@common_bp.route('/confirm_delete/<item_type>/<int:item_id>')
@login_required
def confirm_delete(item_type, item_id):
    return render_template('confirm_delete.html', item_type=item_type, item_id=item_id)

@common_bp.route('/confirm_export_database')
@login_required
def confirm_export_database():
    return render_template('confirm_export_database.html')

@common_bp.route('/perform_delete/<item_type>/<int:item_id>', methods=['POST'])
@login_required
def perform_delete(item_type, item_id):
    try:
        if item_type == 'site':
            SiteHistory.query.filter_by(site_id=item_id, user_id=current_user.id).delete()
            Sites.query.filter_by(id=item_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Site deleted successfully!", "success")
            return redirect(url_for('poker_sites.poker_sites_page'))
        elif item_type == 'asset':
            AssetHistory.query.filter_by(asset_id=item_id, user_id=current_user.id).delete()
            Assets.query.filter_by(id=item_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Asset deleted successfully!", "success")
            return redirect(url_for('assets.assets_page'))
        elif item_type == 'withdrawal':
            Drawings.query.filter_by(id=item_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Withdrawal deleted successfully!", "success")
            return redirect(url_for('withdrawal.withdrawal'))
        elif item_type == 'deposit':
            Deposits.query.filter_by(id=item_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Deposit deleted successfully!", "success")
            return redirect(url_for('deposit.deposit'))
        elif item_type == 'site_history':
            history_record = SiteHistory.query.filter_by(id=item_id, user_id=current_user.id).first()
            if history_record:
                site_id = history_record.site_id
                count = SiteHistory.query.filter_by(site_id=site_id, user_id=current_user.id).count()
                if count <= 1:
                    flash("Cannot delete the last history record for a site. Please delete the site itself.", "danger")
                    return redirect(url_for('poker_sites.site_history', site_id=site_id))
                db.session.delete(history_record)
                db.session.commit()
                flash("History record deleted successfully!", "success")
                return redirect(url_for('poker_sites.site_history', site_id=site_id))
        elif item_type == 'asset_history':
            history_record = AssetHistory.query.filter_by(id=item_id, user_id=current_user.id).first()
            if history_record:
                asset_id = history_record.asset_id
                count = AssetHistory.query.filter_by(asset_id=asset_id, user_id=current_user.id).count()
                if count <= 1:
                    flash("Cannot delete the last history record for an asset. Please delete the asset itself.", "danger")
                    return redirect(url_for('assets.asset_history', asset_id=asset_id))
                db.session.delete(history_record)
                db.session.commit()
                flash("History record deleted successfully!", "success")
                return redirect(url_for('assets.asset_history', asset_id=asset_id))
        else:
            flash("Invalid item type", "danger")
            return "Invalid item type", 400
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting record: {e}", "danger")
        return f"Error deleting record: {e}", 500

@common_bp.route('/perform_export_database', methods=['POST'])
@login_required
def perform_export_database():
    try:
        tables = {
            'sites': Sites,
            'assets': Assets,
            'deposits': Deposits,
            'drawings': Drawings,
            'site_history': SiteHistory,
            'asset_history': AssetHistory,
            'currency': Currency # Include currency table
        }
        output = io.StringIO()
        writer = csv.writer(output)

        for table_name, model in tables.items():
            # Fetch data for the current user, or all data for Currency table
            if model == Currency:
                rows = db.session.query(model).all()
            else:
                rows = db.session.query(model).filter_by(user_id=current_user.id).all()

            if rows:
                # Write table name as a header
                writer.writerow([f"Table: {table_name}"])
                
                # Write headers
                # Get column names from the model's __table__.columns
                headers = [column.name for column in model.__table__.columns]
                writer.writerow(headers)
                
                # Write data rows
                for row in rows:
                    writer.writerow([getattr(row, header) for header in headers])
                writer.writerow([]) # Add an empty row for separation

        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='bankroll_export.csv')

    except Exception as e:
        current_app.logger.error(f"Error exporting database: {e}")
        flash(f"Error exporting database: {e}", "danger")
        return f"Error exporting database: {e}", 500
