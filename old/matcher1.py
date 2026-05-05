# matcher.py
from video_tags import VIDEO_TAGS
import random

def match_video(meme_tags):
    meme_emotions = set(meme_tags["emotions"])
    meme_keywords = set(meme_tags["keywords"])

    best_video = None
    best_score = -1
    tied_videos = []

    for video, tags in VIDEO_TAGS.items():
        video_emotions = set(tags["emotions"])
        video_keywords = set(tags["keywords"])

        # count overlapping emotions and keywords
        emotion_overlap = len(meme_emotions & video_emotions)
        keyword_overlap = len(meme_keywords & video_keywords)

        # emotions weighted more heavily than keywords
        score = (emotion_overlap * 2) + keyword_overlap

        if score > best_score:
            best_score = score
            best_video = video
            tied_videos = [video]
        elif score == best_score:
            tied_videos.append(video)  # track ties

    # if multiple videos have same score pick randomly between them
    if len(tied_videos) > 1:
        best_video = random.choice(tied_videos)

    # if nothing matched at all just pick a random video
    if best_score == 0:
        print("no match found, picking random video")
        best_video = random.choice(list(VIDEO_TAGS.keys()))
    else:
        print(f"matched to {best_video} with score {best_score}")

    return best_video

# test it - actually use the agent output
if __name__ == "__main__":
    from agent import tag_meme
    
    # use the same caption as agent test
    tags = tag_meme("My wife is a vet tech and took this photo today")
    print(f"agent returned: {tags}")
    
    result = match_video(tags)
    print(f"selected video: {result}")