USE ai_defect_detection;

CREATE OR REPLACE VIEW vw_prediction_summary AS
SELECT
    p.id AS prediction_id,
    p.label,
    p.confidence,
    p.status,
    p.model_version,
    p.is_low_confidence,
    p.failure_reason,
    p.similar_case_group,
    p.created_at AS prediction_created_at,
    u.email AS user_email,
    ui.original_filename,
    ui.stored_path,
    rq.review_status,
    rq.human_label,
    rq.ai_review_summary,
    dc.is_dataset_candidate,
    dc.candidate_reason,
    dc.candidate_status
FROM predictions p
JOIN users u ON p.user_id = u.id
JOIN uploaded_images ui ON p.image_id = ui.id
LEFT JOIN review_queue rq ON p.id = rq.prediction_id
LEFT JOIN dataset_candidates dc ON p.id = dc.prediction_id;
