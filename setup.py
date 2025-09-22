from setuptools import setup

APP = ['main.py']
DATA_FILES = ['icon.png']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.png',
    'packages': [
        'sklearn',
        'numpy',
        'PIL',
        'pillow'
    ],
    'includes': [
        'sklearn.cluster._kmeans_lloyd',
        'sklearn.cluster._kmeans_elkan',
        'sklearn.metrics._pairwise_distances_reduction._middle_term_computer',
        'sklearn.metrics._pairwise_distances_reduction._datasets_pair',
        'sklearn.metrics._pairwise_distances_reduction._base',
        'sklearn.utils._openmp_helpers',
        'sklearn.utils._random',
        'sklearn.utils._heap',
        'sklearn.utils._seq_dataset',
        'sklearn.utils._weight_vector',
        'PIL._imaging',
        'PIL.JpegImagePlugin',
        'PIL.PngImagePlugin',
        'PIL.TiffImagePlugin'
    ],
    'resources': ['icon.png']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    name="Glow Engine Colorizer Utility",
)
