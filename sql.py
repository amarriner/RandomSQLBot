#!/usr/bin/env python

"""Script that builds silly SQL statements"""

from cPickle import dump, load
from nltk.corpus import brown
from pattern.en import pluralize, singularize, wordnet
from string import Template

import keys
import nltk
import os
import pattern.en
import random
import sys
import twitter

# Working Directory
PWD = '/home/amarriner/python/sql/'

# Maximum number of tables to generate
MAX_TABLES = 1

# Maximum length of table name
MAX_TABLE_NAME_LENGTH = 7


def build_from_clause(tables):
   """Assembles a FROM clause from a list of tables"""

   from_clause = ''
   for s in tables:
      if from_clause:
         from_clause = from_clause + ', '

      from_clause = from_clause + format(pluralize(s.hypernym[0]))

   return from_clause


def build_select_clause(tables, where_clause):
   """Assemble a SELECT clause from a list of tables"""

   select_clause = ''

   # 25% chance of just SELECT *
   if random.choice(range(1, 100)) < 25:
      select_clause = '*'
   else:
      rnd = random.choice(range(1, 100))

      # 50% chance of a COUNT(*) of types when there is no where clause
      if rnd < 50 and not where_clause:
         select_clause = format(tables[0].hypernym[0]) + '_type, COUNT(*)'
      else:
         select_clause = format(tables[0].hypernym[0]) + '_name'

   return select_clause


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

   # Keeping track of the where clause
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
               format(s.hypernym[0]) + '_type ' + random.choice(['=', '<>']) + ' \'' + c[0] + '\'\n'

         # Type is an in list
         elif rnd < 66 and len(s.hypernym.hyponyms()) > 1:
            where_clause = where_clause + where_and + format(s.hypernym[0]) + '_type IN'

            max = random.randrange(1, len(s.hypernym.hyponyms()))
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

      hypo = random.choice(s.hypernym.hyponyms())
      if len(hypo.hyponyms()):
         sub = random.choice(hypo.hyponyms())[0]
         where_clause = where_clause + where_and + \
            format(s.hypernym[0]) + '_subtype ' +  \
            random.choice(['=', '<>']) + ' \'' + sub + '\'\n'

   return where_clause


def get_tables(words):
   """Build a list of tables for the SQL statement from random words"""

   # http://wordnet.princeton.edu/man/lexnames.5WN.html
   lexnames = ['noun.plant', 
               'noun.animal', 
               'noun.food', 
               'noun.shape',
               'noun.body',
               'noun.artifact',
               'noun.object'
              ]

   # Loop until we find a table name that is less than the MAX_TABLE_NAME_LENGTH and has a
   # noun category that is in the list of lexnames above
   tables = []
   for i in range(0, MAX_TABLES):
      lexname = ''

      while lexname not in lexnames:
         ((word, tag), f) = random.choice(words)
         word = word.lower()

         s = wordnet.synsets(word)

         if len(s):
            s = s[0]
            lexname = s.lexname

            if len(s.hypernym) > MAX_TABLE_NAME_LENGTH:
               lexname = ''
         else:
            lexname = ''

      tables.append(s)

   print '------------------------------------------------------------------------'
   print word
   print tables[0].hyponyms()
   print '------------------------------------------------------------------------'

   return tables


def format(c):
   """Returns a formatted column or table name: lower case, replace spaces with underscores"""

   return c.split(' ')[-1].lower().replace(' ', '_')


def load_words():
   """Build a list of words to choose randomly from"""

   # If there's a cached version of the frequency distribution, load it from disk
   if os.path.isfile(PWD + 'nouns.fd'):

      f = open(PWD + 'nouns.fd', 'rb')
      fdist = load(f)
      f.close()

   # Otherwise generate a new one and cache it 
   else:

      fdist = nltk.FreqDist([w for w in brown.tagged_words() if w[1] == 'NN'])

      f = open(PWD + 'nouns.fd', 'wb')
      dump (fdist, f, -1)
      f.close()

   return fdist.most_common()[100:4000]


def replace_sql(sql, select_clause, from_clause, where_clause):
   """Perform replacement on skeleton SQL"""

   sql = sql.substitute(columns=select_clause, tables=from_clause, where=where_clause)

   # Build a GROUP BY clause if the SELECT has a COUNT 
   group_by = ''
   print str(select_clause.find('COUNT')) + ' :: ' + select_clause
   if select_clause.find('COUNT') >= 0:
      group_by = ' GROUP BY ' + singularize(from_clause.strip().split(' ')[0]) + '_type\n'

   sql = sql + group_by

   # Build an ORDER BY clause 50% of the time
   order_by = ''
   if random.choice(range(1, 100)) < 50:
      if select_clause.split(' ')[0] == '*':
         order_by = ' ORDER BY ' + random.choice(from_clause.strip().split(' ')[0:]) + '_name'
      elif select_clause.split(' ')[0] != 'COUNT(*)':
         order_by = ' ORDER BY ' + select_clause.split(' ')[0].replace(',', '')

      if len(order_by):
         order_by = order_by + random.choice(['', ' ASC', ' DESC'])

   # But only attach the ORDER BY if it keeps us under 140 characters
   if len(sql + order_by) < 140:
      sql = sql + order_by

   return sql.strip() + ';'


def main():
   """Main Entry Point"""

   # Loop until we get an SQL statement that is less than 140 characters
   sql = '' 
   while len(sql) > 140 or not len(sql):
      sql = Template('SELECT $columns         \n'  + \
                     '  FROM $tables          \n'  + \
                     '$where')

      tables = get_tables(load_words())

      from_clause = build_from_clause(tables)
      where_clause = build_where_clause(tables)
      select_clause = build_select_clause(tables, where_clause)

      sql = replace_sql(sql, select_clause, from_clause, where_clause)

   print sql
   print '------------------------------------------------------------------------'

   # Connect to Twitter
   api = twitter.Api(keys.consumer_key, keys.consumer_secret, keys.access_token, keys.access_token_secret)

   # Post tweet text and image
   status = api.PostUpdate(sql)


if __name__ == '__main__':
   sys.exit(main())
