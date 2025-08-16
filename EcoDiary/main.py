from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecret"  # ключ для сессий

# Настройка базы данных
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


with app.app_context():
    db.create_all()    


# ------------------ Роуты ------------------

# Первый экран (главное меню)
@app.route("/")
def first():
    if "username" in session:
        return redirect(url_for("index"))
    return render_template("welcome.html")


# Главная страница (после входа)
@app.route("/index")
def index():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    return redirect(url_for("login"))


# Регистрация
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Такой пользователь уже существует!"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        session["username"] = username
        return redirect(url_for("index"))

    return render_template("register.html")


# Логин
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return "Неверный логин или пароль!"

    return render_template("login.html")


# Выход
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("first"))


# ------------------ Запуск ------------------
if __name__ == "__main__":
    app.run(debug=True)
