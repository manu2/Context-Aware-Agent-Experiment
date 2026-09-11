# If val is object:
for cat, grp_val in val.groupby(f_cat):
    totals[cat] += sum(grp_val)
