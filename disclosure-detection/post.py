import util

class RedditPost():
    def __init__(self, id, text, type, subreddit_name, user_name):
        self.id = id
        self.text = text
        self.type = type
        self.subreddit_name = subreddit_name
        self.user_name = user_name

    def normalise_text(self):
        self.text_original = self.text
        self.text = util.normalise_unicode_to_ascii(self.text)

class RedditSubmission(RedditPost):
    def __init__(self, id, text, author_name, subreddit_name, title):
        super(RedditSubmission, self).__init__(id, text, "submission", subreddit_name, author_name)
        self.title = title
        self.text = "%s\n%s" %(self.title, self.text)

class RedditComment(RedditPost):
    def __init__(self, id, text, author_name, subreddit_name):
        super(RedditComment, self).__init__(id, text, "comment", subreddit_name, author_name)