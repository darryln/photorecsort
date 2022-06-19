
#!/usr/bin/python

from defaults import *
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings, QVariant

# list(str, str, QVariant) 
configItems = [
    # group      #key    #value
    ('General', 'nRuns', '0')
]

log = logging.getLogger(__name__)

def ConfigCheck():
    print(f"Python version {sys.version}")
    QApplication.setApplicationName(DEFAULT_APP_NAME)
    QApplication.setOrganizationName(DEFAULT_ORG_NAME)
    QApplication.setOrganizationDomain(DEFAULT_ORG_DOMAIN)
    settings = QSettings()
    print(settings.fileName())
    nRuns = 0
    if not settings.contains('nRuns'):
        settings.setValue('nRuns', nRuns)
        # TODO: foreach config item, call QSettings.setValue(item default value)
    nRuns = int(settings.value('nRuns')) + 1
    settings.setValue('nRuns', nRuns)
    log.info(f"# program runs = {nRuns}")

