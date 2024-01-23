# ubergraph2asct [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10551712.svg)](https://doi.org/10.5281/zenodo.10551712)


This lib takes a list of seed terms and a list of properties and generates a simpler version of the ASCT+B table. In this case, there are only the AS and CT columns.

Run:

```bash
python3 ubergraph2asct.py --input <seed file> --property <property file> --output <output file path>
```

You can check example of each file in the `test` folder. Using these files, the command would be:

```bash
python3 ubergraph2asct --input test/eye-seed.txt --property -- test/properties.txt --output eye-asct.csv
```
