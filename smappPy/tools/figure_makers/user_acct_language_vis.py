
# coding: utf-8

# In[1]:

import matplotlib.pyplot as plt

from pprint import pprint
from pymongo import MongoClient
from seaborn import color_palette
from collections import OrderedDict
from datetime import datetime, timedelta


# In[2]:

# Config: store languages to capture data on (for users and tweets)
user_acct_langs = ["tr"]
tweet_langs = ["tr", "en"]


# In[3]:

# Config: database
client = MongoClient("smapp-data.bio.nyu.edu", 27011)
database = client["TurkeyParkProtests"]
if not database.authenticate("smapp_readOnly", "smapp_nyu"):
    raise Exception("DB authentication failed")
collection = database["tweets"]


# In[4]:

# Config: time range
start = datetime(2013, 5, 31)
end = datetime(2013, 7, 1)
step = timedelta(days=1)
time_span = end - start

days = [d for d in [start + (i * step) for i in range(time_span.days)]]
print len(days)


# In[6]:

# Init: set up language_usage_dict (lvl 0: day, lvl 1: user acct lang, lvl 2: tweet lang occurrences)
tweet_langs += ["other"]
language_usage_dict = OrderedDict()
for day in days:
    language_usage_dict[day] = {}
    for user_lang in user_acct_langs:
        language_usage_dict[day][user_lang] = {}
        for tweet_lang in tweet_langs:
            language_usage_dict[day][user_lang][tweet_lang] = 0
#pprint(language_usage_dict, indent=4)


# In[7]:

# Run: Query for all day tweets, build up language dict counts
for day in days:
    tweets = collection.find({"timestamp": {"$gte": day, "$lt": day + step}})
    print "Considering day {0}, {1} tweets".format(day, tweets.count(with_limit_and_skip=True))
    
    for tweet in tweets:

        if "lang" not in tweet["user"]:
            continue
        if tweet["user"]["lang"] not in user_acct_langs:
            continue
        
        if "lang" not in tweet:
            if "retweeted_status" in tweet and tweet["retweeted_status"] != None:
                if "lang" in tweet["retweeted_status"]:
                    tweet["lang"] = tweet["retweeted_status"]["lang"]
                else:
                    tweet["lang"] = "unk"
            else:
                tweet["lang"] = "unk"
        
        if tweet["lang"] in tweet_langs:
            language_usage_dict[day][tweet["user"]["lang"]][tweet["lang"]] += 1
        else:
            language_usage_dict[day][tweet["user"]["lang"]]["other"] += 1


# In[8]:

import pickle
outfile = "/home/dpb/data/ukraine/user_acct2tweet_lang_per_day.pkl"
with open(outfile, "w") as handle:
    pickle.dump(language_usage_dict, handle)
print "Stored language usage dict to pkl: {0}".format(outfile)


# In[12]:

import pickle
infile = "/home/dpb/data/turkey/user_acct2tweetlang_per_day.pkl"
with open(infile, "r") as handle:
    language_usage_dict = pickle.load(handle)
print "Recovered language usage dict from pkl:  {0}".format(infile)


# In[10]:

# Plot single acct-lang users - stacked bar style
b_val = 0.000000001
x_res = 2
colors = color_palette("hls", 7)

# Get a list of tweet-language dicts for language 'tr' for each day
tr_tlds = [uld["tr"] for uld in [language_usage_dict[d] for d in days]]

# Get sum of all languages in tweet language dicts for language 'tr'
sums = [float(sum(tld.values())) for tld in tr_tlds]

# Get list of tweet-lang values for each lang in the tweet language dicts
tr_tvals = [float(tld["tr"]) for tld in tr_tlds]
en_tvals = [float(tld["en"]) for tld in tr_tlds]
ot_tvals = [float(tld["other"]) for tld in tr_tlds]

# Get proportions of tweet languages
tr_props= [t[0]/(t[1] + b_val) for t in zip(tr_tvals, sums)]
en_props= [t[0]/(t[1] + b_val) for t in zip(en_tvals, sums)]
ot_props= [t[0]/(t[1] + b_val) for t in zip(ot_tvals, sums)]

# BARS
fig, ax1 = plt.subplots()
tr_bars = ax1.bar(range(len(days)), tr_props, width=0.8, linewidth=0, color=colors[0])
en_bars = ax1.bar(range(len(days)), en_props, width=0.8, linewidth=0, color=colors[4], bottom=[a for a in tr_props])
ot_bars = ax1.bar(range(len(days)), ot_props, width=0.8, linewidth=0, color="#c9c9c9", bottom=[a+b for a,b in zip(tr_props, en_props)])


ax1.set_xlabel("Day, 5/31/2013 to 6/31/2013", fontsize=14)
ax1.set_ylabel("Tweet language proportion", fontsize=14)

plt.xticks(range(len(days))[::x_res], 
           ["{0}-{1}".format(d.month, d.day) for d in days][::x_res], 
           rotation=55, fontsize=13)
plt.axis([0, len(days), 0.0, 1.05])

ax2 = ax1.twinx()
ax2.plot(range(len(days)), sums, linestyle="-", linewidth=3.0, color="#515151", label="Total tweets")
ax2.set_ylabel("Total tweets from Turkish language accounts", fontsize=14)

ax1.legend((tr_bars[0], en_bars[0], ot_bars[0]), ('tr', 'en', 'other'), loc=2, ncol=4, fontsize=14)
ax2.legend(loc=1, fontsize=14)

plt.tick_params(axis="x", which="both", bottom="on", top="off", length=5, width=1, color="#999999")
plt.suptitle("Twitter Language Usage By Day", fontsize=16)
plt.title("Tweet language proportion of users w/ account language 'TR'", fontsize=14)
plt.show()


# In[194]:

# AREAS
fig, ax1 = plt.subplots()
ax1.plot(range(len(days)), ot_props, linestyle="-", color="#a5a5a5", label="Other")
ax1.plot(range(len(days)), ru_props, linestyle="-", color=colors[0], label="RU")
ax1.plot(range(len(days)), en_props, linestyle="-", color=colors[2], label="EN")
ax1.plot(range(len(days)), uk_props, linestyle="-", color=colors[4], label="UK")

ax1.fill_between(range(len(days)), uk_props, 0, color=colors[4], alpha=0.8)
ax1.fill_between(range(len(days)), en_props, 0, color=colors[2], alpha=0.8)
ax1.fill_between(range(len(days)), ru_props, 0, color=colors[0], alpha=0.8)
ax1.fill_between(range(len(days)), ot_props, 0, color="#a5a5a5", alpha=0.8)
ax1.set_xlabel("Days, 11/25/2013 to 2/28/2014", fontsize=14)
ax1.set_ylabel("Tweet language proportion", fontsize=14)
plt.xticks(range(len(days))[::x_res], 
           ["{0}-{1}".format(d.month, d.day) for d in days][::x_res], 
           rotation=55, fontsize=13)
plt.axis([0, len(days)-1, 0.0, 1.0])

ax2 = ax1.twinx()
ax2.plot(range(len(days)), sums, linestyle="--", color="#515151", linewidth=2, label="Total tweets")
ax2.set_ylabel("Total UK-account tweets", fontsize=14)

ax1.legend(fontsize=14, loc=2)
ax2.legend(fontsize=14, loc=1)

plt.tick_params(axis="x", which="both", bottom="on", top="off", length=5, width=1, color="#999999")
plt.suptitle("Twitter Language Usage By Day", fontsize=16)
plt.title("Tweet language proportion of users w/ account language 'UK'", fontsize=14)
plt.show()


# In[195]:



