import pymysql,requests,json,os,re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

usr=os.environ["DB_USER"]
pas=os.environ["DB_PASSWORD"]
aws_host=os.environ["DB_HOST"]
db=os.environ["DB_NAME"]




#Common function to connect with database
def get_connection(query,val):
    cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host,database=db)
    cursor = cnx.cursor ()
    cursor.execute (query, val)
    cnx.commit ()
    cnx.close ()


def update_authkey() :
    url = "https://3.237.38.173:9090/v1/users/login"
    # url = "https://3.80.233.18:9090/v1/users/login"
    
    payload = "{\n\t\"new_password\": \"Khairnar@123\"\n}"
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Basic <base64(username:password)>',
        'Authorization' : 'Basic YWRtaW46S2hhaXJuYXJAMTIz'
    }
    response = requests.request ("POST", url, headers=headers, data=payload, verify=False)
    rs = response.text
    json_data = json.loads (rs)
    return json_data["users"][0]["token"]

authkey = update_authkey ()

def send_message(rcvr, body, message) :
    authkey = update_authkey ()
    url="https://3.237.38.173:9090/v1/messages"
    # url = "https://3.80.233.18:9090/v1/messages"

    body = body
    to = rcvr
    # print("Inside message")
    payload = "{\n  \"to\": \"" + to + "\",\n  \"type\": \"text\",\n  \"recipient_type\": \"individual\",\n  \"text\": {\n    \"body\": \" " + body + " \"\n  }\n}\n"
    # print(payload)
    headers = {
        'Content-Type' : "application/json",
        'Authorization' : "Bearer " + authkey,
        'User-Agent' : "PostmanRuntime/7.20.1",
        'Accept' : "*/*",
        'Cache-Control' : "no-cache",
        'Postman-Token' : "44d01f0f-a3a5-49a7-9b1f-2e2ef88f62bd",
        # 'Host': "3.230.123.214:9090",
        'Host': "54.198.53.204:9090",
        'Accept-Encoding' : "gzip, deflate",
        'Content-Length' : "116",
        'Connection' : "keep-alive",
        'cache-control' : "no-cache"
    }
    # print ("hello again0")
    try :
        response = requests.request ("POST", url, data=payload.encode('utf-8'), headers=headers, verify=False)
        # print(response)
    except Exception as e :
        print (e)
    statuscode = response.status_code
    response = response.text
    savesentlog(rcvr,response,statuscode,message)
    return response

def save_message_status(response) :
    response = response
    message_or_status_id = response["statuses"][0]["id"]
    # sender_id = response["statuses"][0]["recipient_id"]
    status = response["statuses"][0]["status"]
    timestamp1 = datetime.fromtimestamp (int (response["statuses"][0]["timestamp"]))
    # print("Named")
    add_data = "UPDATE tbl_logs SET status = (%s), last_updateddate = (%s) where message_id = '"+message_or_status_id+"'"
    vals = (status,timestamp1)
    try :
        cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host,
                        database=db)  # make changes
        cursor = cnx.cursor ()
        # print("cnx made")

        cursor.execute (add_data, vals)
        cnx.commit ()
        cnx.close ()
    except Exception as a :
        print (a)

def savesentlog(frm, response, statuscode,Body):
    statuscode = str(statuscode)
    response = json.loads(response)
    message_id = str(response["messages"][0]["id"])
    now = str(datetime.now())
    add_data = "insert into tbl_logs(sender_id, timestamp1, message_id, status,messagebody,camp_name) values (%s,%s,%s,%s,%s,%s)"
    val = (str(frm), str(now), message_id, statuscode,Body,"Cocacola")
    cnx = pymysql.connect (user=usr, max_allowed_packet=1073741824, password=pas, host=aws_host,
                        database=db)
    cursor = cnx.cursor ()
    cursor.execute (add_data, val)
    cnx.commit ()
    cnx.close ()

def send_pdf(to, link, caption=""):
    authkey = update_authkey ()
    url = "https://3.237.38.173:9090/v1/messages/"
    # url = "https://54.196.173.242:9090/v1/messages"
    payload = "{\n\t\"to\": \""+to+"\",\n\t\"type\": \"document\",\n\t\"recipient_type\": \"individual\",\n\t\"document\": {\n\t\t\"link\": \""+link+"\",\n\t\t\"caption\": \""+caption+"\"\n\t}\n}\n"
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer "+authkey,
        'cache-control': "no-cache",
        'Postman-Token': "1083c9be-a60e-4a0d-94a4-448ef126085e"
        }

    response = requests.request("POST", url, data=payload, headers=headers, verify = False)
    print(response.text)
    return response


