import sqlite3
import pandas as pd
from sqlite3 import Error

 
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn

 
def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    
    query1 = """
        SELECT *
        FROM FACILITIES
        """
    cur.execute(query1)
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)


def total_revenue_less_than_1000(conn):
    # Q10: Produce a list of facilities with a total revenue less than 1000. The output of facility name and total revenue, sorted by revenue. Remember that there's a different cost for guests and members!
    cur = conn.cursor()
    query_rev = """
            WITH revenue AS (
                SELECT
                    f.facid,
                    f.name,
                    CASE WHEN m.memid = 0 THEN 	(f.guestcost*b.slots) 
                        ELSE (f.membercost*b.slots) END AS cost 
            FROM Facilities AS f
            LEFT JOIN Bookings AS b 
            ON b.facid = f.facid
            LEFT JOIN Members AS m
            ON b.memid = m.memid)

            SELECT
                f.facid, 
                f.name, 
                round(SUM(r.cost),1) AS total_revenue
            FROM Facilities AS f
            LEFT JOIN revenue AS r
            ON r.facid = f.facid
            GROUP BY f.name
            HAVING total_revenue < 1000
            ORDER BY total_revenue DESC
            """
    rz = cur.execute(query_rev)
    rows = cur.fetchall()
    df_rev = pd.DataFrame(rows)
    df_rev.columns = [col[0] for col in cur.description]  # #col_names = list(map(lambda x: x[0], cur.description))
    df_rev.head(10)

def members_recommended(conn):
    # Q11: Produce a report of members and who recommended them in alphabetic surname,firstname order
    cur = conn.cursor()
    query_mem = """
        SELECT 
            m1.firstname || ' ' || m1.surname AS referral,
            m2.firstname || ' ' || m2.surname AS recommender
        FROM Members AS m1
            LEFT JOIN Members AS m2
                ON m1.recommendedby = m2.memid
                     WHERE recommender <> 'None'
    """
    rz = cur.execute(query_mem)
    rows = cur.fetchall()
    df_mem = pd.DataFrame(rows)
    df_mem.columns = [col[0] for col in cur.description] # #col_names = list(map(lambda x: x[0], cur.description))
    df_mem.head(10)

def facility_used_by_membership(conn):
    # Q12: Find the facilities with their usage by member, but not guests
    cur = conn.cursor()
    query_fac = """
        WITH guestuse AS (
            SELECT 
                b.bookid,
                CASE WHEN b.memid=0 THEN 1
                ELSE 0 END AS guestusage
            FROM Bookings AS b),
        memberuse AS (
            SELECT 
                b.bookid,
                CASE WHEN b.memid=0 THEN 0
                ELSE 1 END AS memberusage
            FROM Bookings AS b)
        SELECT 
            DISTINCT f.name,
            b.starttime,
            SUM(guestusage) OVER(PARTITION BY name) AS guest_usage, 
            SUM(memberusage) OVER(PARTITION BY name) AS member_usage, 
            SUM(guestusage+memberusage) OVER(PARTITION BY name) AS total_usage
            --(g.guestusage+m.memberusage) OVER() AS total_usage  -- NOTE THAT THIS DOES NOT WORK!
        FROM Bookings AS b
            LEFT JOIN Facilities AS f
                ON b.facid = f.facid
            LEFT JOIN guestuse AS g 
                ON b.bookid = g.bookid
            LEFT JOIN memberuse AS m 
                ON b.bookid = m.bookid
    """
    rz = cur.execute(query_fac)
    rows = cur.fetchall()
    df_fac = pd.DataFrame(rows)
    df_fac.columns = [col[0] for col in cur.description] # #col_names = list(map(lambda x: x[0], cur.description))
    df_fac

