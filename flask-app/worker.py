from edbn.Experiments import RuneDBN

def solve_edbn(task, filepath, alias):
    # scores, pvalues = RuneDBN.run()
    scores, _, model = RuneDBN.run(default_dataset=filepath, default_alias=alias)
    return scores, model