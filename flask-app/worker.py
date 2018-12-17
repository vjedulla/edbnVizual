from edbn.Experiments import RuneDBN

def solve_edbn(task, filepath, alias):
    # scores, pvalues = RuneDBN.run()
    model = RuneDBN.only_train(default_dataset=filepath, default_alias=alias)
    return model

def train_and_score(model, alias, filename, event_emit_obj):
    event_emit_obj('score_resp', {'step': 1, "msg": "Preparing to train variables."})
    scores = RuneDBN.train_vars_and_test(model, alias, filename, event_emit_obj)
    return scores