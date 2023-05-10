from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import join_room, leave_room, send, SocketIO
#from flask_sqlalchemy import SQLAlchemy
import json
import math
import random
from string import ascii_uppercase


with open('config.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)

app.config['SECRET_KEY'] = 'afdoijasdsoifjaos#'

socketio = SocketIO(app)

if(params['local_server']):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

db = SQLAlchemy(app)


class Posts(db.Model):
    SNO = db.Column(db.Integer(), primary_key= True)
    TITLE = db.Column(db.String(200), unique=False, nullable=False)
    CONTENT = db.Column(db.String(200), unique=False, nullable=False)
    IMAGE = db.Column(db.String(200), unique=False, nullable=False)
class Qa(db.Model):
    SNO = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    phone_num = db.Column(db.Integer(), unique=False, nullable=True)
    email = db.Column(db.String(50), unique=False, nullable=True)
    msg = db.Column(db.String(200), unique=False, nullable=False)
class Video(db.Model):
    sno = db.Column(db.Integer(), primary_key=True)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    img = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(200), unique=False, nullable=False)
class Text(db.Model):
    sno = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(200), unique=False, nullable=False)
    img = db.Column(db.String(60), unique=True, nullable=False)
    content = db.Column(db.String(200), unique=False, nullable=False)

rooms={}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route("/")
def index ():
    return render_template('index.html', title = params['title'])

@app.route("/blogs")
def blogs():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))

    page = request.args.get('page')

    if(not str(page).isnumeric()):
        page = 1


    page= int(page)

    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if (page==1):
        prev = "#"
        next = "/blogs?page="+ str(page+1)
    elif(page==last):
        prev = "/blogs?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/blogs?page=" + str(page - 1)
        next = "/blogs?page=" + str(page + 1)

    return render_template('blogs.html',post=posts, title = params['title'],next=next,prev=prev)

@app.route("/solution")
def solution():
    video = Video.query.filter_by().all()
    last = math.ceil(len(video)/int(params['no_of_posts']))

    page_v = request.args.get('page_v')

    if(not str(page_v).isnumeric()):
        page_v = 1


    page_v= int(page_v)

    video = video[(page_v-1)*int(params['no_of_posts']): (page_v-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if (page_v==1):
        prev_v = "#"
        next_v = "/solution?page_v="+ str(page_v+1)
    elif(page_v==last):
        prev_v = "/solution?page_v=" + str(page_v - 1)
        next_v = "#"
    else:
        prev_v = "/solution?page_v=" + str(page_v - 1)
        next_v = "/solution?page_v=" + str(page_v + 1)

    text = Text.query.filter_by().all()

    last = math.ceil(len(text)/int(params['no_of_posts']))

    page_t = request.args.get('page_t')

    if(not str(page_t).isnumeric()):
        page_t = 1


    page_t= int(page_t)

    text = text[(page_t-1)*int(params['no_of_posts']): (page_t-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if (page_t==1):
        prev_t = "#"
        next_t = "/solution?page_t="+ str(page_t+1)
    elif(page_t==last):
        prev_t = "/solution?page_t=" + str(page_t - 1)
        next_t = "#"
    else:
        prev_t = "/solution?page_t=" + str(page_t - 1)
        next_t = "/solution?page_t=" + str(page_t + 1)

    return render_template('solution.html', title = params['title'],video=video,text=text, prev_v=prev_v, next_v=next_v, prev_t=prev_t, next_t=next_t)
@app.route("/solution/txt/<string:sno>")
def txt_solution(sno):
    file = sno + "-t.html"
    return render_template(file,title=params['title'])

@app.route("/QA", methods=['GET','POST'])
def QA():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Qa(email = email, name= name, phone_num= phone, msg= message)
        db.session.add(entry)
        db.session.commit()
        return render_template('QA.html', show="", title = params['title'])
    return render_template('QA.html', show="hidden", title = params['title'])

@app.route("/contact")
def contact():
    return render_template('contact.html', title = params['title'])

@app.route("/session")
def sessions():
    return render_template('session.html', title = params['title'])

@app.route('/a')
def a():
    return render_template("try.html", title = params['title'])
@app.route('/blog')
def blog():
    file = open("static/1.txt","r")
    post_content = file.read()
    return render_template('blog.html', content = post_content, title = params['title'])
@app.route('/blog/<string:sno>')
def blog_sno(sno):
    blog_file = sno+'.html'
    return render_template(blog_file, title = params['title'])

@app.route('/vid/<string:slug>')
def vid(slug):
    return render_template('video.html', title = params['title'],slug=slug)

@app.route("/chat", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name, title = params['title'])

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name, title = params['title'])

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name, title = params['title'])

        session["room"] = room
        session["name"] = name
        return redirect('/room')

    return render_template("home.html", title = params['title'])

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect("/chat")

    return render_template("room.html", code=room, messages=rooms[room]["messages"], title = params['title'])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == '__main__':
    #socketio.run(app, debug=False)
    app.run(host='0.0.0.0', port = 4000, debug=True)
    socketio.run(app, host='0.0.0.0', port = 4000, debug=True)
