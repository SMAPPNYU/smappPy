"""
Logging module. Imports stdlib logging and sets some of our favorite basicConfig (format)

@jonathanronen 2015/4
"""
import logging
logging.basicConfig(format='%(asctime)s\t%(pathname)s:%(lineno)s--%(levelname)s: %(message)s', level=logging.INFO)