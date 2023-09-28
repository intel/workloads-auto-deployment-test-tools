#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
import logging
from logging.handlers import RotatingFileHandler

class LogHandler():
    def __init__(self, job_id) -> None:
        self.job_id = job_id
    
    def sendlog(self, log_txt):
        fileH = RotatingFileHandler(f'workspace/local/logs/{self.job_id}_provision.log','a',5*1024*1024, backupCount=1)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        fileH.setFormatter(formatter)
        log = logging.getLogger(__file__) 
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fileH)  
        log.setLevel(logging.INFO)
        log.info(log_txt)

                        