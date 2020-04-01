# Website Colors

Analyze colors of websites.

## Installation

### Mac

``` shell
$ brew install python geckodriver
$ pip install pipenv
$ make setup
```

### Arch Linux

``` shell
# pacman -S pipenv geckodriver
$ make setup
```

### Other systems

Install these dependencies manually:

- Python >= 3.7
- pipenv
- geckodriver

Then run:

``` shell
$ make setup
```

## Usage

See the help for all command line options:

``` shell
./website-colors --help
```

## Development

### Installation

``` shell
make setup-dev
```

### Testing and linting

``` shell
make test
make lint
```

### Help

``` shell
make help
```

## Contributing

__Feel free to remix this project__ under the terms of the [Apache License,
Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
