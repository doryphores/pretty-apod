#!/usr/bin/env python
from django.core.management import execute_manager
import sys
import traceback

SETTINGS_ACTIVE_CONTENTS = "\033[1;32mfrom settings.local import *\033[1;33m"

try:
    from settings import active as settings
except ImportError, e:
    print '\033[1;33m'
    print "Apparently you don't have the file settings/active.py yet."
    print "Create it containing '%s'\033[0m" % SETTINGS_ACTIVE_CONTENTS
    print
    print "=" * 20
    print "original traceback:"
    print "=" * 20
    print
    traceback.print_exc(e)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
