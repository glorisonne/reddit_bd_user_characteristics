class Span(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.length = end - start

    def distance(self, other_span):
        if self.end < other_span.start:
            distance = other_span.start - self.end
        else:
            distance = self.start - other_span.end
        return distance

    def __str__(self):
        return ("%d->%d" %(self.start, self.end))

    def __eq__(self, other):
        return (self.start == other.start) and (self.end == other.end)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.start, self.end))

def get_longest_spans(spans):
    """
    takes list of spans, and filters out all spans that start at same position but are not the longest
    :param spans:
    :return:
    """
    span_starts = {}

    for span in spans:
        if span.start in span_starts:
            if span_starts[span.start].length < span.length:
                span_starts[span.start] = span
        else:
            span_starts[span.start] = span

    return list(span_starts.values())

def get_minimum_distance(span_list_1, span_list_2):
    """
    finds the minimum distance between a span in span_list_1 and span_list_2
    distances are capped at 0
    :param span_list_1:
    :param span_list_2:
    :return: minimum_distance, (span_1, span_2) - the span pair that has the minimum distance
    """
    minimum_distance = None
    (span_min_dist_1, span_min_dist_2) = None, None
    for span_1 in span_list_1:
        for span_2 in span_list_2:
            distance = span_1.distance(span_2)
            (span_min_dist_1, span_min_dist_2) = span_1, span_2
            if not minimum_distance or (distance < minimum_distance):
                minimum_distance = distance
            if minimum_distance <= 0:
                return 0, (span_min_dist_1, span_min_dist_2)
    return minimum_distance, (span_min_dist_1, span_min_dist_2)


def get_text_marked_up_spans(text, spans):
    """
    Adds span start and end tags to text, example:
    text = I have a diagnosis of bipolar disorder
    marked_up_text = I have a <diagnosis_term>diagnosis</diagnosis_term> of <condition_term>bipolar disorder</condition_term>
    tricky: need to start inserting span tags from end because otherwise indices don't match
    :param self:
    :param text:
    :param spans: dictionary "name" : list of span objects [Span(), Span()]
    :return:
    """
    # holds tuples (position, string tag to insert)
    tag_insertions = []
    for span_name in spans:
        for i, span in enumerate(spans[span_name]):
            tag_insertions.append((span.start, "<%s_%d>" % (span_name, (i+1))))
            tag_insertions.append((span.end, "</%s_%d>" % (span_name, (i+1))))

    # sort tag_insertions according to position, reverse (start with last) tag_insertions.sort(lambda )
    tag_insertions = sorted(tag_insertions, key=lambda x: x[0], reverse=True)
    # print(tag_insertions)
    for position, tag in tag_insertions:
        text = text[:position] + tag + text[position:]

    return text