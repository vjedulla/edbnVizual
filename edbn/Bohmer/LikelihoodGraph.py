"""
    Implementation of anomaly detection algorithm in multidimensional sequential data:
       [1] Böhmer, Kristof, and Stefanie Rinderle-Ma. "Multi-perspective anomaly detection in business process execution events."
             OTM Confederated International Conferences" On the Move to Meaningful Internet Systems". Springer, Cham, 2016.
"""
import multiprocessing as md

import pandas as pd

man = md.Manager()

global_dict_to_id = dict()
global_dict_to_value = dict()

cache_dict = dict()

dependencies = dict()

dict_evntTypLkly = man.dict()
dict_minLike = man.dict()

def clear_variables():
    global man
    man = md.Manager()

    global global_dict_to_id
    global_dict_to_id = dict()
    global global_dict_to_value
    global_dict_to_value= dict()

    global cache_dict
    cache_dict = dict()

    global dependencies
    dependencies = dict()

    global dict_evntTypLkly
    dict_evntTypLkly = man.dict()
    global dict_minLike
    dict_minLike = man.dict()

def basicLikelihoodGraph(logs, activity_index):
    V = set()
    global_dict_to_value[0] = "START"
    V.add(0)
    global_dict_to_value[1] = "END"
    V.add(1)
    D = set()
    dependencies[0] = []
    dependencies[1] = []

    grouped_logs = logs.groupby("Case") # Group log file according to Cases
    i = 0
    activity_mapping = {}
    for name, group in grouped_logs: # Iterate over all groupes
        print("Case", i, "/", len(grouped_logs))
        i += 1
        a_lst = 0
        for row in pd.DataFrame(group).itertuples(index = False): # Iterate over rows in group
            activity = row[activity_index]
            if activity not in activity_mapping:
                node_id = len(global_dict_to_value)
                dependencies[node_id] = []
                global_dict_to_value[node_id] = activity
                activity_mapping[activity] = node_id
            else:
                node_id = activity_mapping[activity]

            V.add(node_id)
            if node_id not in dependencies[a_lst]:
                D.add((a_lst, node_id, likeA(logs, a_lst, node_id, activity_index)))
                dependencies[a_lst].append(node_id)
            a_lst = node_id
        D.add((a_lst, 1, 1))
        dependencies[a_lst].append((1,1))
    return (V, D)


def likeA(log, a_s, a_e, activity_index):
    a_s = global_dict_to_value[a_s]
    a_e = global_dict_to_value[a_e]
    if a_s == "START":
        return 1

    tc = 0
    ec = 0

    filtered = log.loc[log["Activity"] == a_s]
    tc = len(filtered)
    for idx in filtered.index:
        if idx + 1 in log.index and log.at[idx + 1, "Case"] == log.at[idx, "Case"] and log.at[idx + 1, "Activity"] == a_e:
            ec += 1

    return ec / tc


def extendLikelihoodGraph(graph, logs, activity_index):
    F = set()
    V = graph[0]
    D = graph[1]
    v_cnt = 0
    for v in V:
        print("Variable", v_cnt, "/", len(V))
        v_cnt += 1
        if v == 0 or v == 1: # 0 and 1 are predefined as START and END
            continue
        V_next = {x for x in D if x[0] == v}
        D = D.difference(V_next)
        dependencies[v] = [x for x in dependencies[v] if x == 1] # Reset dependencies for v, only keep dependency to END
        activity_filtered = logs.loc[logs["Activity"] == global_dict_to_value[v]]
        E_r = set(x[1] for x in activity_filtered.itertuples(index=False)) # SELECT resources with activity == v
        for r in E_r:
            r_node_id = len(global_dict_to_value)
            global_dict_to_value[r_node_id] = r
            global_dict_to_id[r] = r_node_id
            F.add(r_node_id)
            like_g = likeG(activity_filtered, v, None, r, None, "resource", activity_index)
            D.add((v, r_node_id, like_g))
            dependencies[v].append((r_node_id, like_g)) # Add dependency from v to r_node_id (from ACTIVITY -> RESOURCE)
            dependencies[r_node_id] = [] # Init new dependency for resource node
            activity_resource_filtered = activity_filtered.loc[activity_filtered["Resource"] == r]
            E_wd = set(x[2] for x in activity_resource_filtered.itertuples(index=False))
            for wd in E_wd:
                wd_node_id = len(global_dict_to_value)
                global_dict_to_value[len(global_dict_to_value)] = wd
                F.add(wd_node_id)
                like_g = likeG(activity_resource_filtered, v, None, r, wd, "weekday", activity_index)
                D.add((r_node_id, wd_node_id, like_g))
                dependencies[r_node_id].append((wd_node_id, like_g)) # Add dependency from r_node_id to wd_node_id (from RESOURCE -> WEEKDAY)
                dependencies[wd_node_id] = [] # Init new dependency for resource node
                for v_next in V_next:
                    likely = likeG((logs, activity_resource_filtered), v, v_next[1], r, wd, "final", activity_index)
                    if likely > 0:
                        D.add((wd_node_id, v_next[1], likely))
                        dependencies[wd_node_id].append((v_next[1], likely))
    return (V.union(F), D)


