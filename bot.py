import os
import telebot
import requests
import speech_recognition as sr
import subprocess
import datetime
import openai


logfile = str(datetime.date.today()) + '.log'

bot = telebot.TeleBot(token)

openai.api_key = api_key
model_id = 'gpt-3.5-turbo'


def audio_to_text(dest_name: str):
    r = sr.Recognizer()\
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result


def ChatGPT_conversation(conversation):
    try:
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation
        )
        conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
        return conversation
    except Exception as e:
        return "Количество запросов закончилось"

@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    conversation = []
    try:
        print("Started recognition...")
        file_info = bot.get_file(message.voice.file_id)
        path = os.path.splitext(file_info.file_path)[0]
        fname = os.path.basename(path)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content)
        process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])
        result = audio_to_text(fname+'.wav')
        conversation.append({'role': 'user', 'content': result})
        conversation = ChatGPT_conversation(conversation)
        if conversation != "Количество запросов закончилось":
            bot.send_message(message.from_user.id, f"{conversation[-1]['content'].strip()}\n")
        else:
            bot.send_message(message.from_user.id, "К сожалению, вы привысили количество запросов в минуту")
    except sr.UnknownValueError as e:
        bot.send_message(message.from_user.id,  "Прошу прощения, но я не разобрал сообщение, или оно пустое...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:
        bot.send_message(message.from_user.id,  "Что-то пошло плохо, но наши смелые инженеры уже трудятся над решением...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) +':'+ str(message.from_user.language_code) +':' + str(e) + '\n')
    finally:
        os.remove(fname+'.wav')
        os.remove(fname+'.oga')

bot.polling(none_stop=True, interval=0)