import configparser
from pathlib import Path
from tqdm import tqdm
from chardet.universaldetector import UniversalDetector

def translateDeepL(job_configuration, inputText):
    """ Translate text with DeepL

    Keyword arguments:
    job_configuration -- argument description goes here
    inputText -- string of text to be transalted
    
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

count = 0
for subtitlePath in tqdm(subtitlePaths):

    encoding = detectEncoding(subtitlePath)

    print(count, encoding, subtitlePath)

    count = count + 1

    indexes = []
    timestamps = []
    textBlocks = []
    block = []   