import csv
import requests
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import random

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = '6367686078:AAFlTgxSDN2j2AW83f9Smlz_FZBaMTgZ2GE'

def extract_recipe_info(csv_file, recipe_name, chat_id):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['RecipeName'].lower() == recipe_name.lower():
                response = f"Recipe: {row['RecipeName']}\n\nIngredients:\n"
                ingredients = row['Ingredients'].split(',')
                for ingredient in ingredients:
                    response += f"- {ingredient.strip()}\n"

                response += "\nProcess:\n"
                input_text = row['Instructions']
                encoded_input = tokenizer.encode(input_text, return_tensors='pt')
                output = model.generate(encoded_input, max_length=100, num_return_sequences=1, temperature=0.7)
                generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
                response += generated_text

                send_message(chat_id, response)
                return

    send_message(chat_id, f"Recipe '{recipe_name}' not found in the dataset.")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, json=params)

def handle_message(message):
    chat_id = message['chat']['id']
    text = message['text']

    if text == '/start':
        welcome_message = "Welcome! I'm a chatbot capable of providing recipes.\n"\
                          "\nPlease enter the dish name in this format: '<dishname> Recipe'\n\nEnter /some_recipes to get 25 random recipes for every click"
        send_message(chat_id, welcome_message)
    elif text == '/some_recipes':
        recipe_list = get_some_recipes(recipe_dataset_file, 25)
        recipe_list_message = "Here are 25 unique recipes from the dataset:\n\n"
        for i, recipe in enumerate(recipe_list, start=1):
            recipe_list_message += f"{i}. {recipe}\n"
        send_message(chat_id, recipe_list_message)
    else:
        extract_recipe_info(recipe_dataset_file, text, chat_id)

def handle_updates(updates):
    for update in updates:
        if 'message' in update:
            handle_message(update['message'])

def get_some_recipes(csv_file, num_recipes):
    recipes = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            recipes.append(row['RecipeName'])
    unique_recipes = random.sample(recipes, num_recipes)
    return unique_recipes

# Example usage
recipe_dataset_file = '/IndianFoodDatasetCSV.csv'

offset = None

# Load the pre-trained GPT-2 model and tokenizer
model_name = 'gpt2'
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

while True:
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {'offset': offset, 'timeout': 60}
    response = requests.get(url, params=params).json()

    if 'result' in response:
        updates = response['result']
        if updates:
            offset = updates[-1]['update_id'] + 1
            handle_updates(updates)
    else:
        print('Error occurred while retrieving updates from the Telegram API.')
