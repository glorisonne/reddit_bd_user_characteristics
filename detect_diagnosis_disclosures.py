from post import RedditComment, RedditSubmission
import filter, config, util

def get_post_objects(json_posts, type):
    if type == "submission":
        posts = [RedditSubmission(json_post["id"], json_post["selftext"], json_post["author"], json_post["subreddit"],
                                  json_post["title"]) for json_post in json_posts]

    elif type == "comment":
        posts = [RedditComment(json_post["id"], json_post["body"], json_post["author"], json_post["subreddit"]) for
                 json_post in json_posts]

    [post.preprocess_diagnosis_post() for post in posts]

    return posts

def identify_self_reported_diagnosis_statements(posts, diagnosis):
    condition_terms_filter = filter.ConditionFilter(diagnosis)
    inclusion_pattern_filter = filter.InclusionPatternFilter(diagnosis)
    exclusion_pattern_filter = filter.ExclusionPatternFilter(diagnosis)

    self_reported_diagnosis_posts = []
    for counter, post in enumerate(posts):
        # contains diagnosis keyword
        if condition_terms_filter.matches(post.text):
            post.add_condition_term_spans(condition_terms_filter)
            # does not match exclusion
            if not exclusion_pattern_filter.matches(post.text):
                # matches inclusion pattern
                if inclusion_pattern_filter.matches(post.text):
                    # get distance between condition keyword and inclusion pattern
                    post.add_inclusion_pattern_spans(inclusion_pattern_filter)
                    # post.add_condition_term_spans(condition_terms_filter)
                    post.compute_minimum_distance_inclusion_pattern_condition_term()
                    # empirically determined maximum character distance between condition term and diagnosis
                    # patterns for self-reported BD patterns with 100 manually annotated randomly selected posts
                    if post.minimum_distance_inclusion_pattern_condition_term <= 55:
                        post.self_reported_diagnosis = True
                        self_reported_diagnosis_posts.append(post)
            #else:
            #    print("Exclusion filter matches: %s" % post.text)
    return self_reported_diagnosis_posts, posts

def detect_disclosures(json_file, type, diagnosis):
    json_posts = util.read_json(json_file)
    posts = get_post_objects(json_posts, type)

    # get only self-reported diagnosis posts
    diagnosis_posts, posts = identify_self_reported_diagnosis_statements(posts, diagnosis)

    # print the ids of posts that were detected to be a self-reported diagnosis
    posts_fname = "%s%s_%ss_posts_marked_up.txt" %(config.output, diagnosis, type)
    with open(posts_fname, "w") as f:
        for post in posts:
            f.write("%s\t%s\n" %(post.id, post.get_text_marked_up_spans()))

    diagnosis_posts_fname = "%s%s_%ss_diagnosis_post_ids.txt" % (config.output, diagnosis, type)
    with open(diagnosis_posts_fname, "w") as f:
        f.write("\n".join(["%s\t%s" %(post.id, post.user_name) for post in diagnosis_posts]))

    print("Identified %d self-reported %s diagnosis posts out of %d %ss" %(len(diagnosis_posts), diagnosis, len(posts),\
                                                                           type))