# Athene

About
-----
Machine learning experiments with pysc2 and Starcraft 2 in the name of the Greek goddess of
wisdom, strategy and organized war.

Build requirements
------------------
1. Install Python 3 (Tested on Python 3.7).
2. Install [pipenv](https://github.com/pypa/pipenv).

Build instructions
------------------

```bash
# Install required dependencies.
$ pipenv install --dev

# Activale virtual environment.
$ pipenv shell

# Run any learning agent, e.g.
$ python -m pysc2.bin.agent --map CollectMineralsAndGas --agent athene.minigames.collect_minerals_and_gas.Agent

# See more info in the corresponding agent.py file.
```

License
-------

Copyright (c) 2018

Licensed under the [MIT license](LICENSE).
