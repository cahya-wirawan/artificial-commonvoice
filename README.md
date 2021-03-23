# CommonVoicer
Common Voice is a crowdsourcing project started by Mozilla to create a free database for speech recognition software.
It aims to provide diverse voice samples from difference languages. Its dataset contains more than 1600 hours of
validated english voices, however many languages are still under presented. Low resource languages are a challenge 
for the training of speech recognition model.

To solve this issue a little, I create CommonVoicer. It generates Common Voices using difference Speech Synthesizer 
services such as Google Text To Speech or Azure Text To Speech (Currently, only Google Text To Speech is supported).
It reads the tab separated value (tsv) file provided by Common Voice which contains client-id, sentence, path of the 
sound file and other information. It sends the sentence one by one to the Speech Synthesizer service like Google TTS, 
and stores the retrieved sound files.

## Usage
```
$ export GOOGLE_APPLICATION_CREDENTIALS="path to the google authentication credentials"
$ python commonvoicer.py -c validated.tsv -v id-ID-Standard-A id-ID-Wavenet-B -o "./output"
```