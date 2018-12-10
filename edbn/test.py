from Experiments import RuneDBN
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import random
from sklearn.preprocessing import normalize
from sklearn.preprocessing import scale


s, pvals = RuneDBN.run()

# s = {
#     '1': [1, 2, 3, 4, 5, 6, 7, 8, 9],
#     '2': [200, 4,22, 43, 3e-9, 23, 5],
#     '3': [12, 43, 11, 33, 89, 4, 5, 8]
# }

cnt = 0

all_colors = 2 * np.pi * np.random.rand(7)

tt = ['r', 'b', 'g', 'y']

def plot_all(ax):
    cnt = 0
    for trace in s:

        if cnt > 200:
            break

        scores, time = zip(*s[trace])
        trace_np = np.array(scores)
        time_np = np.array(time)

        time_np = np.interp(time_np, (0, 9999), (0, +1))

        # mean = np.mean(trace_np)
        std = np.std(trace_np)

        index_bad = np.where(trace_np < std / 4)
        index_good = np.where(trace_np > std / 4)

        topK_bad = trace_np[index_bad]
        topK_good = trace_np[index_good]

        time_bad = time_np[index_bad]
        time_good = time_np[index_good]

        r_good = (1 / np.sqrt(topK_good)) * topK_good
        theta_good = 2 * np.pi * time_good
        area_good = 5 * (1 / r_good) * r_good

        r_bad = (1 / np.sqrt(topK_bad)) * topK_bad
        theta_bad = 20 * np.pi * time_bad
        area_bad = 1 * (1 / r_bad) * r_bad

        r_good_mean = np.mean(r_good)
        r_bad_mean = np.mean(r_bad)
        theta_good_mean = np.mean(theta_good)
        theta_bad_mean = np.mean(theta_bad)

        ax.scatter(theta_bad_mean, r_bad_mean, c='r', s=area_bad, alpha=1, zorder=2)
        ax.scatter(theta_good_mean, r_good_mean, c='b', s=area_good, alpha=0.55, zorder=3)

        ax.set_yticklabels([])
        cnt+=1

def plot(which, ax):
    scores, time = zip(*s[which])
    trace_np = np.array(scores)
    time_np = np.array(time)

    # time_np = scale(time_np, axis=0, with_mean=True, with_std=True, copy=True)
    time_np = np.interp(time_np, (time_np.min(), time_np.max()), (0, +1))

    # mean = np.mean(trace_np)
    std = np.std(trace_np)

    index_bad = np.where(trace_np < std/4)
    index_good = np.where(trace_np > std/4)

    topK_bad = trace_np[index_bad]
    topK_good = trace_np[index_good]

    time_bad = time_np[index_bad]
    time_good = time_np[index_good]

    r_good = trace_np# topK_good # (1/np.sqrt(topK_good)) * topK_good
    theta_good = 2 * np.pi *  time_np#time_good
    area_good = 5 * (1 / r_good) * r_good


    r_bad = trace_np# topK_bad # (1/np.sqrt(topK_bad)) * topK_bad
    theta_bad = 2 * np.pi * time_np# time_bad
    area_bad = 5 * (1/r_bad) * r_bad

    print("r_good:", r_good)
    print("time_good:", time_good)
    print("theta_good:", theta_good)

    print("-"*50)

    max_lim = np.max(r_good)
    min_lim = np.min(r_good)

    # ax.plot(theta_good[0], r_good[0], c='g', s=50, alpha=1, zorder=2)
    # ax.plot(theta_bad, r_bad, c='r', s=area_bad, alpha=1, zorder=2)
    # ax.plot(theta_good, r_good, c='b', s=area_good, alpha=0.55, zorder=3)

    ax.scatter(theta_good[0], r_good[0], c='g', s=50, alpha=1, zorder=2)
    ax.plot(theta_bad, r_bad, '-o', c='b', linewidth=0.7, markersize=0.9)

    # ax.plot(theta_good, r_good, '-o', c='b', linewidth=0.5, markersize=0.9)
    ax.grid(color='#dddddd', zorder=0)

    ax.set_rlim(0, max_lim + min_lim)
    ax.set_yticklabels([])


def plot_ps(pvs, ax):
    bins = 10
    vals = np.array(pvs[1])

    ws = int(np.floor(len(vals)/bins))
    # print("ws", ws)
    # print([(x+1)*ws for x in range(bins)] + [len(vals)-rem])
    data_bins = np.split(vals, [(x+1)*ws for x in range(bins)])
    bin_height = []

    # print(len(data_bins))

    for b in data_bins:
        mean_b = np.mean(b)
        bin_height.append(mean_b)

    # print(bin_height)
    # exit()

    # top = vals[np.where(vals > -1 * std/40)]
    N = len(bin_height)
    print(np.array(bin_height))
    plot_data = np.array(bin_height) - np.min(bin_height)
    print(plot_data)
    # exit()
    # print(plot_data)
    theta = np.arange(0.0, 2 * np.pi, 2*np.pi/N)
    radii = np.array(plot_data)
    width = np.pi/bins
    bars = ax.bar(theta, radii, width=width)

    for r, bar in zip(radii, bars):
        bar.set_facecolor(cm.jet(r))
        bar.set_alpha(0.5)


keyset = list(s.keys())

rand1 = keyset[random.randint(0, len(s)-1)]
rand2 = keyset[random.randint(0, len(s)-1)]
rand3 = keyset[random.randint(0, len(s)-1)]


fig = plt.figure()
# all data
ax1 = fig.add_subplot(221, projection='polar')
plot_all(ax1)

# plot p-values
ax2 = fig.add_subplot(222, projection='polar')
plot_ps(pvals, ax2)

# plot random trace
ax3 = fig.add_subplot(223, projection='polar')
plot(rand1, ax3)

# plot another random trace
ax4 = fig.add_subplot(224, projection='polar')
plot(rand2, ax4)


#
# for trace in s:
#     # print(trace, tt[cnt%len(tt)])
#
#     # if cnt > 2:
#     #     break
#
#     trace_np = np.array(s[trace])
#     # r = np.random.randint(0, len(trace_np))
#     # trace_np[r] = 20
#     # trace_np[r] = np.random.uniform(0, 5e-39)
#
#     # trace_np.sort(kind='mergesort')
#
#     mean = np.mean(trace_np)
#     std = np.std(trace_np)
#
#     # print(std)
#
#     topK_bad = trace_np[np.where(trace_np < std/4)]
#     topK_good = trace_np[np.where(trace_np > std/4)]
#
#     # print(len(topK_good))
#     # print(len(topK_bad))
#
#     r_good = (1/np.sqrt(topK_good)) * topK_good
#     theta_good = 80 * np.pi * r_good
#     area_good = 5 * (1 / r_good) * r_good
#     # area_good = 50 * r_good
#
#
#
#     r_bad = (1/np.sqrt(topK_bad)) * topK_bad
#     theta_bad = 80 * np.pi * r_bad
#     area_bad = 5 * (1/r_bad) * r_bad
#     # area_bad = 50 * r_bad
#
#     ax.scatter(theta_bad, r_bad, c='r', s=area_bad, alpha=1, zorder=2)
#
#     ax.scatter(theta_good, r_good, c='b', s=area_good, alpha=0.55, zorder=3)
#     cnt += 1


# ax.set_title("A line plot on a polar axis", va='bottom')
plt.show()
