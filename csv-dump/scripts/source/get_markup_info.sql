SELECT 
    TblMarkup.id_markup,
    TblReason.reason_name,
    TblGrade.grade_name,
    TblTag.tag_text,
    TblMarkup.correct,
    TblMarkup.token_id
FROM 
    TblMarkup,
    TblReason,
    TblGrade,
    TblTag
WHERE 
    TblMarkup.reason_id = TblReason.id_reason and
    TblMarkup.grade_id = TblGrade.id_grade and
    TblMarkup.tag_id = TblTag.id_tag and 
    TblTag.tag_language_id = 1 and 
    TblTag.markup_type_id = 1
ORDER BY token_id;