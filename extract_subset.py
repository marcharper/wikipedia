import sys

# def remove_siteinfo(filename):
#      handle = open(filename)
#      deleting = False
#      for line in handle:
#          if line.startswith('  <siteinfo>'):
#              deleting = True
#          if not deleting:
#              print(line, end='')
#          if line.startswith('  </siteinfo>'):
#              deleting = False

def extract_pages(filename, count=100):
    handle = open(filename)
    outfile = open("extracted.xml", 'w')
    extract_count = 0
    in_page = False
    print("<mediawiki>", file=outfile)
    for line in handle:
        if line.startswith('  <page>'):
            in_page = True
        if in_page:
            print(line, end='', file=outfile)
        if line.startswith('  </page>'):
            extract_count += 1
            if extract_count == count:
                break
            in_page = False
    print("</mediawiki>", file=outfile)


if __name__ == "__main__":
    filename = sys.argv[1]
    # remove_siteinfo(filename)
    extract_pages(filename)