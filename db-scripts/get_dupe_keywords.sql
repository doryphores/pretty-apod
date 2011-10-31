SELECT		COUNT(*) as dupe_count,
		MAX(label) as mc_label
FROM		apod_keyword
GROUP BY	lower(label)
HAVING		COUNT(*) > 1;