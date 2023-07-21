# Справочник по языку запросов CQL

Язык [Corpus Query Language](https://www.sketchengine.eu/documentation/corpus-querying/)
предназначен для формирования поисковых запросов в размеченных корпусах текстов.

## Простые запросы
* `[word = ”man”]` - точная словоформа
* `[pos = ”NOUN”]` - часть речи
* `[error = ”Error”]` - тип ошибки
* `[]` - любое слово?

## REGEX
* `.*` (точка и звездочка) означает, что на этом месте может быть любой набор символов(включая ноль символов)
* `[word = ”man.*”]` - словоформы начинающиеся на man
* `[word = ”.*man”]` - словоформы, заканчивающиеся на man
* `[word = ”.*man.*”]` - словоформы, содержащие man

## Совокупность запросов
* `[word = ”man” & error = ”Error”]` - и
* `[word = ”man” | error = ”Error”]` - или

## Условные операторы
* `[word = ”man”]` - равно
* `[word != ”man”]` - не равно

## Причина ошибок
| Причина                           | 	Аббревиатура |
|-----------------------------------|---------------|
| Interferenz mit der Muttersprache | 	IM |
| Interferenz mit Englisch | 	IE |
| Tippfehler |	TF |

## Степень грубости ошибки
| Причина |	Аббревиатура |
| --- | --- |
|Der Fehler beeinträchtigt das Verständnis nicht | 	V0 |
|Der Fehler beeinträchtigt das Verständnis |	V1|
|Der Sinn ist unverständlich oder verfälscht |	V2|

## Теги ошибок
|Тег 	|На русском 	| Аббревиатура |
| --- | --- |--------------|
| Grammatik                | Грамматика                 | GR    |
| Substantive              | Существительное            | NN    |
| Artikel                  | Артикль                    | ART   |
| Zahlwörter               | Числительное               | ZW    |
| Pronomen                 | Местоимение                | PN    |
| Verben                   | Глагол                     | V     |
| Partizipien              | Причастие                  | PZ    |
| Präpositionen            | Предлоги                   | PR    |
| Konjunktionen            | Союзы                      | KONJ  |
| Adjektive                | Прилагательное             | ADJ   |
| Adverbien                | Наречия                    | ADV   |
| Wortfolge                | Порядок слов               | WF    |
| Vergleichkonstruktionen  | Сравнительные конструкции  | VGK   |
| Infinitivkonstruktionen  | Инфинитивные конструкции   | INFK  |
| Lexik                    | Лексика                    | LEX   |
| Lexemauswahl             | Выбор лексемы              | LEXW  |
| Feste Wendungen          | Устойчивые обороты         | FESTW |
| Wortbildung              | Словообразование           | WB    |
| Diskurs                  | Дискурс                    | DISK  |
| Logik                    | Логика                     | LOG   |
| Sprachstil                | Стиль                        | STIL    |
| Auslassungen              | Пропуски                     | AUSL    |
| Überflüssige Elemente     | Лишние элементы              | UELEM   |
| Orthographie              | Орфография                   | ORTH    |
| Interpunktion             | Пунктуация                   | PUNKT   |
| Geschlecht                | Род                          | NNG     |
| Numerus                   | Число                        | NNN     |
| Deklination               | Склонение                    | NND     |
| Rektion von Substantiven  | Управление существительного  | NNREK   |
| Bestimmter Artikel        | Определенный артикль         | BART    |
| Unbestimmter Artikel      | Неопределенный артикль       | UBART   |
| Negationsartikel          | Отрицательный артикль        | NEGART  |
| Nullartikel               | Нулевой артикль              | NULLART |
| Kardinalzahlen            | Количественное числительное  | CARD    |
| Ordinalzahlen             | Порядковое числительное      | OZ      |
| Weitere Zahlwörter        | Другие указатели на число    | WZW     |
| Personalpronomen          | Личное местоимение           | PPER    |
| Possessivpronomen         | Притяжательное местоимение   | PPOS    |
| Demonstrativpronomen      | Указательное местоимение     | PD      |
| Interrogativpronomen      | Вопросительное местоимение   | PW      |
| Reflexivpronomen                          | Возвратное местоимение                     | PRF     |
| Deklination des Pronomens                 | Склонение местоимений                      | PND     |
| Konjugation                               | Спряжение                                  | VK      |
| Zeitform                                  | Время                                      | VZ      |
| Modus                                     | Наклонение                                 | VMOD    |
| Genus                                     | Залог                                      | VG      |
| Rektion von Verben                        | Управление глаголов                        | VREK    |
| Partizip I                                | Причастие I                                | VP      |
| Partizip II                               | Причастие II                               | VPP     |
| Wahl der Präposition                      | Выбор предлога                             | PRW     |
| Präpositionen mit einem bestimmten Kasus  | Предлог с определенным падежом             | PRK     |
| Wechselpräpositionen                      | Предлог, управляющий несколькими падежами  | PRWEC   |
| Deklination von Adjektiven                | Склонение прилагательного                  | ADJD    |
| Komparativform                            | Сравнительная степень                      | ADJK    |
| Superlativform                            | Превосходная степень                       | ADJS    |
| Rektion von Adjektiven                    | Управление прилагательного                 | ADJREK  |
| Verbstellung                              | Место глагола                              | WFV     |
| Wortstellung                              | Место второстепенных членов предложения    | WFWS    |
| Infinitivkonstruktionen mit zu            | Инфинитивные конструкции с zu              | INFKZU  |
| Infinitivkonstruktionen ohne zu           | Инфинитивные конструкции без zu            | INFKOZU |
| Derivative Suffixe            | Словообразовательные суффиксы           | DERSUF |
| Derivative Präffixe           | Словообразовательные префиксы           | DERPF  |
| Zusammengesetzte Wörter       | Сложные слова                           | ZMW    |
| Konnektoren                   | Соединительные элементы                 | KON    |
| Modalverben                   | Модальный глагол                        | VM     |
| Starke Verben                 | Сильный глагол                          | VS     |
| Trennbare Verben              | Глагол с отделяемой приставкой          | VT     |
| Untrennbare Verben            | Глагол с неотделяемой приставкой        | VUT    |
| Wahl der Zeitform             | Выбор временной формы                   | VWZ    |
| Bildung der Zeitform          | Образование временной формы             | VBZ    |
| Imperativ                     | Императив                               | VIMP   |
| Konjunktiv                    | Конъюнктив                              | VKONJ  |
| Aktiv                         | Активный залог                          | VGA    |
| Passiv                        | Пассивный залог                         | VGP    |
| Zustandspassiv                | Пассив состояния                        | VGZP   |
| Direkte Wortfolge             | Прямой порядок слов                     | WFD    |
| Indirekte Wortfolge           | Обратный порядок слов                   | WFI    |
| Satzklammer                   | Рамочная конструкция                    | WFSKL  |
| Wortfolge in einer Satzreihe  | Порядок слов в придаточном предложении  | WFSR   |
| Wortstellung in der Negation  | Порядок слов при отрицании              | WFWSN  |
| Thema-Rhema-Gliederung  | Тема-рематическое членение предложения  | TRG  |
| Präsens                 | Презенс                                 | WZPS |
| Präteritum              | Претерит                                | WZPT |
| Perfekt                 | Перфект                                 | WZPF |
| Plusquamperfekt         | Плюсквамперфект                         | WZPQ |
| Futurum I               | Футурум I                               | WZF  |
| Präsens                 | Презенс                                 | BZPS |
| Präteritum              | Претерит                                | BZPT |
| Perfekt                 | Перфект                                 | BZPF |
| Plusquamperfekt         | Плюсквамперфект                         | BZPQ |
| Futurum I               | Футурум I                               | BZF  |

## Теги частей речи
* attributive adjective (including participles used adjectivally)
* predicate adjective; adjective used adverbially
* adverb (never used as attributive adjective)
* preposition left hand part of double preposition
* preposition with fused article
* postposition
* right hand part of double preposition
* article (definite or indefinite)
* cardinal number (words or figures); also declined
* foreign words (actual part of speech in original language may be appended, e.g. FMADV/ FM-NN)
* interjection
* preposition used to introduce infinitive clause
* subordinating conjunction
* co-ordinating conjunction
* comparative conjunction or particle
* noun (but not adjectives used as nouns)
* names and other proper nouns
* demonstrative determiner
* demonstrative pronoun
* indefinite determiner (whether occurring on its own or in conjunction with another determiner)
* indefinite pronoun
* personal pronoun
* possessive determiner
* possessive pronoun
* relative pronoun (i.e. forms of der or welcher)
* relative depending on a noun
* reflexive pronoun
* interrogative pronoun
* interrogative determiner
* interrogative adverb
* PROAV
* infinitive particle
* negative particle
* separable prefix
* answer particle
* particle with adjective or adverb
* truncated form of compound
* finite full verb
* finite auxiliary verb
* finite modal verb
* infinitive of full verb
* infinitive of auxiliary
* infinitive of modal
* imperative of full verb
* imperative of auxiliary
* past participle of full verb
* past participle of auxiliary
* past participle of auxiliary
* infinitive with incorporated zu
* PAV
* XY
* $,
* $(
* $.
* POS
