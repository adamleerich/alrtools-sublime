# alrtools-sublime

A small personal Sublime Text 4 package. For now it does one thing: re-format
GitHub Flavored Markdown (GFM) pipe tables so the columns line up.

```markdown
| Name | Age | Notes |
|---|--:|:-:|
| Alice | 21 | likes tea |
| Bob | 105 | x |
```

becomes

```markdown
| Name  | Age |   Notes   |
| ----- | --: | :-------: |
| Alice |  21 | likes tea |
| Bob   | 105 |     x     |
```

## Install

Clone or copy this folder into your Sublime Text `Packages` directory
(*Preferences → Browse Packages…*) as `alrtools-sublime`.
The restart Sublime Text.

```bat
cd "%appdata%\Sublime Text\Packages"
git clone https://github.com/adamleerich/alrtools-sublime.git
```


## Use

Put the cursor anywhere in a table and press **Ctrl+Alt+F** in a Markdown
file, or run **alrtools: Format Markdown Table** from the Command
Palette. Every cursor is handled, and each cursor stays in the same cell.

To change the key, use *Preferences → Package Settings → alrtools →
Key Bindings*.

## Behavior

- Columns are padded to the widest cell (minimum width 3).
- `:--`, `:-:` and `--:` in the delimiter row set left / center / right
  alignment and are preserved.
- Columns without a marker are right-aligned when every non-empty body cell
  is a number (`12`, `-3.5`, `1,234`, `5%`, `1e6`), otherwise left-aligned.
- The header row is centered.
- Short rows are padded with empty cells.
- East Asian wide characters count as two columns, combining marks as zero.
- Row count never changes; indentation is kept.

Limitations: a table row must start with `|`, pipes inside a cell must be
escaped as `\|`, and other table dialects (Pandoc grid tables, MultiMarkdown
column spans, etc.) are not supported.

## Settings

`alrtools-sublime.sublime-settings`:

| Setting               | Default | Meaning                                         |
| --------------------- | :-----: | ----------------------------------------------- |
| `align_numbers_right` |  true   | Right-align all-numeric columns without a marker |
| `center_header`       |  true   | Center the header row                           |

## Tests

The formatter is plain Python and needs no Sublime Text:

```
python -m unittest discover -s tests -v
```

## Credits and license

This package is derived from
[SublimeTableEditor](https://github.com/vkocubinsky/SublimeTableEditor) by
**Valery Kocubinsky** and contributors, whose work this builds on. The
original is no longer maintained; this version keeps only the Markdown table
formatting.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) and
[NOTICE](NOTICE).
