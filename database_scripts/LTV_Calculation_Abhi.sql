--- CTE calculates the first occurrence of customer and latest order made to calculate the week range
WITH get_date AS
    (
    SELECT
        c.customer_id
        ,min(c.created_at) AS first_enrollment
        ,max(o.event_time) AS latest_order
    FROM customer c
    JOIN "order" o
        ON c.customer_id =o.customer_id
    GROUP BY 1
    )

---CTE calculates total visits made by a customer
,get_customer_total_visit AS
    (
    SELECT
        s.customer_id
        ,COUNT(s.customer_id) AS total_visits
    FROM site_visit s
    GROUP BY 1
    )

--- CTE calculate total expenditure of a customer
,get_customer_total_expenditure AS
    (
    SELECT
        customer_id
        ,SUM(TRIM(' USD' FROM total_amount)::FLOAT) AS total_expenditure
    FROM "order" o
    GROUP BY 1
    )

--- CTE calculates customer value, i.e: expenditure per visit and total visits per week.
-- CASE statement in the denominator checks the week difference, if it is greater than 52 then will take that number else will consider 52 since there are at least 52 weeks in an year
,get_customer_value AS
    (
    SELECT
        te.customer_id
        ,total_expenditure*1.0/total_visits AS expenditure_per_visit
        ,total_visits*1.0 / ( CASE WHEN TRUNC(DATE_PART('Day', latest_order - first_enrollment)/7)+1 <52 THEN 52
                             ELSE TRUNC(DATE_PART('Day', latest_order - first_enrollment)/7)+1 END) AS visits_per_week
    FROM get_customer_total_expenditure te
    JOIN get_customer_total_visit tv
        ON te.customer_id = tv.customer_id
    JOIN get_date tw
        ON te.customer_id = tw.customer_id
    )

--- In this CTE the data set is joined back with all customers. This is because I am assuming that every customer will have to ranked LTV.
-- If there are 8 customers and only 5 have ordered then the rest 3 will have ltv as 0.0
,calculate_ltv AS
    (
    SELECT
        c.customer_id
        ,CAST(COALESCE(52*expenditure_per_visit*visits_per_week*10,0) AS FLOAT) AS ltv
    FROM get_customer_value cv
    RIGHT JOIN customer c
        ON cv.customer_id = c.customer_id
    )

-- THIS CTE ranks customers on LTV. Based on the requirements we can select only topX customers by providing that value to drnk in next SELECT clause
SELECT
    customer_id
    ,DENSE_RANK() OVER (ORDER BY ltv DESC) AS drnk
FROM calculate_ltv;



