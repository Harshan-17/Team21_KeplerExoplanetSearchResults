import pandas as pd
import exoinsight

candidate_data = pd.read_csv("memeber2_candidate_predictions.csv")

candidate_data["priority"] = candidate_data[
    "predicted_confirmed_probability"
].apply(exoinsight.assign_priority)

print(candidate_data.head())