BEGIN;

-- 1. Xóa cột note khỏi bảng enrollment_events
ALTER TABLE enrollment_events 
DROP COLUMN IF EXISTS note;

-- 2. Xóa thông tin phiên bản 002 khỏi schema_migrations
DELETE FROM schema_migrations WHERE version = '002';

COMMIT;