import sys
from datetime import datetime
import openai
import speech_recognition as sr
import pyttsx3
from selenium import webdriver
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QTextEdit, QVBoxLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
import requests
from bs4 import BeautifulSoup

openai.api_key = "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"

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

class VoiceAssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Assistant (Siri-like UI)")
        self.resize(600, 1024)  # Set the resolution to 720x1280
        self.conversation_text = QTextEdit(self)
        self.voice_button = QLabel(self)

        gif_path = 'C:/Users/ARG/Downloads/mic3.gif'
        movie = QMovie(gif_path)
        movie.start()

        self.voice_button.setMovie(movie)
        self.voice_button.setAlignment(Qt.AlignCenter)

        with open("styles.css", "r") as f:
            self.setStyleSheet(f.read())

        layout = QVBoxLayout(self)
        layout.addWidget(self.conversation_text)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.voice_button)
        layout.addLayout(input_layout)

        self.voice_button.setCursor(Qt.PointingHandCursor)
        self.voice_button.setObjectName("voiceButton")
        self.voice_button.mousePressEvent = self.start_listening

        self.browser_driver = None
        self.search_requested = False
        self.fixed_city_code = '5a7fd26b6bc2db9f846a7786c0bbf7b3ce88cc99b90895785c5b75c3e77045ab'

    def launch_browser(self, url):
        driver = webdriver.Edge()
        driver.get(url)
        return driver

    def send_message(self, query):
        if any(keyword in query.lower() for keyword in ["what time is", "what is the time"]):
            self.extract_time(query)
        elif "music" in query.lower():
            self.handle_music_request(query)
        else:
            response = get_chatgpt_response(query)
            self.handle_response(response)

    def handle_music_request(self, query):
        if "music" in query.lower():
            if "search" in query.lower():
                song_to_search = self.extract_search_term(query)
                if song_to_search:
                    spotify_search_url = f"https://open.spotify.com/search/{song_to_search}"
                    self.handle_search_task(spotify_search_url)
            else:
                self.handle_search_task("https://open.spotify.com/")

    def extract_weather(self, query):
        # Directly use the fixed city code
        self.get_weather(self.fixed_city_code)

    def get_weather(self, city_code):
        base_url = f'https://weather.com/en-IN/weather/today/l/{city_code}'

        response = requests.get(base_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            temperature_element = soup.find('span', {'data-testid': 'TemperatureValue'})
            condition_element = soup.find('div', {'data-testid': 'wxPhrase'})

            if temperature_element and condition_element:
                temperature = temperature_element.text.strip()
                condition = condition_element.text.strip()

                weather_info = f"Weather in Dehmi Kalan is {temperature}, {condition}"
                print(weather_info)
                self.handle_response(weather_info)
            else:
                error_message = "Error: Unable to find temperature or condition elements on the page"
                print(error_message)
                self.handle_response(error_message)
        else:
            error_message = f"Error: Unable to fetch weather information for {city_code}"
            print(error_message)
            self.handle_response(error_message)

    def handle_response(self, response):
        self.conversation_text.append("ChatGPT: " + response + "\n")
        self.conversation_text.moveCursor(self.conversation_text.textCursor().End)  # Move cursor to the end
        self.conversation_text.ensureCursorVisible()  # Ensure cursor visibility
        engine.say(response)
        engine.runAndWait()

    def start_listening(self, event):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)

            try:
                query = r.recognize_google(audio)
                self.send_message(query)

            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print("Request error; {0}".format(e))

    def extract_search_term(self, query):
        keywords = ["search", "music"]  # Adjust keywords as needed
        for keyword in keywords:
            if keyword in query.lower():
                search_term = query.lower().split(keyword)[-1].strip()
                return search_term

        return None

    def handle_search_task(self, url):
        if not self.browser_driver:
            self.browser_driver = self.launch_browser(url)
        else:
            self.browser_driver.get(url)

def get_chatgpt_response(query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    app = QApplication([])
    window = VoiceAssistantWindow()
    window.show()
    sys.exit(app.exec_())
