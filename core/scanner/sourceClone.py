import os, aiohttp, aiofiles, asyncio, platform, threading, aiohttp.http_exceptions, pyppeteer, pyppeteer.errors, time
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
import tls_client, random, tls_client.exceptions
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse, urljoin
from pyppeteer_stealth import stealth
from asyncinit import asyncinit
from pyppeteer import launch


@asyncinit
class SourceClone:
    async def __init__(self, url: str, static: bool = None):
        if not url.startswith(("http://", "https://")):
            raise ValueError("Url must start with http:// or https://")

        self.url = url
        self.no_prefix_url = str(url).replace("https://", "").replace("http://", "").replace("/", "-") # works as our filepath also
        self.session = tls_client.Session(client_identifier="Chrome_120")
        self.create_site_main_directory()

        self.inline_count = 0
        self.script_count = 0
        self.user_agent = self.random_user_agent()
        
        await self.save_main_source(self.no_prefix_url)
        async with aiohttp.ClientSession() as s:
            await self.sort_js_scripts(self.no_prefix_url, session=s)

        print("done")
    
    def create_site_main_directory(self):
        # TODO : make this trim the filename length along with every other place its use, must be <250 characters
        return os.makedirs(
            os.path.join(
                "sources",
                self.no_prefix_url
            ),
            exist_ok=True,
        )

    def random_user_agent(self) -> str:
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value] 

        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        return user_agent_rotator.get_random_user_agent()
    
    async def use_tls_client(self, save: bool = None, path: str = None) -> bool:
        try:
            if save:
                code = await asyncio.to_thread(self.session.get, self.url,  headers={"User-Agent": self.user_agent})
                async with aiofiles.open(f"sources/{path}/index.html", "w", encoding="utf-8") as index:
                    await index.write(code.text)
        except (Exception, tls_client.exceptions.TLSClientExeption) as e:
            print(f"An error occured in tls-client: {e}")
        
    async def use_headless_browser(self, save: bool = None, path: str = None) -> bool:
        try:
            if save:
                browser = await launch({"headless": True})
                page = await browser.newPage()
                await stealth(page)

                res = await page.goto(self.url)
                code = await page.content()
                if res.status not in [307, 403] and "Just a moment..." not in code:
                    async with aiofiles.open(f"sources/{path}/index.html", "w", encoding="utf-8") as index:
                        await index.write(code)
                    return True
                else:
                    print("Cloudflare captcha detected, attempting to bypass...")
                    await self.use_tls_client(save=True, path=path)
                    return False
        except (pyppeteer.errors.TimeoutError, pyppeteer.errors.NetworkError) as e:
            print(f"Error in headless browser: {e}")
        finally:
            if browser:
                await browser.close()
        

        
    async def save_main_source(self, path) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                user_agent = self.user_agent
                async with session.get(self.url, headers={ "User-Agent": user_agent }) as code:
                    code.raise_for_status()
                    code = await code.text()
                    async with aiofiles.open(f"sources/{path}/index.html", "w", encoding="utf-8") as index:
                        await index.write(code)
                    return code
        except (Exception, aiohttp.http_exceptions.HttpBadRequest) as e:
            print(f"err in saving the main .html : {e}")
            print("retrying on secure headless browser...")
            return await self.use_headless_browser(save=True, path=path)
            
    async def fetch(self, session, url, max_filename_length: int = 250):
        try:
            user_agent = self.user_agent
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
        
    async def sort_js_scripts(self, path, session: aiohttp.ClientSession = None): # pass in a session at some point so that i dont have to call aiohttp.ClientSession()
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
            
            async with session:
                max_filename_length = 250
                tasks = [self.fetch(session, url) for url in urls]   
                scripts = await asyncio.gather(*tasks)
                
                assert len(scripts) == len(urls), "Index Mismatch between fetched scripts and URLs!"
                for url_idx, url in enumerate(urls):
                    # cleanup
                    filename = url.replace("https://", "").replace("http://", "").replace("/", "_").replace("?", "_").replace("&", "_")
                    if not filename.endswith(".js"):
                        filename += ".js"
                    
                    if len(filename) > max_filename_length:
                        filename = filename[:max_filename_length - 3] + ".js"
                    #end of cleanup
                    
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