# marm compiler documentation

## Basics

The marm compiler translates a high level specification similar but not identical
to C into labvm code. It is a PLY-generated compiler, consisting of the usual
lexer, parser, typechecking and code generation phases.

## Syntax

marm code features

- while loops
- if branches
- function calls
- expression statements
- declaration statements
- procedure declarations

```c
int main(int param1,int param2){
    int i;
    i = 0;
    while (i<param1) {
        i=i+param2;
    }
    return i;
}
```

## Usage

```python
from src.marm.marmcompiler import marmcompiler, coloring
print(coloring('..... marmcode ......'))
print(marmcompiler('filename','........ marmcode.........')
```
