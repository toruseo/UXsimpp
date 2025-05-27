# uxsimppパッケージのビルドと配布手順

このドキュメントでは、uxsimppパッケージをビルドし、配布可能な形式に変換するための手順を説明します。

## 前提条件

以下のソフトウェアがインストールされている必要があります：

- Python 3.9以上
- C++コンパイラ
  - Windows: Visual Studio Build Tools
  - Linux: GCC
  - macOS: Clang
- CMake 3.15以上

## 開発環境のセットアップ

### 仮想環境

```
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 必要なパッケージのインストール

```
pip install scikit-build-core pybind11 cmake ninja pytest build
```


## テストの実行

パッケージが正しく機能するかテストします。

```
pytest tests/test_verification.py -v
```

## 配布用パッケージの作成


### ソースディストリビューションとホイールの作成

```
python -m build
```

このコマンドを実行すると、`dist`ディレクトリに以下のファイルが生成されます：

- `uxsimpp-0.1.0.tar.gz` - ソースディストリビューション
- `uxsimpp-0.1.0-cp39-cp39-win_amd64.whl` - ホイールパッケージ（プラットフォームによって名前が異なります）

## ビルドしたパッケージのテスト

### 既存のパッケージをアンインストール

```
pip uninstall -y uxsimpp
```

### ビルドしたホイールをインストール

```
pip install dist/uxsimpp-0.1.0*.whl
```

### テストの実行

```
pytest tests/test_verification.py -v
```

## PyPIへの公開

### 必要なツールのインストール

```
pip install twine
```

### TestPyPI（テスト用）へのアップロード

```
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### 本番PyPIへのアップロード

```
twine upload dist/*
```
