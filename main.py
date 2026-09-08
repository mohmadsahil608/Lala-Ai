import os
import json
import urllib.request
import urllib.error

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

from plyer import stt, tts


API_KEY = os.environ.get("LALA_API_KEY", "PASTE_API_KEY_HERE")

MODEL = "gpt-5.6-luna"
MEMORY_FILE = "lala_memory.txt"

SYSTEM_PROMPT = """
You are Lala, my personal JARVIS-style AI assistant.
Call me Boss.
Be intelligent, concise and helpful.
Help with AI, programming, robotics, electronics,
engineering, automation, Android, computers and general tasks.
"""


def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def save_memory(text):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def ask_ai(question):
    memory = load_memory()

    prompt = f"""
Saved memory:
{memory}

Boss:
{question}
"""

    data = {
        "model": MODEL,
        "instructions": SYSTEM_PROMPT,
        "input": prompt
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + API_KEY,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "output_text" in result:
        return result["output_text"]

    text = ""

    for item in result.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text += content.get("text", "")

    return text or "No response received."


class LalaApp(App):

    def build(self):
        Window.clearcolor = (0.01, 0.01, 0.015, 1)

        main = BoxLayout(
            orientation="vertical",
            padding=12,
            spacing=8
        )

        header = Label(
            text="L A L A   A I",
            font_size=28,
            size_hint_y=None,
            height=60
        )
        main.add_widget(header)

        self.status = Label(
            text="SYSTEM ONLINE",
            font_size=15,
            size_hint_y=None,
            height=35
        )
        main.add_widget(self.status)

        self.chat = Label(
            text="Lala: Systems initialized.\n"
                 "Lala: Memory online.\n"
                 "Lala: Voice system ready.\n\n",
            font_size=16,
            halign="left",
            valign="top",
            size_hint_y=None
        )

        self.chat.bind(
            width=lambda instance, value:
            setattr(instance, "text_size", (value, None))
        )

        self.chat.bind(
            texture_size=lambda instance, value:
            setattr(instance, "height", value[1])
        )

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        scroll.add_widget(self.chat)
        main.add_widget(scroll)

        self.scroll = scroll

        self.input_box = TextInput(
            hint_text="Command Boss...",
            multiline=False,
            font_size=18,
            size_hint_y=None,
            height=55
        )

        self.input_box.bind(
            on_text_validate=self.send_message
        )

        main.add_widget(self.input_box)

        buttons = BoxLayout(
            size_hint_y=None,
            height=60,
            spacing=8
        )

        send = Button(
            text="SEND",
            font_size=18
        )
        send.bind(on_press=self.send_message)

        voice = Button(
            text="MIC",
            font_size=18
        )
        voice.bind(on_press=self.start_voice)

        buttons.add_widget(send)
        buttons.add_widget(voice)

        main.add_widget(buttons)

        stt.result_callback = self.on_voice_result
        stt.partial_result_callback = self.on_voice_partial
        stt.error_callback = self.on_voice_error

        return main

    def send_message(self, instance):
        question = self.input_box.text.strip()

        if not question:
            return

        if question.lower().startswith("remember:"):
            memory = question[9:].strip()

            if memory:
                save_memory(memory)
                answer = "Memory saved, Boss."
            else:
                answer = "Tell me what to remember."

            self.show_message(question, answer)
            return

        self.show_message(question, "Thinking...")

        try:
            answer = ask_ai(question)
        except Exception as e:
            answer = "Connection error:\n" + str(e)

        self.chat.text += "Lala: " + answer + "\n"

        try:
            tts.speak(answer)
        except:
            pass

        Clock.schedule_once(
            lambda dt: setattr(self.scroll, "scroll_y", 0),
            0.1
        )

    def show_message(self, question, answer):
        self.chat.text += (
            "\nBoss: " + question +
            "\nLala: " + answer +
            "\n"
        )

        self.input_box.text = ""

        try:
            tts.speak(answer)
        except:
            pass

        Clock.schedule_once(
            lambda dt: setattr(self.scroll, "scroll_y", 0),
            0.1
        )

    def start_voice(self, instance):
        try:
            self.status.text = "LISTENING..."
            self.chat.text += "\nLala: Listening...\n"
            stt.start()
        except Exception as e:
            self.status.text = "MIC ERROR"
            self.chat.text += "Lala: " + str(e) + "\n"

    def on_voice_partial(self, results):
        if results:
            self.status.text = "HEARING..."
            self.input_box.text = results[0]

    def on_voice_result(self, results):
        if results:
            self.status.text = "VOICE RECEIVED"
            self.input_box.text = results[0]
            self.send_message(None)

    def on_voice_error(self, error):
        self.status.text = "VOICE ERROR"
        self.chat.text += "Voice error: " + str(error) + "\n"


if __name__ == "__main__":
    LalaApp().run()
