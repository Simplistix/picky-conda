from collections import OrderedDict

from testfixtures import compare

from picky.env import Environment, PackageSpec

sample_serialized = """\
name: package
channels:
- defaults
- conda-forge
dependencies:
- ca-certificates=2018.03.07=0
- certifi=2018.1.18=py36_0
- libcxx=4.0.1=h579ed51_0
- pip:
  - alabaster==0.7.10
  - attrs==17.4.0
  - urllib3==1.22
"""

sample_export = sample_serialized + """\
prefix: /Users/chris/anaconda2/envs/picky-conda
"""



sample_env = Environment({
    'name': 'package',
    'channels': ['defaults', 'conda-forge'],
    'conda': OrderedDict([
        ('ca-certificates', PackageSpec('=', 'ca-certificates', '2018.03.07', '0')),
        ('certifi', PackageSpec('=', 'certifi', '2018.1.18', 'py36_0')),
        ('libcxx', PackageSpec('=', 'libcxx', '4.0.1', 'h579ed51_0')),
    ]),
    'pip': OrderedDict([
        ('alabaster', PackageSpec('==', 'alabaster', '0.7.10', None)),
        ('attrs', PackageSpec('==', 'attrs', '17.4.0', None)),
        ('urllib3', PackageSpec('==', 'urllib3', '1.22', None)),
    ]),
})


class TestEnvironment(object):

    def test_from_string(self):
        compare(Environment.from_string(sample_export),
                strict=True,
                expected=sample_env)

    def test_from_file(self, tmpdir):
        p = tmpdir.join("environment.yaml")
        p.write(sample_export)
        compare(Environment.from_path(str(p)),
                strict=True,
                expected=sample_env)

    def test_to_string(self):
        compare(sample_env.to_string(),
                expected=sample_serialized)

    def test_to_string_miminal(self):
        env = Environment({
            'name': 'test',
            'channels': ['defaults'],
            'conda': OrderedDict([('python', PackageSpec('=', 'python'))]),
        })
        compare(env.to_string(),
                expected=(
                    'name: test\n'
                    'channels:\n'
                    '- defaults\n'
                    'dependencies:\n'
                    '- python\n'
                ))

    def test_round_trip(self):
        compare(Environment.from_string(sample_serialized).to_string(),
                strict=True,
                expected=sample_serialized)