def interactive_template_with_2button(to, body, option1, option2, message):
    authkey = update_authkey ()
    url = "https://3.237.38.173:9090/v1/messages"
    payload = json.dumps({
        "to": to,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "1",
                            "title": option1
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "2",
                            "title": option2
                        }
                    }
                ]
            }
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+authkey
    }
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    # print(response.text)
    statuscode = response.status_code
    response = response.text
    savesentlog(to[2:], response, statuscode, message)
    return response

def interactive_template_with_1button(to, body, option1, message):
    authkey = update_authkey ()
    url = "https://3.237.38.173:9090/v1/messages"
    payload = json.dumps({
        "to": to,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "Menu",
                            "title": option1
                        }
                    }
                ]
            }
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+authkey
    }
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    # print(response.text)
    statuscode = response.status_code
    response = response.text
    savesentlog(to[2:], response, statuscode, message)
    return response


def interactive_template_to_catalog(to, body, option1, message):
    authkey = update_authkey ()
    url = "https://3.237.38.173:9090/v1/messages"
    payload = json.dumps({
        "to": to,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "Text",
                            "title": option1
                        }
                    }
                ]
            }
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+authkey
    }
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    # print(response.text)
    statuscode = response.status_code
    response = response.text
    savesentlog(to[2:], response, statuscode, message)
    return response




def interactive_template_with_menu_1button(to, body, option1, message):
    authkey = update_authkey ()
    url = "https://3.237.38.173:9090/v1/messages"
    payload = json.dumps({
        "to": to,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "Menu",
                            "title": option1
                        }
                    }
                ]
            }
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+authkey
    }
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    # print(response.text)
    statuscode = response.status_code
    response = response.text
    savesentlog(to[2:], response, statuscode, message)
    return response

def send_interactive_helpmenu(frm, message):
    authkey = update_authkey ()
    url = "https://3.237.38.173:9090/v1/messages"
    payload = json.dumps({
        "to": frm,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Welcome To Help Menu"
            },

            "body": {
                "text": "How can we help you today?"
            },
            "action": {
                "button": "Help Menu",
                "sections": [
                    {
                        "rows": [
                            {
                                "id": "1",
                                "title": "Order Placement issue",
                                "description": " ",
                            },
                            {
                                "id": "2",
                                "title": "Order Status issue",
                                "description": " ",
                            },
                            {
                                "id": "3",
                                "title": "Schemes & Offers issue",
                                "description": " ",
                            },
                            {
                                "id": "4",
                                "title": "Query about Program",
                                "description": " ",
                            },
                            {
                                "id": "5",
                                "title": "Status of your Ticket",
                                "description": " ",
                            },
                            {
                                "id": "menu",
                                "title": "Main Menu",
                                "description": " ",
                            }
                        ]
                    },

                ]
            }
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+authkey
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    statuscode = response.status_code
    response = response.text
    # print(response)
    savesentlog(frm, response, statuscode, message)
    return response

def send_interactive_helpmenu_np(frm, message):
    authkey = update_authkey ()
    url = "https://3.237.38.173:9090/v1/messages"
    payload = json.dumps({
        "to": frm,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "मद्दत मेनुमा स्वागत छ।"
            },

            "body": {
                "text": "आज हामी तपाईंको *के मद्दत गर्न सक्दछौं?*"
            },
            "action": {
                "button": "Help Menu",
                "sections": [
                    {
                        "rows": [
                            {
                                "id": "1",
                                "title": "अर्डर प्लेसमेन्ट",
                                "description": " ",
                            },
                            {
                                "id": "2",
                                "title": "अर्डर स्थिति",
                                "description": " ",
                            },
                            {
                                "id": "3",
                                "title": "स्किम ओर ओफ़्रर",
                                "description": " ",
                            },
                            {
                                "id": "4",
                                "title": "सामान्य प्रश्न लागि।",
                                "description": " ",
                            },
                            {
                                "id": "5",
                                "title": "टिकटको स्थिति हेर्न।",
                                "description": " ",
                            },
                            {
                                "id": "menu",
                                "title": "मुख्य मेनु",
                                "description": " ",
                            }
                        ]
                    },

                ]
            }
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+authkey
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False)
    statuscode = response.status_code
    response = response.text
    # print(response)
    savesentlog(frm, response, statuscode, message)
    return response

