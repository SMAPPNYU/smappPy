"""
Module containing twitter supported languages in different formats

@auth dpb
@date 11/13/2013
"""

json_str = '[{"code":"fr","status":"production","name":"French"},{"code":"en","status":"production","name":"English"},{"code":"ar","status":"production","name":"Arabic"},{"code":"ja","status":"production","name":"Japanese"},{"code":"es","status":"production","name":"Spanish"},{"code":"de","status":"production","name":"German"},{"code":"it","status":"production","name":"Italian"},{"code":"id","status":"production","name":"Indonesian"},{"code":"pt","status":"production","name":"Portuguese"},{"code":"ko","status":"production","name":"Korean"},{"code":"tr","status":"production","name":"Turkish"},{"code":"ru","status":"production","name":"Russian"},{"code":"nl","status":"production","name":"Dutch"},{"code":"fil","status":"production","name":"Filipino"},{"code":"msa","status":"production","name":"Malay"},{"code":"zh-tw","status":"production","name":"Traditional Chinese"},{"code":"zh-cn","status":"production","name":"Simplified Chinese"},{"code":"hi","status":"production","name":"Hindi"},{"code":"no","status":"production","name":"Norwegian"},{"code":"sv","status":"production","name":"Swedish"},{"code":"fi","status":"production","name":"Finnish"},{"code":"da","status":"production","name":"Danish"},{"code":"pl","status":"production","name":"Polish"},{"code":"hu","status":"production","name":"Hungarian"},{"code":"fa","status":"production","name":"Farsi"},{"code":"he","status":"production","name":"Hebrew"},{"code":"ur","status":"production","name":"Urdu"},{"code":"th","status":"production","name":"Thai"},{"code":"en-gb","status":"production","name":"English UK"}]'

french = {"code":"fr","status":"production","name":"French"},
english = {"code":"en","status":"production","name":"English"},
arabic = {"code":"ar","status":"production","name":"Arabic"},
japanese = {"code":"ja","status":"production","name":"Japanese"},
spanish = {"code":"es","status":"production","name":"Spanish"},
german = {"code":"de","status":"production","name":"German"},
italian = {"code":"it","status":"production","name":"Italian"},
indonesian = {"code":"id","status":"production","name":"Indonesian"},
portuguese = {"code":"pt","status":"production","name":"Portuguese"},
korean = {"code":"ko","status":"production","name":"Korean"},
turkish = {"code":"tr","status":"production","name":"Turkish"},
russian = {"code":"ru","status":"production","name":"Russian"},
dutch = {"code":"nl","status":"production","name":"Dutch"},
filipino = {"code":"fil","status":"production","name":"Filipino"},
malay = {"code":"msa","status":"production","name":"Malay"},
chinese_tr = {"code":"zh-tw","status":"production","name":"Traditional Chinese"},
chinese_sm = {"code":"zh-cn","status":"production","name":"Simplified Chinese"},
hindi = {"code":"hi","status":"production","name":"Hindi"},
norwegian = {"code":"no","status":"production","name":"Norwegian"},
swedish = {"code":"sv","status":"production","name":"Swedish"},
finnish = {"code":"fi","status":"production","name":"Finnish"},
danish = {"code":"da","status":"production","name":"Danish"},
polish = {"code":"pl","status":"production","name":"Polish"},
hungarian = {"code":"hu","status":"production","name":"Hungarian"},
farsi = {"code":"fa","status":"production","name":"Farsi"},
hebrew = {"code":"he","status":"production","name":"Hebrew"},
urdu = {"code":"ur","status":"production","name":"Urdu"},
thai = {"code":"th","status":"production","name":"Thai"},
english_uk = {"code":"en-gb","status":"production","name":"English UK"}

language_dicts = [french, english, arabic, japanese, spanish, german, italian, indonesian, portuguese,
	korean, turkish, russian, dutch, filipino, malay, chinese_tr, chinese_sm, hindi, norwegian,
	swedish, finnish, danish, polish, hungarian, farsi, hebrew, urdu, thai, english_uk]

language_codes = [ l["code"] for l in language_dicts]
