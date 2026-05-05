from moviepy import ImageClip, VideoFileClip, CompositeVideoClip, TextClip
import os
import json

# paths
MEME_PATH = "template/example_output.png"
CLIPS_FOLDER = "clips"
OUTPUT_PATH = "final_output.mp4"

# dimensions
FINAL_WIDTH = 1080
FINAL_HEIGHT = 1920
HALF_HEIGHT = FINAL_HEIGHT // 2  # 960

def _resize_crop(clip, target_w, target_h):
    clip_ratio = clip.w / clip.h
    target_ratio = target_w / target_h

    if clip_ratio > target_ratio:
        clip = clip.resized(height=target_h)
    else:
        clip = clip.resized(width=target_w)

    clip = clip.cropped(
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=target_w,
        height=target_h
    )
    return clip

def _add_caption(video, caption):
    caption_clip = (TextClip(
        text=caption,
        font="/Library/Fonts/Arial Bold.ttf",
        font_size=60,
        color="black",         # black text inside
        stroke_color="white",  # white outline
        stroke_width=3,        # slightly thicker for visibility
        size=(904, 200),
        method="caption",
        text_align="center"
    )
    .with_duration(video.duration)
    .with_position(("center", FINAL_HEIGHT // 2 - 35 )))
    
    return CompositeVideoClip([video, caption_clip])

def build_video(meme_path, clip_name, caption, output_path=OUTPUT_PATH):
    video = VideoFileClip(os.path.join(CLIPS_FOLDER, clip_name))

    video_resized = _resize_crop(video, FINAL_WIDTH, HALF_HEIGHT)
    meme = ImageClip(meme_path).with_duration(video.duration)
    meme_resized = _resize_crop(meme, FINAL_WIDTH, HALF_HEIGHT)

    meme_positioned = meme_resized.with_position((0, 0))
    video_positioned = video_resized.with_position((0, HALF_HEIGHT))

    final = CompositeVideoClip(
        [meme_positioned, video_positioned],
        size=(FINAL_WIDTH, FINAL_HEIGHT)
    )
    final = _add_caption(final, caption)
    final = final.with_audio(video.audio)
    final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")
    print(f"video saved to {output_path}")

if __name__ == "__main__":
    with open("template/agent_output.json", "r") as f:
        agent_output = json.load(f)
    build_video(MEME_PATH, agent_output["video"], agent_output["caption"])