"""
Tool: tweets per (day, hour, minute) figure, shown and saved optionally
"""

import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime, timedelta

## Config #####################################################################

start = datetime(2014,8,1,12,0)   # Time in UTC
step_size = timedelta(minutes=1)     # Time step to observe (timedelta(hours=1))
num_steps = 60                    # Number of steps to plot

client = MongoClient("smapp-data.bio.nyu.edu", 27011)   # Dataserver host, port
database = client["Ukraine"]                            # Database
collection = database["tweets"]                         # Tweet collection
database.authenticate("smapp_readOnly", "smapp_nyu")    # Auth details

plot_title = "Ukraine: Tweets per minute, 2014-08-01"
x_label = "Time"
y_label = "Tweets"
transparency = 0.70     # Bar transparency
bar_width = 0.8         # Bar width
x_label_step = 2        # How often to show an x-label

## End Config #################################################################

times = [start + (i * step_size) for i in range(num_steps)]
counts = []
for step in times:
    tweets = collection.find({"timestamp": {"$gte": step, "$lt": step + step_size}})
    counts.append(tweets.count())

sns.set_style("darkgrid")
sns.set_palette("husl")

bars = plt.bar(range(num_steps), 
               counts, 
               width=bar_width, 
               linewidth=0.0, 
               alpha=transparency,
               align="edge")

plt.xlim(0, num_steps)
plt.tick_params(axis="x", which="both", bottom="on", top="off", length=8, width=1, color="#999999")
plt.xlabel(x_label)
plt.ylabel(y_label)
plt.title(plot_title)

if step_size.total_seconds() < 60*60:
    plt.xticks(range(num_steps)[::x_label_step],
           ["{0}:{1}".format(t.hour, t.minute) for t in times[::x_label_step]],
           rotation=90)
elif step_size.total_seconds() < 60*60*24:
    plt.xticks(range(num_steps)[::x_label_step],
           ["{0}-{1} {2}:{3}".format(t.month, t.day, t.hour, t.minute) for t in times[::x_label_step]],
           rotation=90)
else:
    plt.xticks(range(num_steps)[::x_label_step],
           ["{0}-{1}-{2}".format(t.year, t.month, t.day) for t in times[::x_label_step]],
           rotation=90)

plt.tight_layout()
plt.show()