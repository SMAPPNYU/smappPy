"""
Takes input text file, outputs new file with all lines no greater than
75 characters. Must preserve all other content (newlines, etc)

@auth dpb
@date 3/24/2014
"""

import argparse
import textwrap

# Main section - read in commandline arguments, format content, write to new file
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Formats input file line length to standard, outputs new file")
    parser.add_argument("-i", "--infile", action="store", dest="infile", required=True,
        help="File to format")
    parser.add_argument("-o", "--outfile", action="store", dest="outfile", required=True,
        help="New file to create with formatted content")
    parser.add_argument("-n", "--linesize", action="store", type=int, dest="max_line", 
        default=75, help="Maximum line size for formatted output file")
    parser.add_argument("-p", "--sep_para", action="store_true", dest="sep_para", default=False,
        help="A flag for separating paragraphs with an extra line break.")
    args = parser.parse_args()

    inhandle = open(args.infile, "r")
    outhandle = open (args.outfile, "w")

    # Get all pre-existing lines in the file
    lines = inhandle.readlines()

    for line in lines:
        wrapped_lines = textwrap.wrap(line, args.max_line)
        for wl in wrapped_lines:
            outhandle.write("{0}\n".format(wl))
        if args.sep_para:
            outhandle.write("\n")

    print "Completed processing: {0}".format(args.infile)
    print "Formatted file: {0}".format(args.outfile)
