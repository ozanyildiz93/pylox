class Scanner(object):
    def __init__(self, source):
        self.source = source

    def scan_tokens(self):
        return []

    def error(self, line, message):
        self.report(line, "", message)

    def report(self, line, where, message):
        print("[line {line}] {where}: {message}".format(line=line,
                                                        where=where,
                                                        message=message))
