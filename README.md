# py-tidy

This is a Python package that helps in tidying up your Python code.

# How to use

use [uvx](https://docs.astral.sh/uv/guides/tools/) for running the script
```bash
# run linting
uvx --from git+https://github.com/tokikanno/py-tidy py-tidy lint

# run formatting. CAUTION: this will overwrite your files!
uvx --from git+https://github.com/tokikanno/py-tidy py-tidy format
```

# What will it fixes

This tool will add empty lines between control blocks to improve readability.
For example, it will transform this:
```python
def test(a: int) -> None:
    if (
       a > 0
       and a == 1
    ):
        # test
        print()
        for i in range(5):
            print(i)
        print("1")
    elif a == 2:
       print("2")
    elif a == 3:
       print("3")    
    else:
        print("else")
    while True:
        print("a")
    else:
        print("b")
    for _ in range(10):
        print("c")
    else:
        print("d")
        try:
           pass
        except Exception as e:
            pass
        finally:
            pass
        with open("xxx.txt") as f:
            print(f.read())
```
into this:
```python
def test(a: int) -> None:
    if (
       a > 0
       and a == 1
    ):
        # test
        print()
        for i in range(5):
            print(i)

        print("1")

    elif a == 2:
       print("2")

    elif a == 3:
       print("3")    

    else:
        print("else")

    while True:
        print("a")

    else:
        print("b")

    for _ in range(10):
        print("c")

    else:
        print("d")
        try:
           pass

        except Exception as e:
            pass

        finally:
            pass

        with open("xxx.txt") as f:
            print(f.read())
    
```