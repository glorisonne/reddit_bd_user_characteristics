import filter

condition = "bipolar"

diagnoses = ["adhd", "anxiety", "autism", "bipolar", "bpd", "depression", "ed", "ocd", "ptsd", "schizophrenia", "schizoaffective"]

for diagnosis in diagnoses:
    print(diagnosis)
    filter.build_self_reported_diagnosis_patterns("inclusion", diagnosis)
    filter.build_self_reported_diagnosis_patterns("exclusion", diagnosis)
