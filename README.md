# ubergraph2asct

This repository takes the output `.nt` from [ccf-rdf-writer](https://github.com/hubmapconsortium/ccf-rdf-writer) and generates a simpler version of the ASCT+B table. In this case, there are only the AS and CT parts.

Run:

```bash
python3 ubergraph2asct.py <input file path> <output file path>
```

The input file is the `.nt` file, and the output file is where the ASCT+B table will be saved.