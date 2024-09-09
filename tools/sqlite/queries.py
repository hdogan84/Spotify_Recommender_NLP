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

        # 3. Id of a specific artist 
        query = "SELECT * FROM Artists WHERE artist_name='adele';"    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)

        # 4. Select some songs a Singer, with artist_id known 
        query = """SELECT  T.track_id
        FROM Transactions AS T
        JOIN Artists AS A on A.artist_id=T.artist_id
        WHERE A.artist_id=1292 LIMIT 10;"""    
        rows = execute_select_query(conn, query)
        print_query_results(query, rows)


        # Close the connection
        conn.close()
        print("\nConnection closed.")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
