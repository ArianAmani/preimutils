from setuptools import setup
import os


setup(
    name="preimutils",
    packages=['preimutils'],
    version='1.0.5',
    description="all you need to prepare and preprocess your annotated images",
    url="https://github.com/mrl-amrl/preimutils",
    download_url='https://github.com/mrl-amrl/preimutils/archive/1.0.5.tar.gz',
    author="Amir Sharifi",
    author_email="ami_rsh@outlook.com",
    license='MIT',
    keywords=['computer vision', 'image processing', 'opencv',
              'matplotlib', 'preprocess image', 'image dataset', 'voc'],
    entry_points={
        'console_scripts': ['preimutils=preimutils.object_detection.run:main'],
    },
    install_requires=[
        'pascal_voc_writer',
        'tqdm',
        'pandas',
        'albumentations',
        'imutils','cv2',
        'imageio'
    ],
    zip_safe=False,
)
