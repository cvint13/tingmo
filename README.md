# TingMo

```
       __
      / \`\          __
      |  \ `\      /`/ \
      \_/`\  \-"-/` /\  \
           |       |  \  |
           (d     b)   \_/
           /       \
       ,".|.'.\_/.'.|.",
      /   /\' _|_ '/\   \
      |  /  '-`"`-'  \  |
      | |             | |
      | \    \   /    / |
       \ \    \ /    / /
        `"`\   :   /'"`
            `""`""`

```

## The copycat domain detector

### How it works

TingMo utilizes the Minhash LSH model as implemented in [datasketch](https://ekzhu.github.io/datasketch/lsh.html)
to identify copycat domains in sublinear runtime. The code takes the set
of unique bigrams from the input domains and queries to model to identify
similar newly registered domains, as provided by [whoisds](https://whoisds.com/newly-registered-domains). 
It also has the built-in capability of ignoring matches with newly registered domains 
that have a [brand TLD](https://dotbrandobservatory.com/dashboard/dot-brand-dashboard/), 
as those are generally benign.

### Usage

```bash
git clone https://github.com/cvint13/tingmo.git
pip install -r requirements.txt
python train_lsh.py
python app.py

``` 

![screenshot](screenshot.png =300x)

### Future Directions

This app will be hosted on Heroku shortly, hence the Procfile.

File upload/download option.