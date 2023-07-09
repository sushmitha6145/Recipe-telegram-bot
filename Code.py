import csv
import requests
import json
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

def get_some_recipes(csv_file, num_recipes):
    recipes = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            recipes.append(row['RecipeName'])
    unique_recipes = random.sample(recipes, num_recipes)
    return unique_recipes

# Example usage
recipe_dataset_file = 'IndianFoodDatasetCSV.csv'

def main():
    print("Welcome! I'm a chatbot capable of providing recipes.")
    print("Enter the dish name in this format: '<dishname> Recipe'")

    while True:
        user_input = input("User: ")
        if user_input == '/some_recipes':
            # Display a unique set of 25 recipes from the dataset
            recipe_list = get_some_recipes(recipe_dataset_file, 25)
            recipe_list_message = "Here are 25 unique recipes from the dataset:\n\n"
            for i, recipe in enumerate(recipe_list, start=1):
                recipe_list_message += f"{i}. {recipe}\n"
            print(recipe_list_message)
        else:
            # Extract and display the recipe information
            extract_recipe_info(recipe_dataset_file, user_input, 1)

if __name__ == "__main__":
    main()
