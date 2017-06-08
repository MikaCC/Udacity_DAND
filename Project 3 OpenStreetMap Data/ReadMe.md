# Project 3: OpenStreetMap Data Wrangling with SQL

**Name:** Sicong Chen

**Map Area**: 

* Location: San Francisco, California
* [OpenStreetMap URL](https://www.openstreetmap.org/relation/111968)
* [MapZen URL](https://mapzen.com/data/metro-extracts/metro/san-francisco_california/)

I went to college at Berkeley and stayed aroud the bay area for a couple of years. San Francisco is the city I was familiar with and I miss it a lot. I am very interested in lookin at the data of this city and hopefully contribute to it myself.

# 1. Tag Overview

### Tags in the Data
First of all I want to know what tags are used in the dataset.
`mapparser.py` is used to count the numbers of each unique tags.

 * 'bounds': 1,
 * 'member': 54957,
 * 'nd': 7774168,
 * 'node': 6559150,
 * 'osm': 1,
 * 'relation': 6227,
 * 'tag': 2124121,
 * 'way': 807513}`
 
 The OSM file is about 1.4G and has more than 19 million top level tags.

### Patterns in the Tags
Using `tags.py`, I created  3 regular expressions for certain tags, and returns the number of each type.

The following reveals count of each tag categories.

*  `"lower" : 1409185`, for tags that contain only lowercase letters and are valid,
*  `"lower_colon" : 689009`, for otherwise valid tags with a colon in their names,
*  `"problemchars" : 130`, for tags that contain problematic charactoers,
*  `"other" : 25797`, for other tags that do not fall into the other three categories.




# 2. Problems Encountered in the Map

### Abbreviated Street Names
One of the problems we encountered in the dataset is the street name inconsistencies. Here are some examples that we want to fix:
 
* **Abbreviations -> Corrected Names** 
    
    *  Woodside Plz -> Woodside Plaza
    *  Tehama Ave -> Tehama Avenue
    *  Peralta St-> Peralta Street
    *  Redwood Hwy -> Redwood Hwy
    *  California Dr -> California Drive
    *  Newark Blvd -> Newark Boulevard
    *  etc.

We create a mapping dictionary that includes all these abbreviations (i.e. 'Rd':'Road') and use 'audit.fix_street' to map abbreviated street names to full street names.


### Long Post Code
Post code should be 5-digit long. We run the audit.audit_postcode to return a list of long post code and observe the following different formats of long post code:

* **Long Post Code** 

    * 'CA 94544' - Include State
    * '941234' - Incorrect 6 digit zipcode
    * '94402-3025' - Zipcode with 4 digit area code
    
### Phone Number Format Inconsistent
We also observed that there are several different formats for phone numbers recorded in the dataset. Here's some example by running audit.audit_phone:

* **Sample Phone Numbers** 

    * +1 510 528 8888
    * (415) 550-5534
    * +1-510-524-7031
    * +1 4152529888
    * etc

To standardize the format, we want it all to be in XXX-XXX-XXXX or 1-XXX-XXX-XXXX. We run the audit.fix_phonenumber to fix to standardize the phone number formatting.



#3. Data Overview

This part we first use the 'data.py' to create csv files that preparing for the dagabase. Then create the database and explore it with SQL queries.

### File sizes:

* `ahmedabad_india.osm: 109.2 MB`
* `nodes_csv: 43.4 MB`
* `nodes_tags.csv: 163.4 KB`
* `ways_csv: 4.6 MB`
* `ways_nodes.csv: 14.7 MB`
* `ways_tags.csv: 2.8 MB`
* `ahmedabad.db: 78.5 MB`

###Number of nodes:
``` python
sqlite> SELECT COUNT(*) FROM nodes
```
**Output:**
```
525565
```

### Number of ways:
```python
sqlite> SELECT COUNT(*) FROM ways
```
**Output:**
```
77866
```

###Number of unique users:
```python
sqlite> SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
```
**Output:**
```
226
```

###Top contributing users:
```python
sqlite> SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;
```
**Output:**

```
uday01			177686
sramesh			136887
chaitanya110	123328
shashi2			49514
vkvora			22216
shravan91		21508
shiva05			19671
bhanu3			12645
Oberaffe		7042
PlaneMad		4969
```

###Number of users contributing only once:
```python
sqlite> SELECT COUNT(*) 
FROM
    (SELECT e.user, COUNT(*) as num
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
     GROUP BY e.user
     HAVING num=1) u;
```
**Output:**
```
44
```

# 4. Additional Data Exploration

###Common ammenities:
```python
sqlite> SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;

```
**Output:**
```
place_of_worship	47
restaurant			31
bank				21
school				18
fuel				14
library				14
hospital			13
cafe				12
fast_food			11
cinema				10
```

###Biggest religion:
```python
sqlite> SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='place_of_worship') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='religion'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 1;
```
**Output:**
```
Hindu :	31
```
###Popular cuisines
```python
sqlite> SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY num DESC;
```
**Output:**
```
regional								4
vegetarian								3
pizza									2
Punjabi,_SouthIndia,_Gujarati Thali		1
burger									1
indian									1
international							1
italian									1
sandwich								1
```

# 5. Conclusion


### Additional Suggestion and Ideas



# Files
* `README.md` : this file
* `sample.osm`: sample data of the OSM file
* `audit.py` : audit street, city and update their names
* `data.py` : parse the data and build 5 seperate CSV files from OSM 
* `database.py` : create database from the CSV files
* `mapparser.py` : find unique tags in the data
* `query.py` : different queries about the database using SQL
* `report.pdf` : pdf of this document
* `sample.py` : extract sample data from the OSM file
* `tags.py` : count number of top level tags
