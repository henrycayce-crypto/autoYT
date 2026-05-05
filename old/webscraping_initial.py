import requests # the requests library is used to make HTTP requests to the Reddit API.

# Settings and variables
SUBREDDITS = ["showerthoughts", "todayilearned"]
POST_LIMIT = 5
TIME_FILTER = "week"

# More descriptive User-Agent fixes the 403 block
HEADERS = {"User-Agent": "python:my_scraper:v1.0"}  # header to avoid request blocking

def get_top_posts(subreddit, limit, time_filter):   # function to retrieve top subreddit posts
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t={time_filter}"    #build reddit API endpoint URL
    
    try:    # error handling for network issues, HTTP errors, and other exceptions
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()  
        posts = []  # store the cleaned posted data here

        for post in data["data"]["children"]:       #loop through the post items
            post_data = post["data"]
            posts.append({
                "title": post_data["title"],     #the following lines are the post details I want returned
                "upvotes": post_data["score"],
                "upvote_ratio": f"{post_data['upvote_ratio'] * 100:.1f}%",
                "num_comments": post_data["num_comments"],
                "post_link": f"https://reddit.com{post_data['permalink']}"
            })  #end appended post dictionary

        return posts  #return processed posts data

    except requests.exceptions.ConnectionError:     #the following lines handle errors
        print("Error: No internet connection.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error: Something went wrong: {e}")
        return None

def display_posts(subreddit, posts):    #print posts in a readable format

    # Fix for NoneType error - check if posts is None before continuing
    if not posts:
        print(f"No posts found for r/{subreddit}")
        return

    print(f"\n{'='*60}")    #top separator line
    print(f"  Top {len(posts)} Posts from r/{subreddit} ({TIME_FILTER})") #section heading details
    print(f"{'='*60}")  #bottom separator line

    for i, post in enumerate(posts, start=1): #loop through posts with numbering
        print(f"\n#{i}: {post['title']}")   #numbered post title
        print(f"  Upvotes      : {post['upvotes']:,}")  #formatted upvote count
        print(f"  Upvote Ratio : {post['upvote_ratio']}")   #print upvote ratio percentage
        print(f"  Comments     : {post['num_comments']:,}")     #print formatted comment count
        print(f"  Post Link    : {post['post_link']}")  #post URL (not necessary, but keeping for now)
        print(f"  {'-'*50}")    #divider 

def main():
    for subreddit in SUBREDDITS:
        posts = get_top_posts(subreddit, POST_LIMIT, TIME_FILTER) # get posts for each subreddit and display them
        display_posts(subreddit, posts)

if __name__ == "__main__":
    main()