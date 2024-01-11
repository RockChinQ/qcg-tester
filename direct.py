import os
import typing
import importlib
import asyncio

import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.StreamHandler()])


async def main():

    test_file = os.environ['TEST_FILE']

    module = importlib.import_module(test_file)

    classes = []

    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type):
            classes.append(obj)

    for cls in classes:
        print(cls.__name__)
        print(cls.__doc__)
        print()

        inst = cls()

        for name in dir(inst):
            if isinstance(getattr(inst, name), typing.Callable):
                if name.startswith('test_'):
                    print(name)
                    getattr(inst, name)()
                    print()

                    await getattr(inst, name)()


if __name__ == "__main__":
    asyncio.run(main())
