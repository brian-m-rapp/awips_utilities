import os
import sys
import argparse
import json
import tarfile
import time

tarname = os.path.expanduser('~/tarredjars_{}.tgz'.format(time.strftime('%Y%m%d_%H%M%S', time.gmtime())))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a tarball containing files listed in the passed file.')
    parser.add_argument('jarsfile', help='Path to file containing json-encoded array of jar files to be archived')

    cargs = parser.parse_args()

    try:
        with open(os.path.expanduser(cargs.jarsfile), 'r') as ifp:
            content = ifp.read()
    except Exception as e:
        print('Exception {} reading from input file'.format(e))
        sys.exit(1)

    try:
        filesList = json.loads(content)
    except Exception as e:
        print('Exception {} parsing list of files from {}'.format(e, cargs.jarsfile))
        sys.exit(1)

    try:
        with tarfile.open(tarname, 'w:gz') as tarball:
            for f in filesList:
                tarball.add(f)
    except Exception as e:
        print('Exception {} creating tarball file {}'.format(e, tarname))
        sys.exit(1)

    print('Wrote tarball to {}'.format(tarname))
