from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

# ------------------ Цитаты ------------------
ecological_quotes = [
    "«Мы не унаследовали Землю у наших предков, мы взяли её взаймы у наших детей.»",
    "«Первое правило экологии — все взаимосвязано со всем.»",
    "«Мысли о природе — это мысли о будущем.»",
    "«Пока не увидишь, как загрязняют реку, не поймёшь, насколько она ценна.»",
    "«Земля — это наш единственный дом. Давайте заботиться о ней.»",
    "«Единственное, что нам останется, если мы будем относиться к природе так, как сейчас, — это воспоминания о ней.»",
    "«Природа не терпит неточностей и не прощает ошибок.»",
    "«Когда срублено последнее дерево, когда отравлена последняя река, когда поймана последняя рыба, — только тогда мы поймём, что деньги нельзя есть.»",
    "«Мы не можем спасти мир, не изменив себя.»",
    "«Забота о природе — это не обязанность, это наша ответственность.»",
    "«Природа — лучший учитель, пока мы готовы её слушать.»",
    "«Мы получили этот мир в подарок, давайте оставим его нашим потомкам не менее прекрасным.»",
    "«Экология — это не мода, это необходимость.»",
    "«Планета — это наш единственный дом, и мы должны беречь его.»",
    "«Природа — это то, что мы потеряем, если будем относиться к ней, как к чему-то само собой разумеющемуся.»",
    "«Думай глобально, действуй локально.»",
    "«Сохраним природу вместе.»",
    "«Чистота начинается с тебя.»",
    "«Будущее в наших руках.»",
    "«Земля не принадлежит нам, это мы принадлежим ей.»",
    "«Измени мир — начни с себя.»"
]


# ------------------ Flask ------------------
app = Flask(__name__)
app.secret_key = "supersecret"

# ------------------ БД ------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------ Модели ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)   
    username = db.Column(db.String(100), nullable=True)              
    password = db.Column(db.String(200), nullable=False)      
    def __repr__(self):
        return f"<User {self.email}>"


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)

    poll_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


# ------------------ Хелперы ------------------
def current_user():
    if "user_id" not in session:
        return None
    return User.query.get(session["user_id"])


# ------------------ Роуты ------------------
@app.route("/")
def first():
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("welcome.html")


@app.route("/index")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    random_quote = random.choice(ecological_quotes)
    user = current_user()
    return render_template("index.html", username=user.username or user.email, quote=random_quote)


# ---------- Регистрация ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip()
        username = request.form.get("username", "").strip()
        password = request.form["password"].strip()

        if not email or not password:
            return "Введите email и пароль."

        if User.query.filter_by(email=email).first():
            return "Пользователь с таким email уже существует!"

        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        return redirect(url_for("index"))

    return render_template("register.html")


# ---------- Вход ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("index"))
        return "Неверный email или пароль!"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("first"))


# ---------- Карточки ----------
@app.route("/cards")
def cards():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = current_user()
    all_cards = Card.query.filter_by(user_id=user.id).order_by(Card.id.desc()).all()
    return render_template("cards.html", cards=all_cards)


@app.route("/create_card", methods=["GET", "POST"])
def create_card():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = current_user()

    if request.method == "POST":
        title = request.form["title"]
        subtitle = request.form["subtitle"]
        text = request.form["text"]

        poll_score = sum(int(v) for v in request.form.getlist("poll_options"))

        card = Card(
            user_id=user.id,
            title=title,
            subtitle=subtitle,
            text=text,
            poll_score=poll_score
        )
        db.session.add(card)
        db.session.commit()
        return redirect(url_for("cards"))

    return render_template("create_card.html")


@app.route("/card/<int:id>")
def view_card(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = current_user()
    card = Card.query.filter_by(id=id, user_id=user.id).first_or_404()

    poll_score = card.poll_score
    thanks = get_thanks_message(poll_score)

    return render_template("card.html", card=card, thanks=thanks)


# ---------- Статистика ----------
def get_thanks_message(score):
    if score == 0:
        return "Сегодня ты ничего не сделал(-а) для природы. 😔"
    elif 0 < score <= 20:
        return "Ты делаешь первые шаги, продолжай в том же духе! 🌱"
    elif 20 < score <= 70:
        return "Ты делаешь успехи! Каждый твой шаг важен. 👏"
    elif 70 < score <= 120:
        return "Впечатляет! Твоя забота о планете очевидна. ✨"
    elif 120 < score <= 170:
        return "Ты — настоящий(-ая) эко-герой(-иня)! Так держать! 🦸‍♀️"
    else:
        return "Ты — абсолютный(-ая) защитник(-ца) природы! Твой вклад неоценим! 🌍"


@app.route("/get_scores")
def get_scores():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = current_user()
    cards = Card.query.filter_by(user_id=user.id).order_by(Card.created_at.asc()).all()
    data = {
        "labels": [c.created_at.strftime("%d-%m") for c in cards],
        "scores": [c.poll_score for c in cards],
        "thanks": [get_thanks_message(c.poll_score) for c in cards]
    }
    return jsonify(data)


@app.route("/stats")
def stats():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = current_user()
    return render_template("stats.html", username=user.username or user.email)


@app.route("/tips")
def tips():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("tips.html")


# ---------- Обратная связь ----------
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        fb = Feedback(name=name, email=email, message=message)
        db.session.add(fb)
        db.session.commit()

        return render_template("feedback_success.html", name=name)

    return render_template("feedback.html")


# ------------------ Запуск ------------------
if __name__ == "__main__":
    app.run(debug=True)
