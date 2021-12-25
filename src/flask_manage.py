from flask import request
from flask import jsonify
from flask import Flask, render_template,redirect
from .__init__ import DIR_TEMPLATES
from .detector import ln_detector
import datetime
from .key_maker import key_generator,apiKeyManagement
from guesslang import Guess
guess=Guess()
template_dir = DIR_TEMPLATES
app = Flask(__name__, template_folder=template_dir)
app.config['JSON_AS_ASCII'] = False
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        #userid = request.form.get('userid')
        email = request.form.get('email')
        #password = request.form.get('password')
        #password_2 = request.form.get('re_password')
        #print(userid,email,password,password_2)
        if not (email):
            return "입력되지 않은 정보가 있습니다"
        else:
            instance_apiKey=apiKeyManagement()
            if instance_apiKey.isemailValid(email):
                return "이미 등록된 이메일 입니다."
            else:
                new_key=key_generator()
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                expired = datetime.datetime.now() +datetime.timedelta(days=2)
                expired = expired.strftime('%Y-%m-%d %H:%M:%S')
                instance_apiKey.key_registered(email,new_key,now,expired)
                instance_apiKey.close()
            return new_key
        return redirect('/')

@app.route("/code_detector", methods=['POST'])
def code_detector():
    start=datetime.datetime.now()
    data = request.get_json()
    code=data.get('code')
    key=data.get('key')
    if key is None:return "Error! Key required"
    instance_key=apiKeyManagement()
    if instance_key.isapiKeyValid(key):
        result=ln_detector(guess,code)
        return result
    return 'invalid Key.\nPlease Contact to jlee@mark87.com with your email and key'

if __name__ == '__main__':
    app.run()