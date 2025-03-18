import argparse, os, sys, asyncio
from util.args import Arguments
from sourceClone import SourceClone


"""
make site grab source code from page on entered in the command line
grab the frameworks/libs it uses such as angular, jquery, etc
use regex to find vulnerable keywords based off framework, etc, innerHTML, document.write, eval, setTimeout, setInterval, other jquery, react, angular and frameworm native keywords
return outputted code and determine the danger.

later updates:
match returned outputted code with the html in the index so we know where to attack
"""

class Main:
    @staticmethod
    async def initialize():
        await SourceClone(Arguments.url)


init = Main()
asyncio.run(init.initialize())