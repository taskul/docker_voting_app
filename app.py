import os
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import SelectField
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_user = os.environ.get('POSTGRES_USER')
db_password = os.environ.get('POSTGRES_PASSWORD')
db_name = os.environ.get('POSTGRES_DB')

if not all([db_user, db_password, db_name]):
    raise ValueError("Missing one or more required environment variables.")

app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{db_user}:{db_password}@{db_name}/votes')
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

db = SQLAlchemy(app)

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    cat = db.Column(db.Integer)
    dog = db.Column(db.Integer)

    @classmethod
    def count_vote(cls, user_vote):
        vote = Vote.query.first()
        if user_vote == 'cat':
            vote.cat += 1
        else:
            vote.dog += 1
        db.session.commit()

class VoteForm(FlaskForm):
    vote = SelectField('Select cat or dog', choices=[('cat', 'Cat'), ('dog', 'Dog')])

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    vote = db.session.query(Vote).first()
    if vote == None:
        first_row = Vote(cat=0, dog=0)
        db.session.add(first_row)
        db.session.commit()
    form = VoteForm()
    if form.validate_on_submit():
        user_vote = form.vote.data
        if vote:
            vote.count_vote(user_vote)

    return render_template('index.html', cat=vote.cat, dog=vote.dog, form=form)

if __name__ =='__main__':
    app.run()