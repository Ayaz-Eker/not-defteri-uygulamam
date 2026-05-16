# Kütüphaneleri yükleme/Flask'a bağlanma
from flask import Flask, render_template, request, redirect, session
# Veti tabanı kütüphanesine bağlanma
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# Oturum için gizli anahtarın ayarlanması
app.secret_key = 'my_top_secret_123'
# SQLite bağlantısı kurma
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Veritabanı oluşturma
db = SQLAlchemy(app)
# Tablo oluşturma

class Card(db.Model):
    # Tablo giriş alanları oluşturma
    # id
    id = db.Column(db.Integer, primary_key=True)
    # Başlık
    title = db.Column(db.String(100), nullable=False)
    # Alt başlık
    subtitle = db.Column(db.String(300), nullable=False)
    # Metin
    text = db.Column(db.Text, nullable=False)
    # Kart sahibinin e-posta adresi
    user_email = db.Column(db.String(100), nullable=False)

    # Nesneyi ve kimliğini çıktı olarak verme
    def __repr__(self):
        return f'<Card {self.id}>'
    

# Görev #1. Kullanıcı tablosunu  oluşturun
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
 
    def __repr__(self):
        return f'<User {self.id}>'
    

with app.app_context():
    db.create_all()

# İçerik sayfasını başlatma
@app.route('/', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']

        user = User.query.filter_by(email=form_login, password=form_password).first()
        if user:
            session['user_email'] = user.email
            return redirect('/index')
        else:
            error = 'E-posta veya şifre yanlış.'

    return render_template('login.html', error=error)



@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Görev #3. Kullanıcı doğrulamasını uygulayın
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        return redirect('/')
    
    else:    
        return render_template('registration.html')


# İçerik sayfasını başlatma
@app.route('/index')
def index():
    if 'user_email' not in session:
        return redirect('/')

    cards = Card.query.filter_by(user_email=session['user_email']).order_by(Card.id).all()
    return render_template('index.html', cards=cards)

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect('/')

# Kart sayfasını başlatma
@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get(id)

    return render_template('card.html', card=card)

# Kart oluşturma sayfasını başlatma
@app.route('/create')
def create():
    if 'user_email' not in session:
        return redirect('/')
    return render_template('create_card.html')

# Kart formu
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if request.method == 'POST':
        if 'user_email' not in session:
            return redirect('/')

        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']

        card = Card(title=title, subtitle=subtitle, text=text, user_email=session['user_email'])

        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create_card.html')

if __name__ == "__main__":
    app.run(debug=True)
