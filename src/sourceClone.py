import os, aiohttp, aiofiles, asyncio
from urllib.parse import urlparse, urljoin
from asyncinit import asyncinit
from bs4 import BeautifulSoup, SoupStrainer


@asyncinit
class SourceClone:
    async def __init__(self, url):
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        
        self.url = url
        self.no_prefix_url = str(url).replace("https://", "").replace("http://", "").replace("/", "-")
        
        self.create_site_main_directory()

        await self.save_main_source(self.no_prefix_url)
        await self.sort_js_scripts(self.no_prefix_url)
    
    def create_site_main_directory(self):    
        return os.makedirs(
            os.path.join("sources", str(self.url).replace("https://", "").replace("http://", "").replace("/", "-")),
            exist_ok=True
        )
        
    async def save_main_source(self, path) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as code:
                try:
                    code.raise_for_status()
                    code = await code.text()
                    async with aiofiles.open(f"sources/{path}/index.html", "w", encoding="utf-8") as index:
                        await index.write(code)
                    return code
                except Exception as e:
                    print(f"An error occured in saving the main .html : {e}")
            
    async def fetch(self, session, url):
        try:
            async with session.get(url) as res:
                return await res.text()
        except Exception as e:
            print(f"Error fetching js file, {e}")
        return None
    
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
                    print(js) # <script></script>

                            
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
                        else:
                            print(f"skipping url {url}, error occured")                       
        except Exception as e:
            print(f"Error sorting JavaScript scripts: {e}")
