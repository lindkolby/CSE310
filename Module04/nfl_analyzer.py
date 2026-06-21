"""
NFLVerse Team Performance Analyzer
Author: Kolby Lind

This program uses real NFLVerse play-by-play data instead of a manually created
CSV file. It downloads NFL data directly from the public NFLVerse GitHub release,
analyzes team performance, creates graphs, and trains a simple machine learning
model.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


NFLVERSE_URL = (
    "https://github.com/nflverse/nflverse-data/releases/download/"
    "pbp/play_by_play_2023.csv"
)

OUTPUT_FOLDER = "outputs"


def load_data():
    """Download NFLVerse play-by-play data."""
    print("Downloading NFLVerse play-by-play data...")
    data = pd.read_csv(NFLVERSE_URL, low_memory=False)
    print(f"Downloaded {len(data):,} rows of NFL play-by-play data.")
    return data


def clean_data(data):
    """Clean the NFLVerse dataset and keep normal run/pass offensive plays."""
    columns_needed = [
        "season", "week", "posteam", "defteam", "play_type", "epa",
        "yards_gained", "success", "touchdown", "interception",
        "fumble_lost", "complete_pass", "sack"
    ]

    available_columns = [column for column in columns_needed if column in data.columns]
    cleaned = data[available_columns].copy()

    cleaned = cleaned[cleaned["posteam"].notna()]
    cleaned = cleaned[cleaned["defteam"].notna()]
    cleaned = cleaned[cleaned["play_type"].isin(["run", "pass"])]

    numeric_columns = [
        "epa", "yards_gained", "success", "touchdown",
        "interception", "fumble_lost", "complete_pass", "sack"
    ]

    for column in numeric_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").fillna(0)

    cleaned["Turnover_Play"] = cleaned["interception"] + cleaned["fumble_lost"]

    print(f"Cleaned dataset contains {len(cleaned):,} run/pass plays.")
    return cleaned


def build_team_metrics(cleaned):
    """Create team-level offensive and defensive statistics."""
    offense = (
        cleaned
        .groupby("posteam")
        .agg(
            Offensive_Plays=("epa", "count"),
            Average_EPA=("epa", "mean"),
            Total_EPA=("epa", "sum"),
            Success_Rate=("success", "mean"),
            Yards_Per_Play=("yards_gained", "mean"),
            Total_Yards=("yards_gained", "sum"),
            Touchdowns=("touchdown", "sum"),
            Turnovers=("Turnover_Play", "sum"),
            Interceptions=("interception", "sum"),
            Fumbles_Lost=("fumble_lost", "sum"),
            Sacks_Taken=("sack", "sum"),
        )
        .reset_index()
        .rename(columns={"posteam": "Team"})
    )

    defense = (
        cleaned
        .groupby("defteam")
        .agg(
            Defensive_Plays=("epa", "count"),
            Defensive_EPA_Allowed=("epa", "mean"),
            Yards_Allowed_Per_Play=("yards_gained", "mean"),
            Defensive_Success_Rate_Allowed=("success", "mean"),
            Takeaways=("Turnover_Play", "sum"),
            Sacks_Created=("sack", "sum"),
            Touchdowns_Allowed=("touchdown", "sum"),
        )
        .reset_index()
        .rename(columns={"defteam": "Team"})
    )

    teams = offense.merge(defense, on="Team", how="inner")

    teams["Turnover_Margin"] = teams["Takeaways"] - teams["Turnovers"]
    teams["EPA_Differential"] = teams["Average_EPA"] - teams["Defensive_EPA_Allowed"]
    teams["Yard_Differential"] = teams["Yards_Per_Play"] - teams["Yards_Allowed_Per_Play"]
    teams["Touchdown_Rate"] = teams["Touchdowns"] / teams["Offensive_Plays"]

    return teams


def filter_top_teams(teams):
    """Demonstrate filtering by showing teams with positive EPA differential."""
    top_teams = teams[teams["EPA_Differential"] > 0].copy()
    top_teams = top_teams.sort_values(by="EPA_Differential", ascending=False)

    print("\nFILTER EXAMPLE")
    print("Teams with positive EPA differential:")
    print(
        top_teams[
            ["Team", "Average_EPA", "Defensive_EPA_Allowed", "EPA_Differential"]
        ].round(3).to_string(index=False)
    )

    return top_teams


def answer_question_one(teams):
    """Question 1: Which NFL teams had the strongest offensive performance?"""
    print("\nQUESTION 1")
    print("Which NFL teams had the strongest offensive performance?")
    print("-" * 70)

    offense_rankings = teams[
        ["Team", "Average_EPA", "Success_Rate", "Yards_Per_Play", "Touchdowns", "Turnovers"]
    ].copy()

    offense_rankings["Offense_Score"] = (
        offense_rankings["Average_EPA"] * 0.50
        + offense_rankings["Success_Rate"] * 0.30
        + offense_rankings["Yards_Per_Play"] * 0.20
    )

    offense_rankings = offense_rankings.sort_values(by="Offense_Score", ascending=False)

    print(offense_rankings.head(10).round(3).to_string(index=False))

    best_team = offense_rankings.iloc[0]

    print(
        f"\nAnswer: The strongest offensive team was {best_team['Team']}. "
        "They had the best overall offensive score based on EPA, success rate, "
        "and yards per play."
    )

    return offense_rankings


def answer_question_two(teams):
    """Question 2: Which statistics are most strongly related to team strength?"""
    print("\nQUESTION 2")
    print("Which statistics are most strongly related to team strength?")
    print("-" * 70)

    comparison_columns = [
        "Average_EPA",
        "Success_Rate",
        "Yards_Per_Play",
        "Defensive_EPA_Allowed",
        "Yards_Allowed_Per_Play",
        "Defensive_Success_Rate_Allowed",
        "Turnover_Margin",
        "Touchdown_Rate",
        "EPA_Differential",
    ]

    correlations = teams[comparison_columns].corr()["EPA_Differential"]
    correlations = correlations.drop("EPA_Differential").sort_values(ascending=False)

    print(correlations.round(3).to_string())

    strongest_stat = correlations.index[0]
    strongest_value = correlations.iloc[0]

    print(
        f"\nAnswer: The statistic most strongly related to team strength was "
        f"{strongest_stat}, with a correlation of {strongest_value:.3f}."
    )

    return correlations


def run_machine_learning_model(teams):
    """Train a Linear Regression model to predict EPA differential."""
    print("\nMACHINE LEARNING")
    print("Predicting EPA differential with Linear Regression")
    print("-" * 70)

    features = [
        "Average_EPA",
        "Success_Rate",
        "Yards_Per_Play",
        "Turnovers",
        "Defensive_EPA_Allowed",
        "Yards_Allowed_Per_Play",
        "Takeaways",
        "Turnover_Margin",
        "Touchdown_Rate",
    ]

    target = "EPA_Differential"

    x = teams[features]
    y = teams[target]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42
    )

    model = LinearRegression()
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    results = pd.DataFrame(
        {
            "Actual_EPA_Differential": y_test,
            "Predicted_EPA_Differential": predictions,
        }
    )

    results["Prediction_Error"] = (
        results["Actual_EPA_Differential"] -
        results["Predicted_EPA_Differential"]
    ).abs()

    print(results.round(3).to_string(index=False))

    mean_error = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print(f"\nMean Absolute Error: {mean_error:.3f}")
    print(f"R-squared Score: {r2:.3f}")

    coefficients = pd.DataFrame(
        {"Feature": features, "Coefficient": model.coef_}
    ).sort_values(by="Coefficient", ascending=False)

    print("\nModel Coefficients:")
    print(coefficients.round(4).to_string(index=False))

    return results, coefficients


def create_graphs(teams, offense_rankings, correlations, ml_results):
    """Create graphs for the stretch challenge."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    top_10 = offense_rankings.head(10).sort_values(by="Offense_Score", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(top_10["Team"], top_10["Offense_Score"])
    plt.title("Top 10 NFL Offenses by Offense Score")
    plt.xlabel("Offense Score")
    plt.ylabel("Team")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/top_10_offenses.png")
    plt.close()

    plt.figure(figsize=(8, 6))
    plt.scatter(teams["Average_EPA"], teams["EPA_Differential"])
    plt.title("Average Offensive EPA vs EPA Differential")
    plt.xlabel("Average Offensive EPA")
    plt.ylabel("EPA Differential")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/epa_vs_team_strength.png")
    plt.close()

    sorted_correlations = correlations.sort_values(ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(sorted_correlations.index, sorted_correlations.values)
    plt.title("Statistics Correlation with Team Strength")
    plt.xlabel("Correlation")
    plt.ylabel("Statistic")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/correlations.png")
    plt.close()

    plt.figure(figsize=(8, 6))
    plt.scatter(
        ml_results["Actual_EPA_Differential"],
        ml_results["Predicted_EPA_Differential"]
    )
    plt.title("Actual vs Predicted EPA Differential")
    plt.xlabel("Actual EPA Differential")
    plt.ylabel("Predicted EPA Differential")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/actual_vs_predicted.png")
    plt.close()

    print("\nGraphs saved in the outputs folder.")


def save_reports(teams, offense_rankings, correlations, ml_results, coefficients):
    """Save result tables as CSV files."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    teams.to_csv(f"{OUTPUT_FOLDER}/team_metrics.csv", index=False)
    offense_rankings.to_csv(f"{OUTPUT_FOLDER}/offense_rankings.csv", index=False)
    correlations.to_csv(f"{OUTPUT_FOLDER}/correlation_results.csv", header=["Correlation"])
    ml_results.to_csv(f"{OUTPUT_FOLDER}/machine_learning_predictions.csv", index=False)
    coefficients.to_csv(f"{OUTPUT_FOLDER}/machine_learning_coefficients.csv", index=False)

    print("\nReports saved in the outputs folder.")


def main():
    """Run the full NFLVerse Team Performance Analyzer."""
    print("=" * 70)
    print("NFLVERSE TEAM PERFORMANCE ANALYZER")
    print("=" * 70)

    raw_data = load_data()
    cleaned_data = clean_data(raw_data)
    team_metrics = build_team_metrics(cleaned_data)

    print("\nDataset Summary:")
    print(f"Teams analyzed: {team_metrics['Team'].nunique()}")
    print(f"Total plays analyzed: {len(cleaned_data):,}")

    filter_top_teams(team_metrics)
    offense_rankings = answer_question_one(team_metrics)
    correlations = answer_question_two(team_metrics)
    ml_results, coefficients = run_machine_learning_model(team_metrics)

    create_graphs(team_metrics, offense_rankings, correlations, ml_results)
    save_reports(team_metrics, offense_rankings, correlations, ml_results, coefficients)

    print("\nProject complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
