#
# Database access functions for the web forum.
# 

import time
import psycopg2


## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    ## Database connection
    DB = psycopg2.connect("dbname=forum")
    cursor = DB.cursor()
    cursor.execute("select content, time from posts order by time desc;")
    
    results = cursor.fetchall()
    posts = [{'content': str(row[0]), 'time': str(row[1])} for row in results]
    
    
    #posts.sort(key=lambda row: row['time'], reverse=True)
    
    DB.close()

    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''

    t = time.strftime('%c', time.localtime())
    
    ## Database connection
    DB = psycopg2.connect("dbname=forum")
    cursor = DB.cursor()
    cursor.execute("INSERT INTO posts (content) VALUES (%s)",
        (content,))

    DB.commit()
    DB.close()
