### Diagram and Schema

![UML](doc/diagram.png)

### Constraints
* There should only be one set of credentials per customer (one to one)
* Many customers may make many orders for many foods at many venues
* Many customers may have many favorites, these preferences will help us give suggestions
* Restaurants, Cafes, and Bars can all serve any kind of food and should serve more than one food (many to many)
