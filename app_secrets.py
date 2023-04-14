import logging
import os


class Secrets:
    def __init__(self):
        pass

    @staticmethod
    def check():
        required = [
            ('OPENAI_API_KEY', 'OpenAI API KEY'),
            ('KEYRING_SECRET_KEY', 'Any secret keyword or words to be used to encode your user information in keyring')]

        errors = []
        for r in required:
            if r[0] not in os.environ:
                errors.append(r)
        if len(errors) == 0:
            return True
        else:
            msg = ["You need to configure in Docker (or in the OS environment directly) the following keys:"]
            for e in errors:
                msg.append(f"{e[0]}: {e[1]}")
            logging.error("\n".join(msg))
            return False
