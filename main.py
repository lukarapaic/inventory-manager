import inventoryDB as iDB

def main():
    #TEMP TESTING
    try:
        conn = iDB.init_database()
    except Exception as e:
        print(f"An error occurred during database initialisation: {e}")
        if conn:
            conn.close()
    
    



if __name__ == "__main__":
    main()