import getopt
import sys

import keyring

SERVICE_ID = "sintentic_qa"


def main(argv):
    opts, args = getopt.getopt(argv, "he:p:", ["email=", "password="])
    email = None
    password = None
    for opt, arg in opts:
        if opt == '-h':
            print('add_key.py -e <email> -p <password>')
            sys.exit()
        elif opt in ("-e", "--email"):
            email = arg
        elif opt in ("-p", "--password"):
            password = arg
    if email is not None and password is not None:
        keyring.set_password(SERVICE_ID, email, password)
    else:
        print('add_key.py -e <email> -p <password>')
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])




