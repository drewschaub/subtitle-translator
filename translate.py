import configparser

def translate_deepl(job_configuration, inputText):
    """ Translate text with DeepL

    Keyword arguments:
    job_configuration -- argument description goes here
    inputText -- string of text to be transalted
    
    """
    payload = {
        "auth_key": deeplapikey, "text": inputText, 
        "target_lang": job_configuration['target_lang'],
        "source_lang": job_configuration['source_lang'], 
        "split_sentences": job_configuration['split_sentences'],
        "preserve_formatting": job_configuration['preserve_formatting']        
    }

    response = requests.post(deeplapiurl, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    return response.text

config = configparser.ConfigParser()
config.read('config.ini')

