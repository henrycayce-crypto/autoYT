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


def _encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _clean_json_response(text):
    text = text.strip()

    # Handles cases where the model accidentally wraps JSON in a markdown code block.
    if text.startswith("```"):
        text = text.split("```", 2)[1].strip()
        if text.startswith("json"):
            text = text[4:].strip()

    return text


def analyze_meme(caption, image_path="template/example_output.png"):
    base64_image = _encode_image(image_path)

    # Build video options string including descriptions.
    video_options = "\n".join([
        f"- {filename}: {data['description']}"
        for filename, data in VIDEO_TAGS.items()
    ])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
Look at this meme and do three things:

1. Choose the best matching video from this list based on the meme's emotion and content:
{video_options}

2. Generate a short funny caption under 60 characters that connects the meme to the chosen video.
Caption rules:
- Do not use emojis.
- Write like you are texting a friend.
- Keep it casual and colloquial.
- Use lowercase as much as possible.
- Try to avoid using ! and ?

3. Generate a YouTube Shorts description in this exact structure:

A short funny meme video: [brief meme description] X [brief video description]


#meme #cyall #pfft #zdak [add up to 4 other relevant hashtags]

Thanks for watching!!!

Description rules:
- Keep the meme description brief.
- Keep the video description brief.
- Include the fixed hashtags exactly: #meme #cyall #pfft #zdak.
- Add no more than 4 extra hashtags.
- Do not add extra sections or extra commentary.

Meme caption: {caption}

Reply in valid JSON only, nothing else:
{{
    "video": "filename.mp4",
    "caption": "short caption here",
    "description": "full YouTube description here"
}}
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    text = response.choices[0].message.content.strip()
    result = json.loads(_clean_json_response(text))

    return {
        "video": result["video"],
        "caption": result["caption"],
        "description": result["description"]
    }


# test it
if __name__ == "__main__":
    with open("template/chosen_post.json", "r") as f:
        post = json.load(f)

    result = analyze_meme(post["caption"])

    with open("template/agent_output.json", "w") as f:
        json.dump(result, f, indent=2)

    print(result)