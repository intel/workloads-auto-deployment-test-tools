class Log:
    def __init__(self, flush=0, log_path='default.log'):

        self.log_path = log_path
        self.flush = flush

    def write(self, message, level):
        message = "Time: %s %s:\n%s\n" % (time.asctime(
            time.localtime(time.time())), level, message)
        if self.flush == 1:
            print(message)
        elif self.flush == 2:
            with open(self.log_path, 'at') as log:
                log.write(message)
        elif self.flush == 3:
            print(message)
            with open(self.log_path, 'at') as log:
                log.write(message)

    def debug(self, message):
        self.write(message, 'DEBUG')

    def info(self, message):
        self.write(message, 'INFO')

    def warning(self, message):
        self.write(message, 'WARNING')

    def error(self, message):
        self.write(message, 'ERROR')

    def critical(self, message):
        self.write(message, 'CRITIAL')

    def clean_log(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
