import argparse, os, sys, asyncio, json, time
from wappalyzer import analyze
from core.args import Arguments
from core.scanner.sourceClone import SourceClone
from core.Formatter.formatter import beautify


"""
make site grab source code from page on entered in the command line
grab the frameworks/libs it uses such as angular, jquery, etc
use AST'S to find vulnerable keywords based off framework, etc, innerHTML, document.write, eval, setTimeout, setInterval, other jquery, react, angular and frameworm native keywords
return outputted code and determine the danger.

later updates:
match returned outputted code with the html in the index so we know where to attack
"""

class Main:
    @staticmethod
    async def initialize():
        #results = analyze(Arguments.url)
        start_time = time.time()
        
        await SourceClone(Arguments.url, ...) # damn we gotta add if statements and shi for args.py
        print(f"Took: {time.time() - start_time}")
        print("Beginning File beautification...")
        await beautify(Arguments.url)

init = Main()
asyncio.run(init.initialize())