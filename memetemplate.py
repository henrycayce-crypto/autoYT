from email.mime import image
import random
import requests  # used to download the image from the url
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from webscraping import get_top_posts, load_seen_posts, save_seen_posts, SUBREDDITS, POST_LIMIT, TIME_FILTER


# settings and variables
TEMPLATE_PATH = "template/memetemplate.png"
WATERMARK_PATH = "template/babomar_watermark.png"
OUTPUT_PATH = "template/example_output.png"
FONT_SIZE = 52
FONT_COLOR = (255, 255, 255)

# coordinates for where things get placed on the 1024x1024 template
CAPTION_X = 90
CAPTION_Y = 220
IMAGE_X = 60
IMAGE_Y = 330
IMAGE_WIDTH = 904
IMAGE_HEIGHT = 600
MAX_WIDTH = 1024 - (CAPTION_X * 2)

# watermark settings
WATERMARK_WIDTH = 200
WATERMARK_PADDING = 20


def build_meme(caption, image_url, output_path=OUTPUT_PATH):  # main function to build the meme

    # load the base template
    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(template)

    # load font, falls back to default if arial isnt found
    # fit font size to caption length and draw onto template
    CAPTION_HEIGHT = IMAGE_Y - CAPTION_Y
    font, wrapped_caption = _fit_font(caption, MAX_WIDTH, CAPTION_HEIGHT)
    draw.text((CAPTION_X, CAPTION_Y), wrapped_caption, font=font, fill=FONT_COLOR)

    # download and crop the scraped image into the template
    image = _load_image(image_url)
    if image:
        resized = _resize_to_fit(image, IMAGE_WIDTH, IMAGE_HEIGHT)

    # add watermark onto the resized image before pasting onto template
        resized = _add_watermark(resized)

        paste_x = IMAGE_X + ((IMAGE_WIDTH - resized.width) // 2)
        paste_y = IMAGE_Y + ((IMAGE_HEIGHT - resized.height) // 2)
        template.paste(resized, (paste_x, paste_y))

    # save the finished meme
    template.save(output_path)
    print(f"meme saved to {output_path}")
    return output_path

def _fit_font(caption, max_width, max_height):  # shrinks font until caption fits in box
    font_size = FONT_SIZE  # start at max size
    
    while font_size > 20:  # don't go smaller than 20
        try:
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                font = ImageFont.load_default()
        
        wrapped = _wrap_text(caption, font, max_width)
        
        # calculate total height of wrapped text
        lines = wrapped.split("\n")
        line_height = font_size * 1.2  # 1.2 = line spacing
        total_height = len(lines) * line_height
        
        if total_height <= max_height:
            return font, wrapped  # fits! return it
        
        font_size -= 2  # too big, try smaller
    
    return font, wrapped  # return whatever we have at minimum size

'''
def _add_watermark(image):
    watermark = Image.open(WATERMARK_PATH).convert("RGB")

    # resize watermark proportionally to WATERMARK_WIDTH
    original_width, original_height = watermark.size
    scale = WATERMARK_WIDTH / original_width
    new_height = int(original_height * scale)
    watermark = watermark.resize((WATERMARK_WIDTH, new_height))

    # bottom-right of the image area (904 x 560)
    start_x = IMAGE_WIDTH - WATERMARK_WIDTH - WATERMARK_PADDING   # 20px from right
    start_y = IMAGE_HEIGHT - new_height - WATERMARK_PADDING        # 20px from bottom

    image_pixels = image.load()
    watermark_pixels = watermark.load()

    watermark_width, watermark_height = watermark.size

    for y in range(watermark_height):
        for x in range(watermark_width):
            r, g, b = watermark_pixels[x, y]
            if r < 50 and g < 50 and b < 50:  # only black "Babomar" text pixels
                tx, ty = start_x + x, start_y + y
                image_pixels[tx, ty] = _darken(image_pixels[tx, ty], 40)

    return image


def _darken(pixel, level):  # darkens a pixel by a given level
    r, g, b = pixel
    r = max(0, r - (level * 5))
    g = max(0, g - (level * 5))
    b = max(0, b - (level * 5))
    return (r, g, b)
''' # here is code from out assignment that adds a watermark, but this becomes complicated for images with darker backrgounds

def _add_watermark(image):
    watermark = Image.open(WATERMARK_PATH).convert("RGBA")

    # resize watermark
    watermark = watermark.resize((WATERMARK_WIDTH, int(watermark.height * WATERMARK_WIDTH / watermark.width)))

    # make white transparent, turn black pixels into cloudy gray
    pixels = watermark.load()
    for y in range(watermark.height):
        for x in range(watermark.width):
            r, g, b, a = pixels[x, y]
            if r > 200 and g > 200 and b > 200:  # white → transparent
                pixels[x, y] = (255, 255, 255, 0)
            else:                                  # black → cloudy gray, 50% opacity
                pixels[x, y] = (150, 150, 150, 120)

    # bottom-right position
    x = image.width - watermark.width - WATERMARK_PADDING
    y = image.height - watermark.height - WATERMARK_PADDING + 15

    image.paste(watermark, (x, y), watermark)

    return image

def _wrap_text(text, font, max_width):  # wraps based on pixel width not character count
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        line_width = font.getlength(test_line)

        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)  # line is full, start a new one
            current_line = word

    lines.append(current_line)
    return "\n".join(lines)

def _resize_to_fit(image, target_width, target_height):  # resizes image to fit box without cropping or squishing
    original_width, original_height = image.size
    scale = min(target_width / original_width, target_height / original_height)

    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    return image.resize((new_width, new_height))

def _load_image(url):  # downloads image from url and returns rgb
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert("RGB") 
        return img
    except Exception as e:
        print(f"Error: couldnt load image: {e}")
        return None

def main():
    with open("template/chosen_post.json", "r") as f:
        chosen = json.load(f)
    build_meme(caption=chosen["caption"], image_url=chosen["image_url"])

if __name__ == "__main__":
    main()