"""
Simple script to extract fields from tweets, writing to CSV

For all fields of a tweet, see the Twitter documentation: 
https://dev.twitter.com/docs/platform-objects/tweets
"""

import csv
import json
import argparse


def write_csv(inhandle, outhandle, counter=10000):
    """Takes json infile handle and csv outfile handle. Writes CSV from JSON"""

    ## ADD FIELDS HERE. These are the CSV column headers. Should reflect the
    ## fields chosen below, so that the CSV contains accurate column labels
    csv_header = [
        "TweetId",
        "UserID",
        "UserScreenName",
        "TweetDate",
        "TweetText",
        "IsRetweet",
        "RetweetedID",
    ]

    csv_writer = csv.writer(outhandle)
    csv_writer.writerow(csv_header)
    line_count = 0
    for line in inhandle:
        if line_count % counter == 0:
            print "Processing tweet {0}".format(line_count)
        line_count += 1

        json_tweet = json.loads(line)
        row = []

        ## ADD FIELDS HERE. For all available fields, refer to the Twitter doc
        ## page above. Note that tweet fields are accessed via the ["FIELD"]
        ## notation. Nested fields (eg: user) can be chained together, as in
        ## json_tweet["user"]["screen_name"]
        add_field_to_row(row, json_tweet["id_str"])
        add_field_to_row(row, json_tweet["user"]["id_str"])
        add_field_to_row(row, json_tweet["user"]["screen_name"])
        add_field_to_row(row, json_tweet["created_at"])
        add_field_to_row(row, json_tweet["text"])

        # Check whether tweet is an official Retweet
        if "retweeted_status" in json_tweet:
            add_field_to_row(row, "True")
            add_field_to_row(row, json_tweet["retweeted_status"]["id_str"])
        else:
            add_field_to_row(row, "False")
            add_field_to_row(row, "NA")

        # ... etc:
        # add_field_to_row(row, json_tweet["SOME FIELD"])

        csv_writer.writerow(row)
    print "Complete. CSV Outfile: {0}".format(outhandle.name)


## IGNORE THIS. Simple code to clean tweet fields
def add_field_to_row(row, field):
    """Adds field to row list, making sure field is safe"""
    if type(field) == unicode:
        field = field.encode("utf8")
    else:
        field = str(field)
    field = " ".join(field.split())
    row.append(field)

## IGNORE THIS. Code to read command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reads JSON tweet file, exports simple CSV")
    parser.add_argument("-i", "--infile", type=argparse.FileType("r"), required=True,
        dest="inhandle", help="Input file of tweets. JSON format, tweet-per-line")
    parser.add_argument("-o", "--outfile", type=argparse.FileType("wb"), required=True,
        dest="outhandle", help="Tweet CSV output file to create")
    args = parser.parse_args()
    write_csv(args.inhandle, args.outhandle)


