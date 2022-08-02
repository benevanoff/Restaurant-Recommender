
## Stage 5 final demo

### 1. Explain your choice for the advanced database program and how it is suitable for your application.

* Combination chosen: trigger + stored procedure
1. Smarter detection of favorites -- TRIGGER (addSmartFav_)  

```sql
    -- trigger
    DELIMITER $$
    CREATE TRIGGER AddSmartFav_bar
        AFTER INSERT ON OrderBar  -- EVENT
        FOR EACH ROW
        BEGIN
            SET @already_fav = (EXISTS(SELECT * FROM Favorites AS f 
                                WHERE f.username = NEW.username AND f.food_id = NEW.food_id));
            
            SET @num_orders = (SELECT COUNT(*) FROM OrderBar AS t 
                               WHERE t.username = NEW.username AND t.food_id = NEW.food_id);
            
            IF (NOT @already_fav) AND @num_orders >= 3 THEN -- CONDITION
                INSERT INTO Favorites(username, food_id)  -- ACTION
                VALUES(new.username, new.food_id);
            END IF;
            
        END$$
    DELIMITER ;
```

Here the purpose of the trigger is to add more favorite food items to a user's profile if more than 
3 entries of ordering the same food were detected, that is, if a user ordered the same food for at least 3
times. We repeat the same trigger for bar, restaurant, and cafe.

2. Easier recommendation -- Stored Procedure (findUserCandidatePlaces)

```sql
-- Stored Procedure
DELIMITER $$

CREATE PROCEDURE userSummary(IN username_in varchar(35))
	BEGIN
		DECLARE fav_food VARCHAR(255);
		DECLARE done int default 0;
        DECLARE fav_cur CURSOR FOR (SELECT food_id FROM Favorites WHERE username=username_in);
        DECLARE CONTINUE HANDLER FOR NOT FOUND SET done=1;
        
        DROP TABLE IF EXISTS userSummaryReport;
        
        CREATE TABLE userSummaryReport (
			fav_food VARCHAR(255),
			res_name VARCHAR(255),
            price_level INT,
			rating double
        );
        
        OPEN fav_cur;
        REPEAT 
			FETCH fav_cur INTO fav_food;
            INSERT INTO userSummaryReport(
            
				WITH places AS(
                (SELECT s.food_id, res_name, price_level, rating
				FROM ServeCafe s NATURAL JOIN Cafe
				WHERE s.food_id=fav_food)
				UNION
				(SELECT s.food_id, res_name, price_level, rating
				FROM ServeBar s NATURAL JOIN Bar
				WHERE s.food_id=fav_food)
                UNION
				(SELECT s.food_id, res_name, price_level, rating
				FROM ServeRestaurant s NATURAL JOIN Restaurant
				WHERE s.food_id=fav_food)
                )
                
                SELECT dish_name, res_name, places.price_level, max_ratings
				FROM Food 
					JOIN places on Food.id = places.food_id
					JOIN 
					(SELECT price_level, MAX(rating) as max_ratings
					FROM places
					GROUP BY price_level) AS temp
					ON places.price_level = temp.price_level
					   AND places.rating = temp.max_ratings
				ORDER BY places.price_level
				
                );
		UNTIL done
        END REPEAT;
        

    END$$
DELIMITER ;
```

We also implemented recommendation algorithm to better help the suggestion provided to our user.
During this process, we may need to repeatedly extract ideal places for a specific user.
This SP, once input a specific user:
1. extract all places, regardless of types, that offers the food items the user likes
2. find for each price_level, the places with max rating scores.  

The output table will be the candidate restaurants that may be recommended to the user.


### 2. How did the creative component add extra value to your application?


### 3. How would you want to further improve your application? In terms of database design and system optimization?
* Database design: re-design our schema: 
  * choose the smallest data type possible (e.g. real_name: varchar(255))
  * normalization to remove redundancy or denormalization to improve efficiency
* System optimization
  * query optimization
* Website functionality
  * add more supported cities
  * link to order take-out website

### 4. What were the challenges you faced when implementing and designing the application? How was it the same/different from the original design?
* Challenges:
  * data collection process: Hard to find actual data that we need
  * implementing database schema: Hard to find a good index for our queries (see our stage 3 report)
* Compared to original design:
  * Most basic functionalities and layouts are the same
  * We changed from tags (e.g. spice lovers) to favorite foods (e.g. tacos) for more specific
recommendations and better connected with the menu from restaurants.

### 5. If you were to include a NoSQL database, how would you incorporate it into your application?
* Given the flexibility, scalability of nosql db, we may add functionalities such as asking users to put their comments for food or recommendations we made
and build the nosql database on these comments, plus their favorites, past orders (wchich kept growing)
for a better recommendation algorithm and possibly displaying these comments for each recommendation
we made.

