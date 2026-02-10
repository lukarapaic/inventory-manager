import inventoryDB as iDB
import argparse
import inventoryTest as test

def main():
    #TEMP TESTING
    try:
        conn = iDB.initDatabase()
    except Exception as e:
        print(f"An error occurred during database initialisation: {e}")
        if conn:
            conn.close()
    #TESTING ADDING LOCATIONS
    #variant = int(input("Enter variant id: "))
    #text_body = input("Input the product variant review: ")
    #user_name = input("Input the user name: ")
    #rating = int(input("Enter your rating for the variant: "))
    try:
        pass
        #iDB.addReview(conn, variant, text_body, user_name, rating)
        print(iDB.fetchReviews(conn, 1))
        rating = iDB.getVariantRating(conn,1)
        print("Average rating is {}".format(rating))
    except Exception as e:
        print(e)
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inventory Manager")

    parser.add_argument("--test_populate", action = "store_true", help = "Populate the DB with a test example")
    parser.add_argument("--init", action = "store_true", help = "initialises the DB tables")
    args = parser.parse_args()
    
    if args.test_populate:
        #Populate the db
        test.populate()
    elif args.init:
        #Initialise the db
        iDB.initDatabase()
    else:
        main()