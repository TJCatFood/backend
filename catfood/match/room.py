from enum import Enum
from queue import Queue
import uuid

class RoomStatus(Enum):

    WAIT = 1
    READY = 2
    START = 3


class Room():
    
    def __init__(self, user_id, total_count):
        self.user_id_list = [user_id]
        self.channel_id = uuid.uuid4().int & (1 << 64) - 1
        self.total_count = total_count
        self.cur_count = 1
        self.ready_count = 0
        self.ready_list = [False] * total_count
        self.status = RoomStatus.WAIT
        

    def add_user(self, user_id):
        self.user_id_list.append(user_id)
        self.cur_count += 1

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
        del self.user_id_list[index]

    def user_ready(self, user_id):
        try:
            index = self.user_id_list.index(user_id)
        except:
            print('user not found!')
            return None
        else:
            self.ready_list[index] = true
            self.ready_count += 1

    def clear_ready(self):
        for item in self.ready_list:
            item = False
        self.ready_count = 0

    def bis_all_ready(self):
        return self.ready_count == self.total_count

    def set_status(self, status):
        self.status = status


class ContestRooms:

    def __init__(self):
        self.start_rooms = []
        self.wait_rooms = Queue()
