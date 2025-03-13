import whisper
import sys
import torch
import time

class Whis():
    def __init__(self):
        self.whisper_model = whisper.load_model("tiny", device="cuda:0")
        