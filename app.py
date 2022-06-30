from sayfer import *
import openai

key_file = open('../key')
key_data = json.load(key_file)

KEY_FILE = key_data['key_file']
LOCATION = key_data['location']
openai.api_key = key_data['openapi_key']
key_file.close()

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

session_prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: "

speech_key, service_region = KEY_FILE, LOCATION
speech_config_stt = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config_stt.speech_recognition_language="uz-UZ"
#audio_config_stt = speechsdk.audio.AudioConfig(device_name="{0.0.1.00000000}.{c91342cf-e781-4464-93ef-0a8e17804c64}") #headset
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config_stt)

audio_config_tts = speechsdk.audio.AudioConfig(device_name='c91342cf-e781-4464-93ef-0a8e17804c64') #computer
speech_config_tts = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config_tts.speech_synthesis_voice_name = "uz-UZ-MadinaNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config_tts)

conf_file = open('settings.conf')
conf_data = json.load(conf_file)

voice_activation = conf_data['voice_activation']
robot_name = conf_data['robot_name']

conf_file.close()

generalNotes = {
      "notes" : [],
      "dates" : []
}

knowledgeNotes = {
      "notes" : [],
      "dates" : []
}

#Loading existing data
if os.path.isfile('knowledgeNotes.json'):
    knowledgeNotesRaw = open('knowledgeNotes.json')
    knowledgeNotes = json.load(knowledgeNotesRaw)
    knowledgeNotesRaw.close()

if os.path.isfile('generalNotes.json'):
    generalNotesRaw = open('generalNotes.json')
    generalNotes = json.load(generalNotesRaw)
    generalNotesRaw.close()



