# Employee Engagement, Satisfaction & Burnout Diagnostic Analysis

A Streamlit-based HR analytics project using the supplied employee dataset.

## Dataset
- 1,470 employee records and 31 columns
- Missing cells in the supplied CSV: 0
- Attrition is encoded as 0/1 in this file (1 = left, 0 = stayed).

## Features
- Engagement Index from JobInvolvement, JobSatisfaction, EnvironmentSatisfaction and RelationshipSatisfaction.
- Heuristic burnout-risk grouping using overtime and work-life balance.
- Department, satisfaction, workload, career-stage and attrition visualizations.
- Interactive department and risk filters.
- Optional CSV upload in the sidebar.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.
5. Open the local URL printed by Streamlit.

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload this folder's contents.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Select the repository, branch, and `app.py`.
4. Deploy. Keep `data/Palo Alto Networks.csv` in the repository so the app can load it.
5. Test the public URL in a private/incognito browser window.

## Methodology notes
EngagementIndex = ((mean of the four 1–4 dimensions − 1) / 3) × 100.
BurnoutRisk is a transparent operational screening rule:
- High: OverTime = Yes AND WorkLifeBalance ≤ 2
- Medium: exactly one of those conditions is true
- Low: neither condition is true

This is a heuristic proxy, not a validated psychological instrument or medical diagnosis. Attrition is analyzed as a historical outcome and must not be interpreted as proof of causation.

## Project structure
```
employee_engagement_project/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── Palo Alto Networks.csv
```
