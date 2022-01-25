import configparser
from pathlib import Path
from datetime import datetime
from tracemalloc import start, stop
from tqdm import tqdm
from chardet.universaldetector import UniversalDetector

RGX_INDEX = r"-?[0-9]+\.?[0-9]*"

def translateDeepL(job_configuration, inputText):
    """ Translate text with DeepL

    Keyword arguments:
    job_configuration -- argument description goes here
    inputText -- string of text to be translated
    
    """
    payload = {
        "auth_key": deeplapikey, "text": inputText, 
        "targetLang": job_configuration['target_lang'],
        "sourceLang": job_configuration['source_lang'], 
        "split_sentences": job_configuration['split_sentences'],
        "preserve_formatting": job_configuration['preserve_formatting']        
    }

    response = requests.post(deeplapiurl,
                             data=payload,
                             headers={'Content-Type': 
                                      'application/x-www-form-urlencoded'})
    
    return response.text

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
                currentSubtitleBlock = SubtitleBlock(index, startTime,
                                                     stopTime, subtitleText)
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
targetLang = config['LANG']['sourceLang']

splitSentences = 1
preserveFormatting = 0
job_configuration = {'sourceLang' : sourceLang, 
                     'targetLang' : targetLang,
                     'split_sentences' : splitSentences, 
                     'preserve_formatting' : preserveFormatting}

# Generate list of paths using recursive directory search for .srt files
subtitlePaths = [path for path in inputPath.rglob('*.srt')]
print('Detected the following subtitlefiles: ')
for path in subtitlePaths:
    rootPathLength = len(config['PATHS']['dataPath']) + 1
    print(str(path)[rootPathLength:])
print('\n')

for subtitlePath in tqdm(subtitlePaths):

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
"""
deepL_job_configuration = {'source_lang' : source_lang,
                           'target_lang' : target_lang,
                           'split_sentences' : split_sentences,
                           'preserve_formatting' : preserve_formatting}
"""