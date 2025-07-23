# ML recommendation logic will go here.

import pandas as pd
from datetime import datetime

def load_data():
    return pd.read_csv("data/health_plans.csv")

def get_season(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"

def recommend_plan(symptoms, df, age=None, gender=None):
    scores = []
    month = datetime.now().month
    season = get_season(month)

    for _, row in df.iterrows():
        plan_name = row["plan"].lower()
        plan_symptoms = row["symptoms"].lower().split(", ")
        match_score = sum(1 for s in symptoms if s.lower() in plan_symptoms)

        # 🎯 Season-aware logic
        if "hydration" in plan_name and season == "summer":
            match_score += 3
        if "immunity" in plan_name and season == "winter":
            if any(s.lower() in ["cold", "cough", "flu"] for s in symptoms):
                match_score += 3

        # 👵 Age-based recommendations
        if age:
            if age > 60 and "routine checkup" in plan_name:
                match_score += 2
            elif age < 12 and "pediatric" in plan_name:
                match_score += 2
            elif age < 25 and "youth" in plan_name:
                match_score += 1

        # 🚺 Gender-based logic
        if gender and gender.lower() == "female":
            if "fatigue" in [s.lower() for s in symptoms] and "iron" in plan_name:
                match_score += 2

        scores.append((row["plan"], match_score))

    # Sort and return top 3
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return scores[:3]



