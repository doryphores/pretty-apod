UPDATE	apod_picture_keywords pk
SET	keyword_id = dupes.id
FROM	(
SELECT id, label FROM apod_keyword WHERE label IN (
	SELECT		MAX(label) as mc_label
	FROM		apod_keyword
	GROUP BY	lower(label)
	HAVING		COUNT(*) > 1)
) AS dupes, apod_keyword k
WHERE	keyword_id = k.id AND keyword_id != dupes.id AND lower(k.label) = lower(dupes.label);

DELETE
FROM	apod_keyword
WHERE	id NOT IN (SELECT keyword_id FROM apod_picture_keywords);