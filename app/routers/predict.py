conn = get_connection()
cursor = conn.cursor()
try:
    # 외래키 제약 임시 비활성화
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    
    cursor.execute(
        """
        INSERT INTO uploaded_images (user_id, original_filename, stored_path, mime_type, file_size, file_hash)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (1, file.filename, stored_path, file.content_type, file_size, file_hash)
    )
    image_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO predictions (image_id, user_id, label, confidence, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (image_id, 1, result["prediction"], result["confidence"], "success")
    )
    
    # 외래키 제약 다시 활성화
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()
except Exception as e:
    conn.rollback()
    raise e
finally:
    cursor.close()
    conn.close()
