#!/usr/bin/env python

"""Script that builds silly SQL statements"""

from cPickle import dump, load
from nltk.corpus import brown
from pattern.en import pluralize, singularize, wordnet
from string import Template

import json
import keys
import nltk
import os
import pattern.en
import random
import requests
import sys


def build_from_clause(tables):
   """Assembles a FROM clause from a list of tables"""

   from_clause = ''
   for s in tables:
      if from_clause:
         from_clause = from_clause + ', '

      from_clause = from_clause + format(pluralize(s.hypernym[0]))

   return from_clause


def build_where_clause(tables):
   """Assembles a WHERE clause from a list of tables"""

   # The first table in the where clause to join every other table to
   first = format(singularize(tables[0].hypernym[0]))

   # Loop through the rest of the tables joining by ID
   where_clause = ''
   for s in tables[1:]:
      t = format(s.hypernym[0])

      if not where_clause:
         where_clause = ' WHERE '
      else:
         where_clause = where_clause + '   AND '

      where_clause = where_clause + first + '_id = ' + format(singularize(t)) + '_' + first + '_id\n'

   where_and = ' WHERE '
   if len(where_clause):
      where_and = '   AND '

   # Percent chance to insert additional filters
   for s in tables:
      if random.choice(range(1, 100)) < 80:

         # Randomly pick a style of filter
         rnd = random.choice(range(1, 100))

         # Type is a single value
         if rnd < 33:
            c = random.choice(s.hypernym.hyponyms())

            where_clause = where_clause + where_and + \
               format(s.hypernym[0]) + '_type = \'' + \
               c[0] + '\'\n'

         # Type is an in list
         elif rnd < 66 and len(s.hypernym.hyponyms()) > 1:
            where_clause = where_clause + where_and + format(s.hypernym[0]) + '_type IN'

            max = random.randrange(len(s.hypernym.hyponyms()))
            if max > 5:
               max = 5

            in_list = ''
            for c in random.sample(s.hypernym.hyponyms(), max):
               if not in_list:
                  in_list = in_list + ' ('
               else:
                  in_list = in_list + ', '

               in_list = in_list + '\'' + c[0] + '\''

            in_list = in_list + ')\n'

            where_clause = where_clause + in_list

         # Type is an OR
         elif rnd < 100 and len(s.hypernym.hyponyms()) > 1:
            c = random.sample(s.hypernym.hyponyms(), 2)
            where_clause = where_clause + where_and + '(' + format(s.hypernym[0]) + '_type = \''
            where_clause = where_clause + c[0][0] + '\'\n'
            where_clause = where_clause + '    OR  ' + format(s.hypernym[0]) + '_type = \''
            where_clause = where_clause + c[1][0] + '\')\n'

      if len(where_clause):
         where_and = '   AND '

   return where_clause


def format(c):
   """Returns a formatted column or table name: lower case, replace spaces with underscores"""

   return c.split(' ')[-1].lower().replace(' ', '_')

def load_words():
   """Build a list of words to choose randomly from"""

   #fdist = nltk.FreqDist([w for w in brown.tagged_words(categories=['humor', 'fiction', 'adventure', 'hobbies']) if w[1] == 'NN'])
   if os.path.isfile('nouns.fd'):

      f = open('nouns.fd', 'rb')
      fdist = load(f)
      f.close()

   else:

      fdist = nltk.FreqDist([w for w in brown.tagged_words() if w[1] == 'NN' and len(w[0]) < 6])

      f = open('nouns.fd', 'wb')
      dump (fdist, f, -1)
      f.close()

   return fdist.most_common()[100:4000]


def replace_sql(sql, from_clause, where_clause):
   """Perform replacement on skeleton SQL"""

   return sql.substitute(columns='*', tables=from_clause, where=where_clause)


def main():
   """Main Entry Point"""

   sql = Template('SELECT $columns         \n'  + \
                  '  FROM $tables          \n'  + \
                  '$where')

   columns = ['type',
              'length',
             ]

   # http://wordnet.princeton.edu/man/lexnames.5WN.html
   lexnames = ['noun.plant', 
               'noun.animal', 
               'noun.food', 
               'noun.shape'
              ]

   tables = []
   words = load_words()

   for i in range(0, 1):
      lexname = ''

      while lexname not in lexnames:
         ((word, tag), f) = random.choice(words)
         word = word.lower()

         s = wordnet.synsets(word)

         if len(s):
            s = s[0]
            lexname = s.lexname
         else:
            lexname = ''

      tables.append(s)

   sql = replace_sql(sql, build_from_clause(tables), build_where_clause(tables))
   print sql
   print len(sql)


if __name__ == '__main__':
   sys.exit(main())
