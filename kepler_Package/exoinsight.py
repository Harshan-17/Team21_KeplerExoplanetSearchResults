import pandas as pd


# Load dataset
def load_data(file_path):
    return pd.read_csv(file_path)


# Get confirmed planets
def get_confirmed_planets(data):
    return data[data["koi_disposition"] == "CONFIRMED"]


# Get false positives
def get_false_positives(data):
    return data[data["koi_disposition"] == "FALSE POSITIVE"]


# Get candidate planets
def get_candidates(data):
    return data[data["koi_disposition"] == "CANDIDATE"]


# Calculate average of a column
def calculate_average(data, column):
    return data[column].mean()


# Generate summary statistics
def get_summary(data, columns):
    return data[columns].describe()


# Assign priority based on probability
def assign_priority(probability):
    if probability >= 0.80:
        return "High"
    elif probability >= 0.50:
        return "Medium"
    else:
        return "Low"


# Add priority to candidate predictions
def add_priority(data, probability_column):
    data = data.copy()

    data["priority"] = data[probability_column].apply(assign_priority)

    return data