def likeG(logs, a_s, a_e, r, wd, type, activity_index):
    cache_tuple = (a_s, a_e, r, wd, type)
    if cache_tuple in cache_dict:
        return cache_dict[cache_tuple]

    tc = 0
    ec = 0

    if type == "resource":
        tc = len(logs)
        ec = len(logs.loc[logs["Resource"] == r])
    elif type == "weekday":
        tc = len(logs)
        ec = len(logs.loc[logs["Weekday"] == wd])
    elif type == "final":
        log = logs[0]
        filtered = logs[1]
        filtered = filtered.loc[filtered["Weekday"] == wd]
        tc = len(filtered)
        for idx in filtered.index:
            if idx + 1 in log.index and log.at[idx + 1, "Case"] == log.at[idx, "Case"] and \
                    (log.at[idx + 1, "Activity"] == global_dict_to_value[a_e] or log.at[idx + 1, "Activity"] == global_dict_to_value[1]):
                ec += 1

    if tc == 0 or ec == 0:
        return 0
    if cache_tuple not in cache_dict:
        cache_dict[cache_tuple] = ec / tc

    return ec / tc

def mapEvents(graph, logs, lst_v, lst_va, f, lst_l, punAct, punOth):
    D = {x for x in graph[1] if x[0] == lst_v}
    fnd = False
    likly = 0
    for d in D:
        if global_dict_to_value[d[1]] == f: # f is a successor of the last successfully mapped event lst_v then
            lst_v = d[1]
            likly = d[2]
            fnd = True
            break
    if not fnd: # if the event f was not recorded in L then
        pun = punAct if isActivity(f) else punOth
        if lst_va is not None:
            tmp = evntTypLkly(graph, f, lst_va)
            f_avglkli = [x[1] for x in tmp if x[0] == f]
            if len(f_avglkli) != 0:
                likly = f_avglkli[0] * pun
            else:
                likyhds = [x[1] for x in tmp]
                gLkli = 1 - gini(sorted(list(likyhds)), len(likyhds))
                cLkly = 1 - classLkly(logs, f, lst_va, lst_v)
                likly = gLkli * cLkly * pun
        else:
            likly = lst_l + pun
    if isActivity(f):
        matchingActivities = [x for x in graph[0] if global_dict_to_value[x] == f]
        if len(matchingActivities) > 0:
            lst_v = matchingActivities[0]
            lst_va = lst_v
        else:
            lst_va = None
    return lst_v, lst_va, likly * lst_l

def minLike(graph, logs, a, s_max):
    if (a, s_max) in dict_minLike:
        return dict_minLike[(a, s_max)]
    min = 1
    grouped = logs.groupby("Case")
    for name, group in grouped:
        s_c = 0
        found_a = False
        l_c = 1
        for e_idx in group.index:
            e = list(group.loc[e_idx])
            s_c += 1
            # Determine l_a2r (ACTIVITY -> RESOURCE)
            id = -1 # Find ID for ACTIVITY NODE
            for key in dependencies.keys():
                if global_dict_to_value[key] == e[0]:
                    id = key
                    break

            try:
                l_a2r = [x for x in dependencies[id] if global_dict_to_value[x[0]] == e[1]][0] # (resource_id, likely)
            except IndexError:
                print("Error:", e)
                print(id, dependencies[id])
            # Determine l_r2wd (RESOURCE -> WEEKDAY)
            l_r2wd = [x for x in dependencies[l_a2r[0]] if global_dict_to_value[x[0]] == e[2]][0] # (weekday_id, likely)
            # Determine l_wd2a (WEEKDAY -> ACTIVITY
            if e_idx + 1 in group.index:
                l_wd2a = [x for x in dependencies[l_r2wd[0]] if global_dict_to_value[x[0]] == group.at[e_idx + 1, "Activity"]][0] # (activity, likely) | TODO: Possible to improve?
            else:
                l_wd2a = (0,1)
            l_c = l_c * l_a2r[1] * l_r2wd[1] * l_wd2a[1]
            if a in global_dict_to_value and e[0] == global_dict_to_value[a] and s_c == s_max:
                found_a = True
                break
            elif s_c > s_max:
                break
        if found_a and l_c < min:
            min = l_c
        elif not found_a:
            min = 0
    dict_minLike[(a, s_max)] = min
    return min

def isActivity(node):
    return node.startswith("a_")

def isRes(node):
    return node.startswith("r_")

def isWeekday(node):
    return node.startswith("wd_")

