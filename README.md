# RandomSQLBot

*Silly twitter bot that tweets random SQL statements*

The original intent was to build a rather complex or robust SQL statement, but adding even two tables to the mix almost 
always puts the resulting SQL statement over 140 characters. So some of this script works fine for multiple tables in the 
FROM, but some of the functions will break or the SQL won't look correct sometimes if there's more than one.

**Dependencies**
 * [NLTK](http://nltk.org)
 * [pattern.en](http://www.clips.ua.ac.be/pages/pattern-en)
 * [python-twitter](https://github.com/bear/python-twitter)
 * [Twitter API](https://dev.twitter.com/)
