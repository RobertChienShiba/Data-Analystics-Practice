/* 建立資料表 */
CREATE TABLE sailors (
    sname VARCHAR(15) PRIMARY KEY,
    rating INT
);


CREATE TABLE boats (
    bname VARCHAR(15),
    color VARCHAR(10), 
    rating INT,
    PRIMARY KEY(bname)
);


CREATE TABLE days (
    day VARCHAR(15) PRIMARY KEY
);


CREATE TABLE reservations (
    sname VARCHAR(15),
    bname VARCHAR(15),
    day VARCHAR(15),
    PRIMARY KEY(sname, bname, day),
    FOREIGN KEY(sname) REFERENCES sailors(sname),
    FOREIGN KEY(bname) REFERENCES boats(bname),
    FOREIGN KEY(day) REFERENCES days(day)
);


/* 刪除資料表 */
DROP TABLE reservations;
DROP TABLE sailors, boats, days;


/* 新增資料 */
INSERT INTO sailors VALUES ('Brutus', 1);
INSERT INTO sailors VALUES ('Andy', 8);
INSERT INTO sailors VALUES ('Horatio', 7);
INSERT INTO sailors VALUES ('Rusty', 8);
INSERT INTO sailors VALUES ('Bob', 1);

INSERT INTO boats VALUES ('SpeedQueen', 'white', 9);
INSERT INTO boats VALUES ('Interlake', 'red', 8);
INSERT INTO boats VALUES ('Marine', 'blue', 7);
INSERT INTO boats VALUES ('Bay', 'red', 3);

INSERT INTO days VALUES ('Monday');  
INSERT INTO days VALUES ('Tuesday');
INSERT INTO days VALUES ('Wednesday');
INSERT INTO days VALUES ('Thursday');
INSERT INTO days VALUES ('Friday');
INSERT INTO days VALUES ('Saturday');
INSERT INTO days VALUES ('Sunday');

INSERT INTO reservations VALUES ('Andy', 'Interlake', 'Monday');
INSERT INTO reservations VALUES ('Andy', 'Bay', 'Wednesday');
INSERT INTO reservations VALUES ('Andy', 'Marine', 'Saturday');
INSERT INTO reservations VALUES ('Rusty', 'Bay', 'Sunday');
INSERT INTO reservations VALUES ('Rusty', 'Interlake', 'Wednesday');
INSERT INTO reservations VALUES ('Rusty', 'Marine', 'Wednesday');
INSERT INTO reservations VALUES ('Bob', 'Bay', 'Monday');




/* 查詢資料 */

-- SELECT [DISTINCT] select-list
-- FROM from-list
-- WHERE qualification


SELECT * FROM sailors;
SELECT * FROM boats;
SELECT * FROM days;
SELECT * FROM reservations;

SELECT * 
FROM sailors
WHERE rating > 5;

SELECT COUNT(*)
FROM sailors;

SELECT COUNT(rating)
FROM sailors;

SELECT SUM(rating)
FROM sailors;

SELECT AVG(rating)
FROM sailors;

SELECT MAX(rating)
FROM sailors;

SELECT MIN(rating)
FROM sailors;

SELECT *
FROM boats
GROUP BY color;

SELECT color, COUNT(*)
FROM boats
GROUP BY color;

SELECT *
FROM sailors
ORDER BY rating;

SELECT *
FROM sailors
ORDER BY rating DESC;



/* 1. 列出所有在星期三預約的船名 跟它們的顏色 */

SELECT b.bname, b.color 
FROM boats b, reservations r 
WHERE b.bname = r.bname AND r.day = 'Wednesday';


/* 2. 列出最高評分的水手 */

/* (i) 用 MAX */
SELECT s.sname
FROM sailors s 
WHERE s.rating >= (
    SELECT max(rating) 
    FROM sailors);


/* 不用 MAX. */
SELECT s.sname
FROM sailors s 
WHERE NOT EXISTS 
    (SELECT s2.sname
    FROM sailors s2 
    WHERE s2.rating > s.rating);


/* 3. 列出所有有在同一天預約船的水手名字，避免重複 */

SELECT DISTINCT r1.sname, r2.sname
FROM reservations r1, reservations r2
WHERE r1.day = r2.day AND r1.sname <> r2.sname;


/* 4. 每一天，列出那天預約紅色船的數量。
如果那天沒紅色船被預約，數字應該是0，如果那一天完全沒有出現在預約表格裡，
那天數字也應該要是0。 */

SELECT d.day, ifnull(sub.num,0) AS number 
FROM days d LEFT OUTER JOIN (
    SELECT r.day,COUNT(*) AS num 
    FROM boats b, reservations r 
    WHERE b.bname=r.bname AND b.color='red' GROUP BY r.day)AS sub
ON d.day = sub.day; 


/* 5. 列出只有紅船被預約的那些天 */

SELECT distinct r.day 
FROM boats b, reservations r 
WHERE b.bname=r.bname AND b.color = 'red' AND NOT EXISTS (
    SELECT s.day 
    FROM reservations s,boats c 
    WHERE c.bname = s.bname AND s.day = r.day AND c.color <> 'red');


/* 6. 列出沒有紅船預約的天。如果那天沒出現在預約表格裡，也應該是0。 */

SELECT d.day 
FROM days d 
WHERE NOT EXISTS (
    SELECT r.day 
    FROM boats b,reservations r 
    WHERE b.bname = r.bname AND b.color = 'red' and r.day = d.day );


/* 7. 列出全部紅船都被預約的天，如果不存在紅船，那每天都該吻合。 

/* – 使用 NOT IN */
SELECT d1.day 
FROM days d1
WHERE day NOT IN ( 
    SELECT d2.day
    FROM  days d2, boats b
    WHERE b.color = 'red' AND b.bname NOT IN (
            SELECT c.bname
            FROM boats c, reservations r
            WHERE r.day = d2.day AND c.bname = r.bname
        ) 
);

/* 使用 NOT EXISTS */
SELECT d.day
FROM days d
WHERE NOT EXISTS ( 
    SELECT b.bname
    FROM  boats b
    WHERE b.color = 'red' AND NOT EXISTS (
            SELECT r.day
            FROM reservations r
            WHERE r.day = d.day AND b.bname = r.bname
        ) 
);

/* 使用 COUNT */
SELECT d.day
FROM days d
WHERE (
    SELECT count(*)       
    FROM  boats b
    WHERE b.color = 'red' AND (
            SELECT count(*)
            FROM reservations r
            WHERE r.day=d.day AND b.bname =r.bname
        ) = 0
)=0;


/* 8. 針對出現在預約表裡的天，列出那天所有水手的平均分數。
(小心重複的項目) */

SELECT sub.DAY, AVG(sub.rat) AS "ave-rating"
FROM (
    SELECT DISTINCT d.day AS DAY, s.sname, s.rating AS rat
    FROM sailors s, reservations r, days d
    WHERE r.sname = s.sname AND d.day = r.day) sub
GROUP BY sub.DAY; 


/* 9. 列出最忙的一天，也就是最多預約的一天 */
SELECT sub1.day
FROM(  
  SELECT day, COUNT(*) AS rcount
  FROM reservations
  GROUP BY day
  ) sub1
WHERE sub1.rcount >= (
  SELECT MAX(rcount)
  FROM
     ( SELECT COUNT(*) AS rcount
     FROM reservations
     GROUP BY day
     ) sub2
);