"""
Tool: tweets per (day, hour, minute) figure, shown and saved optionally
"""

import argparse
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime, timedelta

## COMMANDLINE ################################################################
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--user", default="smapp_readOnly")
parser.add_argument("-w", "--password", required=True)
args = parser.parse_args()

## CONFIG #####################################################################
start = datetime(2010,1,1)   # Time in UTC
step_size = timedelta(days=10)     # Time step to observe (timedelta(hours=1))
num_steps = 200                    # Number of steps to plot

client = MongoClient("smapp-politics", 27011)   # Dataserver host, port
database = client["USLegislator"]                            # Database
collection = database["tweets"]                         # Tweet collection

plot_title = "USLEG: Tweets per 10-day"
x_label = "Time"
y_label = "Tweets"
transparency = 0.70     # Bar transparency
bar_width = 0.8         # Bar width
x_label_step = 5        # How often to show an x-label

## MAIN #######################################################################

# Auth to DB
if not database.authenticate(args.user, args.password):
  raise Exception("DB authentication failed")


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
