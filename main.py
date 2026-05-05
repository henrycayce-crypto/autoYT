import json
import random
from pathlib import Path

from webscraping import (
    get_top_posts,
    load_seen_posts,
    save_seen_posts,
    display_posts,
    SUBREDDITS,
    POST_LIMIT,
    TIME_FILTER,
)

from memetemplate import build_meme
from agent import analyze_meme
from combine import build_video, MEME_PATH, OUTPUT_PATH
from youtube_upload import upload_video


CHOSEN_POST_PATH = Path("template/chosen_post.json")
AGENT_OUTPUT_PATH = Path("template/agent_output.json")
FINAL_VIDEO_PATH = Path(OUTPUT_PATH)

UPLOAD_TO_YOUTUBE = True
ASK_BEFORE_UPLOAD = True


def choose_reddit_post():
    seen_posts = load_seen_posts()

    for subreddit in SUBREDDITS:
        posts = get_top_posts(subreddit, POST_LIMIT, TIME_FILTER)

        if not posts:
            continue

        unseen = [p for p in posts if p["post_link"] not in seen_posts]

        if not unseen:
            print(f"All posts seen for r/{subreddit}. Resetting history.")
            seen_posts = []
            unseen = posts

        chosen = random.choice(unseen)
        display_posts(subreddit, [chosen])

        CHOSEN_POST_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(CHOSEN_POST_PATH, "w") as f:
            json.dump(
                {
                    "caption": chosen["title"],
                    "image_url": chosen["image_url"],
                    "post_link": chosen["post_link"],
                },
                f,
                indent=2,
            )

        seen_posts.append(chosen["post_link"])
        save_seen_posts(seen_posts)

        return chosen

    raise RuntimeError("No usable Reddit posts found.")


def save_agent_output(agent_output):
    AGENT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(AGENT_OUTPUT_PATH, "w") as f:
        json.dump(agent_output, f, indent=2)


def confirm_upload():
    if not ASK_BEFORE_UPLOAD:
        return True

    confirm = input("Upload final_output.mp4 to YouTube? Type YES to continue: ")
    return confirm == "YES"


def main():
    print("Step 1: Choosing Reddit post.")
    post = choose_reddit_post()

    print("Step 2: Building meme image.")
    build_meme(
        caption=post["title"],
        image_url=post["image_url"],
    )

    print("Step 3: Running agent.")
    agent_output = analyze_meme(post["title"])
    save_agent_output(agent_output)

    print("Step 4: Building final video.")
    build_video(
        meme_path=MEME_PATH,
        clip_name=agent_output["video"],
        caption=agent_output["caption"],
        output_path=OUTPUT_PATH,
    )

    if not FINAL_VIDEO_PATH.exists():
        raise FileNotFoundError(f"Final video was not created: {FINAL_VIDEO_PATH}")

    if UPLOAD_TO_YOUTUBE:
        print("Step 5: Preparing YouTube upload.")

        if confirm_upload():
            upload_video(str(FINAL_VIDEO_PATH))
        else:
            print("Upload cancelled.")
    else:
        print("Upload skipped.")


if __name__ == "__main__":
    main()