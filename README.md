# 🎵 PlayMusica - Reprodutor de Áudio Local para Windows

Um reprodutor de áudio local minimalista, ultraleve e de alta performance para Windows, inspirado na experiência fluida e elegante do clássico **Google Play Music**.

---

## ✨ Características Principais

- **🚀 Ultraleve e Inicialização Instantânea:** Desenvolvido em Python + PySide6 (Qt 6) utilizando o pipeline nativo de multimídia do Windows (FFmpeg/Media Foundation). **Zero Electron, zero Chromium, consumo mínimo de memória RAM (40–70 MB).**
- **🌙 Dark Mode Nativo:** Paleta sofisticada de alto contraste e conforto visual (`#121212`, `#181818`, `#1E1E1E`) com detalhes no icônico tom laranja Google Play Music (`#FF5722`).
- **📁 Navegação Hierárquica por Pastas:** Painel lateral dinâmico que espelha fielmente a hierarquia de diretórios da sua biblioteca musical, com opção de visualizar todas as faixas ou isolar álbuns/subpastas com um clique.
- **⚡ Busca em Tempo Real:** Filtragem instantânea por nome da faixa, artista, álbum, nome do arquivo ou pasta, com contagem dinâmica de resultados.
- **🎛️ Barra de Reprodução Completa:**
  - Play / Pause (botão primário circular de destaque).
  - Faixa Anterior / Próxima (com reinício inteligente se reproduzido > 3s).
  - Barra de progresso clicável com seek direto para qualquer ponto da música.
  - Indicadores de tempo decorrido e duração total formatados.
  - Controle de volume com atalho de silenciamento (*mute*).
  - Modos **Shuffle** (ordem aleatória sem repetições imediatas) e **Repeat** (Desligado / Repetir Todas / Repetir Uma).
- **⚙️ Gerenciamento Automático de Configuração (`config.json`):**
  - Criação automática na primeira execução com valores padrão seguros.
  - Diálogo visual de configurações para alterar a pasta de músicas via explorador nativo do Windows ou campo de texto.
  - Persistência imediata de volume, modos de reprodução e dimensões de janela.
- **🧵 Indexação 100% Assíncrona:** Varredura recursiva em thread dedicada (`QThread`), garantindo que pastas com milhares de músicas nunca travem ou causem lentidão na interface gráfica.
- **⌨️ Atalhos de Teclado:** Controle de reprodução rápido via teclado (`Espaço`, setas, `Ctrl+F`).

---

## 📂 Estrutura do Projeto

O projeto adota uma arquitetura modular orientada a responsabilidades bem definidas (Clean Code & SOLID):

```text
PlayerMusica/
│
├── core/                           # Lógica de negócio e infraestrutura
│   ├── __init__.py
│   ├── config.py                   # Gerenciador do config.json (leitura/escrita/defaults)
│   ├── models.py                   # Modelos de dados (Track, FolderNode)
│   ├── tag_reader.py               # Leitor puro-Python de metadados ID3v1/ID3v2, WAV, FLAC e OGG
│   ├── scanner.py                  # Scanner assíncrono de diretórios (QThread)
│   └── audio_engine.py             # Engine de áudio (QMediaPlayer/QAudioOutput, fila, shuffle, repeat)
│
├── ui/                             # Camada de apresentação e interface gráfica
│   ├── __init__.py
│   ├── theme.py                    # Paleta de cores, tipografia e QSS (Dark Mode)
│   ├── icons.py                    # Fábrica de ícones vetoriais SVG de alta resolução
│   ├── main_window.py              # Janela principal e orquestração de componentes
│   └── components/                 # Componentes visuais desacoplados
│       ├── __init__.py
│       ├── slider.py               # Slider horizontal com clique direto para seek
│       ├── player_bar.py           # Barra inferior fixa de reprodução
│       ├── sidebar.py              # Painel lateral de navegação e hierarquia de pastas
│       ├── track_table.py          # Tabela virtualizada de faixas com destaque da faixa ativa
│       ├── search_bar.py           # Campo de busca instantânea com contadores
│       └── settings_dialog.py      # Modal para troca de pasta raiz e inspeção do config.json
│
├── tests/                          # Suíte de testes unitários automatizados
│   ├── __init__.py
│   └── test_core.py                # Testes de config, tags, scanner e modelos
│
├── resources/                      # Scripts e recursos visuais
│   ├── generate_icon.py            # Gerador de ícones .ico e .png em alta definição
│
├── .gitignore                      # Exclui arquivos locais e artefatos gerados
├── main.py                         # Ponto de entrada da aplicação
├── config.example.json             # Exemplo da configuração local
├── PlayMusica.spec                 # Configuração de build do PyInstaller
├── requirements.txt                # Dependências do projeto
└── README.md                       # Documentação completa
```

