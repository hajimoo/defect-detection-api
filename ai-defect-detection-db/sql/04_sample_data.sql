USE ai_defect_detection;

INSERT INTO users (email, password_hash, role, is_active)
VALUES
('user1@test.com', 'hashed_pw_1', 'user', 1),
('admin@test.com', 'hashed_pw_admin', 'admin', 1);

INSERT INTO uploaded_images (
    user_id,
    original_filename,
    stored_path,
    mime_type,
    file_size,
    file_hash,
    width,
    height
)
VALUES
(1, 'sample1.jpg', '/data/sample1.jpg', 'image/jpeg', 245678, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 1024, 768),
(1, 'sample2.jpg', '/data/sample2.jpg', 'image/jpeg', 198234, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 800, 600);

INSERT INTO predictions (
    image_id,
    user_id,
    model_version,
    label,
    confidence,
    status,
    is_low_confidence,
    failure_reason,
    similar_case_group
)
VALUES
(1, 1, 'v1.0.0', 'normal', 0.9500, 'success', 0, NULL, 'group_a'),
(2, 1, 'v1.0.0', 'defect', 0.5200, 'review_needed', 1, NULL, 'group_b');

INSERT INTO review_queue (
    prediction_id,
    review_status,
    human_label,
    ai_review_summary,
    ai_review_recommendation,
    reviewed_at
)
VALUES
(2, 'pending', NULL, 'Low confidence score requires additional review', 'Manual verification recommended', NULL);

INSERT INTO dataset_candidates (
    prediction_id,
    is_dataset_candidate,
    candidate_reason,
    candidate_status
)
VALUES
(2, 1, 'Low confidence case registered as retraining candidate', 'pending');

INSERT INTO request_logs (
    user_id,
    prediction_id,
    request_id,
    endpoint,
    method,
    client_ip,
    status_code,
    latency_ms
)
VALUES
(1, 1, 'REQ-001', '/predict', 'POST', '127.0.0.1', 200, 312),
(1, 2, 'REQ-002', '/predict', 'POST', '127.0.0.1', 200, 487);

INSERT INTO error_logs (
    request_log_id,
    error_code,
    error_message,
    error_detail
)
VALUES
(2, 'LOW_CONF_WARN', 'Low confidence detected', 'Prediction confidence was below the review threshold.');
