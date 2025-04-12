import aiohttp.http_exceptions
from random_user_agent.params import SoftwareName, OperatingSystem
import os, aiohttp, aiofiles, asyncio, platform, threading
from random_user_agent.user_agent import UserAgent
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse, urljoin
from asyncinit import asyncinit
from pyppeteer import launch


@asyncinit
class SourceClone:
    async def __init__(self, url: str, static: bool = None):
        if not url.startswith(("http://", "https://")):
            raise ValueError("Url must start with http:// or https://")

        self.url = url
        self.no_prefix_url = str(url).replace("https://", "").replace("http://", "").replace("/", "-") # works as our filepath also
        
        self.create_site_main_directory()

        self.inline_count = 0
        self.script_count = 0
        await self.save_main_source(self.no_prefix_url)
        await self.sort_js_scripts(self.no_prefix_url)
        print('done')
    
    def create_site_main_directory(self):
        return os.makedirs(
            os.path.join(
                "sources",
                str(self.url)
                .replace("https://", "")
                .replace("http://", "")
                .replace("/", "-"),
            ),
            exist_ok=True,
        )

    def random_user_agent(self) -> str:
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   

        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        return user_agent_rotator.get_random_user_agent()
        
    async def use_headless_browser(self, save: bool = None, path: str = None) -> bool:
        if save:
            browser = await launch({"headless": True})
            page = await browser.newPage()
            await page.goto(self.url)
            code = await page.content()
            async with aiofiles.open(f"sources/{path}/index.html", "w", encoding="utf-8") as index:
                await index.write(code)
            await browser.close()
            return True

        
    async def save_main_source(self, path) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                user_agent = self.random_user_agent()
                async with session.get(self.url, headers={ "User-Agent": user_agent }) as code:
                    code.raise_for_status()
                    code = await code.text()
                    async with aiofiles.open(f"sources/{path}/index.html", "w", encoding="utf-8") as index:
                        await index.write(code)
                    return code
        except (Exception, aiohttp.http_exceptions.HttpBadRequest) as e:
            print(f"err in saving the main .html : {e}")
            print("retrying...")
            return await self.use_headless_browser(save=True, path=path)
            
                    
            
    async def fetch(self, session, url):
        try:
            user_agent = self.random_user_agent()
            async with session.get(url, headers={ "User-Agent": user_agent }) as res:
                return await res.text()
        except Exception as e:
            print(f"Error fetching js file, {e}")
        return None
    

    def log_script_count(self):
        if platform.system() in ["Darwin", "Linux"]:
            os.system("clear")
        else:
            os.system("cls")
                            
        print(f"[✓] Stored {self.inline_count} inline scripts")
        print(f"[✓] Stored {self.script_count} scripts")
        
    async def sort_js_scripts(self, path):
        try:
            content = None
            async with aiofiles.open(f"sources/{path}/index.html", "r", encoding="utf-8") as index:
                content = await index.read()
            
            if content is None:
                raise ValueError("Could not detect .html file from code, terminating...")
                
            urls = []
            for js in BeautifulSoup(content, "html.parser", parse_only=SoupStrainer("script")):
                if js.has_attr("src"):
                    src = js["src"]
                    if src.startswith("http://") or src.startswith("https://"):
                        urls.append(src) # content from a full URL 
                    else:
                        #urls.append(self.url + src) # content from a relative path (/file/code.js)
                        urls.append(urljoin(self.url, src))
                else:
                    if not os.path.isdir(f"sources/{path}/inlines"):
                        os.mkdir(f"sources/{path}/inlines")
                    
                    async with aiofiles.open(f"sources/{path}/inlines/inline-file-{self.inline_count}.js", "w", encoding="utf-8") as inline:
                        self.inline_count += 1
                        await inline.write(str(js.text))
                        
                        self.log_script_count()
                    #print(js) # <script></script>
                            
            async with aiohttp.ClientSession() as session:
                tasks = [self.fetch(session, url) for url in urls]   
                scripts = await asyncio.gather(*tasks)
                
                assert len(scripts) == len(urls), "Index Mismatch between fetched scripts and URLs!"
                for url_idx, url in enumerate(urls):
                    filename = url.replace("https://", "").replace("http://", "").replace("/", "_").replace("?", "_").replace("&", "_") + ".js"
                    filepath = f"sources/{path}/{filename}"
                    async with aiofiles.open(filepath , "w",encoding="utf-8") as jsfile:
                        if scripts[url_idx] is not None:
                            await jsfile.write(scripts[url_idx])
                            self.script_count += 1
                            self.log_script_count()
                        else:
                            print(f"skipping url {url}, error occured")                       
        except Exception as e:
            print(f"Error sorting JavaScript scripts: {e}")
