import configparser
import requests
import time
from chardet.universaldetector import UniversalDetector
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from tracemalloc import start, stop
from tqdm import tqdm

LANG_DICT = {'EN' : 'English', 'JA' : 'Japanese', 'ZH' : 'Chinese'}

def detectEncoding(subtitlePath):
    with open(subtitlePath, "rb") as myfile:
        detector = UniversalDetector()
        for line in myfile:
            detector.feed(line)
            if detector.done: break
        detector.close()

    return detector.result['encoding']

def generateSubtitleBlocks(content):
    """ Convert subtitle file into subtitle blocks

    Keyword arguments:
    content -- file object readLines
    
    returns list of subtitle objects

    """
    # currentState = -1 (initial state), 1 (numeric), 2 (times), 3 (text)
    currentState = -1 # stores state corresponding to last line read
    subtitleBlocks = [] # empty list to store subtitle block objects

    for line in content:

        # If more than one line of text in subtitle block
        if currentState == 2:
            # If blank line detected, generate a block object
            if line in ['\n', '\r\n']:
                replacedText = replaceText(subtitleText)

                currentSubtitleBlock = SubtitleBlock(index, startTime,
                                                     stopTime, replacedText)
                subtitleBlocks.append(currentSubtitleBlock)

                # Increment state by 1 to begin looking for new index
                currentState = 3
            else:
                subtitleText = subtitleText + line

        # Extract start and stop times
        if currentState == 1:
            timeLineAsText = line
            
            startTime, stopTime = timeLineAsText.split('-->')
            startTime = startTime.strip()
            stopTime = stopTime.strip()

            # Will be used to check for issues with timestamps (action item)
            startTimeDatetime = datetime.strptime(startTime, '%H:%M:%S,%f')
            stopTimeDatetime = datetime.strptime(stopTime, '%H:%M:%S,%f')
            subtitleText = ''
            
            # Increment state by 1 to begin looking for subtitle text
            currentState = 2

        # Looks for index value from each subtitle block in SRT file
        if str(line)[:-1].isdecimal():
            if (currentState == -1) or (currentState == 3):
                index = int(line)

                # Increment state by 1 to begin looking for time information
                currentState = 1

    # If there is no last line in subtitle fi
    if currentState == 2:
        currentSubtitleBlock = SubtitleBlock(index, 
                                                startTime,
                                                stopTime,
                                                subtitleText)
        subtitleBlocks.append(currentSubtitleBlock)

    return subtitleBlocks

def replaceText(text):
    """ replace carriage-return and a few other symbols

    Keyword arguments:
    text -- str
    
    returns str with text replacements

    """

    text = text.replace("\\N", " ")
    text = text.replace("\n", " ")
    text = text.replace('♬', '音楽')
    text = text.replace('☎', '[電話] ')

    return text

def request(text):
    translatedText = '<<NOT ASSIGNED>>'
    try:
        responseText = translate_core_deepl(job_configuration, text.strip(), deepLApiURL).replace('\\', '')
        textPrefix = len('{"translations":[{"detected_source_language":"EN","text":"')
        translatedText = responseText[textPrefix:-4]
    except Exception as e:
        print(e)
        translatedText = 'ERROR! ERROR! ERROR! TRANSLATION FAILED'
        print('ERROR! Translation failed for: {}'.format(text))
        pass

    return translatedText

