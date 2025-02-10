WITH upsert AS (
    UPDATE img_lig
    SET 
        kit_name = 'Kit1',
        project_name = 'ProjectA',
        task_num = 1,
        img_path_list = ARRAY['/path/to/img1.jpg', '/path/to/img2.jpg'],
        update_at = to_char(current_timestamp, 'YYYY-MM-DD HH24:MI:SS')
    WHERE model_read_path = '/path/to/model'
    RETURNING *
)
INSERT INTO img_lig (kit_name, project_name, task_num, model_read_path, img_path_list)
SELECT 'Kit1', 'ProjectA', 1, '/path/to/model', ARRAY['/path/to/img1.jpg', '/path/to/img2.jpg']
WHERE NOT EXISTS (SELECT 1 FROM upsert);