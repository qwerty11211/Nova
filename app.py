import time
import random
import requests
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy.orm import Session
from verbwire import generate_nft_from_file, trade_nft, view_my_nft, add_file_to_ipfs

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SECRET_KEY"] = "the random string"
db = SQLAlchemy(app)

# --Models--
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    address = db.Column(db.String(50))
    image = db.Column(db.String(50))
    about = db.Column(db.String(50))
    score = db.Column(db.Integer, default=100)
    resume = db.Column(db.String(50))


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(50))
    shortdescription = db.Column(db.String(200))
    detaileddescription = db.Column(db.String(200))
    pay = db.Column(db.String(200))
    status = db.Column(db.Integer, default="Pending")
    askedby_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    askedby_name = db.Column(db.String(200))
    askedby_img = db.Column(db.String(200))


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    image = db.Column(db.String(50))
    description = db.Column(db.String(200))
    pay = db.Column(db.Integer)
    questionID = db.Column(db.Integer, db.ForeignKey("question.id"))


class Assigned(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    createdbyId = db.Column(db.Integer, db.ForeignKey("user.id"))
    questionID = db.Column(db.Integer, db.ForeignKey("question.id"))
    assignedto_ID = db.Column(db.Integer, db.ForeignKey("user.id"))
    # To display the name of user and question in history section
    questionName = db.Column(db.String(200))
    assignedName = db.Column(db.String(200))


class NFT(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    url = db.Column(db.String(200))
    transactionHash = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# -- Authentication --
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        data = User.query.filter_by(username=username, password=password).first()
        print("datadata", data)
        if data is not None:
            session["user"] = data.id
            print(session["user"])
            return redirect(url_for("index"))

        return render_template("incorrectLogin.html")


@app.route("/register/", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        new_user = User(
            username=request.form["username"],
            password=request.form["password"],
            about=request.form["about"],
            image=request.form["image"],
            address=request.form["address"],
        )
        print("new_user", new_user.id)
        db.session.add(new_user)
        db.session.commit()
        for i in range(5):
            response = requests.get("https://picsum.photos/200/300")
            image_url = response.url
            transactionHash = generate_nft_from_file(
                f"RegisterationNFT{i}", "Auto generated NFT for registering", image_url
            )
            nft = NFT(
                id=transactionHash,
                url=image_url,
                user_id=1,
                transactionHash=transactionHash,
            )
            db.session.add(nft)
            db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# -- Dashboard--
@app.route("/index")
def index():
    user = User.query.get(session["user"])
    username = user.username
    about = user.about
    print("YOU ARE LOGGINED IN AS", username)
    showQuestion = Question.query.order_by(desc(Question.id))
    rank_user = User.query.order_by(desc(User.score)).limit(4).all()

    return render_template(
        "index.html",
        username=username,
        about=about,
        showQuestion=showQuestion,
        rank_user=rank_user,
     
    )


# Route to add a new question
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        user_id = session["user"]
        new_question = Question(
            question=request.form["question"],
            shortdescription=request.form["shortdescription"],
            detaileddescription=request.form["detaileddescription"],
            pay=request.form["pay"],
            askedby_id=user_id,
            askedby_name=User.query.get(user_id).username,
            askedby_img=User.query.get(user_id).image,
        )
        flash("New question has been succesfully added")
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for("index"))

    else:
        return render_template("AddQuestion.html")


@app.route("/ParticularQuestion", methods=["GET", "POST"])
def ParticularQuestion():
    if request.method == "POST":
        id = request.args["questionid"]
        username = User.query.get(session["user"]).username
        image = User.query.get(session["user"]).image
        print("question id is", id)
        new_response = Response(
            username=username,
            description=request.form["description"],
            pay=request.form["pay"],
            questionID=id,
            image=image,
        )
        db.session.add(new_response)
        db.session.commit()
        return redirect(url_for("index"))
    else:
        args = request.args
        print("args in q url is", args)
        questionid = Question.query.get(args["questionid"])

        isSamePerson = args["user"]
        print("isSamePerson", isSamePerson)
        user = questionid.askedby_id
        img = User.query.get(user).image
        username = User.query.get(user).username
        response = Response.query.filter_by(questionID=questionid.id).all()
        print("response is", response)
        return render_template(
            "ParticularQuestion.html",
            question=questionid,
            username=username,
            img=img,
            response=response,
            isSamePerson=isSamePerson,
        )


@app.route("/DoubtSolved")
def DoubtSolved():
    id = request.args
    q = Question.query.get(id)
    q.status = "Solved"
    db.session.commit()
    return render_template("DoubtSolved.html", q=q)


@app.route("/Delete")
def Delete():
    id = int(request.args["id"])
    print("to be deleted ", id)
    obj = Question.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/payment")
def payment():
    details = request.args
    print(details)
    mentor = str(details["recipient_name"])
    recipient_address = str(details["recipient_address"])
    tokenId = details["nft"]
    user_id = session["user"]
    current_user = User.query.get(user_id)
    mentor = User.query.filter_by(username=mentor).first()
    topay = User.query.get(mentor.id)
    if current_user.score > 0:
        amt = 10
        flash("Payment successfully made")
        print(current_user.score)
        current_user.score = current_user.score - int(amt)
        topay.score += int(amt)
        db.session.commit()
        trade_nft(current_user.address, recipient_address, tokenId)
        return redirect(url_for("index"))
    else:
        return render_template(
            "404.html",
            display_content="Transcation unsuccessful due to lack of credits",
        )


@app.route("/assign")
def assign():
    qid = int(request.args["qid"])
    assignedto_ID = int(request.args["userid"])
    createdbyId = session["user"]
    print("to be assign ", id)
    obj = Question.query.filter_by(id=qid).one()
    print("obj is", obj)
    print(obj.question)
    obj.status = "Assigned"
    assign = Assigned(
        createdbyId=createdbyId,
        questionID=qid,
        assignedto_ID=assignedto_ID,
        assignedName=request.args["assignedName"],
        questionName=request.args["questionName"],
    )
    db.session.add(assign)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/scoreBoard")
def scoreBoard():
    rank_user = User.query.order_by(desc(User.score))
    return render_template("scoreBoard.html", rank_user=rank_user)

def generate_random_image_url():
    image_ids = ["https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=500&h=500&fit=crop", "https://images.unsplash.com/photo-1502630859934-b3b41d18206c?w=500&h=500&fit=crop", "https://images.unsplash.com/photo-1498471731312-b6d2b8280c61?w=500&h=500&fit=crop", "https://images.unsplash.com/photo-1515023115689-589c33041d3c?w=500&h=500&fit=crop"]  # Replace with your actual image URLs
    return random.choice(image_ids)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    userid = session["user"]
    print("userid is", userid)
    user = User.query.filter_by(id=userid).one()
    if request.method == "POST":
        url = request.form.get("resume_url")
        ipfs_url = add_file_to_ipfs(url)
        user.resume = ipfs_url
        db.session.commit()

        return redirect(url_for("profile"))
    else:
        nft_list=view_my_nft()
        for nft in nft_list:
            nft["image_url"] = generate_random_image_url()
        print(nft_list)
        return render_template("profile.html", user=user, nft_list="nft_list")


# Shows the list of tasks assigned to and by a particular user
@app.route("/history")
def history():
    user_id = session["user"]
    askedByme = Assigned.query.filter_by(createdbyId=user_id).all()
    toBeDoneByMe = Assigned.query.filter_by(assignedto_ID=user_id).all()
    myQuestion = Question.query.filter_by(askedby_id=user_id).all()
    print(myQuestion)
    return render_template(
        "history.html",
        askedByme=askedByme,
        toBeDoneByMe=toBeDoneByMe,
        myQuestion=myQuestion,
        user_id=user_id,
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
