"""
Audit every Empire Builder build against the installed game files.

This is a command-line wrapper around advisor.validate (the same checker the app
uses to show its "Verified usable" badge). Run it after a patch or new DLC:

    python audit_builds.py
"""

from advisor.builds import BUILDS
from advisor.validate import validate_build, _catalogs


def main():
    if not _catalogs()['install']:
        print('Stellaris install not found — cannot audit.')
        return
    total = 0
    for b in BUILDS:
        result = validate_build(b)
        if not result['verified']:
            total += len(result['issues'])
            print(f'\n### {b["name"]}  [{b["authority"]}]')
            for issue in result['issues']:
                print('   - ' + issue)
    print(f'\n{"=" * 50}\nTotal issues: {total} across {len(BUILDS)} builds')


if __name__ == '__main__':
    main()
