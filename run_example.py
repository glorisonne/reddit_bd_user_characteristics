import filter, config, detect_diagnosis_disclosures as d, extract_dob_gender

submissions_json = config.data + "submissions-example.json"
comments_json = config.data + "comments-example.json"

run_build_diagnosis_patterns = True
run_identify_diagnoses = True
run_extract_dob_gender = True

# build self-reported diagnosis patterns
if run_build_diagnosis_patterns:
    for diagnosis in config.diagnoses:
        print(diagnosis)
        filter.build_self_reported_diagnosis_patterns("inclusion", diagnosis)
        filter.build_self_reported_diagnosis_patterns("exclusion", diagnosis)

# identify self-reported diagnoses
if run_identify_diagnoses:
    for diagnosis in config.diagnoses:
        # from submissions
        d.detect_disclosures(submissions_json, "submission", diagnosis)
        # from comments
        d.detect_disclosures(comments_json, "comment", diagnosis)

# extract self-reported age and gender
if run_extract_dob_gender:
    extract_dob_gender.dataset_extract_dob_gender(submissions_json)