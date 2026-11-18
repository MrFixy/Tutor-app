-- Optional one-time cleanup for databases created by the older Stats/Coding Tutor.
-- Back up the database before running this migration. It removes old exercise,
-- mastery, and standalone track lesson data; ordinary chat history is retained.

DROP TABLE IF EXISTS attempts CASCADE;
DROP TABLE IF EXISTS mastery_score CASCADE;

DELETE FROM lesson_content WHERE domain IN ('stats', 'coding');
DELETE FROM study_plan_items WHERE domain IN ('stats', 'coding');
DELETE FROM study_plans plan
WHERE NOT EXISTS (
    SELECT 1 FROM study_plan_items item WHERE item.plan_id = plan.id
);

ALTER TABLE questions DROP COLUMN IF EXISTS intent_domain;
ALTER TABLE questions DROP COLUMN IF EXISTS intent_subtopic;
ALTER TABLE questions DROP COLUMN IF EXISTS intent_confidence;
ALTER TABLE questions DROP COLUMN IF EXISTS classified_json;

-- Phase + lesson slugs can be longer than the old standalone-track values.
ALTER TABLE IF EXISTS lesson_content
    ALTER COLUMN subtopic TYPE VARCHAR(255);

-- This nullable column was used only by the old multi-track roadmap format.
ALTER TABLE IF EXISTS study_plan_items DROP COLUMN IF EXISTS language;