def translate_core_deepl(job_configuration, inputText, deepLApiURL):
    
    payload = {
        "auth_key": deepLApiKey, "text": inputText, 
        "target_lang": job_configuration['targetLang'],
        "source_lang": job_configuration['sourceLang'], 
        "split_sentences": job_configuration['splitSentences'],
        "preserve_formatting": job_configuration['preserveFormatting']
     } 
    response = requests.post(deepLApiURL, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    return response.text

class SubtitleBlock(object):
    """ A class used to represent a subtitle block

    Attributes
    ----------
    index : int
        numeric counter for subtitle block indices
    startTime : datetime
        datetime for start of subtitle
    stopTime : datetime
        datetime for stop of subtitle
    subtitleText : str
        subtitle text to be displayed

    """
    def __init__(self, index, startTime, stopTime, subtitleText):
        """Class method docstrings go here."""
        self.index = index
        self.startTime = startTime
        self.stopTime = stopTime
        self.subtitleText = subtitleText

config = configparser.ConfigParser()
configPath = Path('..', 'config', 'config.ini')
config.read(configPath)

inputPath = Path(config['PATHS']['dataPath'], config['PATHS']['inputFolder'])
outputPath = Path(config['PATHS']['dataPath'], config['PATHS']['outputFolder'])

sourceLang = config['LANG']['sourceLang']
targetLang = config['LANG']['targetLang']

translator = config['SERVICES']['translator']

# Generate list of paths using recursive directory search for .srt files
subtitlePaths = [path for path in inputPath.rglob('*.srt')]
print('Detected the following subtitlefiles: ')
for path in subtitlePaths:
    rootPathLength = len(config['PATHS']['dataPath']) + 1
    print('  {}'.format(str(path)[rootPathLength:]))
print('')

for subtitlePath in tqdm(subtitlePaths):
    # Generate path of translated subtitle file
    relativeFilePathString = str(subtitlePath)[len(str(inputPath)) + 1:]
    relativeFilePathString = relativeFilePathString.replace(LANG_DICT[sourceLang], LANG_DICT[targetLang])
    relativeFilePath = Path(outputPath, relativeFilePathString)

    # If paths don't exist call mkdir and make the directories
    relativeFileParentPath = Path(outputPath, relativeFilePath).parents[0]
    relativeFileParentPath.mkdir(parents=True, exist_ok=True)

    # Detect encoding of subtitle file
    encoding = detectEncoding(subtitlePath)

    print(encoding, subtitlePath)

    try:
        with open(subtitlePath, "r", encoding=encoding) as f:
                content = f.readlines()
    except:
        # GBK causes issues
        with open(subtitlePath, "r", encoding='GBK') as f:
                content = f.readlines()
        pass

    currentSubtitleBlocks = generateSubtitleBlocks(content)

    if translator == 'deepLPro':
        apiAuthKeyPrompt = config['SERVICES'].getboolean('apiAuthKeyPrompt')
        deepLApiURL = 'https://api.deepl.com/v2/translate'

        if apiAuthKeyPrompt:
            deepLApiKey = input('Enter your DeepL API Key (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx): ')
        else:
            deepLApiKey = config['SERVICES']['deepLApiKey']

        splitSentences = 1
        preserveFormatting = 0
        job_configuration = {'sourceLang' : sourceLang, 
                            'targetLang' : targetLang,
                            'splitSentences' : splitSentences, 
                            'preserveFormatting' : preserveFormatting}

        threadCount = int(config['SERVICES']['deepLthreads'])
        pool = ThreadPool(threadCount)

        textBlocks = []
        for subtitleBlock in currentSubtitleBlocks:
            textBlocks.append(subtitleBlock.subtitleText)

        time1 = time.time()
        translationResults = pool.map(request, textBlocks)
        pool.close()
        pool.join()
        time2 = time.time()

        print("Translating %s subtitle elements, a total of %s s"%(len(textBlocks),time2 - time1))

        counter = 0
        translatedText = ''

        translatedContent = ''

        for subtitleBlock in currentSubtitleBlocks:
            # Part 1 - index
            reindex = config['FILE-OPTIONS'].getboolean('reindex')
            if reindex:
                index = counter + 1
            else:
                index = subtitleBlock.index

            # Part 2 - timestamps
            timestampLine = subtitleBlock.startTime + ' --> ' + subtitleBlock.stopTime

            # Part 3 - subtitle text (translated)
            translatedText = translationResults[counter]

            newTranslatedBlock = '{}\n{}\n{}\n\n'.format(str(index), timestampLine, translatedText)
            translatedContent = translatedContent + newTranslatedBlock

            counter = counter + 1

        relativeFilePath.write_text(translatedContent)
        print('Finished: {}'.format(relativeFilePath))


