#!/usr/bin/env python

"""Script that builds silly SQL statements"""

from nltk.corpus import brown
from string import Template

import nltk
import random
import sys

FIELDS = None

WORDS = None

def load_words():
   """Build a list of words to choose randomly from"""

   WORDS = brown.words()


def replace_sql(sql):
   """Perform replacement on skeleton SQL"""

   return sql.substitute(columns='cat_name', tables='cats')


def main():
   """Main Entry Point"""

   SQL = Template('SELECT $columns         \n' + \
                  '  FROM $tables          \n')

   load_words()
   SQL = replace_sql(SQL)

   print SQL


if __name__ == '__main__':
   sys.exit(main())
