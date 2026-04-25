# meme automation pipline
# takes reddit posts, slaps an ai image on it, pairs with a meme clip
# outputs a short form vertical video ready to post

import os
import json
import praw
import requests
from pathlib import Path  #maybe beuatiful soup too

'''
sample data strutures (this is what flows thru the pipline)
'''

SAMPLE_POST = {
    "id": "abc123",
    "text": "i spent 3 hours cooking and my roomate ordered pizza anyway",
    "upvotes": 4200,
    "emotion": None,      # filled in later
    "image_path": None,   # filled in later
    "clip_path": None     # filled in later
}

SAMPLE_CLIP = {
    "filename": "clip_047.mp4",
    "primary_emotion": "angry",
    "vibe": "betrayed energy",
}

'''
module 1 - reddit scraper
scrapes short relatable posts above a like threshold
filters out anything too long or already seen befoer
'''

class RedditScraper:
    def __init__(self, client_id, client_secret):
        # TODO: connect to reddit via praw
        # TODO: load cache of seen post ids so we dont repost
        pass

    def scrape(self, subreddits, min_upvotes=1000):
        # TODO: loop thru subreddits
        # TODO: filter for short text only posts
        # TODO: skip anything already in cache
        # TODO: return list of SAMPLE_POST dicts
        pass


'''
module 2 - emotion detector
sends post text to an llm and gets back an emotion label
caches results so we dont waste api calls
'''

class EmotionDetector:
    def __init__(self, api_key):
        # TODO: init openai client
        # TODO: load emotion cache from disk
        pass

    def analyze(self, post):
        # TODO: build a prompt asking llm for emotion in json format
        # TODO: call gpt-4o with the post text
        # TODO: parse response and atach emotion to post dict
        # TODO: save to cache by post id
        pass


'''
module 3 - clip matcher
scans local /clips folder and tags each clip with an emotion
finds the best matching clip for a given post emotion
'''

class ClipMatcher:
    def __init__(self, clips_folder="clips"):
        # TODO: load or create clips_manifest.json
        # TODO: scan for any untagged clips and send to llm
        pass

    def find_match(self, emotion):
        # TODO: search manifest for clips matching the emotion
        # TODO: return path to best match
        pass


'''
module 4 - image generator
  -turns the post text into a dalle3 image prompt
  -saves image locally and returns the path
'''

class ImageGenerator:
    def __init__(self, api_key):
        # TODO: init openai client
        pass

    def generate(self, post):
        # TODO: ask gpt to turn post text into a visual scene descrption
        # TODO: append a consistent style suffix for channel brandign
        # TODO: call dalle3 and save the image
        # TODO: return local image path
        pass


'''
module 5 - video composer
stacks the ai image on top and meme clip on botom
adss the post text as an overlay and exports as 1080x1920
'''

class VideoComposer:
    def compose(self, post, image_path, clip_path):
        # TODO: load and resize image to top half
        # TODO: load and resize clip to botom half
        # TODO: overlay post text with word by word animation
        # TODO: add quiet background music
        # TODO: export to /output as mp4
        pass


#main pulls everything together

def run():
    scraper = RedditScraper("client_id", "client_secret")
    detector = EmotionDetector("openai_key")
    matcher = ClipMatcher()
    generator = ImageGenerator("openai_key")
    composer = VideoComposer()

    posts = scraper.scrape(["mildlyinfuriating", "tifu", "trueoffmychest"])

    for post in posts:
        detector.analyze(post)
        clip = matcher.find_match(post["emotion"])
        image = generator.generate(post)
        composer.compose(post, image, clip)
        print(f"done: {post['text'][:40]}")

if __name__ == "__main__":
    run()