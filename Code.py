import csv
import requests
import json

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
                process = row['Instructions']
                steps = []
                current_step = ""
                for char in process:
                    current_step += char
                    if char == '.':
                        if current_step[-2:].isdigit():
                            continue
                        else:
                            steps.append(current_step.strip())
                            current_step = ""

                for step, instruction in enumerate(steps, start=1):
                    response += f"{step}. {instruction.strip()}\n"

                # Send the response message to the specified chat_id
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

# Example usage
recipe_dataset_file = '/IndianFoodDatasetCSV.csv'

def handle_updates(updates):
    for update in updates:
        if 'message' in update:
            message = update['message']
            text = message.get('text')
            chat_id = message['chat']['id']
            if text:
                extract_recipe_info(recipe_dataset_file, text, chat_id)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
offset = None

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
        print('Error occurred while retrieving updates.')
