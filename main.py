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
    main()