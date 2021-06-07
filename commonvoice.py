import pandas as pd
from pathlib import Path
from google.cloud import texttospeech
import argparse
import logging
import random
import time


class CommonVoice:
    """
    CommonVoice is a Common Voice Generator using difference types of Speech Synthesizer such as
    Google Text To Speech or Azure Text To Speech.
    """

    def __init__(self, commonvoice_filename=None):
        if commonvoice_filename:
            self.commonvoice = pd.read_csv(commonvoice_filename, sep='\t', header=0, quoting=3)
        pass

    def synthesize(self, text, voice_type, output_dir, file_name, rewrite=False):
        pass


class GoogleCommonVoice(CommonVoice):
    """
    GoogleCommonVoice
    """
    audio_encoding = {
        "LINEAR16": texttospeech.AudioEncoding.LINEAR16,
        "MP3": texttospeech.AudioEncoding.MP3,
        "OGG_OPUS": texttospeech.AudioEncoding.OGG_OPUS
    }

    def __init__(self, commonvoice_filename=None):
        self.client = texttospeech.TextToSpeechClient()
        super().__init__(commonvoice_filename)

    def list_voice_types(self):
        """
        List the supported voice types
        """
        voices = self.client.list_voices()
        print(voices)

    def synthesize(self, text, voice_type, output_dir, file_name, rewrite=False, audio_encoding="MP3",
                   random_pitch=False, random_pitch_minmax=5.0,
                   random_speed=False, random_speed_minmax=0.1):
        """
        Synthesizes speech from the input string of text.
        """
        path = Path(output_dir)/voice_type
        path.mkdir(parents=True, exist_ok=True)
        file = path / file_name
        if not rewrite and file.exists():
            logging.debug(f'{file} is ignored')
            return False

        input_text = texttospeech.SynthesisInput(text=text)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.VoiceSelectionParams({
            "language_code": '-'.join(voice_type.split('-')[:2]),
            "name": voice_type
        })

        if random_pitch:
            pitch = (2*random.random() - 1) * random_pitch_minmax
        else:
            pitch = 0.0
        if random_speed:
            speed = 1.0 + (2*random.random() - 1) * random_speed_minmax
        else:
            speed = 1.0
        audio_config = texttospeech.AudioConfig({
            "audio_encoding": GoogleCommonVoice.audio_encoding[audio_encoding],
            "pitch": pitch,
            "speaking_rate": speed
        })

        response = self.client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

        # The response's audio_content is binary.
        with open(path / file_name, "wb") as out:
            out.write(response.audio_content)
            logging.info(f'{file} created')
        return True

    def generate(self, voice_types, output_dir, rewrite=False,
                 sleep=False, sleep_time=0.1, audio_encoding="MP3",
                 random_pitch=False, random_pitch_minmax=5.0,
                 random_speed=False, random_speed_minmax=0.1,
                 start=0, end=-1):
        stats = {"number_of_chars": 0}
        start = min(max(0, start), len(self.commonvoice))
        if end == -1:
            end = len(self.commonvoice)
        else:
            end = min(max(0, end), len(self.commonvoice))
        for voice_type in voice_types:
            for i in range(start, end):
                row = self.commonvoice.iloc[i]
                stats["number_of_chars"] += len(row["sentence"])
                result = self.synthesize(row["sentence"], voice_type, output_dir, row["path"], rewrite=rewrite,
                                         random_pitch=random_pitch, random_pitch_minmax=random_pitch_minmax,
                                         random_speed=random_speed, random_speed_minmax=random_speed_minmax,
                                         audio_encoding=audio_encoding)
                if result and sleep:
                    time.sleep(sleep_time)
        return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--commonvoice_file", type=str, required=False,
                        help="Common Voice file, a tab separates value file contains client_id, path, sentence, etc..")
    parser.add_argument("-o", "--output_dir", type=str, required=False,
                        help="Output directory where the sound files will be stored")
    parser.add_argument("-l", "--list_voice_types", required=False, action='store_true',
                        help="List supported voice types")
    parser.add_argument("-v", "--voice_types", type=str, nargs='+', required=False,
                        help="List of voice types such as id-ID-Standard-A or id-ID-Wavenet-B")
    parser.add_argument("--audio_encoding", type=str, required=False, default="MP3",
                        help="The encoding determines the output audio format that we'd like. Following audio "
                             "encoding are supported: LINEAR16, MP3 and OGG_OPUS")
    parser.add_argument("--random_pitch", required=False, default=False, action='store_true',
                        help="Enable random pitch between -random_pitch_minmax to random_pitch_minmax")
    parser.add_argument("--random_pitch_minmax", type=float, required=False, default=5.0,
                        help="The value for random pitch")
    parser.add_argument("--random_speed", required=False, default=False, action='store_true',
                        help="Enable random speed between (1.0-random_speed_minmax) to (1+random_pitch_minmax)")
    parser.add_argument("--random_speed_minmax", type=float, required=False, default=0.1,
                        help="The value for random speed")
    parser.add_argument("-q", "--quite", required=False, action='store_true',
                        help="Disable info about a successful sound file creation")
    parser.add_argument("-d", "--debug", required=False, action='store_true',
                        help="Enable debug messages")
    parser.add_argument("-s", "--sleep", required=False, action='store_true',
                        help="Enable sleep in second between request")
    parser.add_argument("-t", "--sleep_time", type=float, required=False, default=0.1,
                        help="Sleep time in second between request")
    parser.add_argument("--start", type=int, required=False, default=0,
                        help="Which line will the request will start?")
    parser.add_argument("--end", type=int, required=False, default=-1,
                        help="Which line will the request will end?")
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.quite:
        logging.basicConfig(level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.INFO)
    if not args.list_voice_types and not (args.commonvoice_file and args.output_dir and args.voice_types):
        parser.print_help()
        exit(1)
    if args.list_voice_types:
        commonvoice = GoogleCommonVoice()
        commonvoice.list_voice_types()
    else:
        commonvoice = GoogleCommonVoice(args.commonvoice_file)
        stats = commonvoice.generate(args.voice_types, args.output_dir, sleep=args.sleep, sleep_time=args.sleep_time,
                             random_pitch=args.random_pitch, random_pitch_minmax=args.random_pitch_minmax,
                             random_speed=args.random_speed, random_speed_minmax=args.random_speed_minmax,
                             audio_encoding=args.audio_encoding, start=args.start, end=args.end)
        print(f'Synthesized characters: {stats["number_of_chars"]}')


if __name__ == "__main__":
    main()
