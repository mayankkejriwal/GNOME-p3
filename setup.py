from distutils.core import setup
import setuptools

setup(name='monopoly_simulator_test',
      version='0.0.6',
      description='USC/ISI monopoly simulator',
      author='Min-Hsueh Chiu',
      author_email='minhsueh@isi.edu',
      url = "https://github.com/mayankkejriwal/GNOME-p3/tree/phase3_simulator_v1",
      #packages=['monopoly'],
      #package_dir={'monopoly': 'monopoly/monopoly_simulator'},
      #package_data={'monopoly': ['./*.json']},
      python_requires="==3.7.6",
      packages=setuptools.find_packages(),
      data_files=[
            ('', ['monopoly_simulator/monopoly_game_schema_v1-2.json']),
            ('', ['monopoly_simulator/phase3_novelty_config.json'])
      ],
      include_package_data=True,
      install_requires=['numpy==1.18.4', 'xlsxwriter==1.2.8']
     )