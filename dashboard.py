import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models.user import get_user_by_id, update_balance, get_stats
from ..models.transaction import create_transaction, get_transactions, get_recent

dashboard_bp = Blueprint('dashboard', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../../uploads')


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated


def fmt_fcfa(n):
    return f"{int(n):,}".replace(',', ' ')


# ── DASHBOARD ──
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user  = get_user_by_id(session['user_id'])
    txs   = get_recent(user['id'], 6)
    stats = get_stats(user['id'])
    msg   = session.pop('flash_success', None)
    return render_template('dashboard/index.html', user=user, txs=txs, stats=stats,
                           success=msg, fmt=fmt_fcfa)


# ── HISTORY ──
@dashboard_bp.route('/history')
@login_required
def history():
    user   = get_user_by_id(session['user_id'])
    f      = request.args.get('filter', 'all')
    txs    = get_transactions(user['id'], limit=100, filter_type=f)
    stats  = get_stats(user['id'])
    return render_template('dashboard/history.html', user=user, txs=txs, stats=stats,
                           current_filter=f, fmt=fmt_fcfa)


# ── PROFILE ──
@dashboard_bp.route('/profile')
@login_required
def profile():
    user  = get_user_by_id(session['user_id'])
    stats = get_stats(user['id'])
    return render_template('dashboard/profile.html', user=user, stats=stats, fmt=fmt_fcfa)


# ── DEPOSIT ──
@dashboard_bp.route('/deposit', methods=['POST'])
@login_required
def deposit():
    amount = float(request.form.get('amount', 0) or 0)
    source = request.form.get('source', 'Dépôt').strip()
    if amount <= 0:
        flash('Montant invalide.', 'error')
        return redirect(url_for('dashboard.index'))

    user = get_user_by_id(session['user_id'])
    new_balance = user['balance'] + amount
    update_balance(user['id'], new_balance)
    create_transaction(user['id'], 'credit', 'deposit', f'Dépôt — {source}',
                       amount, new_balance)
    session['flash_success'] = f"Dépôt de {fmt_fcfa(amount)} FCFA effectué avec succès !"
    return redirect(url_for('dashboard.index'))


# ── TRANSFER ──
@dashboard_bp.route('/transfer', methods=['POST'])
@login_required
def transfer():
    amount     = float(request.form.get('amount', 0) or 0)
    recipient  = request.form.get('recipient', '').strip()
    message    = request.form.get('message', '').strip()
    media_type = request.form.get('media_type', '') or None

    if amount <= 0 or not recipient:
        flash('Montant ou destinataire invalide.', 'error')
        return redirect(url_for('dashboard.index'))

    user = get_user_by_id(session['user_id'])
    if amount > user['balance']:
        flash('Solde insuffisant pour ce transfert.', 'error')
        return redirect(url_for('dashboard.index'))

    new_balance = user['balance'] - amount
    update_balance(user['id'], new_balance)

    # Handle media upload
    media_path = None
    file = request.files.get('media_file')
    if file and file.filename and media_type:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        ext = os.path.splitext(file.filename)[1]
        fname = f'media_{uuid.uuid4().hex}{ext}'
        file.save(os.path.join(UPLOAD_FOLDER, fname))
        media_path = f'/uploads/{fname}'

    create_transaction(user['id'], 'debit', 'transfer', recipient,
                       amount, new_balance,
                       media_type=media_type, media_path=media_path,
                       message=message or None)
    session['flash_success'] = f"Transfert de {fmt_fcfa(amount)} FCFA vers {recipient} effectué !"
    return redirect(url_for('dashboard.index'))


# ── PAYMENT ──
@dashboard_bp.route('/payment', methods=['POST'])
@login_required
def payment():
    amount   = float(request.form.get('amount', 0) or 0)
    merchant = request.form.get('merchant', 'Marchand').strip()

    if amount <= 0:
        flash('Montant invalide.', 'error')
        return redirect(url_for('dashboard.index'))

    user = get_user_by_id(session['user_id'])
    if amount > user['balance']:
        flash('Solde insuffisant.', 'error')
        return redirect(url_for('dashboard.index'))

    new_balance = user['balance'] - amount
    update_balance(user['id'], new_balance)
    create_transaction(user['id'], 'debit', 'payment', merchant, amount, new_balance)
    session['flash_success'] = f"Paiement de {fmt_fcfa(amount)} FCFA à {merchant} effectué !"
    return redirect(url_for('dashboard.index'))


# ── WITHDRAW ──
@dashboard_bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    amount = float(request.form.get('amount', 0) or 0)
    mode   = request.form.get('mode', 'Orange Money').strip()

    if amount <= 0:
        flash('Montant invalide.', 'error')
        return redirect(url_for('dashboard.index'))

    user = get_user_by_id(session['user_id'])
    if amount > user['balance']:
        flash('Solde insuffisant.', 'error')
        return redirect(url_for('dashboard.index'))

    new_balance = user['balance'] - amount
    update_balance(user['id'], new_balance)
    create_transaction(user['id'], 'debit', 'withdraw', f'Retrait — {mode}',
                       amount, new_balance)
    session['flash_success'] = f"Retrait de {fmt_fcfa(amount)} FCFA via {mode} confirmé !"
    return redirect(url_for('dashboard.index'))
