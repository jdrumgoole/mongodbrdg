import threading
from datetime import datetime

import pymongo
from mongodbrdg.blockinserter import BlockInserter


#          locale="en",
#          idstart=1,
#          idend=10,
#          maxfriends=0,
#          startyear=2015,
#          endyear=2022,
#          seed=None):
#
# self._user = User(locale=locale,
#                   user_id_start=idstart,
#                   user_id_end=idend,
#                   max_friends=maxfriends,
#                   start_year=startyear,
#                   end_year=endyear,
#                   seed=seed)

class ThreadedInserter:

    def __init__(self,
                 c: pymongo.collection,
                 doc_generator,
                 thread_count=1,
                 user_count=4):

        self._thread_count = thread_count
        self._user_count = user_count
        self._threads = {}
        self._collection = c

        self._doc_generator = doc_generator
        self._thread_counter = 0
        self._start = None
        self._end = None

    @staticmethod
    def distribute(thread_count, user_count):
        """ Yield n successive chunks from l.
        """
        newn = int(user_count / thread_count)
        for i in range(0, user_count, thread_count):
            if (i+thread_count) > user_count:
                bound = user_count
            else:
                bound = i+thread_count
            yield i+1, bound
        #     i * newn + newn
        # yield thread_count * newn - newn
        #
        # # if thread_count < 1:
        #     raise ValueError("thread_count must be 1 or greater")
        # if user_count < 1:
        #     raise ValueError("user_count must be 1 or greater")
        #
        # subset = round(user_count / thread_count)
        # surplus = user_count % thread_count
        # segments = [(0, subset)]
        # for i in range(thread_count - 1):
        #     start = subset*i
        #     end = subset*(i+1) -1
        #     if i == thread_count - 1:
        #         segments.append((start, end+surplus))
        #     else:
        #         segments.append((start, end + surplus))
        # return segments

    @property
    def elapsed(self):
        return self._end - self._start

    def start(self, thread_count, user_count):
        self._start = datetime.utcnow()
        for start_id, end_id in self.distribute(thread_count, user_count):
            #print(f"start_id={start_id} end_id={end_id}")
            self._thread_counter = self._thread_counter + 1
            generator = self._doc_generator()
            inserter = BlockInserter(self._collection)
            self._threads[self._thread_counter] = threading.Thread(target=self.insert_func,
                                                                   args=[inserter, generator, start_id, end_id],
                                                                   daemon=True)
            self._threads[self._thread_counter].start()

    def stop(self):
        if self._thread_counter > 0 :
            for _, v in self._threads.items():
                v.join()
                self._thread_counter = self._thread_counter - 1
        self._end = datetime.utcnow()

    @staticmethod
    def insert_func(inserter, doc_generator, start_id, end_id):
        try:
            for user_doc_count, user in enumerate(doc_generator.make_docs(start_id, end_id), 1):
                #print(f"Adding user : {user['first_name']}")
                inserter.insert_one(user)
            inserter.flush()
        except pymongo.errors.BulkWriteError as e:
            print(f"Bulk Writer Error: {e}")

# tc=10
# uc=5
# print(f"Distribute {tc},{uc}")
# for i in ThreadedInserter.distribute(tc, uc):
#     print(i)
