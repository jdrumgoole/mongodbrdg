
class DataGenerator:

    def __init__(self):
        pass

    def make_doc(self)->dict:
        return {}

    def make_docs(self, count=None):
        if count is None:
            while True:
                yield self.make_doc()
        else:
            for _ in range(count):
                yield self.make_doc()

