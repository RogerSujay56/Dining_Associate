from flask import Flask ,request
import requests





app=Flask(__name__)


@app.route("/",methods=['POST','GET'])
def get_message():
    response=request.json
    print("first_response",response)
    try:

        if "messages" in response:
            print("inside messages")


            pass
    except Exception as e:
        return 'Success'


if __name__ == '__main__':

    app.run(host="0.0.0.0",port=4000,debug=True)