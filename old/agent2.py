import os
from dotenv import load_dotenv
load_dotenv("API_key.env")
from openai import OpenAI
from video_tags import VIDEO_TAGS
import base64
import json   

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)
    
# extract all unique emotions and keywords from VIDEO_TAGS
all_emotions = list(set(e for v in VIDEO_TAGS.values() for e in v["emotions"]))
all_keywords = list(set(k for v in VIDEO_TAGS.values() for k in v["keywords"]))

def _encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def tag_meme(caption, image_path="template/example_output.png"):
    base64_image = _encode_image(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": f"""
                    Look at this meme and return the most matching emotions and keywords.
                    You MUST only use emotions and keywords from these lists:

                    Available emotions: {", ".join(all_emotions)}
                    Available keywords: {", ".join(all_keywords)}

                    Caption: {caption}

                    Reply in this exact format, nothing else:
                    emotions: emotion1, emotion2
                    keywords: keyword1, keyword2, keyword3
                """},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }}
            ]}
        ]
    )

    text = response.choices[0].message.content
    lines = text.strip().split("\n")

    emotions = lines[0].replace("emotions:", "").strip().split(", ")
    keywords = lines[1].replace("keywords:", "").strip().split(", ")

    return {
        "emotions": emotions,
        "keywords": keywords
    }

# test it
if __name__ == "__main__":
    with open("template/chosen_post.json", "r") as f:
        post = json.load(f)
    result = tag_meme(post["caption"])
    print(result)