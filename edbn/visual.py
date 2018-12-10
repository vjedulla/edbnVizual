from Experiments import RuneDBN
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import random

import seaborn as sns


from ConceptDrift import ConceptDrift


from scipy.stats import gaussian_kde

def flatten(d):
	for child in d:
		t = np.array(d[child])
		yield np.log10(np.sum(t)/len(t))
		# for f in d[child]:
		# 	yield f

def kde_scipy(x, x_grid, bandwidth=None, **kwargs):
	"""Kernel Density Estimation with Scipy"""
	# kde = gaussian_kde(x, bw_method=bandwidth / x.std(ddof=1))
	# kde = gaussian_kde(x, bw_method='scott')
	bandwidth = float(np.std(x)/5) if bandwidth is None else bandwidth
	kde = gaussian_kde(x, bw_method=bandwidth)
	return kde.evaluate(x_grid)


s, pvals, model = RuneDBN.run(default_dataset="Data/BPIC15_1_sorted.csv", default_alias="run/")

x, y = ConceptDrift.plot_single_scores(s)

flatten_scores = list(flatten(s))

every_val = np.array(flatten_scores)
N = len(every_val)

# np.random.shuffle(every_val)

min_val = np.min(every_val)
max_val = np.max(every_val)

print("Min:", min_val)
print("Max:", max_val)

# every_val = np.interp(every_val, (min_val, max_val), (0, +1))

x_grid = np.linspace(min_val, max_val, N)

# z = np.polyfit(x_grid, every_val, 1)

fig, ax = plt.subplots(2, 1, figsize=(12, 6))
names = ['Kernel Density Estimation', '3 random traces KDE']
arrays = [(every_val, x_grid)]

main_pal = sns.cubehelix_palette(8)
# scale down the kernel as https://en.wikipedia.org/wiki/Kernel_density_estimation#Definition
# 1/nh * h = 1/n
pdf = kde_scipy(every_val, x_grid, bandwidth=0.05) * 0.05
check = np.max(pdf)
# print("CHECK", check/0.05)
ax[0].stackplot(x_grid, pdf, color=main_pal[np.random.randint(4, len(main_pal))], alpha=0.5)
ax[0].set_title(names[0])


keys = list(s)
how_many = 3


# pal = sns.color_palette("Blues_d")
pal = sns.xkcd_palette(["reddish orange", "lightblue", "ocean green"])
print(pal)

for i in range(how_many):
	ri = np.random.randint(0, len(keys))
	trace = np.array(s[keys[ri]])
	trace_norm = np.log10(trace)

	trace_max_v = np.max(trace_norm)
	trace_min_v = np.min(trace_norm)
	x_grid_trace_tmp = np.linspace(trace_min_v, trace_max_v, len(trace_norm))
	x_grid_trace = np.linspace(trace_min_v-1, trace_max_v+1, 1000)

	pdf_trace = kde_scipy(trace_norm, x_grid_trace, bandwidth=0.05) * 0.05
	ax[1].stackplot(x_grid_trace, pdf_trace, color=pal[i], alpha=0.6)


ax[1].set_title(names[1])
plt.legend(loc='upper left')
plt.show()
