EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, class_section_id, event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
  AND student_id = '22000001'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
ORDER BY occurred_at DESC
LIMIT 50;

-- ==========================================
-- BÀI TẬP TỰ THỰC HÀNH - BÀI 3: CHỈ MỤC THỨ HAII
-- ==========================================

-- 1. Đo truy vấn chưa có Index mới
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, event_type, occurred_at
FROM enrollment_events
WHERE class_section_id = 'WEB-01'
  AND event_type = 'CREATED'
ORDER BY occurred_at DESC;

-- 2. Tạo Composite Index ghép cho (class_section_id, event_type, occurred_at DESC)
CREATE INDEX idx_enrollment_events_section_type_time
ON enrollment_events (class_section_id, event_type, occurred_at DESC);

ANALYZE enrollment_events;

-- 3. Đo lại truy vấn sau khi có Index
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, event_type, occurred_at
FROM enrollment_events
WHERE class_section_id = 'WEB-01'
  AND event_type = 'CREATED'
ORDER BY occurred_at DESC;