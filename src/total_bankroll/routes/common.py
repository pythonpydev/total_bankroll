from flask import Blueprint, render_template, request, redirect, url_for
from flask_security import current_user
from ..db import get_db

common_bp = Blueprint('common', __name__)

@common_bp.route('/confirm_delete/<item_type>/<int:item_id>')
def confirm_delete(item_type, item_id):
    return render_template('confirm_delete.html', item_type=item_type, item_id=item_id)

@common_bp.route('/perform_delete/<item_type>/<int:item_id>', methods=['POST'])
def perform_delete(item_type, item_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        if item_type == 'site':
            cur.execute("DELETE FROM sites WHERE id = %s AND user_id = %s", (item_id, current_user.id))
            conn.commit()
            return redirect(url_for('poker_sites.poker_sites_page'))
        elif item_type == 'asset':
            cur.execute("DELETE FROM assets WHERE id = %s AND user_id = %s", (item_id, current_user.id))
            conn.commit()
            return redirect(url_for('assets.assets_page'))
        elif item_type == 'withdrawal':
            cur.execute("DELETE FROM drawings WHERE id = %s AND user_id = %s", (item_id, current_user.id))
            conn.commit()
            return redirect(url_for('withdrawal.withdrawal'))
        elif item_type == 'deposit':
            cur.execute("DELETE FROM deposits WHERE id = %s AND user_id = %s", (item_id, current_user.id))
            conn.commit()
            return redirect(url_for('deposit.deposit'))
        else:
            return "Invalid item type", 400
    except Exception as e:
        conn.rollback()
        return f"Error deleting record: {e}", 500
    finally:
        cur.close()
        conn.close()