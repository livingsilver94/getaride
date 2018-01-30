SELECT planner_step.*
FROM
  planner_step
  JOIN (
         SELECT
           trip_id,
           MIN("order") AS 'min',
           MAX("order") AS 'max'
         FROM
           planner_step
           JOIN planner_trip ON
                               planner_trip.id = planner_step.trip_id
         WHERE
           (
             destination_id = %s
             OR (
               origin_id = %s
               AND hour_origin BETWEEN %s AND %s
             )
           )
           AND planner_trip.date_origin = %s
         GROUP BY
           trip_id
         ORDER BY
           planner_step."order"
       ) AS 'filter_table' ON
                             planner_step.trip_id = filter_table.trip_id
WHERE
  planner_step."order" BETWEEN filter_table."min" AND filter_table."max"