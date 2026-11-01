# alrtools-sublime


## Credits and license

This package is derived from
[SublimeTableEditor](https://github.com/vkocubinsky/SublimeTableEditor) by
**Valery Kocubinsky** and contributors, whose work this builds on. The
original is no longer maintained; this version keeps only the Markdown table
formatting.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) and
[NOTICE](NOTICE).



## Intro

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

|        Setting        | Default |                     Meaning                      |
| --------------------- | :-----: | ------------------------------------------------ |
| `align_numbers_right` |  true   | Right-align all-numeric columns without a marker |
| `center_header`       |  true   | Center the header row                            |

## Tests

The formatter is plain Python and needs no Sublime Text:

```bat
python -m unittest discover -s tests -v
```



## Markdown Table Types


### [Pipe Tables](https://pandoc.org/MANUAL.html#extension-pipe_tables)

Standard for GitHub-flavored markdown -- examples above are all pipe tables.



### [Simple Tables](https://pandoc.org/MANUAL.html#extension-simple_tables)

```markdown
  Right     Left     Center     Default
-------     ------ ----------   -------
     12     12        12            12
    123     123       123          123
      1     1          1             1
-------     ------ ----------   -------

Table: simple
```

```markdown
  Right     Left     Center     Default
-------     ------ ----------   -------
     12     12        12            12
    123     123       123          123
      1     1          1             1

Table: tail-less simple
```

```markdown
-------     ------ ----------   -------
     12     12        12             12
    123     123       123           123
      1     1          1              1
-------     ------ ----------   -------

Table: headless simple
```

Rules:

* The table must end with a blank line, or a line of dashes followed by a blank line
* If there is no header row, there must be a terminal line of dashes
* No multiline rows



### [Multiline Tables](https://pandoc.org/MANUAL.html#extension-multiline_tables)


```markdown
-------------------------------------------------------------
 Centered   Default           Right Left
  Header    Aligned         Aligned Aligned
----------- ------- --------------- -------------------------
   First    row                12.0 Example of a row that
                                    spans multiple lines.

  Second    row                 5.0 Here's another one. Note
                                    the blank line between
                                    rows.
-------------------------------------------------------------

Table: multi
```

```markdown
----------- ------- --------------- -------------------------
   First    row                12.0 Example of a row that
                                    spans multiple lines.

  Second    row                 5.0 Here's another one. Note
                                    the blank line between
                                    rows.
----------- ------- --------------- -------------------------

Table: headless multi
```

Rules:

* They must begin with a row of dashes, before the header text (unless the header row is omitted)
* They must end with a row of dashes, then a blank line
* The rows must be separated by blank lines
* The header may be omitted in multiline tables as well as simple tables



### [Grid Tables](https://pandoc.org/MANUAL.html#extension-grid_tables)

```markdown
+---------------+---------------+--------------------+
| Fruit         | Price         | Advantages         |
+===============+===============+====================+
| Bananas       | $1.34         | - built-in wrapper |
|               |               | - bright color     |
+---------------+---------------+--------------------+
| Oranges       | $2.10         | - cures scurvy     |
|               |               | - tasty            |
+---------------+---------------+--------------------+

Table: no-merge grid
```

```markdown
+---------------------+----------+
| Property            | Earth    |
+=============+=======+==========+
|             | min   | -89.2 °C |
| Temperature +-------+----------+
| 1961-1990   | mean  | 14 °C    |
|             +-------+----------+
|             | max   | 56.7 °C  |
+-------------+-------+----------+

Table: merge grid
```

```markdown
+---------------------+-----------------------+
| Location            | Temperature 1961-1990 |
|                     | in degree Celsius     |
|                     +-------+-------+-------+
|                     | min   | mean  | max   |
+=====================+=======+=======+=======+
| Antarctica          | -89.2 | N/A   | 19.8  |
+---------------------+-------+-------+-------+
| Earth               | -89.2 | 14    | 56.7  |
+---------------------+-------+-------+-------+

Table: multiheader grid
```

```markdown
+--------------:+:--------------+:------------------:+
| Right         | Left          | Centered           |
+---------------+---------------+--------------------+

Table: headless grid
```

```markdown 
+---------------+---------------+
| Fruit         | Price         |
+===============+===============+
| Bananas       | $1.34         |
+---------------+---------------+
| Oranges       | $2.10         |
+===============+===============+
| Sum           | $3.44         |
+===============+===============+

Table: footed grid
```

Rules:

* Can be headless
* Table header may contain more than one row
* Alignments can be specified as with pipe tables
* Also can have footers



