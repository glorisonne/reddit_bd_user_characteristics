import sys
from post import RedditPost, RedditComment, RedditSubmission
import util

def read_json(f):
    """
    read in file that contains one json post object per line
    :param f:
    :return:
    """
    posts = []
    with open(file_with_json_lines) as f:
        for line in f.readlines():
            posts.append(json.loads(line))

    print("Read in %d posts from %s" % (len(json_posts), file_with_json_lines))
    return posts

def get_post_objects(json_posts, type):
    if type == "submission":
        posts = [RedditSubmission(json_post["id"], json_post["selftext"], json_post["author"], json_post["subreddit"],
                                  json_post["title"]) for json_post in json_posts]

    elif type == "comment":
        posts = [RedditComment(json_post["id"], json_post["body"], json_post["author"], json_post["subreddit"]) for
                 json_post in json_posts]

    [post.normalise_text() for post in posts]

    return posts

def identify_self_reported_diagnosis_statements(posts, diagnosis):
    condition_terms_filter = filtering.filter.ConditionFilter(diagnosis)
    inclusion_pattern_filter = filtering.filter.InclusionPatternFilter(social_media_name, diagnosis)
    exclusion_pattern_filter = filtering.filter.ExclusionPatternFilter(social_media_name, diagnosis)

    self_reported_diagnosis_posts = []
    for counter, post in enumerate(posts):
        text_without_quotes = util.remove_reddit_quotes(post.text, remove_in_line_quotes=True)
        # contains diagnosis keyword
        if condition_terms_filter.matches(text_without_quotes):
            # does not match exclusion
            if not exclusion_pattern_filter.matches(text_without_quotes):
                # matches inclusion pattern
                if inclusion_pattern_filter.matches(text_without_quotes):
                    # get distance between condition keyword and inclusion pattern
                    post.add_inclusion_pattern_spans(inclusion_pattern_filter)
                    post.add_condition_term_spans(condition_terms_filter)
                    post.compute_minimum_distance_inclusion_pattern_condition_term()
                    # ToDo add distance threshold here
                    post.self_reported_diagnosis = True

                    self_reported_diagnosis_posts.append(post)
    return self_reported_diagnosis_posts

def detect_disclosures(json_file, type, diagnosis):
    json_posts = read_json(json_file)
    posts = get_post_objects(json_posts, type)

    # get only self-reported diagnosis posts
    diagnosis_posts = identify_self_reported_diagnosis_statements(posts, diagnosis)

    # print the ids of posts that were detected to be a self-reported diagnosis
    fname = "%s_%s_diagnosis_posts.njson"
    with open(fname, "w") as f:
        for post in diagnosis_posts:
            f.print(post.id +"\n")


if __name__ == '__main__':
    json_file = sys.argv[1]
    type = sys.argv[2]  # submission or comment
    diagnosis = sys.argv[3] # bipolar, schizophrenia, etc.
    detect_disclosures(json_file, type, diagnosis)