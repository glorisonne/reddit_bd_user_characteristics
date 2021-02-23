#!/usr/bin/env python3

import copy
import os
import re

from datamodel.span import Span, get_longest_spans

FILTER_FILES_FOLDER = "/mnt/dhr/filtering/"


class Filter(object):
    def __init__(self, name, ignore_case=True):
        self.name = name
        self.ignore_case = ignore_case
        self.filters = None

    def matches(self, text):
        """
        returns True if a given text matches one of the filter_terms
        tries to exclude cases where a filter term matches only a part of a term in text:
        each match of a filter term has to be preceeded and succeeded by space, punctuation or start/end of text
        :param filter_terms:
        :param text:
        :return:
        """
        # print ("List of filter terms %s" %self.filter_terms)
        # if self.ignore_case:
        #    text = text.lower()
        for filter in self.filters:
            # print(filter)
            # print(text)
            if re.search(filter, text):
                # print("Matches filter %s" % filter)
                return True
        return False

    def get_all_matches(self, text):
        """
        returns list of start, end indices of all matches of filters in the text
        if several matches start at the same position, only keep the longest one
        :param text
        :return:
        """
        spans_of_matches = []

        for filter in self.filters:
            matches = re.finditer(filter, text)
            for match in matches:
                start, end = match.span()
                span = Span(start, end)
                spans_of_matches.append(span)

        return get_longest_spans(spans_of_matches)

    def _build_filters(self, filter_srings):
        pass


class PhraseFilter(Filter):
    def __init__(self, name, filter_file, ignore_case=True):
        super(PhraseFilter, self).__init__(name, ignore_case)

        filter_phrases = read_filter_list(filter_file, self.ignore_case, has_heading=False, only_first_column=False)
        self.filters = self._build_filters(filter_phrases)

    def _build_filters(self, filter_phrases):
        filters = []
        if self.ignore_case:
            for filter_term in filter_phrases:
                # full_filter_term = re.compile(r"%s" % filter_term, re.IGNORECASE)
                full_filter_term = re.compile(r"%s\S*(\s+|$)" % filter_term, re.IGNORECASE)
                filters.append(full_filter_term)

        # case-sensitive version: do not add re.IGNORECASE to regex
        else:
            for filter_term in filter_phrases:
                # full_filter_term = re.compile(r"%s" % filter_term)
                full_filter_term = re.compile(r"%s\S*(\s+|$)" % filter_term)
                filters.append(full_filter_term)

        return filters

class InclusionPatternFilter(PhraseFilter):
    def __init__(self, social_media_name, condition="bipolar"):
        super(InclusionPatternFilter, self).__init__("include-%s" %condition, get_patterns_file_name(condition, "positive-diagnosis", social_media_name))

class ExclusionPatternFilter(PhraseFilter):
    def __init__(self, social_media_name, condition="bipolar"):
        super(ExclusionPatternFilter, self).__init__("exclude-%s" %condition, get_patterns_file_name(condition, "negative-diagnosis", social_media_name))

class TermFilter(Filter):
    """
    matches filter terms as isolated words, so term, term., (term), -term, term,, but not prefixterm, suffixterm
    """
    def __init__(self, name, filter_file, ignore_case=True, has_heading=False):
        super(TermFilter, self).__init__(name, ignore_case)
        self.filter_terms = read_filter_list(filter_file, self.ignore_case, has_heading=has_heading)
        self.filters = self._build_filters(self.filter_terms)

    def build_OR_filter(self):
        return " OR ".join(self.filter_terms)

    def _build_filters(self, filter_terms):
        filters = []
        if self.ignore_case:
            for filter_term in filter_terms:
                if filter_term.startswith("#"): # need to add \b before # of twitter hashtags in regex
                    full_filter_term = re.compile(r"%s\b" % filter_term, re.IGNORECASE)
                else:
                    full_filter_term = re.compile(r"\b%s\b" % filter_term, re.IGNORECASE)
                filters.append(full_filter_term)

        # case-sensitive version: do not add re.IGNORECASE to regex
        else:
            for filter_term in filter_terms:
                if filter_term.startswith("#"): # need to add \b before # of twitter hashtags in regex
                    full_filter_term = re.compile(r"%s\b" % filter_term)
                else:
                    full_filter_term = re.compile(r"\b%s\b" % filter_term)
                filters.append(full_filter_term)

        return filters


