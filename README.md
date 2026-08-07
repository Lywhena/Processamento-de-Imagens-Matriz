# Editor de Imagens

Editor de imagens em Python para a disciplina de Processamento de Imagens. Nesta etapa inicial: abre imagens (PNG/JPG/JPEG) ou uma matriz `.txt` própria, exibe na tela e salva a imagem carregada como matriz `.txt`.

## Como rodar

```bash
pip install -r requirements.txt
python main.py
```

## Como rodar os testes

```bash
pytest
```

## Formato do arquivo de matriz (`.txt`)

```
largura altura canais

<matriz do canal 1: `altura` linhas com `largura` valores inteiros 0-255 separados por espaço>

<matriz do canal 2, se canais == 3>

<matriz do canal 3, se canais == 3>
```

- `canais = 1`: imagem em escala de cinza, um único bloco de matriz.
- `canais = 3`: imagem RGB, três blocos de matriz na ordem R, G, B, separados por linha em branco.

## Estrutura do projeto

```
core/               modelo de dados (ImageModel) e leitura/escrita de arquivos
  fileFormats/       um handler por formato (PNG/JPG, matriz .txt) + registry por extensão
processing/          ponto de extensão para filtros/transformações futuras (ImageFilter)
ui/                  janela Tkinter (MainWindow) e widget de exibição (ImageCanvas)
tests/               testes de round-trip (salvar e reabrir sem perda)
```

Novos formatos de arquivo: criar uma classe que implemente `FormatHandler` e registrar em `core/fileFormats/formatRegistry.py`. Novos filtros: criar uma classe que implemente `ImageFilter` em `processing/`.
