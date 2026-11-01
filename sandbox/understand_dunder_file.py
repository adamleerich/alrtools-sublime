import os

# import sys
# import unittest

# sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main():
    drr = os.path.dirname(os.path.abspath(__file__))

    print("__file__ =                                    ", __file__)
    print("__name__ =                                    ", __name__)
    print("os.path.abspath(__file__) =                   ", os.path.abspath(__file__))
    print("os.path.dirname(os.path.abspath(__file__)) =  ", drr)
    

if __name__ == "__main__":
    main()
