#!/usr/bin/env python3

import psycopg2


def connect(dbname="news"):
    """ this function connects to the PostgreSQL database news.
        Args:
            it will take database name as an argument.
        Retuns:
            it will return database connection.
    """
    db = psycopg2.connect("dbname = {}".format(dbname))
    c = db.cursor()
    return db, c


def articles_view():

    """ this function creates a view for the most popular
        articles of all time.
    """

    db, c = connect()
    query = "create or replace view articles_view as \
            (select title, count(*) as num from articles, log \
            where log.path like concat('%', articles.slug, '%') \
            and log.status like '%200%' \
            group by articles.title \
            order by num desc \
            limit 3);"
    c.execute(query)
    db.commit()
    db.close()


def authors_view():

    """ this function creates a view for the most popular
        article authors of all time.
    """

    db, c = connect()
    query = "create or replace view authors_view as \
            (select authors.name, count(*) as num \
            from articles, authors, log \
            where articles.author = authors.id \
            and log.path like concat('%', articles.slug, '%') \
            and log.status like '%200%' \
            group by authors.name \
            order by num desc);"
    c.execute(query)
    db.commit()
    db.close()


def log_view():

    """ this function creates a view for the error log.
    """

    db, c = connect()
    query = "create or replace view log_view as \
            (select * from \
            (select to_char(time, 'Mon DD, YYYY') as day, \
            round((sum(case log.status when '200 OK' then 0 else 1 end) \
            * 100.0) / count(log.status), 2) as error_per \
            from log \
            group by day \
            order by error_per desc) as result \
            where error_per > 1);"
    c.execute(query)
    db.commit()
    db.close()


def print_articles():
    """ this function prints the data for the most popular
        articles using the articles_view.
    """

    db, c = connect()
    query = "select * from articles_view;"
    c.execute(query)
    result = c.fetchall()
    db.close()

    print "\n>> The most popular three articles of all time...\n"
    for data in result:
        print "\"" + data[0] + "\" -- " + str(data[1]) + " views"

    print "-----------------------------------------------------------"


def print_authors():
    """ this function prints the data for the most popular
        article authors using the authors_view.
    """

    db, c = connect()
    query = "select * from authors_view;"
    c.execute(query)
    result = c.fetchall()
    db.close()

    print "\n>> The most popular article authors of all time...\n"
    for data in result:
        print data[0] + " -- " + str(data[1]) + " views"

    print "-----------------------------------------------------------"


def print_log():
    """ this function prints the data for the error log
        using the error_log_view.
    """

    db, c = connect()
    query = "select * from log_view;"
    c.execute(query)
    result = c.fetchall()
    db.close()

    print "\n>> The days when more than 1% of requests lead to errors...\n"
    for data in result:
        print str(data[0]) + " -- " + str(data[1]) + "% errors"

    print "-----------------------------------------------------------\n\n"


if __name__ == '__main__':

    articles_view()  # creates view for most popular articles
    authors_view()  # creates view for most popular authors
    log_view()  # creates view for error log

    print "\n\nReport Analysis of news Database"
    print "-----------------------------------------------------------"
    print_articles()  # prints result of article view
    print_authors()  # prints view of authors view
    print_log()  # prints view of error log
