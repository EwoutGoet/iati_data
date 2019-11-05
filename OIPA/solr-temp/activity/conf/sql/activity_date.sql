                    SELECT
                        id,
                        type_id,
                        TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS iso_date,
                        CASE WHEN type_id = '1' THEN TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') END AS start_planned,
                        CASE WHEN type_id = '2' THEN TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') END AS start_actual,
                        CASE WHEN type_id = '3' THEN TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') END AS end_planned,
                        CASE WHEN type_id = '4' THEN TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') END AS end_actual,
                        CAST((
                                SELECT
                                       ROW_TO_JSON(activity_date_record) AS activity_date
                                FROM (
                                    SELECT
                                           type_id AS type,
                                           TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS iso_date,
                                           JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                    FROM (
                                        SELECT
                                               language_id AS lang,
                                               content AS text
                                        FROM iati_narrative, django_content_type
                                        WHERE related_object_id = iati_activitydate.id
                                            AND django_content_type.model = 'activitydate'
                                            AND related_content_type_id =
                                                django_content_type.id
                                    ) as narrative_record
                                ) AS activity_date_record
                        ) AS VARCHAR)
                    FROM iati_activitydate
                    /*
                    WHERE activity_id=${activity.id}
                     */