O `config.json` é criado localmente na primeira execução e não deve ser versionado;
o `.gitignore` já o exclui, assim como os diretórios gerados `build/` e `dist/`.
O `config.example.json` documenta o formato da configuração sem incluir caminhos
pessoais.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+ (compatível com 3.10, 3.11, 3.12, 3.13, 3.14).
- **Framework de Interface:** [PySide6 (Qt for Python)](https://doc.qt.io/qtforpython-6/) — widgets nativos de alta performance com aceleração de hardware.
- **Engine de Áudio:** `PySide6.QtMultimedia` (`QMediaPlayer` + `QAudioOutput`) com backend integrado FFmpeg/Windows Media Foundation.
- **Leitor de Metadados:** Extrator puro em Python (sem dependências externas) para headers MP3 (ID3v1, ID3v2.3, ID3v2.4), WAV (RIFF), FLAC (Vorbis comments) e OGG.
- **Empacotador:** [PyInstaller](https://pyinstaller.org/) para compilação em executável único `.exe` (incluído em `requirements.txt`).

---

## 🚀 Como Executar em Modo de Desenvolvimento

### 1. Clonar ou Acessar o Diretório
```bash
cd C:\Codes\PlayerMusica
```

### 2. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 3. Iniciar o Reprodutor
```bash
python main.py
```

---

## 🧪 Como Rodar os Testes Automatizados

O projeto inclui testes de unidade para validação de leitura/escrita de configuração, extração de metadados e hierarquia de diretórios:

```bash
python -m unittest discover tests
```

---

## 📦 Como Gerar o Executável (.exe) Portátil

Para gerar um arquivo executável autônomo portátil (`PlayMusica.exe`) para Windows, sem janela de console preta e com empacotamento completo de todas as bibliotecas necessárias:

### Preparar o ambiente e instalar as dependências:
```powershell
python -m pip install -r requirements.txt
```

### Gerar o executável:
```powershell
python -m PyInstaller --clean --noconfirm PlayMusica.spec
```

Use `python -m pip` e `python -m PyInstaller` para garantir que a instalação e o build usem o mesmo interpretador. O arquivo `.spec` interrompe o build com uma mensagem clara se o PySide6 não estiver instalado nesse ambiente.

> **Resultado do Build:**
>
> O executável final será gerado em:
>
> `dist\PlayMusica.exe`

Ao copiar `PlayMusica.exe` para qualquer máquina Windows, basta executá-lo com dois cliques. Ele criará o arquivo `config.json` no mesmo diretório caso este não exista.

---

## ⌨️ Atalhos de Teclado

| Tecla / Combinação | Ação |
| :--- | :--- |
| `Espaço` | Reproduzir / Pausar (*Play/Pause*) |
| `Seta para Esquerda` | Voltar 5 segundos (*Seek Backward*) |
| `Seta para Direita` | Avançar 5 segundos (*Seek Forward*) |
| `Ctrl + Seta para Esquerda` | Faixa Anterior |
| `Ctrl + Seta para Direita` | Próxima Faixa |
| `Seta para Cima` | Aumentar Volume (+5%) |
| `Seta para Baixo` | Diminuir Volume (-5%) |
| `Ctrl + F` | Focar na barra de busca |
| `Esc` | Limpar campo de busca e retornar o foco para a tabela |

---

## 📄 Estrutura do `config.json`

O arquivo `config.json` é criado automaticamente no diretório do executável ou script:

```json
{
    "music_directory": "C:\\Users\\SeuUsuario\\Music",
    "volume": 0.8,
    "shuffle": false,
    "repeat_mode": "none",
    "window_width": 1120,
    "window_height": 720,
    "is_maximized": false
}
```

- `music_directory`: Caminho absoluto da pasta raiz contendo seus arquivos de música.
- `volume`: Valor decimal de 0.0 (mudo) a 1.0 (máximo).
- `shuffle`: `true` para ordem aleatória inteligente, `false` para sequencial.
- `repeat_mode`: `"none"` (para ao fim da lista), `"all"` (reinicia ao final), `"one"` (repete a mesma faixa em loop).
- `window_width` / `window_height` / `is_maximized`: Mantém o tamanho e estado de janela configurados pelo usuário na última sessão.
