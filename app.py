import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect  # <--- IMPORTANTE

# 1. Cargar secretos del archivo .env
load_dotenv()

app = Flask(__name__)

# 2. Configuración de Seguridad
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or 'clave-por-si-falla-env'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cisco_dev.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Inicializar Protecciones
db = SQLAlchemy(app)
csrf = CSRFProtect(app)  # <--- ESTO ARREGLA TU ERROR
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- SISTEMA DE USUARIO ---
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Creamos el Hash de tu contraseña para que sea segura
# Usuario: magnus_solis | Contraseña: os.getenv('ADMIN_PASS')
admin_username = os.getenv('ADMIN_USER')
admin_password_hash = generate_password_hash(os.getenv('ADMIN_PASS') or 'solis200917')

# --- MODELO DE BASE DE DATOS ---
class Plantilla(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))
    imagen_url = db.Column(db.String(300), default="/static/images/cisco_dev.png")

with app.app_context():
    db.create_all()

# --- RUTAS ---

@app.route('/')
def index():
    plantillas = Plantilla.query.all()
    return render_template('index.html', plantillas=plantillas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        # Verificamos si el usuario coincide y si la contraseña es correcta usando el hash
        if user == admin_username and check_password_hash(admin_password_hash, pw):
            login_user(User(1))
            return redirect(url_for('admin'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    plantillas = Plantilla.query.all()
    return render_template('admin.html', plantillas=plantillas)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    nuevo = Plantilla(
        nombre=request.form.get('nombre'),
        descripcion=request.form.get('descripcion'),
        precio=float(request.form.get('precio')),
        categoria=request.form.get('categoria'),
        imagen_url=request.form.get('imagen_url') or "/static/images/cisco_dev.png"
    )
    db.session.add(nuevo)
    db.session.commit()
    flash('Script agregado con éxito')
    return redirect(url_for('admin'))

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    p = Plantilla.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Configurado para que tu Nubia Neo 3 5G pueda entrar
    app.run(debug=True, host='0.0.0.0', port=5000)
