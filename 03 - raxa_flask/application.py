from flask import Flask, request, flash, redirect, session
from flask_login import login_user, logout_user, login_required
from flask import render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import sqlite3


app = Flask(__name__)
app.secret_key = "thisissosecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)

#conect a sqlite3 databse in the project

#create the teams database 
class Team(db.Model):
    team_id = db.Column('team_id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(255), nullable=False, unique=True)
    
    #quero que o time tenha relação com um id de um jogador.
    people = db.relationship('Person', backref='team')

    # pessoas = db.relationship("Person", back_populates="times")

class Person(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column('name', db.String(255), unique=True, nullable=False)
    password = db.Column('password', db.String(255), unique=True, nullable=False)
    username = db.Column('username', db.String(255), unique=True, nullable=False)
 
    #quero que a pessoa tenha uma tabela relacionada com  o id do seu time
    p_team_id = db.Column(db.Integer, db.ForeignKey('team.team_id'))
    #team = db.relationship('Team', backref='person')
    

    
    # times = db.relationship("Team", back_populates="pessoas")
    # times_id = db.Column('team_id', db.Integer, db.ForeignKey('team.team_id'))
    


class Raxa(db.Model):
    raxa_id = db.Column('raxa_id', db.Integer, primary_key=True)
    #store the time of game
    datetime =  db.Column('datetime', db.DateTime, nullable=False)
    adress = db.Column('adress', db.String(510), nullable=False)



@app.route("/")
def index():
    #TODO

    return render_template("index.html")



@app.route("/raxa", methods=["GET", "POST"])
def raxa():
    if request.method == "POST":
        name =  request.form.get("search")
        #working name
        q_team = Team.query.filter_by(name=name).first()
        if not q_team:
            return render_template("error.html", message="team not found")

        #criar uma forma para selecionar o time
        #insert the data of raxa
        name =  request.form.get("{{row.id}}")
        print(name)
        


    else:
        #gets all from team database to use on table

        t_team = Team.query.all()
        return render_template("raxa.html", t_team=t_team)


@app.route("/join_team", methods=["GET", "POST"])
def join_team():
    if request.method == "POST":
        #incomplete teams
        name = request.form.get("team_name")

        if not name:
            return render_template("error.html", message="worked")

        #current logged user id
        user_id = session["name"][1]

        #query for this name on db
        team_query = Team.query.filter_by(name=name).first()
     
        if not team_query:
            return render_template("error.html", message="time nao encontrado")

        team_query = team_query.team_id

        #update user team_id

        user_valid = Person.query.filter_by(id=user_id).first()

        user_valid.p_team_id = team_query
        db.session.commit()



        print(team_query, user_valid)


        # db.session.add()
        

        return redirect("/raxa")
        

    return render_template("join_team.html")

        


@app.route("/create_team", methods=["GET","POST"])
def create_team():
    if request.method == "POST":
        name = request.form.get("team_name")


        if not name:
            return render_template("error.html", message="must have a team name!")


        if len(name) < 1:
            return render_template("error.html", message="must have a team name!")
        
        owner_id = session["name"]
        team_query = Team.query.filter_by(name=name).first()
        if team_query:
            return render_template("error.html", message="This name already exists'")
        
        

        owner_id = session["name"][1]
        
        team = Team(name=name)
        check = Team.query.filter_by(name=name).first()

        
        db.session.add(team)
        db.session.commit()
        
        #when team created i wanna set this team id to the user team table
        user_id = session["name"][1]
        #query for this name on db
        team_query = Team.query.filter_by(name=name).first()
        if not team_query:
            return render_template("error.html", message="Something wrong happened!")
        team_query = team_query.team_id
        #update user team_id
        user_valid = Person.query.filter_by(id=user_id).first()
        user_valid.p_team_id = team_query
        db.session.commit()
        


        return redirect('/raxa')

          
    return render_template("create_team.html")



@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        #verify if the login data is correct. and keep the user logged in.
        #select from datrabase if the data from database is the same as the data from forms.
        username = request.form.get("username")
        password =  request.form.get("password")

        if len(username) < 6:
            return render_template("error.html", message="Nome de usuario deve conter 6 ou mais caracteres")
        
        if len(password) < 8:
            return render_template("error.html", message="A senha deve conter 8 ou mais caracteres")
        
        
        #verify if this user in on db
        qr = Person.query.filter_by(username=username).first()

        if qr and check_password_hash(qr.password, password):
            session['name'] = qr.name, qr.id

            #print(session['name'][1])
            

            
        else:
            render_template("error.html", message="nome de usuario nao encontrado")
        
        

        return redirect("/")
        

    return render_template("login.html")



@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":    
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        name =  request.form.get("name")
        

        if not username:
            return render_template("error.html", message="Você deve inserir um nome de usuario")
        if not password:
            return render_template("error.html", message="Você deve inserir uma senha") 
        if confirmation != password:
            return render_template("error.html", message="Senhas não coincidem")
        if not name:
            return render_template("error.html", message="Você deve inserir um nome")
        
        #verify if the password and username lenght is according to specs.
        if len(username) < 6:
            return render_template("error.html", message="Nome de usuario deve conter 6 ou mais caracteres")
        

        if len(password) < 8:
            return render_template("error.html", message="A senha deve conter 8 ou mais caracteres")


        #generate the hash of the password
        password = generate_password_hash(password)
        #log in the user
        user = Person(name=name, password=password, username=username)
        db.session.add(user)
        db.session.commit()
        
        #insert data into the database
        return redirect("/")
        
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop('name', None)
    return redirect("/")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)