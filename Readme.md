# 계산기

## 소개

파이썬으로 만들어보는 간단한 계산기

```python
>>> (1 + 1) ** 10
1024
```

## 설명

- [렉서](src/lexer.py)
    - 소스 코드를 토큰화
- [빌더](src/builder.py)
    - 토큰들로 트리 구축해주는 파서
- [머신](src/machine.py)
    - 트리를 직접 실행해주는 인터프리터