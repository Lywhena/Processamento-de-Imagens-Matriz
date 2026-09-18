# Editor de Imagens

Editor de imagens em Python para a disciplina de Processamento de Imagens. Nesta etapa inicial: abre imagens (PNG/JPG/JPEG) ou uma matriz `.txt` própria, exibe na tela e salva a imagem carregada como matriz `.txt`.

## Como rodar

```bash
pip install -r requirements.txt ou 
py -m pip install -r requirements.txt

python main.py ou
py main.py
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
  edgeDetection/     detecção de bordas e linhas
    manual/          Sobel, LoG e Hough implementados sem funções prontas
    library/         demais métodos com OpenCV
ui/                  janela Tkinter (MainWindow) e widget de exibição (ImageCanvas)
tests/               testes de round-trip (salvar e reabrir sem perda)
```

Novos formatos de arquivo: criar uma classe que implemente `FormatHandler` e registrar em `core/fileFormats/formatRegistry.py`. Novos filtros: criar uma classe que implemente `ImageFilter` em `processing/`.

## Detecção de bordas e linhas

Menu **Detecção de Bordas**. A opção "Bordas pretas sobre fundo branco" inverte o resultado (exceto Hough). Imagens coloridas são convertidas para cinza com os pesos ITU-R BT.601 (0,299 R + 0,587 G + 0,114 B).

**Implementação manual** (`processing/edgeDetection/manual/`): apenas Python puro (`math` e laços), com numpy usado só para armazenar o resultado. Nenhum módulo dessa pasta importa OpenCV, scipy ou scikit-image.

| Letra | Método | Detalhes |
|---|---|---|
| c | Sobel | Máscaras 3×3, magnitude √(Gx²+Gy²), borda replicada. Saída em magnitude ou binária por limiar |
| k | LoG | Núcleo ∇²G com raio ⌈3σ⌉, aplicado de forma separável (G''(x)G(y) + G(x)G''(y)); bordas nos cruzamentos por zero cuja inclinação supera 10% da resposta máxima |
| m | Transformada de Hough | Bordas do Sobel manual, acumulador ρ–θ (1 px × 1°), picos acima do limiar com supressão de não-máximos; retas desenhadas em vermelho sobre a imagem |

**Com OpenCV** (`processing/edgeDetection/library/`):

| Letra | Método | Funções |
|---|---|---|
| a | Roberts | `cv2.filter2D` com as máscaras 2×2 |
| b | Prewitt | `cv2.filter2D` com as máscaras 3×3 |
| d | Kirsch | `cv2.filter2D` com as 8 máscaras de bússola, resposta máxima |
| e | Frei-Chen | `cv2.filter2D` com a base de 9 máscaras, medida √(M/S) |
| f | Laplaciano | `cv2.Laplacian` |
| g | Gaussiano | `cv2.GaussianBlur` + `cv2.Sobel` (gradiente da Gaussiana) |
| h | Canny | `cv2.GaussianBlur` (σ = 1,4) + `cv2.Canny` |
| i | Boie-Cox | `cv2.sepFilter2D` com filtros casados de derivada gaussiana alongados na direção da borda + `cv2.Canny(dx, dy)` para supressão de não-máximos e histerese; limiar alto = 5× o ruído estimado (MAD) |
| j | Scharr | `cv2.Scharr` |
| l | Gabor | `cv2.getGaborKernel` em 8 orientações, energia do par par/ímpar |

Os métodos manuais rodam em Python puro e podem levar alguns segundos em imagens grandes.
