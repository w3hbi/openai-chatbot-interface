import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

import openai
import json

kivy.require("1.10.1")


def connect():
    with open('API_KEY.json') as file:
        data = json.load(file)

    openai.api_key = data["API_KEY"]


class ScrollableLabel(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)

        self.chat_history = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label()

        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    # Methods called externally to add new message to the chat history
    def update_chat_history(self, message):
        # First add new line and message itself
        self.chat_history.text += '\n' + message

        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.90, None)

        self.scroll_to(self.scroll_to_point)


class ChatPage(App):
    def __init__(self):
        super().__init__()

        self.window = GridLayout()

        # We are going to use 1 column and 2 rows
        self.window.cols = 1
        self.window.rows = 2

        # First row is going to be occupied by our scrollable label
        # We want it be take 90% of app height
        self.history = ScrollableLabel(height=self.window.size[1] * 5, size_hint_y=None)

        self.new_message = TextInput(width=self.window.size[0] * 6, size_hint_x=None, multiline=False)
        self.send = Button(text="Send", background_color='#00FFCE')
        self.send.bind(on_press=self.send_message)

        self.bottom_line = GridLayout(cols=2)
        self.bottom_line.add_widget(self.new_message)
        self.bottom_line.add_widget(self.send)

        self.window.size = (800, 680)

    def send_message(self, _):
        # Get message text and clear message input field
        message = self.new_message.text
        self.new_message.text = ''

        PROMPT = """The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.

        Human: Hello, who are you?
        AI: I am an AI created by OpenAI. How can I help you today?
        """

        if message:
            # Our messages - use red color for the name
            self.history.update_chat_history(f'[color=dd2020]Me[/color]  > {message}')

            start_sequence = "\nAI:"
            restart_sequence = "\nHuman: "

            PROMPT = PROMPT + restart_sequence + message + start_sequence

            response = openai.Completion.create(
                engine="davinci",
                prompt=PROMPT,
                temperature=0.9,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
                stop=["\n", " Human:", " AI:"]
            )

            self.history.update_chat_history(f'[color=555855]Bot[/color]  > {response.choices[0].text}')

    def build(self):

        self.window.add_widget(self.history)
        self.window.add_widget(self.bottom_line)

        return self.window


# run Say Hello App Class
if __name__ == "__main__":
    connect()
    ChatPage().run()
