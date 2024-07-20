import json
import os
import random
import re
from collections import defaultdict, Counter

# ChatBot class
class ChatBot:
    def __init__(self):
        self.model = defaultdict(Counter)
        self.version = '1.0.2'
        self.history = []

    def load_model(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                model_data = json.load(file)
                self.model = defaultdict(Counter, {k: Counter(v) for k, v in model_data.items()})
        else:
            print(f"Model file '{filename}' not found. Starting with empty model.")

    def save_model(self, filename):
        model_data = {k: dict(v) for k, v in self.model.items()}
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(model_data, file)

    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def generate_response(self, sentence):
        words = self.tokenize(sentence)
        if not words:
            return "I dont understand"

        # Użycie historii do generowania odpowiedzi
        context_words = self.get_context_words()
        if context_words:
            words += context_words

        current_word = random.choice(words)
        generated_response = [current_word]
        for _ in range(len(words)):
            next_words = list(self.model[current_word].elements())
            if not next_words:
                break
            next_word = random.choice(next_words)
            generated_response.append(next_word)
            current_word = next_word

        return ' '.join(generated_response)

    def get_context_words(self):
        # Wyodrębnij słowa z ostatnich kilku wymian w historii
        context_words = []
        for exchange in self.history[-3:]:  # Ostatnie 3 wymiany
            context_words += self.tokenize(exchange['user'])
            context_words += self.tokenize(exchange['bot'])
        return context_words

    def learn_from_input(self, sentence, response):
        sentence_words = self.tokenize(sentence)
        response_words = self.tokenize(response)
        self.learn_sequence(sentence_words)
        self.learn_sequence(response_words)

    def learn_sequence(self, words):
        for i in range(len(words) - 1):
            current_word = words[i]
            next_word = words[i + 1]
            self.model[current_word][next_word] += 1

    def update_history(self, user_input, bot_response):
        self.history.append({'user': user_input, 'bot': bot_response})
        if len(self.history) > 4:
            self.history.pop(0)

    def train_from_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for i in range(0, len(lines) - 1, 2):
                    user_input = lines[i].strip()
                    response = lines[i + 1].strip()
                    self.learn_from_input(user_input, response)
        else:
            print(f"Training file '{filename}' not found.")

def main():
    bot = ChatBot()
    model_filename = 'model.json'
    bot.load_model(model_filename)

    print("Welcome!")

    while True:
        user_input = input("you: ").strip()
        if user_input:
            if user_input.lower() in ['.koniec', '.exit', '.quit']:
                bot.save_model(model_filename)
                break
            elif user_input.lower() in ['.save']:
                bot.save_model(model_filename)
            elif user_input.lower() in ['.train']:
                bot.train_from_file('data.txt')
            else:
                if user_input.lower() in ['.version']:
                    response = f"--version: {bot.version}--"
                elif user_input.lower() in ['.about']:
                    response = f"VAI its an ai made by Funcieq and Keyyq / Raynixx. \n version: {bot.version}"
                else:
                    response = bot.generate_response(user_input)
                    bot.learn_from_input(user_input, response)
                    bot.update_history(user_input, response)
                print(f"VAI: {response}")

if __name__ == "__main__":
    main()
