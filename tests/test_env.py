from collections import OrderedDict
from textwrap import dedent

from testfixtures import compare, OutputCapture

from picky.env import Environment, PackageSpec, modify, diff

sample_serialized = """\
name: package
channels:
- conda-forge
- defaults
dependencies:
- ca-certificates=2018.03.07=0
- certifi=2018.1.18=py36_0
- libcxx=4.0.1=h579ed51_0
- pip:
  - alabaster==0.7.10
  - attrs==17.4.0
  - urllib3==1.22
  - -e .
"""

sample_export = sample_serialized + """\
prefix: /Users/chris/anaconda2/envs/picky-conda
"""


sample_env = Environment({
    'name': 'package',
    'channels': ['conda-forge', 'defaults'],
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
    'develop': OrderedDict([
        ('.', PackageSpec(' ', '-e', '.', None)),
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


class TestFilter(object):

    def test_pass_through(self):
        compare(modify(sample_env), expected=sample_env)

    def test_ignore(self):
        compare(modify(sample_env, ignore={'ca-certificates', 'attrs'}),
                expected=Environment({
                    'name': 'package',
                    'channels': ['conda-forge', 'defaults'],
                    'conda': OrderedDict([
                        ('certifi', PackageSpec('=', 'certifi', '2018.1.18', 'py36_0')),
                        ('libcxx', PackageSpec('=', 'libcxx', '4.0.1', 'h579ed51_0')),
                    ]),
                    'pip': OrderedDict([
                        ('alabaster', PackageSpec('==', 'alabaster', '0.7.10', None)),
                        ('urllib3', PackageSpec('==', 'urllib3', '1.22', None)),
                    ]),
                    'develop': OrderedDict([
                        ('.', PackageSpec(' ', '-e', '.', None)),
                    ]),
                }))

    def test_develop(self):
        compare(modify(sample_env, develop={'attrs': '.'}),
                expected=Environment({
                    'name': 'package',
                    'channels': ['conda-forge', 'defaults'],
                    'conda': OrderedDict([
                        ('ca-certificates', PackageSpec('=', 'ca-certificates', '2018.03.07', '0')),
                        ('certifi', PackageSpec('=', 'certifi', '2018.1.18', 'py36_0')),
                        ('libcxx', PackageSpec('=', 'libcxx', '4.0.1', 'h579ed51_0')),
                    ]),
                    'pip': OrderedDict([
                        ('alabaster', PackageSpec('==', 'alabaster', '0.7.10', None)),
                        ('urllib3', PackageSpec('==', 'urllib3', '1.22', None)),
                    ]),
                    'develop': OrderedDict([
                        ('.', PackageSpec(' ', '-e', '.', None)),
                    ]),
                }))


class TestDiff(object):

    def test_same(self):
        with OutputCapture() as output:
            result = diff(sample_env, sample_env)
        assert result == 0
        output.compare('')

    def test_name_different(self):
        other_env = sample_env.copy()
        other_env['name'] = 'other'
        with OutputCapture() as output:
            result = diff(sample_env, other_env)
        assert result == 0
        output.compare('')

    def test_channel_order_different(self):
        other_env = sample_env.copy()
        other_env['channels'].reverse()
        with OutputCapture() as output:
            result = diff(sample_env, other_env)
        assert result == 0
        output.compare('')

    def test_others_different(self):
        other_env = Environment({
            'name': 'package',
            'channels': ['conda-forge'],
            'conda': OrderedDict([
                ('ca-certificates', PackageSpec('=', 'ca-certificates', '2018.03.07', '0')),
                ('libcxx', PackageSpec('=', 'libcxx', '4.0.1', 'h579ed51_0')),
            ]),
            'pip': OrderedDict([
                ('alabaster', PackageSpec('==', 'alabaster', '0.7.10', None)),
                ('urllib3', PackageSpec('==', 'urllib3', '1.22', None)),
            ]),
            'develop': OrderedDict(),
        })
        with OutputCapture() as output:
            result = diff(sample_env, other_env)
        assert result == 1
        output.compare(dedent("""\
            Expected environment does not match actual:
            --- expected
            +++ actual
            @@ -1,13 +1,9 @@
             channels:
             - conda-forge
            -- defaults
             dependencies:
             - ca-certificates=2018.03.07=0
            -- certifi=2018.1.18=py36_0
             - libcxx=4.0.1=h579ed51_0
             - pip:
               - alabaster==0.7.10
            -  - attrs==17.4.0
               - urllib3==1.22
            -  - -e .
            """))
