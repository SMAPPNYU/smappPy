# -*- coding: utf-8 -*-
from pymongo import MongoClient
from datetime import datetime, timedelta
from seaborn import color_palette
import matplotlib.pyplot as plt

## Config #####################################################################
start = datetime(2014, 1, 1)
step_size = timedelta(days=1)
num_steps = 181

client = MongoClient("smapp-data.bio.nyu.edu", 27011)
database = client["RandomUsers"]
collection = database["tweets"]
database.authenticate("smapp_readOnly", "smapp_nyu")

plot_super_title = "Random User Collection - Tweets per day"
plot_sub_title = "Tweets per day through 2014"
x_label = "Day, 1/01/2014 (280 days)"
transparency = 0.4
line_width = 2.0
line_color = "red"
x_label_step = 10


# List of events, event is a tuple (day number (from 0), event description, position 
# ("top" or "bottom"))
# Turkey:
#events = [
#    (1, "First instance of excessive force used against protesters by police", "bottom"),
#    (11, "Police begin to clear the square", "top"),
#    (15, "Police clear Gezi Park", "top"),
#    (17, "Standing Man protest begins", "top"),
#]
# Ukraine:
# events = [
#     (5, "Protesters beaten by riot police", "top"),
#     (52, "Anti-protest law passed", "top"),
#     (55, "Hrushevskoho standoff", "top"),
#     (58, "First fatalities during protest", "top"),
#     (87, "Worst single day of violence", "bottom"),
#     (89, "Yanukovych flees", "bottom"),
# ]
events = []
## End Config #################################################################


# Get tweets per day
tweets_per_day = []
for step in range(num_steps):
    query_start = start + (step * step_size)
    tweets = collection.find({"timestamp": {"$gte": query_start, "$lt": query_start + step_size}})
    total = tweets.count(with_limit_and_skip=True)
    tweets_per_day.append(total)
    print "{0}: {1} - {2}: {3}".format(step, query_start, query_start + step_size, total)

# <codecell>

plt.plot(range(num_steps), tweets_per_day, alpha=transparency, linewidth=line_width, color=line_color)

ymin, ymax = plt.ylim()
for e in events:
    plt.axvline(e[0], linestyle="--", color="#999999")
    if e[2] == "bottom":
        plt.text(e[0] + 0.2, ymin + (0.05 * ymax), e[1], rotation=-90, verticalalignment="bottom")
    else:
        plt.text(e[0] + 0.2, ymax - (0.05 * ymax), e[1], rotation=-90, verticalalignment="top")
    
    

plt.xlim(0, num_steps-1)
plt.xlabel(x_label)
plt.ylabel("# Tweets")
plt.suptitle(plot_super_title, fontsize=14)
plt.title(plot_sub_title)
plt.tick_params(axis="x", which="both", bottom="on", top="off", length=8, width=1, color="#999999")
plt.xticks(range(num_steps)[::x_label_step],
           ["{0}-{1}-{2}".format(d.year, d.month, d.day) for d in [start + (i * step_size) for i in range(num_steps)[::x_label_step]]],
           rotation=55)
plt.show()

