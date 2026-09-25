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

## Equalização de histograma

Menu **Histograma → Equalizar Histograma**, escolhendo a quantidade de classes (2, 4, 8, 16, 32, 64 ou 128, como na tabela "Qtd Classes / Faixa de Bits" da planilha). Implementação manual em `processing/histogramEqualization.py`, em Python puro (sem `cv2.equalizeHist`). Imagens coloridas são convertidas para cinza com os mesmos pesos BT.601 da detecção de bordas. Com a opção "Mostrar tabela da equalização" marcada, abre uma janela com a tabela da planilha calculada para a imagem.

Os 256 tons são divididos em L classes de mesma largura (Faixa = 256 / L) e a equalização é feita sobre o histograma dessas classes:

| Coluna da planilha | Campo em `ClassTableRow` | Cálculo |
|---|---|---|
| Classes | `classNumber` | k = 1 … L |
| Faixa Int Inicial / Final | `rangeStart` / `rangeEnd` | (k − 1) × Faixa até k × Faixa − 1 |
| nk | `pixelCount` | quantidade de pixels com tom dentro da faixa |
| pr(rk) | `probability` | nk / Σnk |
| sk | `cumulativeProbability` | soma acumulada de pr(rk) |
| rk(R) | `referenceLevel` | (k − 1) / (L − 1), em passos de FLA = 1 / (L − 1) |
| new (sk) | `newClassNumber` | classe cujo rk(R) é o mais próximo de sk, isto é, sk × (L − 1) arredondado, + 1 |
| Diferença | `difference` | new (sk) − Classes |
| FxD | `shift` | Faixa × Diferença |

Cada pixel recebe o deslocamento da sua classe: **Novo Pixel = Pixel + FxD**. Ele muda de faixa, mas mantém a posição dentro dela. Exemplo da planilha: 130 está na classe 5 (128–159), new (sk) = 7, Diferença = 2, FxD = 32 × 2 = 64, novo pixel = 194.

A planilha trunca pr(rk) em 3 casas e acumula o passo arredondado 0,143, por isso mostra sk = 0,997 e rk(R) = 1,001 na última classe. O programa usa os valores exatos (os dois terminam em 1) e, em caso de empate, arredonda para cima, como o `ARRED` do Excel. Com os dados da planilha a coluna new (sk) sai idêntica: 1, 3, 5, 6, 7, 8, 8, 8.

A imagem `core/images/teste equalização planilha.png` (128 × 128 = 16384 pixels) tem exatamente os nk da planilha: equalizando com 8 classes, a tabela sai igual à do professor.
