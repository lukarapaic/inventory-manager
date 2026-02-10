import inventoryDB as iDB

def populate():
    conn = iDB.initDatabase()
    product1 = iDB.addProduct(conn, "Nike Air Max", "Footwear")
    product2 = iDB.addProduct(conn, "Adidas Rainproof Jacket", "Jackets")
    product3 = iDB.addProduct(conn, "Ippon Karate Gloves", "Sports accessories")

    variant1_1 = iDB.addVariant(conn, product1, "38, Purple", 99)
    variant1_2 = iDB.addVariant(conn, product1, "38, White", 99)
    variant1_3 = iDB.addVariant(conn, product1, "42, Purple", 99)

    variant2_1 = iDB.addVariant(conn, product2, "M", 42)
    variant2_2 = iDB.addVariant(conn, product2, "L", 45)
    variant2_3 = iDB.addVariant(conn, product2, "XL", 47)

    variant3_1 = iDB.addVariant(conn, product3, "M", 67)
    variant3_2 = iDB.addVariant(conn, product3, "L", 69)

    location1 = iDB.addLocation(conn, "Greenwich Warehouse", True, "SE12 XXZ, Greenwich Road 20, London, UK")
    location2 = iDB.addLocation(conn, "Sporty Sports Greenwich", False, "SE11 ZZY, Greenwich Path 99, London, UK")
    location3 = iDB.addLocation(conn, "Central Dojo", False, "Buckingham Palace, London, UK")

    iDB.addReview(conn, variant1_1, "Slightly larger than the usual size 38, my favourite colour!", "i_luv_purple",4)
    iDB.addReview(conn, variant1_1, "Perfect", "eternal_optimist", 5)
    iDB.addReview(conn, variant1_1, "Horrible colour, the shoe itself is ok but not worth the price", "meh", 2)

    iDB.addReview(conn, variant3_2, "Marvellous!", "Charlie", 5)

    


