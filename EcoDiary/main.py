from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.secret_key = "supersecret"

# Настройка базы данных
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------ Модели ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    poll_score = db.Column(db.Integer, default=0)  # Сумма баллов опроса


with app.app_context():
    db.create_all()

# ------------------ Роуты ------------------

# Главный экран
@app.route("/")
def first():
    if "username" in session:
        return redirect(url_for("index"))
    return render_template("welcome.html")

# Главная после входа
@app.route("/index")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["username"])

# Регистрация
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            return "Пользователь уже существует!"
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session["username"] = username
        return redirect(url_for("index"))
    return render_template("register.html")

# Вход
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["username"] = username
            return redirect(url_for("index"))
        return "Неверный логин или пароль!"
    return render_template("login.html")

# Выход
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("first"))

# ------------------ Карточки ------------------

# Страница со списком карточек
@app.route("/cards")
def cards():
    if "username" not in session:
        return redirect(url_for("login"))
    all_cards = Card.query.order_by(Card.id.desc()).all()
    return render_template("cards.html", cards=all_cards)

# Создание карточки
@app.route("/create_card", methods=["GET","POST"])
def create_card():
    if request.method == "POST":
        title = request.form["title"]
        subtitle = request.form["subtitle"]
        text = request.form["text"]

        # Суммируем баллы
        poll_score = sum(int(score) for score in request.form.getlist("poll_options"))

        card = Card(
            title=title,
            subtitle=subtitle,
            text=text,
            poll_score=poll_score  # добавь поле poll_score в модель, если хочешь хранить
        )
        db.session.add(card)
        db.session.commit()
        return redirect(url_for("cards"))

    return render_template("create_card.html")


# Просмотр карточки
@app.route("/card/<int:id>")
def view_card(id):
    if "username" not in session:
        return redirect(url_for("login"))
    
    card = Card.query.get_or_404(id)
    
    return render_template("card.html", card=card)

# ------------------ Запуск ------------------
if __name__ == "__main__":
    app.run(debug=True)
