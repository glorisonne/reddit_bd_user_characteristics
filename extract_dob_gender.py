"""
extracts age and gender from reddit submission titles
"""

import sys
import re
import datetime

# 3rd party packages
import pandas as pd
pd.set_option('display.max_colwidth', None)
from dateutil.relativedelta import relativedelta

import config


# space is optional : \s?
# re.I: ignore case
# non-greedy operator between parentheses matching: .*?
# also allow age/gender info at beginning of line without me/self before (yields maybe less false positives): re.compile(r'\b(me|I|my|myself)\s?(\(|\[)\D*?(\d{2})\D*?(\)|\])', re.I)
self_age_gender = re.compile(r'(\bme|\bI|\bmy|\bmyself|\A)\s?(\(|\[)\D*?(\d{2})\D*?(\)|\])', re.I)

# extract age_gender in parentheses
content_in_parentheses = re.compile(r'(\(|\[)(.+)(\)|\])')
gender_pattern = re.compile(r'(m|f)', re.I)
age_pattern = re.compile(r'\d{2}')

# possible improvements: replace \d{2} by [1-9][0-9]
# only allow m/f dd or dd m/f with optionally zero or max. one characters in between: (?m/f?dd?) (?dd?m/f?)
def self_age_gender_regex_test():
    # \A matches start of string - check if works with \b before
    # \D matches any character which is not a digit
    # maybe also impose that needs to contain m/f
    self_age_gender = re.compile(r'(\bme|\bI|\bmy|\bmyself|\A)\s?(\(|\[)\D*?(\d{2})\D*?(\)|\])', re.I)
    # match
    assert re.search(self_age_gender, "I [32f] have an issue").group(0) == "I [32f]"
    # match: start of title without preceding self
    assert re.search(self_age_gender, "[32f] girl").group(0) == "[32f]"

    #No match: self is not individual word
    assert re.search(self_age_gender, "xxxme [32f]") is None
    # no match: more than two succeeding digits
    assert re.search(self_age_gender, "I [322sssf]") is None
    # no match: more than two digits
    assert re.search(self_age_gender, "I [32/33f]") is None

    # matches because only contains 2 digits, \D can match everything except digits (including parentheses)
    assert re.search(self_age_gender, "[CA][H] 73 Trainer Cards [W] Offers?").group(0) is None
    # matches because do not enforce that content in parentheses must contain m/f
    assert re.search(self_age_gender, "[04 CRV] Very squealy ... ").group(0) is None

def extract_age_gender(title):
    """
    returns pd.NA if neither age nor gender could be extracted,
    otherwise returns "age gender" (one of them can be None)
    """
    match = re.search(self_age_gender, title)
    if match:
        return extract_age_gender_from_matched_substring(match.group(0))
    else:
        return pd.NA, pd.NA

def extract_age_gender_from_matched_substring(string):
    """
    extract age, gender from mention of self + age + gender
    :param string:
    :return:
    """
    age_gender = re.search(content_in_parentheses, string)
    # print(string, age_gender)
    age_gender = age_gender.group(2)
    # print(age_gender)

    age = re.search(age_pattern, age_gender)
    if age:
        age = age.group(0)
    else:
        age = pd.NA
    gender = re.search(gender_pattern, age_gender)
    if gender:
        gender = gender.group(0).lower()
    else:
        gender = pd.NA

    return age, gender

def extract_definite_date_of_birth(dates_of_birth):
    """
    extracts date of birth from dates of birth computed from submissions
    if only one date of birth -> return date of birth
    if separate dates of birth within range of < 1 year -> return earliest date of birth
    else: return "?"
    :param dates_of_birth:
    :return:
    """
    # sort from earliest to latest date of birth
    dates_of_birth = sorted(list(dates_of_birth))
    # no date of birth extracted -> NA
    if len(dates_of_birth) == 0:
        return pd.NA
    # only one date of birth extracted - take this
    elif len(dates_of_birth) == 1:
        return dates_of_birth[0]
    # more than one date of birth extracted - check if amounts to same age
    else:
        range = dates_of_birth[-1] - dates_of_birth[0]
        # print(range)
        # there is less than a year difference between dates of birth calculated from submission timestamps
        # it is possible that the user's birthday falls in this range
        if range.days < 365:
            return dates_of_birth[0]
        else:
            return pd.NA

def calculate_date_of_birth(created_at, age):
    """
    calculates date of birth for each submission that indicates age as follows:
    DOB = created_at - age
    :param created_at:
    :param age:
    :return:
    """
    if pd.isnull(age):
        return age

    date_of_birth = (created_at - relativedelta(years=int(age))).date()

    return date_of_birth

def dataset_extract_dob_gender(f):
    """
    matches age_gender regex against every title and adds as additional column
    :param f: submissions json file
    """
    posts = pd.read_json(f)

    print("%d users" %posts.author.nunique())

    posts["age"], posts["gender"] = zip(*posts.title.apply(extract_age_gender))

    posts["dob"] = posts.apply(lambda x: calculate_date_of_birth(x.created_at, x.age), axis=1)

    # users = posts.groupby(["author"]).agg(lambda x: tuple(x)).applymap(set).reset_index()
    users = posts.groupby("author").dob.apply(lambda x: set(x.dropna())).reset_index()
    user_genders = posts.groupby("author").gender.apply(lambda x: set(x.dropna())).reset_index()
    users = users.merge(user_genders, on="author")

    # determine users' gender if there is more than one matched title for a user
    users.loc[:, "gender"] = users.gender.apply(lambda x: list(x)[0] if len(x) == 1 else pd.NA)
    print("%d users with self-reported gender" %len(users[users.gender.notna()]))
    print(users.gender.value_counts())

    # determine users' date of birth if there is more than one matched age for a user
    users.loc[:, "dob"] = users["dob"].apply(extract_definite_date_of_birth)

    print("%d users with self-reported date of birth" %len(users[users.dob.notna()]))

    users[["author", "dob", "gender"]].to_csv(config.output + "users_age_gender.csv")

if __name__ == '__main__':
    # regex test
    self_age_gender_regex_test()
