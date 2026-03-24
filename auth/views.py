from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from auth.forms import RegistrationForm, LoginForm # フォームをインポート
from models import db, User
from auth import auth_bp

@auth_bp.route('/signup', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('アカウントが作成されました！これでログインできます。', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', title='登録', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('ログインに失敗しました。メールアドレスまたはパスワードを確認してください。', 'danger')
    return render_template('login.html', title='ログイン', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('ログアウトしました。', 'info')
    return redirect(url_for('index'))