class DiagnosisFilter(TermFilter):
    def __init__(self):
        super(DiagnosisFilter, self).__init__("diagnosis",
                                              os.path.join(FILTER_FILES_FOLDER, "diagnosis-filter-terms.txt"), ignore_case=True, has_heading=True)

class ConditionFilter(TermFilter):
    def __init__(self, condition):
        super(ConditionFilter, self).__init__(condition, os.path.join(FILTER_FILES_FOLDER,
                                                                      "condition-filter-terms/%s-filter-terms.txt" %(condition)))

class BipolarFilter(ConditionFilter):
    def __init__(self, social_media_name):
        super(BipolarFilter, self).__init__("bipolar")

def read_filter_list(filter_file, ignore_case=True, has_heading=True, only_first_column=True):
    """
    read in file that contains one term per line
    if has_heading, discard first line
    :param filter_term_file:
    :return:
    """
    with open(filter_file, "r") as f:
        filters = f.readlines()
        if has_heading:
            filters = filters[1:]

    if only_first_column:
        filters = [filter.split("\t")[0] for filter in filters]

    if ignore_case:
        filters = [filter.lower() for filter in filters]

    filters = [filter.strip() for filter in filters]

    return filters

def get_subreddit_filter(filter_file):
    subreddits = read_filter_list(filter_file, ignore_case=False, has_heading=False, only_first_column=False)
    subreddit_filter = ["subreddit_name = '%s'" % sub for sub in subreddits]
    subreddit_filter = " OR ".join(subreddit_filter)
    print(subreddit_filter)
    return subreddit_filter

def expand_patterns_with(filter_file):
    filters = read_filter_list(filter_file, has_heading = False, only_first_column=False)
    filters_with_expanded = []

    with_filter = re.compile(r"\bwith\b", re.IGNORECASE)

    for filter in filters:
        if re.search(with_filter, filter):
            filters_with_expanded.append(re.sub(r"\bwith\b", "w", filter))
            filters_with_expanded.append(re.sub(r"\bwith\b", "w/", filter))

    filters_with_expanded += filters

    with open(filter_file + "_with_expanded", "w") as f:
        f.write("\n".join(filters_with_expanded))


def build_self_reported_diagnosis_patterns(name, condition, social_media_name):
    """

    :param name: positive-diagnosis or negative-diagnosis
    :param social_media_name: twitter or reddit
    :param condion: currently bipolar and psychotic-disorder supported
    :return:
    """
    doctor_expansions = read_filter_list(
        os.path.join(FILTER_FILES_FOLDER, "doctor-expansion-terms.txt"), has_heading=False, only_first_column=False)

    condition_expansions = read_filter_list(
        os.path.join(FILTER_FILES_FOLDER, "condition-filter-terms/%s-filter-terms.txt" % (condition)), has_heading = False)

    referent_expansions = []
    if name == "negative-diagnosis":
        referent_expansions = read_filter_list(
            os.path.join(FILTER_FILES_FOLDER, "referent-expansion-terms.txt"), has_heading=False,
            only_first_column=False)

    expansions = {"_doctor": doctor_expansions, "_condition": condition_expansions, "_ref": referent_expansions}

    diagnosis_patterns = read_filter_list(
        os.path.join(FILTER_FILES_FOLDER, "%s-patterns_%s.txt" % (name, social_media_name)), has_heading=False,
        only_first_column=False)
    diagnosis_patterns = expand_patterns_with_placeholders(diagnosis_patterns, expansions)

    # if name == "negative-diagnosis":
    #     psychotic_disorder_filter_terms =  read_filter_list(
    #     os.path.join(FILTER_FILES_FOLDER, "psychotic-disorder-filter-terms.txt"))
    #     diagnosis_patterns.extend(psychotic_disorder_filter_terms)

    with open(get_patterns_file_name(condition, name, social_media_name), "w") as f:
        f.write("\n".join(diagnosis_patterns))

