import requests # the requests library is used to make HTTP requests to the Reddit API.

# settings and variables
SUBREDDITS = ["funny"]
POST_LIMIT = 20
TIME_FILTER = "day"

# more descriptive User-Agent fixes the 403 block
HEADERS = {"User-Agent": "python:my_scraper:v1.0"}  # header to avoid request blocking

def get_top_posts(subreddit, limit, time_filter):  # function to retrieve top subreddit posts
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t={time_filter}"  # build reddit API endpoint

    try:  # error handling for network issues, HTTP errors, and other exceptions
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        posts = []  # store the cleaned post data here

        for post in data["data"]["children"]:  # loop through the post items
            post_data = post["data"]

            # skip posts that dont have an image attached
            if not _has_image(post_data):
                continue

            posts.append({
                "title": post_data["title"],        # the following lines are the post details i want returned
                "upvotes": post_data["score"],
                "upvote_ratio": f"{post_data['upvote_ratio'] * 100:.1f}%",
                "num_comments": post_data["num_comments"],
                "post_link": f"https://www.reddit.com{post_data['permalink']}",
                "image_url": _get_image_url(post_data)  # grab the image url from the post
            })  # end appended post dictionary

        return posts  # return processed posts data

    except requests.exceptions.ConnectionError:     # the following lines handle errors
        print("Error: No internet connection.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error: Something went wrong: {e}")
        return None


def _has_image(post_data):  # checks if the post has a valid image attached
    url = post_data.get("url", "")
    return any(url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"])


def _get_image_url(post_data):  # pulls the image url out of the post data
    return post_data.get("url", None)


def display_posts(subreddit, posts):  # print posts in a readable format

    # fix for NoneType error - check if posts is None before continuing
    if not posts:
        print(f"No posts found for r/{subreddit}")
        return

    print(f"\n{'='*60}")
    print(f" Top {len(posts)} Posts from r/{subreddit} ({TIME_FILTER})")  # section heading details
    print(f"{'='*60}")

    for i, post in enumerate(posts, start=1):  # loop through posts with numbering
        print(f"\n#{i}: {post['title']}")        # numbered post title
        print(f"  Upvotes    : {post['upvotes']:,}")   # formatted upvote count
        print(f"  Upvote Ratio : {post['upvote_ratio']}")  # print upvote ratio percentage
        print(f"  Comments   : {post['num_comments']:,}")   # print formatted comment count
        print(f"  Post Link  : {post['post_link']}")  # post URL
        print(f"  Image URL  : {post['image_url']}")  # image url attached to the post
        print(f"  {'-'*50}")  # divider

# Then in main(), instead of displaying all posts:
def main():
    for subreddit in SUBREDDITS:
        posts = get_top_posts(subreddit, POST_LIMIT, TIME_FILTER)
        if posts:
            # Randomly pick ONE post from the list
            random_post = random.choice(posts)
            display_posts(subreddit, [random_post])  # wrap in list
            
if __name__ == "__main__":
    main()