import util
import span

class RedditPost():
    def __init__(self, id, text, type, subreddit_name, user_name):
        self.id = id
        self.text = text
        self.type = type
        self.subreddit_name = subreddit_name
        self.user_name = user_name

        # variables related to computing distance of condition term to inclusion pattern match
        self.inclusion_pattern_spans = [] # spans that indicate start, end of each inclusion pattern
                                         #  (self reported diagnosis) match in self.text
        self.condition_term_spans = []  # spans that indicate start, end of each condition term in self.text
        self.minimum_distance_inclusion_pattern_condition_term = None
        self.inclusion_pattern_span_with_minimum_distance = None
        self.condition_term_span_with_minimum_distance = None

    # methods to identify self-reported diagnoses
    def add_inclusion_pattern_spans(self, filter):
        self.inclusion_pattern_spans = filter.get_all_matches(self.text)

    def add_condition_term_spans(self, filter):
        self.condition_term_spans = filter.get_all_matches(self.text)

    def add_diagnosis_term_spans(self, filter):
        self.diagnois_term_spans = filter.get_all_matches(self.text)

    def compute_minimum_distance_inclusion_pattern_condition_term(self):
        if len(self.inclusion_pattern_spans) < 1 or len(self.condition_term_spans) < 1:
            print("Error: cannot compute minimum distance of inclusion pattern and condition term matches\n"
                  "inclusion pattern matches: %s\ncondition term matches: %s\ntext: %s\nid: %d" %
                  (str([str(span) for span in self.inclusion_pattern_spans]),
                   str([str(span) for span in self.condition_term_spans]), self.text, self.id))
        else:
            self.minimum_distance_inclusion_pattern_condition_term, (self.inclusion_pattern_span_with_minimum_distance,
                                                                 self.condition_term_span_with_minimum_distance)\
            = span.get_minimum_distance(self.inclusion_pattern_spans, self.condition_term_spans)

    def get_text_marked_up_spans(self):
        # inclusion pattern and condition term match
        if self.minimum_distance_inclusion_pattern_condition_term:
            span_dict = {"inclusion_pattern" : self.inclusion_pattern_spans,
                         "condition_term" : self.condition_term_spans,
                         "inclusion_pattern_minimum_distance": [self.inclusion_pattern_span_with_minimum_distance],
                         "condition_term_minimum_distance=%s" %str(self.minimum_distance_inclusion_pattern_condition_term):
                             [self.condition_term_span_with_minimum_distance]}
        else:
            # no match or only inclusion or condition term match
            span_dict = {"inclusion_pattern": self.inclusion_pattern_spans,
                         "condition_term": self.condition_term_spans}
        # pprint.pprint(span_dict)
        text_marked_up_spans = span.get_text_marked_up_spans(self.text, span_dict)
        return text_marked_up_spans

    def normalise_text(self):
        self.text_original = self.text
        self.text = util.normalise_unicode_to_ascii(self.text)

    def remove_quotes(self, remove_in_line_quotes):
        self.text = util.remove_reddit_quotes(self.text, remove_in_line_quotes)

    def tokenize(self):
        self.text = util.tokenize(self.text)

    def preprocess_diagnosis_post(self):
        """
        Pre-processing when want to match self-reported diagnoses: remove in line quotes and Reddit quotes
        """
        self.normalise_text()
        self.remove_quotes(remove_in_line_quotes=True)
        self.tokenize()

    def preprocess_post(self):
        """
        Pre-processing for all user posts: keep in line quotes (indicated via quotation marks)
        when don't want to match self-reported diagnoses; only remove Reddit quotes
        """
        self.normalise_text()
        self.remove_quotes(remove_in_line_quotes=False)
        self.tokenize()



class RedditSubmission(RedditPost):
    def __init__(self, id, text, author_name, subreddit_name, title):
        super(RedditSubmission, self).__init__(id, text, "submission", subreddit_name, author_name)
        self.title = title
        self.text = "%s\n%s" %(self.title, self.text)

class RedditComment(RedditPost):
    def __init__(self, id, text, author_name, subreddit_name):
        super(RedditComment, self).__init__(id, text, "comment", subreddit_name, author_name)