DO $$
BEGIN
    -- 먼저 해당 레코드를 업데이트 시도합니다.
    UPDATE img_lig
    SET 
        kit_name = 'Kit1',
        project_name = 'ProjectA',
        task_num = 1,
        img_path_list = ARRAY['/path/to/img1.jpg', '/path/to/img2.jpg'],
        update_at = to_char(current_timestamp, 'YYYY-MM-DD HH24:MI:SS')
    WHERE model_read_path = '/path/to/model';

    -- 만약 업데이트된 행이 없으면 (즉, 해당 레코드가 존재하지 않으면) INSERT를 수행합니다.
    IF NOT FOUND THEN
        INSERT INTO img_lig (kit_name, project_name, task_num, model_read_path, img_path_list)
        VALUES ('Kit1', 'ProjectA', 1, '/path/to/model', ARRAY['/path/to/img1.jpg', '/path/to/img2.jpg']);
    END IF;
END $$;