def individual_booking_CTE(conn):
    """ Q8: Produce a list of bookings on the day of 2012-09-14 which
    will cost the member (or guest) more than $30. Remember that guests have
    different costs to members (the listed costs are per half-hour 'slot'), and
    the guest user's ID is always 0. Include in your output the name of the
    facility, the name of the member formatted as a single column, and the cost.
    Order by descending cost, and do not use any subqueries."""
    cur = conn.cursor()
    query_book = """
    WITH costtable AS (
	        SELECT
                b.bookid,
                CASE WHEN m.memid = 0 THEN (f.guestcost*b.slots) 
                    ELSE (f.membercost*b.slots) END AS cost 
      		FROM Bookings AS b
    		LEFT JOIN Facilities AS f 
    		ON b.facid = f.facid
    		LEFT JOIN Members AS m
    		USING (memid)
    )
	SELECT 
        f.name, m.memid, b.starttime, m.firstname, m.surname, b.slots, c.cost
    FROM Bookings AS b
    LEFT JOIN Facilities AS f 
    ON b.facid = f.facid
    LEFT JOIN Members AS m
    ON b.memid = m.memid
	LEFT JOIN costtable AS c
	USING (bookid)
    WHERE b.starttime LIKE '2012-09-14%' AND c.cost > 30
    ORDER BY cost DESC
    """
    rz = cur.execute(query_book)
    rows = cur.fetchall()
    df_book = pd.DataFrame(rows)
    df_book.columns = [col[0] for col in cur.description] # #col_names = list(map(lambda x: x[0], cur.description))
    df_book

def individual_booking_subquery(conn):
    """ Q8: Produce a list of bookings on the day of 2012-09-14 which
    will cost the member (or guest) more than $30. Remember that guests have
    different costs to members (the listed costs are per half-hour 'slot'), and
    the guest user's ID is always 0. Include in your output the name of the
    facility, the name of the member formatted as a single column, and the cost.
    Order by descending cost, and do not use any subqueries."""
    cur = conn.cursor()
    query_book = """
	SELECT 
        f.name, m.memid, b.starttime, m.firstname, m.surname, b.slots, c.cost
    FROM Bookings AS b
    LEFT JOIN Facilities AS f 
    ON b.facid = f.facid
    LEFT JOIN Members AS m
    ON b.memid = m.memid
	LEFT JOIN (
        	SELECT
                b.bookid,
                CASE WHEN m.memid = 0 THEN (f.guestcost*b.slots) 
                    ELSE (f.membercost*b.slots) END AS cost 
      		FROM Bookings AS b
    		LEFT JOIN Facilities AS f 
    		ON b.facid = f.facid
    		LEFT JOIN Members AS m
    		USING (memid)) AS c
	USING (bookid)
    WHERE b.starttime LIKE '2012-09-14%' AND c.cost > 30
    ORDER BY cost DESC
    """
    rz = cur.execute(query_book)
    rows = cur.fetchall()
    df_book = pd.DataFrame(rows)
    df_book.columns = [col[0] for col in cur.description] # #col_names = list(map(lambda x: x[0], cur.description))
    df_book

def facility_used_by_membership_month(conn):
    # Q13: Find the facilities usage by month, but not guests
    cur = conn.cursor()
    query_fac_member_month = """
        WITH guestuse AS (
            SELECT 
                b.bookid,
                CASE WHEN b.memid=0 THEN 1
                ELSE 0 END AS guestusage
            FROM Bookings AS b),
        memberuse AS (
            SELECT 
                b.bookid,
                CASE WHEN b.memid=0 THEN 0
                ELSE 1 END AS memberusage
            FROM Bookings AS b)
        SELECT 
            DISTINCT f.name,
            strftime('%m', b.starttime) AS month,
            SUM(guestusage) OVER(PARTITION BY name, strftime('%m', b.starttime)) AS guest_usage, 
            SUM(memberusage) OVER(PARTITION BY name, strftime('%m', b.starttime)) AS member_usage, 
            SUM(guestusage+memberusage) OVER(PARTITION BY name, strftime('%m', b.starttime)) AS total_usage
        FROM Bookings AS b
            LEFT JOIN Facilities AS f
                ON b.facid = f.facid
            LEFT JOIN guestuse AS g 
                ON b.bookid = g.bookid
            LEFT JOIN memberuse AS m 
                ON b.bookid = m.bookid
    """
    rz = cur.execute(query_fac_member_month)
    rows = cur.fetchall()
    df_fac_member_month = pd.DataFrame(rows)
    df_fac_member_month.columns = [col[0] for col in cur.description] # #col_names = list(map(lambda x: x[0], cur.description))
    df_fac_member_month

def main():
    database = "sqlite_db_pythonsqlite.db"
 
    # create a database connection
    conn = create_connection(database)
    with conn: 
        print("2. Query all tasks")
        select_all_tasks(conn)
        total_revenue_less_than_1000(conn)
        members_recommended(conn)
        facility_used_by_membership(conn)
        individual_booking_CTE(conn)
        individual_booking_subquery(conn)
        facility_used_by_membership_month(conn)

if __name__ == '__main__':
    main()