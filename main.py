import inventoryDB as iDB

def main():
    #TEMP TESTING
    try:
        conn = iDB.initDatabase()
    except Exception as e:
        print(f"An error occurred during database initialisation: {e}")
        if conn:
            conn.close()
    #TESTING ADDING LOCATIONS
    product_name = input("Enter product name: ")
    description = input("Input the product variant description: ")
    price = int(input("Input the Starting price: "))
    try:
        pass
        iDB.addVariant(conn, product_name, description, price)
    except Exception as e:
        print(e)
    



if __name__ == "__main__":
    main()