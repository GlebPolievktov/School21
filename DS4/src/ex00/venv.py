#!/usr/bin/env python3
import os

if __name__ == "__main__":
    fullstring = "Your current virtual env is " + os.environ.get("VIRTUAL_ENV")
    print(fullstring)
