SELECT 
    TblSentence.text_id,
    TblToken.id_token,
    TblToken.text,
    TblSentence.order_number as sentence_order,
    TblToken.order_number as token_order
FROM 
    TblToken,
    TblSentence,
    TblText
WHERE 
    TblText.language_id = 1 and 
    TblSentence.text_id = TblText.id_text and 
    TblToken.sentence_id = TblSentence.id_sentence
ORDER BY text_id, sentence_order, token_order;