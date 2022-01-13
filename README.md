# subtitle_translator
translate subtitles between english, japanese and chinese

This serves to automate subtitle translation for media server use. 

Subtitles containing chinese or japanese text may be encoded in many different formats which may cause issues when trying to translate. This program detects the underlying file encoding of each subtitle file in a folder and do bulk translation. 

Supported encodings include: 
```
EUC-CN
HZ
GBK
CP936
GB18030
EUC-TW
BIG5
CP950
BIG5-HKSCS
BIG5-HKSCS:2004
BIG5-HKSCS:2001
BIG5-HKSCS:1999
ISO-2022-CN
ISO-2022-CN-EXT
```