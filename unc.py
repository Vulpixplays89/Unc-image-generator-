import requests
import uuid
import json
import telebot
import time
from flask import Flask
from threading import Thread

BOT_TOKEN = "7718128084:AAFrT0BCk7lf3-sd15ByVFUZbD8T3a4tkAo"
bot = telebot.TeleBot(BOT_TOKEN)
PRIVATE_CHANNEL_ID = "-1002416741340"  # Updated private channel ID

app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run_http_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http_server)
    t.start()
    
    
# Function to generate session hash
def generate_session_hash():
    return str(uuid.uuid4()).replace("-", "")[:11]

# Function to get image URL
def get_image_url(prompt, chat_id):
    try:
        post_url = "https://ehristoforu-dalle-3-xl-lora-v2.hf.space/queue/join?__theme=light"
        session_hash = generate_session_hash()

        post_data = {
            "data": [
                prompt,
                "(deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, (NSFW:1.25)",
                True,
                1873092507,
                1024,
                1024,
                6,
                True
            ],
            "event_data": None,
            "fn_index": 3,
            "session_hash": session_hash,
            "trigger_id": 6
        }

        requests.post(post_url, json=post_data)
        
        # Simulating progress animation
        progress_messages = ["10%🟩⬜⬜⬜⬜⬜ ⏳", "30%🟩🟩⬜⬜⬜⬜ ⏳", "50%🟩🟩🟩⬜⬜⬜ ⏳", "69%🟩🟩🟩🟩⬜⬜ ⏳", "90%🟩🟩🟩🟩🟩⬜ ⏳", "✅ Done!"]
        progress_msg = bot.send_message(chat_id, "🎨 Generating image... Please wait!")
        
        for progress in progress_messages:
            time.sleep(2)
            bot.edit_message_text(f"🎨 Generating image... \n{progress}", chat_id, progress_msg.message_id)
        
        # Remove progress message when done
        time.sleep(1)
        bot.delete_message(chat_id, progress_msg.message_id)

        get_url = f"https://ehristoforu-dalle-3-xl-lora-v2.hf.space/queue/data?session_hash={session_hash}"

        with requests.get(get_url, stream=True) as get_response:
            for line in get_response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if "process_completed" in decoded_line:
                        data = json.loads(decoded_line.replace("data: ", ""))
                        image_url = data['output']['data'][0][0]['image']['url']
                        return image_url
    except Exception as e:
        print(f"Error: {e}")
    return None

# Command: /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = (
        "👋 **Welcome to the Image Generator Bot!**\n\n"
        "✨ Send me a prompt and I'll create an amazing image just for you!\n"
        "🚀 Let's get started!"
    )
    bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown')

# Handling text messages
@bot.message_handler(func=lambda message: True)
def handle_prompt(message):
    chat_id = message.chat.id
    user_username = message.from_user.username if message.from_user.username else "Unknown User"
    prompt = message.text

    image_url = get_image_url(prompt, chat_id)
    if image_url:
        bot.send_photo(chat_id, image_url, caption="✨ Here is your generated image!")
        
        # Forward to private channel with username
        bot.send_message(PRIVATE_CHANNEL_ID, f"📝 Prompt: {prompt}\n👤 From: @{user_username}")
        bot.send_photo(PRIVATE_CHANNEL_ID, image_url, caption="🔹 Generated Image")
    else:
        bot.send_message(chat_id, "😔 Sorry, image generation failed. Please try again!")

keep_alive ( )

# Start bot polling
if __name__ == '__main__':
    bot.polling(none_stop=True)