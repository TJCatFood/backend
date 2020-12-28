from enum import Enum
from queue import Queue
import uuid


class RoomStatus(Enum):

    WAIT = 1
    READY = 2
    START = 3


class Room():

    def __init__(self, user_id, total_count, contest_id):
        self.user_id_list = [user_id]
        self.channel_id = uuid.uuid4().hex
        self.total_count = total_count
        self.cur_count = 1
        self.ready_count = 0
        self.ready_list = [False] * total_count
        self.status = RoomStatus.WAIT
        self.contest_id = contest_id
        self.submit_count = 0
        self.submit_list = [False] * total_count

    def user_submit(self, user_id):
        try:
            index = self.user_id_list.index(user_id)
        except ValueError:
            print('user not found!')
            return None
        else:
            if self.submit_list[index]:
                return -1
            self.submit_list[index] = True
            self.submit_count += 1
            return index

    def add_user(self, user_id):
        self.user_id_list.append(user_id)
        self.cur_count += 1

    def bis_end(self):
        return self.submit_count == self.total_count

    def bis_empty(self):
        return self.cur_count == 0

    def bis_full(self):
        return self.cur_count == self.total_count

    def delete_user(self, user_id):
        self.cur_count -= 1
        return self.user_id_list.remove(user_id)

    def delete_user_index(self, index):
        if(index >= self.total_count):
            return
        self.cur_count -= 1
        user = self.user_id_list[index]
        del self.user_id_list[index]
        return user

    def user_ready(self, user_id):
        try:
            index = self.user_id_list.index(user_id)
        except ValueError:
            print('user not found!')
            return None
        else:
            if self.ready_list[index]:
                return -1
            self.ready_list[index] = True
            self.ready_count += 1
            return user_id

    def clear_ready(self):
        for index in range(len(self.ready_list)):
            self.ready_list[index] = False
        self.ready_count = 0

    def bis_all_ready(self):
        return self.ready_count == self.total_count

    def set_status(self, status):
        self.status = status

    def get_user_index(self, user_id):
        try:
            index = self.user_id_list.index(user_id)
        except ValueError:
            return -1
        else:
            return index


class ContestRooms:

    def __init__(self):
        self.start_rooms = []
        self.wait_rooms = Queue()
