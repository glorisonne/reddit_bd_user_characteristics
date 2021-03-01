# requirements: unicodedata, re, nltk


# 1) build self-reported diagnosis patterns
# resulting CONDITION_inclusion-patterns.txt and CONDITION_exclusion-patterns.txt
# are stored in disclosure-detection\disclosure-patterns\expanded-diagnosis-patterns
python build_patterns.py