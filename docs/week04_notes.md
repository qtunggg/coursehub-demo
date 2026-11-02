# CourseHub - Buoi 4 Notes

- Migration 001: enrollment_events.
- Demo class: RACE-01, capacity = 1.
- POST /enrollments: lock class_sections bang FOR UPDATE.
- Concurrency test: 1 request 201, 1 request 409.
- Performance data: 100000 rows, dataset=performance.
- Index: idx_enrollment_events_dataset_student_time.
- Scan type truoc/sau: Seq Scan -> Index Scan.

- Index Bai 3: idx_enrollment_events_section_type_time (class_section_id, event_type, occurred_at DESC).
- Scan type Bai 3: Seq Scan -> Index Scan.