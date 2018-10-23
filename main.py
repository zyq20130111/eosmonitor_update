# -*- coding: utf-8 -*-
# filename: main.py
import threading
import time
import sys
from accountmgr.py import accountMgr

if __name__ == '__main__':

    accountMgr().Instance().Start()
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

