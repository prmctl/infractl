
import tempfile
from pathlib import Path
import yaml
import generate_nav

def main():
    generate_nav.main()
    nav = yaml.safe_load(Path('mkdocs.generated.yml').read_text())['nav']
    assert [next(iter(x)) for x in nav] == ['Home', 'Common Commands', 'Laboratories', 'Templates']
    for key, folder in [('Common Commands','commands'), ('Laboratories','laboratories'), ('Templates','templates')]:
        section = next(x[key] for x in nav if key in x)
        assert section[0] == f'{folder}/index.md'
    print('Navigation checks passed')
if __name__ == '__main__': main()
