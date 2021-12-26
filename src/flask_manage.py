from flask import request
from flask import jsonify
from flask import Flask, render_template,redirect
from .__init__ import DIR_TEMPLATES
from .detector import ln_detector
import datetime
from .key_maker import key_generator,apiKeyManagement,Logs
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
        email = request.form.get('email')
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
    try:
        ip=request.remote_addr
        data = request.get_json()
        code=data.get('code')
        key=data.get('key')
        if key is None:return "Error! Key required"
        instance_key=apiKeyManagement()
        instance_log=Logs()
        if instance_key.isapiKeyValid(key):
            result=ln_detector(guess,code)
            instance_key.close()
            instance_log.insert(key,ip,'SUCCESS',result)
            instance_log.close()
            return result
        instance_key.close()
        instance_log.insert(key,ip,'FAIL','INVALID_KEY')
        instance_log.close()
        return 'invalid Key.\nPlease Contact to jlee@mark87.com with your email and key'
    except Exception as err:
        instance_log=Logs()
        instance_log.insert(key,ip,'ERROR',str(err))
        instance_log.close()
        return "ERROR-{}".format(str(err))

@app.route("/logs", methods=['GET'])
def log():
    #naverID = request.args.get('naverID')
    #content_number = request.args.get('article')
    instance_log=Logs()
    list_logs = instance_log.selectQuery()
    list_logs = list(map(lambda x: "<p>" + '\t'.join(list(map(lambda y: str(y), x))) + "</p>", list_logs))
    instance_log.close()
    return ''.join(list_logs)

if __name__ == '__main__':
    app.run()