# Website Colors

Analyze the history of colors of a websites from screenshots acquired from the
Internet Archive and plot the data using Datawrapper.

TODO: Add link to the Weekly Chart blog post

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

Example:

``` shell
export AUTH_TOKEN='<your datawrapper auth token>'
./website-colors \
    --url http://www.google.com/ \
    --date-interval 2006-02-01-2010-02-01 \
    --every-months 12
```

This will make a screenshot of <http://www.google.com/> from historic snapshots
archived by the Internet Archive every year on February 1 since 2006 until 2010.

Then it will analyze the colors of each of the screenshots and create a chart at
<https://app.datawrapper.de/>.

All intermediate data will be stored in the directory `data/`.

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
