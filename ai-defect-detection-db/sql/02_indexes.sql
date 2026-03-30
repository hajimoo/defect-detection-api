USE ai_defect_detection;

CREATE INDEX idx_uploaded_images_user_id
    ON uploaded_images(user_id);

CREATE INDEX idx_uploaded_images_file_hash
    ON uploaded_images(file_hash);

CREATE INDEX idx_predictions_user_id
    ON predictions(user_id);

CREATE INDEX idx_predictions_image_id
    ON predictions(image_id);

CREATE INDEX idx_predictions_status
    ON predictions(status);

CREATE INDEX idx_predictions_model_version
    ON predictions(model_version);

CREATE INDEX idx_predictions_created_at
    ON predictions(created_at);

CREATE INDEX idx_request_logs_user_id
    ON request_logs(user_id);

CREATE INDEX idx_request_logs_prediction_id
    ON request_logs(prediction_id);

CREATE INDEX idx_request_logs_created_at
    ON request_logs(created_at);

CREATE INDEX idx_request_logs_status_code
    ON request_logs(status_code);

CREATE INDEX idx_error_logs_request_log_id
    ON error_logs(request_log_id);

CREATE INDEX idx_error_logs_error_code
    ON error_logs(error_code);

CREATE INDEX idx_review_queue_status
    ON review_queue(review_status);

CREATE INDEX idx_dataset_candidates_flag
    ON dataset_candidates(is_dataset_candidate);

CREATE INDEX idx_dataset_candidates_status
    ON dataset_candidates(candidate_status);

CREATE INDEX idx_predictions_user_created
    ON predictions(user_id, created_at);

CREATE INDEX idx_predictions_status_created
    ON predictions(status, created_at);

CREATE INDEX idx_review_queue_status_created
    ON review_queue(review_status, created_at);

CREATE INDEX idx_dataset_candidates_status_created
    ON dataset_candidates(candidate_status, created_at);