def evntTypLkly(graph, f, lst_va):
    if (f, lst_va) in dict_evntTypLkly:
        return dict_evntTypLkly[(f, lst_va)]

    E = [(d,d[2]) for d in graph[1] if d[0] == lst_va]
    E_extend = E.extend

    fnd_fs = set()
    fnd_fs_add = fnd_fs.add
    fnd_fs_diff = fnd_fs.difference
    kwn_e = set()
    kwn_e_add = kwn_e.add
    i = 0
    while i < len(E):
        e = E[i]
        i += 1
        kwn_e_add(e[0])
        if getType(global_dict_to_value[e[0][1]]) == getType(f):
            fnd_f = [x for x in fnd_fs if x[0] == global_dict_to_value[e[0][1]]]
            if len(fnd_f) == 0:
                fnd_fs.add((global_dict_to_value[e[0][1]], e[1]))
            else:
                fnd_fs = fnd_fs.difference(fnd_f)
                fnd_fs.add((fnd_f[0][0], fnd_f[0][1] + e[1]))
        else:
            E_extend([(x, e[1] * x[2]) for x in graph[1] if x[0] == e[0][1] and x not in kwn_e])
      #      i = 0
    dict_evntTypLkly[(f, lst_va)] = fnd_fs
    return fnd_fs

def getType(node):
    if node.startswith("a_"):
        return "Activity"
    elif node.startswith("r_"):
        return "Resource"
    elif node.startswith("wd_"):
        return "Weekday"

def classLkly(logs, f, lst_a, lst_v):
    tc = 0
    ec = 0

    if isRes(f):
        #print("ClassLkly - Resource")
        tc = len(logs.Resource.unique()) # total amount of resources
        ec = len(logs.loc[logs["Activity"] == global_dict_to_value[lst_a]].Resource.unique()) # total amount of resources with given activity
    elif isWeekday(f):
        #print("ClassLkly - Weekday")
        tc = len(logs.Weekday.unique()) # total amount of weekdays
        if isRes(global_dict_to_value[lst_v]):
            ec = len(logs.loc[(logs["Activity"] == global_dict_to_value[lst_a]) & (logs["Resource"] == global_dict_to_value[lst_v])]) # total amount of weekdays with given activity and resource
        else:
            ec = len(logs.loc[logs["Activity"] == global_dict_to_value[lst_a]].Weekday.unique())
    else:
        #print("ClassLkly - Else")
        filtered = logs.loc[logs["Activity"] == global_dict_to_value[lst_a]]
        tc = len({logs.at[idx + 1, "Activity"] for idx in filtered.index if idx + 1 in logs.index and logs.at[idx, "Case"] == logs.at[idx + 1, "Case"]})

        if isRes(global_dict_to_value[lst_v]):
            filtered = filtered.loc[filtered["Resource"] == global_dict_to_value[lst_v]]
            ec = len({logs.at[idx + 1, "Activity"] for idx in filtered.index if idx + 1 in logs.index and logs.at[idx, "Case"] == logs.at[idx + 1, "Case"]})
        else:
            filtered = filtered.loc[filtered["Weekday"] == global_dict_to_value[lst_v]]
            ec = len({logs.at[idx + 1, "Activity"] for idx in filtered.index if idx + 1 in logs.index and logs.at[idx, "Case"] == logs.at[idx + 1, "Case"]})
    try:
        max = 0.5
        min = 1 / (tc + 1)
        rawLkly = ec / tc
        if rawLkly > max:
            rawLkly = 1 - rawLkly
        return (rawLkly - min) / (max - min)
    except ZeroDivisionError:
        return 0


def gini(x,n):
    tmp = 0
    for i in range(0, n):
        tmp += (i+1) * x[i]
    if n == 0:
        return 0
    return (2 * tmp) / (n * sum(x)) - (n+1) / n


def ongoingLikelihoodDiff(graph, logs, trace, unused_attrs = 0):
    lst_v = 0
    lst_va = None
    lst_l = 1
    punAct = 0.9
    punOth = 0.95
    min_prob = 1
    i = 0
    for e in trace:
        i += 1
        for x_idx in range(len(e) - unused_attrs):
            f = e[x_idx]
            lst_v, lst_va, lst_l = mapEvents(graph, logs, lst_v, lst_va, f, lst_l, punAct, punOth)
      #  min_lik = minLike(graph, logs, lst_va, i)
      #  prob = lst_l - min_lik
        prob = lst_l
        if prob < min_prob:
            min_prob = prob
    return min_prob


def test_trace(graph, log, trace, unused_attrs = 0):
    """
    Return score for a trace given the graph and log

    :param graph: Trained Event graph to use
    :param log: Log file used for training
    :param trace: Current trace to score
    :param unused_attrs: Number of attributes to skip
    :return:
    """
    print("Testing")
    return ongoingLikelihoodDiff(graph, log, trace, unused_attrs)

def test_trace_parallel(graph, log, trace, results, unused_attrs = 0):
    """
    Same function as test_trace_get_diff but can be used in a parallel setting (multiple processes)
    """
    print("Testing")
    results.put((ongoingLikelihoodDiff(graph, log, trace, unused_attrs), trace[-1][-1] == '1'))

def test_trace_parallel_for(graph, log, trace, unused_attrs = 0):
    """
    Same function as test_trace_get_diff but can be used in a parallel setting (multiple processes)
    """
    print("Testing")
    trace = list(trace.itertuples(index=False))
    return (trace[-1][-2], ongoingLikelihoodDiff(graph, log, trace, unused_attrs), trace[-1][-1] == '1')