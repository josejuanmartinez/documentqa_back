import getopt
import sys

import keyring

SERVICE_ID = "sintentic_qa"
USAGE = 'add_key.py -e <email> -p <password>'


def main(argv):
    opts, args = getopt.getopt(argv, "he:p:", [])
    email = None
    password = None
    for opt, arg in opts:
        if opt == '-h':
            print(USAGE)
            sys.exit()
        elif opt == "-e":
            email = arg
        elif opt == "-p":
            password = arg
    if email is not None and password is not None:
        keyring.set_password(SERVICE_ID, email, password)
    else:
        print(USAGE)
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])




