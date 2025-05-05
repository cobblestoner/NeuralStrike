import jsbeautifier, aiofiles, os, asyncio
from asyncinit import asyncinit
from typing import Optional, List

@asyncinit
class beautify:
    async def __init__(self, url: str):
        self.options = jsbeautifier.default_options()
        self.path = str(url).replace("https://", "").replace("http://", "").replace("/", "-")
        
        self.final_filepath = os.path.join("sources", self.path) # must use this one over self.path
        self.inlines = os.path.join("sources", self.path, "inlines")
        await self.gather_and_beatify_files()

    async def gather_and_beatify_files(self) -> List[bool]:
        file_list = []


        for file in os.scandir(self.final_filepath):
            file_list.append(file.name)
            
        for file in os.scandir(self.inlines):
            file_list.append(
                os.path.join("inlines", file.name)
            )
        
            
        tasks = [self.finalize_beatification(fp=file) for file in file_list]

        return await asyncio.gather(*tasks)

    async def finalize_beatification(self, fp: str) -> Optional[bool]:
        use_path = os.path.join(self.final_filepath, fp)

        
        if os.path.isdir(use_path) or not use_path.endswith((".html", ".js")):
            return
        
        
        async with aiofiles.open(use_path, 'r', encoding="utf-8") as fcontent:
            file_content = await fcontent.read()
        
        async with aiofiles.open(use_path, 'w', encoding="utf-8") as file:
            await file.write(
                jsbeautifier.beautify(file_content, self.options)
            )
        return True