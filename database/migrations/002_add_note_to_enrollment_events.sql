BEGIN;

-- 1. Bổ sung cột note vào bảng enrollment_events
ALTER TABLE enrollment_events 
ADD COLUMN IF NOT EXISTS note VARCHAR(200);

-- 2. Ghi nhận phiên bản migration 002
INSERT INTO schema_migrations (version, description)
VALUES ('002', 'Add note column to enrollment_events');

COMMIT;