# subtitle_translator
translate subtitles between english, japanese and chinese

This serves to automate subtitle translation for media server use. 

## Directions

In the ```config.ini``` file specify the location of your subtitles. It's setup assuming it's for media server use, so includes support for nested folder searching. The user can specify the same input and output path locations if desired, allowing the user to translate all existing subtitles files in their current media path. The subtitles to be translated need to include the input subtitle language.

if the user wants to translate all Japanese ```.srt``` files than those need to include ```.Japanese```, ```.ja```, or ```.jpn``` in their filenames to be detected by the system. The full list of language representations can be found in ISO 639.2 and listed here for reference: [https://www.loc.gov/standards/iso639-2/php/code_list.php](https://www.loc.gov/standards/iso639-2/php/code_list.php). For example, in the folder ```桜の塔 (2021)/Season 01```, ```translator.py``` would detect and translate the following file as it specifies the language in the file name:

```
桜の塔 S01E06.Japanese.srt
```

If the user is using a DeepL Pro account they may choose to store the API key in their ```config.ini``` file. However, for security reasons the user may also have ```translate.py``` prompt them for their auth key by setting ```apiAuthKeyPrompt = True``` in ```config.ini``` under ```[SERVICES]```. 

## Current Support

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

The range of unicode characters which are routinely used for Chinese and Japaense text[1] are:

1. U+3040 - U+30FF: hiragana and katakana (Japanese only)
2. U+3400 - U+4DBF: CJK unified ideographs extension A (Chinese, Japanese, and Korean)
3. U+4E00 - U+9FFF: CJK unified ideographs (Chinese, Japanese, and Korean)
4. U+F900 - U+FAFF: CJK compatibility ideographs (Chinese, Japanese, and Korean)
5. U+FF66 - U+FF9F: half-width katakana (Japanese only)



There are multiple data formats for subtitles. This initial version supports ```.srt```, though I have other file formats planned for the future.

This initial version currently only supports the paid version of DeepL, though I will add support for the non-paid version, as well as Google Translate. 

## Future Directions
1. Incorporate use of an autotranslater, such as PyTranscriber for automatic generation of text from audiofiles.
2. Include pre- and post-processing of subtitle files to handle nuances that arise with subtitle files, such as the use of ```♫``` and other symbols which may confuse the translator models being useds by this automation tool. 

## References
[1] https://stackoverflow.com/questions/43418812/check-whether-a-string-contains-japanese-chinese-characters
