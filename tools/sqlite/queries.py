import sqlite3

# Function to create a connection to the SQLite database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database: {db_file}")
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite database: {e}")
    return conn

# Function to execute a SELECT query
def execute_select_query(conn, query):
    try:
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None

# Function to print query results
def print_query_results(query, rows):
    print(f"\nQuery: {query}")
    print("Results:")
    if rows:
        for row in rows:
            print(row)
    else:
        print("No results found.")

# Main function
def main():
    database = "songs.db"  # Replace with your .db file

    # Create a database connection
    conn = create_connection(database)

    if conn is not None:
        # Example SELECT queries

        # 1. Select artists names from Artists table
        query = "SELECT DISTINCT artist_name FROM Artists LIMIT 10;"    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

        # 2. Select Genre descriptions
        query = "SELECT DISTINCT genre_desc FROM Genres;"    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

        # 3. Select number of distinct song names 
        query = "SELECT COUNT(DISTINCT track_id) FROM Tracks;"    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

        # 4. Id of a specific artist 
        query = "SELECT COUNT(DISTINCT artist_id) FROM Artists;"    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

        # 5. Id of a specific artist 
        query = "SELECT * FROM Artists WHERE artist_name='adele';"    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

        # 6. Select some songs a Singer, with artist_id known 
        query = """SELECT  T.track_id
        FROM Transactions AS T
        JOIN Artists AS A on A.artist_id=T.artist_id
        WHERE A.artist_id=1292 LIMIT 10;"""    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)
        
        #select most popular 10 song
        query = """SELECT T.track_id, COUNT(*) as play_count
                     FROM Transactions AS T
                     GROUP BY T.track_id
                     ORDER BY play_count DESC
                     LIMIT 10;"""    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

        #select most popular 10 artist
        query = """SELECT A.artist_name, COUNT(*) as track_count
                    FROM Transactions AS T
                    JOIN Artists AS A ON T.artist_id = A.artist_id
                    GROUP BY A.artist_name
                    ORDER BY track_count DESC
                    LIMIT 10;"""    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

       #select most popular 10 genre
       query = """SELECT G.genre_desc, COUNT(*) as track_count
                    FROM Transactions AS T
                    JOIN Genres AS G ON T.genre_id = G.genre_id
                    GROUP BY G.genre_desc
                    ORDER BY track_count DESC
                    LIMIT 10;"""    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

        #select artists and their tracks
       query = """SELECT A.artist_name, T.track_name
                    FROM Transactions AS Tr
                    JOIN Artists AS A ON Tr.artist_id = A.artist_id
                    JOIN Tracks AS T ON Tr.track_id = T.track_id
                    ORDER BY A.artist_name, T.track_name;"""    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)





        # Close the connection
        conn.close()
        print("\nConnection closed.")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
