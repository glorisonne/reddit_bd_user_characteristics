# Diagnosis terms
diagnosis-filter-terms.txt

# Terms for mental health conditions (including bipolar disorder)
condition-terms

Adapted from "-white" and "-syns" files from http://ir.cs.georgetown.edu/data/smhd/conditions/ in accordance with CC BY 4.0 https://creativecommons.org/licenses/by/4.0/

# Patterns to identify self-reported diagnoses
inclusion-patterns.txt

Identify a self-reported diagnosis for a condition if the post matches any of the inclusion patterns and any of the terms for this condition with a maximum distance of 55 characters.

Adapted from http://ir.cs.georgetown.edu/data/smhd/diagpatterns_positive.txt in accordance with CC BY 4.0 https://creativecommons.org/licenses/by/4.0/

# Exclusion patterns for self-reported diagnoses
exclusion-patterns.txt

Do not consider a self-reported diagnosis match if the post also matches any of the exclusion patterns. 

Adapted from http://ir.cs.georgetown.edu/data/smhd/diagpatterns_negative.txt in accordance with CC BY 4.0 https://creativecommons.org/licenses/by/4.0/

Within positive/negative-diagnosis-patterns
_condition can match any condition term for the target condition
_ref can match any term in referent-expansion-terms.txt (taken from https://github.com/Georgetown-IR-Lab/emnlp17-depression/blob/master/user_selection/expansions.json "_ref" in accordance with CC BY 4.0 https://creativecommons.org/licenses/by/4.0/)
_professional can match any term in professional-expansion-terms.txt (taken from taken from https://github.com/Georgetown-IR-Lab/emnlp17-depression/blob/master/user_selection/expansions.json "_doctor" in accordance with CC BY 4.0 https://creativecommons.org/licenses/by/4.0/)
