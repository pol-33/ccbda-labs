# 2026_1-2-20
## Team Members
- Zhehan Xiang
- Pol Plana

## Task 1: Deepen Your AWS Cloud Knowledge
### ❓ Question 1: Include screenshots of key steps and briefly explain what you learned or observed.
In this task, we continued our AWS course by completing the module 6, focused on computing services. We learned how to create and deploy an EC2 instance, a Lambda function, and an Elastic Beanstalk application.
We observed that AWS provides a wide range of computing services that can be used to deploy and manage applications in the cloud. We also learned about the different pricing models for these services, including on-demand, reserved, and spot instances.
The most challenging part of this task was to understand the different configurations and settings for each service. However, the step-by-step instructions provided in the module were very helpful in guiding us through the process. In particular, the fac this module not ony includes a lab and a quiz, but also two activities  that allow us to practice in a real AWS environment.

In previous modules, we had already created an EC2 instance, so we think he main advance in this one is on creating a Lambda function and an Elastic Beanstalk application.
In the image below, we can see the different steps we followed to create a Lambda function that runs a simple Python script. We also created an Elastic Beanstalk application that deploys a web application using a pre-configured environment.

![lambdaCreation.png](media/lambdaCreation.png)
![beanstalkEnvironmnt.png](media/beanstalkEnvironmnt.png)
![beanstackAppRunning.png](media/beanstackAppRunning.png)

### ❓ Question 2: Include screenshots of key steps and briefly explain what you learned or observed.

## Task 2: Getting Started with NLTK
### ❓ Question 3: Add your comments to `README.md
We ran `WordCountTensorFlow_1.py`, installed NLTK and downloaded the tokenizer. We also needed to download the input file `FirstContactWithTensorFlow.txt` in the project root.
Then, after reviewing the entire code to understand how it works, we added the total word count print in `main()` after tokenization:
````
total = len(tokens)
print(f"\nTotal number of words: {total}")
````
We considered that the total number of words is the length of the tokens list, because it contains all the words in the text after tokenization.

### ❓ Question 4: Add the code to WordCountTensorFlow_2.py and your comments to `README.md

After adding the code provided that removes punctuations, we observed that the result changed.

In WordCountTensorFlow_1.py the total number of words are 19593.

In WordCountTensorFlow_2.py the total number of words are 21661.

### ❓ Question 5: Why isn’t "TensorFlow" the most frequent word?
After running `WordCountTensorFlow_2.py`, we observed that "tensorflow" is not the most frequent word in the text. Instead, common words like "the", "and", and "to" appear more frequently.
```
First 10 tokens: ['first', 'contact', 'with', 'tensorflow', 'get', 'started', 'with', 'deep', 'learning', 'programming']
The 10 most common words are:
'the' appears 1445 times.
'of' appears 587 times.
'to' appears 532 times.
'in' appears 509 times.
'a' appears 496 times.
'and' appears 347 times.
'tf' appears 304 times.
'is' appears 289 times.
'we' appears 283 times.
'that' appears 276 times.
```

This is happening because the counting logic in the code does not filter out common stop words, so common stopwords and code tokens dominate. For example, words like the, of, to, etc. appear far more often than topical terms.

### ❓ Question 6: Which are the Stop Words?

From the previous question, we can observe that words such as “the,” “of,” “to,” “in,” “a,” “and,” “is,” “we,” “that,” and “tf” occur frequently but carry little meaningful information. These are considered stop words, as they do not contribute significantly to the overall understanding or analysis of the text.

### ❓ Question 7: Add the code to WordCountTensorFlow_3.py and your comments to `README.md

## Task 3: Using the BlueSky API in Python
### ❓ Question 8: Did the data print correctly?

Yes, this is the output:
```
INFO:httpx:HTTP Request: POST https://bsky.social/xrpc/com.atproto.server.createSession "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: GET https://pholiota.us-west.host.bsky.network/xrpc/app.bsky.actor.getProfile?actor=zhehan02.bsky.social "HTTP/1.1 200 OK"
INFO:__main__:Login successful. Welcome, !
INFO:httpx:HTTP Request: POST https://pholiota.us-west.host.bsky.network/xrpc/com.atproto.repo.createRecord "HTTP/1.1 200 OK"
INFO:__main__:Post sent successfully: at://did:plc:r5jq6sggdoy6v6q5mnusu3zf/app.bsky.feed.post/3m27uhiwqot2e
INFO:httpx:HTTP Request: POST https://pholiota.us-west.host.bsky.network/xrpc/com.atproto.repo.createRecord "HTTP/1.1 200 OK"
INFO:__main__:Post liked successfully: at://did:plc:r5jq6sggdoy6v6q5mnusu3zf/app.bsky.feed.post/3m27uhiwqot2e
```
### ❓ Question 9: Add the code to BlueSky_2.py and your comments to `README.md