def run_app():
    if(voice_activation == 0):

        wikipedia.set_lang("uz")

        query = drop_characters(speech_recognizer.recognize_once_async().get().text).lower()
        answer = day_filter(year_filter(get_response(query)))
        print(query)

        get_response(query)

        #Wikipedia knowledge base inclusion (Wikipedia dan qidirish)
        if "haqida" in query and "sayfer" in query.split():
            try:
                words = query.split()
                for word in words:
                    if word == "sayfer":
                        words.remove(word)

                joint_query = ' '.join(words)
                wiki_question = joint_query.split(' haqida', 1)[0]
                suggested_wiki_answer = wikipedia.suggest(f"{wiki_question}")             

                # if (suggested_wiki_answer is not None):
                #     wiki_answer = random.choice(suggested_wiki_answer.options)
                try:
                    speech_synthesizer.speak_text_async(f"{wiki_question} haqida qidiryabman").get()
                    wiki_answer = wikipedia.summary(wiki_question, sentences=3)
                except wikipedia.DisambiguationError as e:
                    s = e.options[-1]
                    wiki_answer = wikipedia.summary(s, sentences=3)

                speech_synthesizer.speak_text_async(day_filter(year_filter(wiki_answer))).get()
                return 1
            except Exception as e:
                print(e)


        #Dasturlarni ochish
        if("Xrom" in answer and "sayfer" in query.lower()):
            speech_synthesizer.speak_text_async(answer)
            call(["chrome.exe"])
            return 1
        elif("Kalkulyator" in answer and "sayfer" in query.lower()):
            speech_synthesizer.speak_text_async(answer)
            call(["calc.exe"])
            return 1
        elif("Telegram" in answer and "sayfer" in query.lower()):
            speech_synthesizer.speak_text_async(answer)
            subprocess.Popen("c:\\Users\\Peter\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe")
            return 1

        #Soatni so'rash
        if "soat" in query.lower() and "sayfer" in query.lower().split():
            currentTime = get_current_time()
            speech_synthesizer.speak_text_async(currentTime).get()
            return 1
        #TakeNotes malumotlarni saqlab qolish

        if answer == "Ilmiy ma'lumotlarni saqlayman" and "sayfer" in query.lower().split():
            note = query.split("eslab qol")[0]
            print(note)

            if("umumiy" in query):
                note = query.split("umumiy")[0]
                speech_synthesizer.speak_text_async("umumiy ma'lumot kiritildi").get()
                generalNotes["notes"].append(note)
                generalNotes["dates"].append(str(mydate))

            elif("ilmiy" in query):
                note = query.split("ilmiy")[0]
                speech_synthesizer.speak_text_async("Ilmiy ma'lumot kiritildi").get()
                knowledgeNotes["notes"].append(note)
                knowledgeNotes["dates"].append(str(mydate))

            else:
                speech_synthesizer.speak_text_async("Qaysi datasetga ma'lumot kiritayotganingizni ayting: ilmiy yoki umumiy").get()

                playsound('audio.mp3', block=False)
                confirmation = speech_recognizer.recognize_once_async().get().text

                if("ilmiy" in confirmation.lower()):
                    speech_synthesizer.speak_text_async("ilmiy ma'lumotlar bazasiga kiritaman").get()
                    knowledgeNotes["notes"].append(note)
                    knowledgeNotes["dates"].append(str(mydate))

                elif("umumiy" in confirmation.lower()):
                    speech_synthesizer.speak_text_async("umumiy ma'lumotlar bazasiga kiritaman").get()
                    generalNotes["notes"].append(note)
                    generalNotes["dates"].append(str(mydate))

                else:          
                  speech_synthesizer.speak_text_async("Bunday ma'lumotlar ba'zasi topilmadi, saqlashni bekor qilaman").get()


            k = open('knowledgeNotes.json', 'w')
            k.write(json.dumps(knowledgeNotes))
            k.close()

            g = open('generalNotes.json', 'w')
            g.write(json.dumps(generalNotes))
            g.close()
            return 1


        #ReadNotes Ma'lumotlarni o'qish
        if answer == "Bugungi kiritilgan ilmiy ma'lumotlarni o'qib eshittiraman":
            if(os.path.isfile('knowledgeNotes.json')):
                knowledgeNotesRaw = open('knowledgeNotes.json')
                knowledgeNotes = json.load(knowledgeNotesRaw)
                knowledgeNotesRaw.close()
            else:
                speech_synthesizer.speak_text_async("Ilmiy ma'lumotlar bazasi topilmadi")

            knowledgeNotesText = []
            knowledgeNotesDate = []


            for q in knowledgeNotes["dates"]:
                date = datetime.strptime(q, '%y-%m-%d')
                date_final = date.strftime('%y-%m-%d')
                knowledgeNotesDate.append(date_final)

            for i in knowledgeNotes["notes"]:
                knowledgeNotesText.append(i)

            knowledgeNotesArray = np.stack((knowledgeNotesText, knowledgeNotesDate), axis=1)

            speakingKnowledgeNotes = []

            for data in knowledgeNotesArray:
                if data[1] == mydate:
                    speakingKnowledgeNotes.append(data[0])


            if len(speakingKnowledgeNotes) == 0:
                speech_synthesizer.speak_text_async("Bugungi kiritilgan ilmiy ma'lumotlar mavjud emas")
            else:
                speech_synthesizer.speak_text_async("Bugungi kiritilgan ilmiy ma'lumotlarni o'qib eshittiraman")
                for note in speakingKnowledgeNotes:
                    speech_synthesizer.speak_text_async(note)
            return 1
        if answer == "Bugungi kiritilgan umumiy ma'lumotlarni o'qib eshittiraman":

            if(os.path.isfile('generalNotes.json')):  
                generalNotesRaw = open('generalNotes.json')
                generalNotes = json.load(generalNotesRaw)
                generalNotesRaw.close()
            else:
                speech_synthesizer.speak_text_async("Umumiy ma'lumotlar bazasi topilmadi")

            generalNotesText = []
            generalNotesDate = []


            for k in generalNotes["dates"]:
                date = datetime.strptime(k, '%y-%m-%d')
                date_final = date.strftime('%y-%m-%d')
                generalNotesDate.append(date_final)

            for t in generalNotes["notes"]:
                generalNotesText.append(t)

            generalNotesArray = np.stack((generalNotesText, generalNotesDate), axis=1)

            speakingGeneralNotes = []

            for data in generalNotesArray:
                if data[1] == mydate:
                    speakingGeneralNotes.append(data[0])

            if len(speakingGeneralNotes) == 0:
                speech_synthesizer.speak_text_async("Bugungi kiritilgan umumiy ma'lumotlar mavjud emas")
            else:
                speech_synthesizer.speak_text_async("Bugungi kiritilgan umumiy ma'lumotlarni o'qib eshittiraman")
                for note in speakingGeneralNotes:
                    speech_synthesizer.speak_text_async(note)


            return 1
    
    elif(voice_activation == 1): 
        wikipedia.set_lang("uz")
        sayfer_status = "offline" 
     
        if(sayfer_status == "offline"):
            query = speech_recognizer.recognize_once_async().get().text
            print(query)
            if(robot_name in query.lower()):
                sayfer_status = "online"

        if(sayfer_status == "online"):

            playsound('audio.mp3', block=False)
            query = speech_recognizer.recognize_once_async().get().text
            answer = day_filter(year_filter(get_response(query)))
            print(query)

            get_response(query)

            #Wikipedia knowledge base inclusion (Wikipedia dan qidirish)
            if ("haqida" in query):
                sayfer_status = "offline"
                try:
                    wiki_question = query.split(' haqida', 1)[0]
                    suggested_wiki_answer = wikipedia.suggest(f"{wiki_question}")             

                    try:
                        speech_synthesizer.speak_text_async(f"{wiki_question} haqida qidiryabman").get()
                        wiki_answer = wikipedia.summary(wiki_question, sentences=3)
                    except wikipedia.DisambiguationError as e:
                        s = e.options[-1]
                        wiki_answer = wikipedia.summary(s, sentences=3)

                    speech_synthesizer.speak_text_async(day_filter(year_filter(wiki_answer))).get()
                    
                    return 1
                except Exception as e:
                    print(e)

            #Dasturlarni ochish
            if("Xrom" in answer):
                call(["chrome.exe"])
                sayfer_status = "offline"
                return 1
            elif("Kalkulyator" in answer):
                call(["calc.exe"])
                sayfer_status = "offline"
                return 1
            elif("Telegram" in answer):
                subprocess.Popen("c:\\Users\\Peter\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe")
                sayfer_status = "offline"
                return 1

            #Soatni so'rash
            sayfer_status = "online"
            if ("soat" in query.lower()):
                currentTime = get_current_time()
                speech_synthesizer.speak_text_async(currentTime).get()
                sayfer_status = "offline"
                return 1

            if(sayfer_status != "offline"):
                #Buyruq aniqlanmagan holatda
                if(answer == "tushunmadim"):
                    sayfer_status = "offline"
                    speech_synthesizer.speak_text_async("tushunmadim").get()
                else:
                    answer = day_filter(year_filter(answer))
                    speech_synthesizer.speak_text_async(answer).get()
                    return 1
    return 0
def run_gpt3(question, chat_log=None):
  global session_prompt
  if chat_log is None: 
    chat_log = session_prompt 

  prompt_text = f'{chat_log}{restart_sequence}: {question}{start_sequence}:'
  
  response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt_text,
    temperature=0.9,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.6,
    stop=[" Human:", " AI:"]
    #stop=["\n"],
  )
  story = response['choices'][0].text

  session_prompt = f'{chat_log}{restart_sequence}: {question}{start_sequence}: {story}:'
  return str(story)


if __name__ == "__main__":
    while True:
        #run_app()
        #if run_app() != 1:
        activation = speech_recognizer.recognize_once_async().get().text.lower()
        if('sayfer' in activation):
            playsound('audio.mp3', block=False)
            qinUz = speech_recognizer.recognize_once_async().get().text.lower()
            qinEn = uzbek_to_english(qinUz)
            aninEn = run_gpt3(qinEn)
            aninUz = english_to_uzbek(aninEn)

            print(aninUz)