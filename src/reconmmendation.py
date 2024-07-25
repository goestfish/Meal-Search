import random
import openai
import json
import os, time

# Configure your OpenAI API key
openai.api_key = ''


def generate_recommendation():
    with open('../meal.txt', 'r') as file:
        meals = json.load(file)
    meal = random.choice(meals)

    # Generate AI recommendation using OpenAI API with retry logic
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a assistant working for Dish Discover."},
                    {"role": "user",
                     "content": f"Suggest a meal: {meal}. Your content must ends with 'Thank you for choosing Dish Discoverer'"}
                ]
            )
            ai_recommendation = response['choices'][0]['message']['content'].strip()
            return ai_recommendation
        except openai.error.RateLimitError:
            if attempt < 2:
                time.sleep(5)  # Wait for 5 seconds before retrying
            else:
                return "Rate limit exceeded. Please try again later."