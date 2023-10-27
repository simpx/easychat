from setuptools import setup, find_packages

setup(
    name='easychat',
    version='0.1.1',
    packages=find_packages(),
    url='https://github.com/simpx/easychat',
    license='MIT',
    author='simpx',
    author_email='simpxx@gmail.com',
    description='A simple chatbot framework',
    install_requires=[
        'Flask', 
		'pycryptodome',
		'PyYAML'
    ],
    classifiers=[
        # 选择合适的分类器
        'Development Status :: 3 - Alpha',  # 或其他状态
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
