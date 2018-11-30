from datasketch import MinHash, MinHashLSH
from tld import get_tld
from datetime import datetime,timedelta
import zipfile
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

class TingMo:

    def __init__(self,newly_registered_url='https://whoisds.com/newly-registered-domains/',n_days=1):

        self._download_domains(newly_registered_url,n_days)
        self.new_domains = self._read_clean_domains()
        self.brand_tlds = self.fetch_brand_tlds()
        self.lsh = self._train_LSH()

    # help from https://github.com/gfek/Hunting-New-Registered-Domains/blob/master/hnrd.py
    def _download_domains(self,url, n_days=1):

        # get table of dates with urls
        r = requests.get(url)
        soup = BeautifulSoup(r.text,features='lxml')
        table = soup.find('table')

        # convert to pd df and clean
        link_df = pd.read_html(str(table))[0]
        link_df = link_df.iloc[1:,]
        link_df.columns = ['date', 'count', 'creation_date', 'download_button']

        # extract hrefs for download
        links = re.findall('href=\"([^>]*)\"',str(table))
        link_df['url'] = links

        for i in range(min(n_days,link_df.shape[0])):

            # get date label
            d = datetime.now() - timedelta(days=i)
            d = d.strftime('%Y-%m-%d')

            if not os.path.isfile('./new_domains/' + d):
                nrd_zip = link_df.iloc[i,]['url']
                try:
                    resp = requests.get(nrd_zip, stream=True)

                    print("Downloading File {} - Size {}...".format(d + '.zip', resp.headers['Content-length']))
                    if resp.headers['Content-length']:
                        with open(d + ".zip", 'wb') as f:
                            for data in resp.iter_content(chunk_size=1024):
                                f.write(data)
                        try:
                            zip = zipfile.ZipFile(d + ".zip")
                            zip.extractall(path='new_domains/'+d,)
                        except:
                            print("File is not a zip file.")
                except:
                    print("File {}.zip does not exist on the remote server.".format(d))

    # read in newly registered domains, remove brand TLD domains
    def _read_clean_domains(self,n_days=1):

        domains = []

        for i in range(n_days):

            # get date label
            d = datetime.now() - timedelta(days=i)
            d = d.strftime('%Y-%m-%d')

            with open('new_domains/' + d + '/domain-names.txt') as f:
                domains += f.readlines()

        domains = [dom.strip().lower() for dom in domains]

        return domains

    # fetch brand TLDs
    def fetch_brand_tlds(self, tld_url = 'https://dotbrandobservatory.com/dashboard/dot-brand-dashboard/'):

        # read in table
        tld = requests.get(tld_url)
        tld = pd.read_html(tld.text)[0]
        tld.columns = ['tld', 'Contract', 'Country', 'Delegation', 'Domains',
                       'who_knows', 'Vertical/Industry', 'Websites']

        return [t.lower().strip() for t in tld['tld']]

    def _train_LSH(self):

        # create LSH model
        lsh = MinHashLSH(weights=(.5, .5))

        # train LSH model
        for dom in self.new_domains:

            # remove TLD
            tld_info = get_tld('http://'+dom, as_object=True, fail_silently=True)
            if tld_info is None:
                continue

            d = tld_info.domain

            # ignore super short new domains
            if len(d) <= 3:
                continue

            # create bigram set
            bigrams = [d[i:i+2] for i in range(len(d) - 1)]
            bigrams = set(bigrams)

            # create and update minhash obj
            m = MinHash()
            for b in bigrams:
                m.update(b.encode('utf-8'))

            lsh.insert(dom,m)

        print('LSH Trained!')
        return lsh

    def query_LSH(self, domain_list, exclude=False):

        matches = {}

        for domain in domain_list:

            print(domain)

            tld_info = get_tld(domain, as_object=True, fix_protocol=True)
            just_dom = tld_info.domain

            bigrams = set([just_dom[i:i+2] for i in range(len(just_dom) - 1)])

            m = MinHash()
            for b in bigrams:
                m.update(b.encode('utf-8'))

            match = self.lsh.query(m)

            if exclude:
                for item in match:
                    match = [i for i in item if get_tld(i) not in self.brand_tlds]

            # this part will remove matches with brand tlds later

            matches[just_dom] = match

        return matches


