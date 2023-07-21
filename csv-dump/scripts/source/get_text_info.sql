SELECT TblText.id_text, TblText.header, TblText.assessment, TblGroup.course_number, TblText.text
FROM  TblText, TblTextGroup, TblGroup 
WHERE TblText.language_id = 1 and TblTextGroup.text_id = TblText.id_text and TblTextGroup.group_id = TblGroup.id_group 
ORDER BY TblText.id_text;