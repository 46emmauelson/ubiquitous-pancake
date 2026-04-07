from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models.user import create_user, get_user_by_email_or_phone, verify_password, email_exists

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    tab = request.args.get('tab', 'login')
    return render_template('auth/index.html', tab=tab)


@auth_bp.route('/login', methods=['POST'])
def login():
    identifier = request.form.get('identifier', '').strip()
    password   = request.form.get('password', '')

    if not identifier or not password:
        flash('Veuillez remplir tous les champs.', 'error')
        return redirect(url_for('auth.index'))

    user = get_user_by_email_or_phone(identifier)
    if not user or not verify_password(user, password):
        flash('Identifiants incorrects. Vérifiez et réessayez.', 'error')
        return redirect(url_for('auth.index'))

    session['user_id']   = user['id']
    session['user_name'] = f"{user['first_name']} {user['last_name']}"
    return redirect(url_for('dashboard.index'))


@auth_bp.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('first_name', '').strip()
    last_name  = request.form.get('last_name',  '').strip()
    email      = request.form.get('email',      '').strip()
    phone      = request.form.get('phone',      '').strip()
    password   = request.form.get('password',   '')

    if not all([first_name, last_name, email, phone, password]):
        flash('Tous les champs sont obligatoires.', 'error')
        return redirect(url_for('auth.index', tab='register'))

    if len(password) < 8:
        flash('Le mot de passe doit contenir au moins 8 caractères.', 'error')
        return redirect(url_for('auth.index', tab='register'))

    if email_exists(email):
        flash('Cette adresse email est déjà utilisée.', 'error')
        return redirect(url_for('auth.index', tab='register'))

    user = create_user(first_name, last_name, email, phone, password)
    if not user:
        flash('Erreur lors de la création du compte.', 'error')
        return redirect(url_for('auth.index', tab='register'))

    session['user_id']   = user['id']
    session['user_name'] = f"{user['first_name']} {user['last_name']}"
    flash(f"Bienvenue sur PayZen, {first_name} !", 'success')
    return redirect(url_for('dashboard.index'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))
