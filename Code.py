import csv
import requests
import json

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = '6367686078:AAFlTgxSDN2j2AW83f9Smlz_FZBaMTgZ2GE'

def extract_recipe_info(csv_file, recipe_name, chat_id):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        found_recipes = []
        for row in reader:
            if row['RecipeName'].lower() == recipe_name.lower():
                found_recipes.append(row)

        if found_recipes:
            for recipe in found_recipes:
                response = f"Recipe: {recipe['RecipeName']}\n\nIngredients:\n"
                ingredients = recipe['Ingredients'].split(',')
                for ingredient in ingredients:
                    response += f"- {ingredient.strip()}\n"

                response += "\nProcess:\n"
                process = recipe['Instructions']
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
        else:
            send_message(chat_id, f"No recipes found for '{recipe_name}' in the dataset.")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, json=params)

def handle_updates(updates):
    for update in updates:
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            if 'text' in message:
                text = message['text']
                # Check if the user entered the /start command
                if text == '/start':
                    welcome_message = "Welcome! I'm a chatbot capable of giving recipes.\n" \
                                      "Please enter the dish name in this format: '<dishname> Recipe'"
                    send_message(chat_id, welcome_message)
                else:
                    # Extract and display the recipe information
                    extract_recipe_info(recipe_dataset_file, text, chat_id)
            else:
                send_message(chat_id, "Please enter the recipe name.")

# Example usage
recipe_dataset_file ='IndianFoodDatasetCSV.csv'

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
