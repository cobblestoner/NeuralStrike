import argparse

class Arguments:
    parser = argparse.ArgumentParser(description="NeuralStrike XSS Hunter")
    parser.add_argument("--website", help="add the domain in which you want to search for vulnerabilities", required=True)
    parser.add_argument("--type", help="choose if you want dom based xss, reflected, or stored")
    parser.add_argument("--flush", help="")
    parser.add_argument("--headers", help="Add an specific headers for authentication html pages, etc",required=False)
    parser.add_argument("--crawler", help="for url crawler to find xss")
    parser.add_argument("--scraler", help="stored xss crawler")
    opts = parser.parse_args()
    url = opts.website



