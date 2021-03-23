import pandas as pd
from pathlib import Path
from google.cloud import texttospeech
import argparse
import logging

class CommonVoicer:
    """
    CommonVoicer is a Common Voice Generator using difference types of Speech Synthesizer such as
    Google Text To Speech or Azure Text To Speech.
    """

    def __init__(self, commonvoice_filename):
        self.commonvoice = pd.read_csv(commonvoice_filename, sep='\t', header=0)
        pass

    def synthesize(self, text, voice_type, output_dir, file_name, rewrite=False):
        pass


class GoogleCommonVoicer(CommonVoicer):
    """
    GoogleCommonVoicer
    """

    def __init__(self, commonvoice_filename):
        self.client = texttospeech.TextToSpeechClient()
        super().__init__(commonvoice_filename)

    def synthesize(self, text, voice_type, output_dir, file_name, rewrite=False):
        """
        Synthesizes speech from the input string of text.
        """
        path = Path(output_dir)/voice_type
        path.mkdir(parents=True, exist_ok=True)
        file = path / file_name
        if not rewrite and file.exists():
            return

        input_text = texttospeech.SynthesisInput(text=text)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.VoiceSelectionParams({
            "language_code": '-'.join(voice_type.split('-')[:2]),
            "name": voice_type
        })

        audio_config = texttospeech.AudioConfig({
            "audio_encoding": texttospeech.AudioEncoding.MP3
        })

        response = self.client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

        # The response's audio_content is binary.
        with open(path / file_name, "wb") as out:
            out.write(response.audio_content)
            logging.info(f'Audio content written to file {file_name}')

    def generate(self, voice_types, output_dir, rewrite=False):
        for voice_type in voice_types:
            for i, row in self.commonvoice.iterrows():
                self.synthesize(row["sentence"], voice_type, output_dir, row["path"], rewrite=rewrite)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--commonvoice_file", type=str, required=True,
                        help="Common Voice file, a tab separates value file contains client_id, path, sentence, etc..")
    parser.add_argument("-o", "--output_dir", type=str, required=True,
                        help="Output directory where the sound files will be stored")
    parser.add_argument("-v", "--voice_types", type=str, nargs='+', required=True,
                        help="List of voice types such as id-ID-Standard-A or id-ID-Wavenet-B")
    args = parser.parse_args()
    commonvoicer = GoogleCommonVoicer(args.commonvoice_file)
    commonvoicer.generate(args.voice_types, args.output_dir)


if __name__ == "__main__":
    main()
