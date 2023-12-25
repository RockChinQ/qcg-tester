import abc


class AbsPlatformMock(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def run(self) -> int:
        pass

    @abc.abstractmethod
    async def send_friend_message(self, msg: dict):
        pass

    @abc.abstractmethod
    async def send_group_message(self, msg: dict):
        pass

    @abc.abstractmethod
    async def send_stranger_message(self, msg: dict):
        pass