def build_exclusion_patterns(condition, social_media_name):
    """
    matches patterns where user states having no diagnosis or self-diagnosing;
    exclusion-patterns contain manually filtered subset of negative-diagnosis-patterns without _ref having diagnosis
    :param condition:
    :param social_media_name:
    :return:
    """
    exclusion_patterns = read_filter_list(
        os.path.join(FILTER_FILES_FOLDER, "exclusion-patterns.txt"), has_heading=False,
        only_first_column=False)
    condition_expansions = read_filter_list(
        os.path.join(FILTER_FILES_FOLDER, "condition-filter-terms/%s-filter-terms.txt" % (condition)), has_heading=False)
    exclusion_patterns = expand_patterns_with_placeholders(exclusion_patterns, {"_condition": condition_expansions})
    with open(get_patterns_file_name(condition, "exclusion", social_media_name), "w") as f:
        f.write("\n".join(exclusion_patterns))


def _substitute_placeholders(text, placeholders, results):
    # print("Call substitute place holders with text %s, results %s" % (text, str(results)))
    contains_placeholder = False
    for placeholder in placeholders:
        if placeholder in text:
            contains_placeholder = True
            substitutions = placeholders[placeholder]
            for substitution in substitutions:
                text_placeholder_substituted = copy.deepcopy(text)
                text_placeholder_substituted = text_placeholder_substituted.replace(placeholder, substitution)
                # recursion!
                _substitute_placeholders(text_placeholder_substituted, placeholders, results)
            # only replace one placeholder in one loop
            break

    # important: do not append unfinished patterns
    if not(contains_placeholder):
        results.append(text)

    return results

def expand_patterns_with_placeholders(patterns, expansions):
    """
    expansions is a dictionary of placeholder: lists that provide list of substitutions for each placeholder
    :param patterns:
    :param expansions:
    :return:
    """

    patterns_placeholder_extended = []
    for pattern in patterns:
        pattern_placeholder_extended = _substitute_placeholders(pattern, expansions, [])
        # print(pattern_placeholder_extended)
        patterns_placeholder_extended.extend(pattern_placeholder_extended)

    print ("Expanded %d patterns to %d patterns" % (len(patterns), len(patterns_placeholder_extended)))
    return patterns_placeholder_extended

def get_patterns_file_name(condition, name, social_media_name):
    return os.path.join(FILTER_FILES_FOLDER, "expanded-diagnosis-patterns/%s-%s-patterns_%s.txt" % (condition, name, social_media_name))

def compute_minimum_distance_inclusion_pattern_condition_term(included_posts, social_media_name):
    inclusion_pattern_filter = InclusionPatternFilter(social_media_name)
    condition_terms_filter = BipolarFilter(social_media_name)

    for post in included_posts:
        post.add_inclusion_pattern_spans(inclusion_pattern_filter)
        post.add_condition_term_spans(condition_terms_filter)
        post.compute_minimum_distance_inclusion_pattern_condition_term()
        # print("%s\nMinimum distance: %d" %(post.get_text_marked_up_spans(),
        #                                   post.minimum_distance_inclusion_pattern_condition_term))

    return included_posts

def test_phrase_filter():
    test_phrases = ["I was diagnos with bipolar", "I was diagnosed with bipolar", "I was diagnosed", "I was diagnos."]

    # match text until next whitespace or end of string
    filter = re.compile(r"%s\S*(\s+|$)" %"I was diagnos", re.IGNORECASE)

    for test_phrase in test_phrases:
        print("%s: %s" %(bool(re.search(filter, test_phrase)), test_phrase))

        matches = re.finditer(filter, test_phrase)
        for match in matches:
            print(match)


