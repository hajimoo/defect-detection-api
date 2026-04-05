CREATE DATABASE IF NOT EXISTS ai_defect_detection
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE ai_defect_detection;

CREATE TABLE users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_users_username (username)
) ENGINE=InnoDB;

CREATE TABLE uploaded_images (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) DEFAULT NULL,
    file_size BIGINT UNSIGNED DEFAULT NULL,
    file_hash CHAR(64) DEFAULT NULL,
    width INT DEFAULT NULL,
    height INT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_uploaded_images_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE predictions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    image_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    model_version VARCHAR(100) DEFAULT NULL,
    label VARCHAR(100) DEFAULT NULL,
    confidence DECIMAL(5,4) DEFAULT NULL,
    status ENUM('pending', 'success', 'failed', 'review_needed') NOT NULL DEFAULT 'pending',
    is_low_confidence TINYINT(1) NOT NULL DEFAULT 0,
    failure_reason TEXT DEFAULT NULL,
    similar_case_group VARCHAR(100) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_predictions_image
        FOREIGN KEY (image_id) REFERENCES uploaded_images(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_predictions_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE review_queue (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    prediction_id BIGINT UNSIGNED NOT NULL,
    review_status ENUM('pending', 'reviewed', 'rejected') NOT NULL DEFAULT 'pending',
    human_label VARCHAR(100) DEFAULT NULL,
    ai_review_summary TEXT DEFAULT NULL,
    ai_review_recommendation TEXT DEFAULT NULL,
    reviewed_at DATETIME DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_review_queue_prediction_id (prediction_id),
    CONSTRAINT fk_review_queue_prediction
        FOREIGN KEY (prediction_id) REFERENCES predictions(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE dataset_candidates (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    prediction_id BIGINT UNSIGNED NOT NULL,
    is_dataset_candidate TINYINT(1) NOT NULL DEFAULT 0,
    candidate_reason VARCHAR(255) DEFAULT NULL,
    candidate_status ENUM('pending', 'approved', 'excluded') NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_dataset_candidates_prediction_id (prediction_id),
    CONSTRAINT fk_dataset_candidates_prediction
        FOREIGN KEY (prediction_id) REFERENCES predictions(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE request_logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    prediction_id BIGINT UNSIGNED DEFAULT NULL,
    request_id VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    client_ip VARCHAR(45) DEFAULT NULL,
    status_code INT DEFAULT NULL,
    latency_ms INT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_request_logs_request_id (request_id),
    CONSTRAINT fk_request_logs_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_request_logs_prediction
        FOREIGN KEY (prediction_id) REFERENCES predictions(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE error_logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    request_log_id BIGINT UNSIGNED NOT NULL,
    error_code VARCHAR(100) DEFAULT NULL,
    error_message VARCHAR(255) DEFAULT NULL,
    error_detail TEXT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_error_logs_request_log
        FOREIGN KEY (request_log_id) REFERENCES request_logs(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
