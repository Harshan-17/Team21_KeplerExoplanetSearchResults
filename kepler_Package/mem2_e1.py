import exoinsight

data = exoinsight.load_data("prepared_data.xls")

confirmed = exoinsight.get_confirmed_planets(data)

false_positives = exoinsight.get_false_positives(data)

candidates = exoinsight.get_candidates(data)

print("Confirmed:", len(confirmed))
print("False Positives:", len(false_positives))
print("Candidates:", len(candidates))