## Task 4: Posts pre-processing
### ❓ Question 10: Add the code to BlueSky_3.py and your comments to README.md.

We have change the proviuos code so that it only extract 10 post and apply the code porvided.

After executing BlueSky_3.py, we can observe that "@", "#" and "emotions" are tokenized correctly. 

Outout of BlueSky_3.py:
```
INFO:httpx:HTTP Request: POST https://bsky.social/xrpc/com.atproto.server.createSession "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: GET https://pholiota.us-west.host.bsky.network/xrpc/app.bsky.actor.getProfile?actor=zhehan02.bsky.social "HTTP/1.1 200 OK"
INFO:__main__:Login successful. Welcome, !
INFO:httpx:HTTP Request: GET https://pholiota.us-west.host.bsky.network/xrpc/app.bsky.feed.getAuthorFeed?actor=upc.edu&cursor=&includePins=false&limit=10 "HTTP/1.1 200 OK"
['👍', 'Distinci', 'ó', 'Jaume', 'Vicens', 'Vives', 'a', 'la', 'professora', 'de', 'la', '@upctelecos', '.', 'bsky', '.', 'social', 'Eva', 'Vidal', 'i', 'al', 'projecte', '‘', 'InnoCrowd', '’', ',', 'de', 'la', '@upcvilanova', '.', 'upc', '.', 'edu', '.', 'Els', 'guardons', 'es', 'lliuraran', 'el', '7', 'd', '’', 'octubre', 'en', 'el', 'marc', 'la', 'inauguraci', 'ó', 'oficial', 'del', 'curs', 'acad', 'èmic', 'del', 'sistema', 'universitari', 'catal', 'à', '.', 'www', '.', 'upc', '.', 'edu', '/', 'ca', '/', 'sala-de-p', '.', '.', '.', 'El', 'Canal', 'Terrassa', "s'ha", 'fet', 'ress', 'ó', 'del', 'primer', 'simposi', 'sobre', 'propulsi', 'ó', 'a', "l'aviaci", 'ó', 'amb', 'energies', 'renovables', 'que', 'vàrem', 'celebrar', 'ahir', 'a', "l'ESEIAAT", 'de', 'la', '@upc', '.', 'edu', 'organitzat', 'pel', 'nostre', 'professor', '@frikosal', '.', 'bsky', '.', 'social', 'Veieu', 'la', 'video', 'noticia', 'aqu', 'í', '👇', 'youtu', '.', 'be', '/', 'YrblHWPw', '_0k', '?', '.', '.', '.', 'Surten', 'de', 'la', 'universitat', 'els', 'primers', 'graduats', 'en', '#IA', ':', '"', 'Les', 'empreses', 'ens', 'busquen', '"', '@fib', '.', 'upc', '.', 'edu', '#ArtificialIntelligence', 'www', '.', '3', 'cat', '.', 'cat', '/', '3', 'catinfo', '/', 'sur', '.', '.', '.', 'El', 'Grup', "d'Hidrologia", 'Subterr', 'ània', '(', 'GHS', ')', 'de', 'la', '@upc', '.', 'edu', 'participa', 'en', 'el', 'projecte', '#LIFEREMAR', '.', 'L', '’', 'objectiu', 'és', 'desenvolupar', 'una', 'soluci', 'ó', 'innovadora', 'i', 'sostenible', 'per', 'reutilitzar', 'aig', 'ües', 'residuals', 'tractades', 'mitjan', 'çant', 'infiltraci', 'ó', '.', '#EDAR', '#Cambrils', 'IDAEA', '-', '@csic', '.', 'es', '@cnrs', '.', 'fr', '@rdi', '.', 'upc', '.', 'edu', '🔗', 'https://bit.ly/4pMWFogLa', 'catedr', 'àtica', '#UPC', 'Karina', 'Gibert', ',', 'Medalla', "d'Honor", 'del', 'Parlament', 'de', 'Catalunya', '✅', 'La', 'professora', 'de', 'la', '@fib', '.', 'upc', '.', 'edu', ',', 'cofundadora', 'de', "l'IDEAI-UPC", 'i', 'experta', 'en', 'intel', '·', 'lig', 'ència', 'artificial', 'rep', 'el', 'reconeixement', '"', 'la', 'seva', 'aportaci', 'ó', 'a', 'la', 'governan', 'ça', 'de', 'la', 'intel', '·', 'lig', 'ència', 'artificial', '.', 'www', '.', 'upc', '.', 'edu', '/', 'ca', '/', 'sala-de-p', '.', '.', '.', 'És', 'viable', 'l', '’', 'energia', 'renovable', 'a', 'l', '’', 'aviaci', 'ó', 'comercial', '?', 'I', 'l', '’', 'hidrogen', '?', 'Què', 'són', 'els', 'combustibles', 'd', '’', 'aviaci', 'ó', 'sostenibles', '(', 'SAF', ')', '?', 'Aquestes', 'i', 'altres', 'qüestions', 'es', 'debatran', 'al', 'simposi', 'sobre', 'propulsi', 'ó', 'a', "l'aviaci", 'ó', 'amb', 'energies', 'renovables', ',', 'l', "'", '1', 'd', '’', 'octubre', ',', 'a', 'l', '’', '@eseiaat', '-', 'upc', '.', 'bsky', '.', 'social', '.', 'www', '.', 'upc', '.', 'edu', '/', 'ca', '/', 'sala-de-p', '.', '.', '.', 'Les', 'investigadores', 'Maria', 'Pau', 'Ginebra', 'i', 'Jezabel', 'Curbelo', 'i', 'l', '’', 'investigador', 'Sergi', 'Abadal', ',', 'guardonats', 'amb', 'els', 'Premis', 'Nacionals', "d'Investigaci", 'ó', '2025', '.', 'Enhorabona', '!', '👏', '@eebe', '.', 'upc', '.', 'edu', '@ccem', '-', 'upc', '.', 'bsky', '.', 'social', '@upctelecos', '.', 'bsky', '.', 'social', '@mat', '.', 'upc', '.', 'edu', '@fme', '.', 'upc', '.', 'edu', 'www', '.', 'upc', '.', 'edu', '/', 'ca', '/', 'sala-de-p', '.', '.', '.', 'L', '’', 'Ajuntament', 'de', 'Manresa', 'aprova', 'les', 'bases', 'per', 'al', 'concurs', 'del', 'projecte', 'd', '’', 'interiors', 'de', 'la', 'Fàbrica', 'Nova', '.', 'Un', 'nou', 'pas', 'per', 'definir', 'els', 'espais', 'i', 'els', 'usos', 'de', 'l', '’', 'antic', 'recinte', ',', 'que', 'esdevindr', 'à', 'pol', 'de', 'formaci', 'ó', ',', 'recerca', ',', 'emprenedoria', 'i', 'innovaci', 'ó', 'de', 'la', 'mà', 'de', 'la', '#UPC', '@manresa', '.', 'upc', '.', 'edu', 'www', '.', 'upc', '.', 'edu', '/', 'ca', '/', 'sala-de-p', '.', '.', '.', '💫', 'El', 'poder', 'de', 'la', 'imaginaci', 'ó', 'protagonitza', 'la', 'inauguraci', 'ó', 'del', 'curs', 'acad', 'èmic', '2025', '-', '2026', 'a', 'la', '#UPC', '💫', 'En', 'un', 'acte', 'que', 'ha', 'recreat', 'l', '’', 'univers', 'de', 'Hogwarts', ',', 'l', '’', 'escola', 'de', 'màgia', 'de', 'la', 'saga', 'Harry', 'Potter', ',', 'a', 'la', 'sala', 'd', '’', 'actes', 'de', 'l', '’', '@eseiaat', '-', 'upc', '.', 'bsky', '.', 'social', '.', '🔗', 'www', '.', 'upc', '.', 'edu', '/', 'ca', '/', 'sala-de-p', '.', '.', '.', '💫', 'Avui', ',', 'inaugurem', 'oficialment', 'el', 'curs', '2025', '-', '2026', '!', 'A', 'les', '12', 'h', ',', 'a', 'l', "'", '@eseiaat', '-', 'upc', '.', 'bsky', '.', 'social', ',', 'amb', 'un', 'acte', 'que', 'posar', 'à', "l'accent", 'en', 'el', 'poder', 'de', 'la', 'imaginaci', 'ó', 'com', 'a', 'motor', 'de', 'la', 'innovaci', 'ó', 'i', 'del', 'futur', 'STEAM', '.', 'En', 'directe', 'a', 'YouTube', ':', 'www', '.', 'youtube', '.', 'com', '/', 'live', '/', '5', 'hmgevN', '.', '.', '.']
```

## Submit Your Assignment
### ❓ Question 11: How much time did you spend on this session?

### ❓ Question 12: What challenges did you encounter, and how did you overcome them?



