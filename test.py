import requests
from src import key_maker
import datetime


# instance_api=key_maker.apiKeyManagement()
# df=instance_api.selectQuery("""select * from api_key""")
# print(df)

now=datetime.datetime.now()
key='WRovARvKXqBYdembJhsiv0LZE--VsJy-nw5mPlVquLSrxHhfDDo'
data = {'code': """public class Main {
  public static void main(String[] args) {
    System.out.println("Hello World");
  }
}""",'key':key}
res = requests.post(r"http://127.0.0.1:5000/code_detector",json=data)
print(res.text)
print((datetime.datetime.now()-now).total_seconds())
