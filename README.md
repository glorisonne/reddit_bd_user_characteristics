# Code accompanying the paper "Understanding who uses Reddit: Profiling individuals with a self-reported bipolar disorder diagnosis"

Identify Reddit users with a self-reported Bipolar Disorder Diagnosis and profile their user characteristics

## Requirements
unicodedata, re, nltk

## Folder structure
The data/ folder contains examples (paraphrased from real posts) for submissions and comments.
To receive the full original dataset under a Data Usage Agreement, please contact <email address anonymised for blind review>.

The output/ folder will contain any output files generated by the three steps below

The disclosure-patterns/ folder contains self-reported diagnosis patterns and mental health diagnosis terms (see separate README.txt within the folder)

## Code

1) Identify self-reported diagnosis posts
a) Build patterns:
For each diagnosis (CONDITION), CONDITION_inclusion-patterns.txt and CONDITION_exclusion-patterns.txt
are saved to /disclosure-patterns/expanded-diagnosis-patterns/
b) Apply patterns:
Prints post.id \t post.user_name to one file for each diagnosis and input file to the output/ folder

2) Extract self-reported age and gender
Extracts self-reported age and gender from submission titles, writes results to output/users_age_gender.csv

Run all steps on example data (demonstrates code usage):
python run_example.py
