"""
Extrator de Metadados e Duração de Áudio Puro-Python.
Suporta formatos MP3 (ID3v1, ID3v2.3, ID3v2.4), WAV (RIFF), FLAC e OGG.
Construído com a biblioteca padrão do Python (sem dependências externas).
"""

import os
import re
import struct
from typing import Dict, Tuple


# =============================================================================
# BLOCO 1: Funções Utilitárias de Formatação e Limpeza de Texto
# =============================================================================

def format_duration(ms: int) -> str:
    """
    Converte uma duração em milissegundos para o formato amigável 'MM:SS' ou 'HH:MM:SS'.
    Exemplos:
      45000 ms   -> '00:45'
      215000 ms  -> '03:35'
      3665000 ms -> '1:01:05'
    """
    if ms <= 0:
        return "00:00"

    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def clean_filename_title(filename: str) -> str:
    """
    Gera um título limpo a partir do nome do arquivo quando a tag ID3 não existir.
    Remove extensões e numerações iniciais típicas de faixas de álbum.
    Exemplos:
      '01 - Bohemian Rhapsody.mp3' -> 'Bohemian Rhapsody'
      '02. Hotel California.flac'  -> 'Hotel California'
      'track_sample_audio.wav'     -> 'track sample audio'
    """
    base = os.path.splitext(filename)[0]
    # Expressão regular: remove dígitos iniciais seguidos de traço, ponto ou espaço
    cleaned = re.sub(r"^\d+[\s\.\-_]+", "", base).strip()
    if not cleaned:
        cleaned = base
    return cleaned.replace("_", " ")


# =============================================================================
# BLOCO 2: Classe Leitora de Metadados (AudioTagReader)
# =============================================================================

class AudioTagReader:
    """
    Parser binário de cabeçalhos de arquivos de áudio.
    Lê tags e calcula a duração de forma ultrarrápida lendo apenas os primeiros
    e últimos bytes do arquivo, sem carregar todo o áudio na memória RAM.
    """

    @classmethod
    def read_metadata(cls, file_path: str) -> Dict[str, any]:
        """
        Ponto de entrada principal: identifica o formato pela extensão, executa o
        parser específico e aplica fallbacks seguros para qualquer campo em branco.
        """
        ext = os.path.splitext(file_path)[1].lower()
        title = ""
        artist = ""
        album = ""
        duration_ms = 0

        # Roteamento de acordo com o formato do arquivo
        try:
            if ext == ".mp3":
                title, artist, album, duration_ms = cls._read_mp3(file_path)
            elif ext == ".wav":
                title, artist, album, duration_ms = cls._read_wav(file_path)
            elif ext == ".flac":
                title, artist, album, duration_ms = cls._read_flac(file_path)
            elif ext in (".ogg", ".oga"):
                title, artist, album, duration_ms = cls._read_ogg(file_path)
        except Exception:
            # Qualquer falha de leitura em arquivo corrompido não quebra a aplicação
            pass

        # Estratégia de Fallback: preenchimento de campos ausentes
        filename = os.path.basename(file_path)
        if not title:
            title = clean_filename_title(filename)
        if not artist:
            artist = "Artista Desconhecido"
        if not album:
            # Usa o nome da pasta em que a música está como nome do Álbum
            parent_dir = os.path.basename(os.path.dirname(file_path))
            album = parent_dir if parent_dir else "Álbum Desconhecido"

        return {
            "title": title.strip(),
            "artist": artist.strip(),
            "album": album.strip(),
            "duration_ms": duration_ms,
            "duration_str": format_duration(duration_ms),
        }

    # =========================================================================
    # BLOCO 3: Parser de Arquivos MP3 (ID3v2 e ID3v1)
    # =========================================================================

    @classmethod
    def _read_mp3(cls, path: str) -> Tuple[str, str, str, int]:
        """
        Lê metadados de MP3. Primeiro tenta o cabeçalho moderno ID3v2 no início
        do arquivo. Se não encontrar, tenta o formato clássico ID3v1 nos últimos 128 bytes.
        """
        title, artist, album = "", "", ""
        duration_ms = 0

        # 1. Tentativa com ID3v2 (no início do arquivo)
        try:
            with open(path, "rb") as f:
                header = f.read(10)
                # O cabeçalho ID3v2 sempre inicia com os 3 caracteres 'ID3'
                if len(header) == 10 and header[:3] == b"ID3":
                    major_ver = header[3]  # ID3v2.3 ou ID3v2.4
                    # Tamanho synchsafe (7 bits por byte) do bloco de tags
                    tag_size = (
                        (header[6] << 21)
                        | (header[7] << 14)
                        | (header[8] << 7)
                        | header[9]
                    )
                    tag_data = f.read(tag_size)
                    tags = cls._parse_id3v2_frames(tag_data, major_ver)

                    title = tags.get("TIT2", "")  # Título
                    artist = tags.get("TPE1", "") # Artista
                    album = tags.get("TALB", "")  # Álbum
                    tlen_str = tags.get("TLEN", "") # Duração em ms
                    if tlen_str.isdigit():
                        duration_ms = int(tlen_str)
        except Exception:
            pass

        # 2. Tentativa com ID3v1 (últimos 128 bytes do arquivo) caso ainda falte informação
        if not title or not artist or not album:
            try:
                file_size = os.path.getsize(path)
                if file_size >= 128:
                    with open(path, "rb") as f:
                        f.seek(file_size - 128)
                        id3v1 = f.read(128)
                        # ID3v1 começa com os 3 bytes 'TAG'
                        if id3v1[:3] == b"TAG":
                            if not title:
                                title = id3v1[3:33].decode("latin-1", errors="ignore").strip("\x00 ").strip()
                            if not artist:
                                artist = id3v1[33:63].decode("latin-1", errors="ignore").strip("\x00 ").strip()
                            if not album:
                                album = id3v1[63:93].decode("latin-1", errors="ignore").strip("\x00 ").strip()
            except Exception:
                pass

        return title, artist, album, duration_ms

    @classmethod
    def _parse_id3v2_frames(cls, data: bytes, version: int) -> Dict[str, str]:
        """
        Decodifica frames ID3v2 individuais (TIT2, TPE1, TALB, TLEN, TRCK).
        Respeita a especificação de inteiros Synchsafe para v2.4 e big-endian para v2.3.
        """
        tags: Dict[str, str] = {}
        pos = 0
        data_len = len(data)

        # Itera pelos blocos de frames (cada frame possui cabeçalho de 10 bytes)
        while pos + 10 <= data_len:
            frame_id_bytes = data[pos : pos + 4]
            # Padding de zeros indica o fim dos frames úteis
            if frame_id_bytes[0] == 0:
                break

            try:
                frame_id = frame_id_bytes.decode("ascii")
            except Exception:
                break

            # Cálculo do tamanho do payload do frame
            if version == 4:
                # No ID3v2.4 o tamanho é um inteiro synchsafe (4 bytes de 7 bits)
                size = (
                    (data[pos + 4] << 21)
                    | (data[pos + 5] << 14)
                    | (data[pos + 6] << 7)
                    | data[pos + 7]
                )
            else:
                # No ID3v2.3 é um inteiro tradicional big-endian de 32 bits
                size = struct.unpack(">I", data[pos + 4 : pos + 8])[0]

            pos += 10
            if size <= 0 or pos + size > data_len:
                break

            frame_content = data[pos : pos + size]
            pos += size

            # Guarda os campos mais relevantes para a interface do player
            if frame_id in ("TIT2", "TPE1", "TALB", "TLEN", "TRCK"):
                tags[frame_id] = cls._decode_id3_text(frame_content)

        return tags

    @classmethod
    def _decode_id3_text(cls, content: bytes) -> str:
        """
        Decodifica o payload de texto ID3 de acordo com o byte de codificação:
          0x00 -> ISO-8859-1 (Latin-1)
          0x01 -> UTF-16 com BOM
          0x02 -> UTF-16BE sem BOM
          0x03 -> UTF-8
        """
        if not content:
            return ""
        encoding_byte = content[0]
        text_bytes = content[1:]
        try:
            if encoding_byte == 0:
                return text_bytes.decode("latin-1", errors="ignore").strip("\x00")
            elif encoding_byte == 1:
                return text_bytes.decode("utf-16", errors="ignore").strip("\x00")
            elif encoding_byte == 2:
                return text_bytes.decode("utf-16-be", errors="ignore").strip("\x00")
            elif encoding_byte == 3:
                return text_bytes.decode("utf-8", errors="ignore").strip("\x00")
            else:
                return text_bytes.decode("utf-8", errors="ignore").strip("\x00")
        except Exception:
            return ""

    # =========================================================================
    # BLOCO 4: Parser de Arquivos WAV (RIFF WAVE)
    # =========================================================================

    @classmethod
    def _read_wav(cls, path: str) -> Tuple[str, str, str, int]:
        """
        Lê cabeçalho RIFF de arquivos WAV e calcula duração exata em milissegundos:
        duração_ms = (tamanho_dados_bytes / taxa_bytes_por_segundo) * 1000.
        """
        duration_ms = 0
        try:
            with open(path, "rb") as f:
                header = f.read(12)
                if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
                    while True:
                        chunk_hdr = f.read(8)
                        if len(chunk_hdr) < 8:
                            break
                        chunk_id = chunk_hdr[:4]
                        chunk_size = struct.unpack("<I", chunk_hdr[4:8])[0]

                        # Chunk 'fmt ': contém taxa de amostragem e byte_rate
                        if chunk_id == b"fmt ":
                            fmt_data = f.read(chunk_size)
                            if len(fmt_data) >= 16:
                                audio_fmt, channels, sample_rate, byte_rate = struct.unpack(
                                    "<HHII", fmt_data[:12]
                                )
                                cls_byte_rate = byte_rate
                        # Chunk 'data': tamanho dos frames de áudio brutos
                        elif chunk_id == b"data":
                            if "cls_byte_rate" in locals() and cls_byte_rate > 0:
                                duration_ms = int((chunk_size / cls_byte_rate) * 1000)
                            f.seek(chunk_size, 1)
                        else:
                            f.seek(chunk_size, 1)
        except Exception:
            pass
        return "", "", "", duration_ms

    # =========================================================================
    # BLOCO 5: Parser de Arquivos FLAC (STREAMINFO e Vorbis Comments)
    # =========================================================================

    @classmethod
    def _read_flac(cls, path: str) -> Tuple[str, str, str, int]:
        """
        Lê arquivos FLAC:
        1. Bloco STREAMINFO: sample_rate e total_samples -> calcula duração milimétrica.
        2. Bloco VORBIS_COMMENT: extrai 'TITLE', 'ARTIST' e 'ALBUM'.
        """
        title, artist, album = "", "", ""
        duration_ms = 0
        try:
            with open(path, "rb") as f:
                # Assinatura mágica de arquivos FLAC
                if f.read(4) != b"fLaC":
                    return "", "", "", 0

                while True:
                    hdr = f.read(4)
                    if len(hdr) < 4:
                        break
                    is_last = (hdr[0] & 0x80) != 0
                    block_type = hdr[0] & 0x7F
                    length = (hdr[1] << 16) | (hdr[2] << 8) | hdr[3]
                    data = f.read(length)

                    # Bloco 0 = STREAMINFO (metadados de áudio)
                    if block_type == 0 and len(data) >= 18:
                        sample_rate = (data[10] << 12) | (data[11] << 4) | (data[12] >> 4)
                        total_samples = (
                            ((data[13] & 0x0F) << 32)
                            | (data[14] << 24)
                            | (data[15] << 16)
                            | (data[16] << 8)
                            | data[17]
                        )
                        if sample_rate > 0:
                            duration_ms = int((total_samples / sample_rate) * 1000)

                    # Bloco 4 = VORBIS_COMMENT (tags de texto)
                    elif block_type == 4:
                        comments = cls._parse_vorbis_comments(data)
                        title = comments.get("title", "")
                        artist = comments.get("artist", "")
                        album = comments.get("album", "")

                    if is_last:
                        break
        except Exception:
            pass
        return title, artist, album, duration_ms

    # =========================================================================
    # BLOCO 6: Parser de Arquivos OGG e Leitura de Vorbis Comments
    # =========================================================================

    @classmethod
    def _read_ogg(cls, path: str) -> Tuple[str, str, str, int]:
        """Procura o bloco vorbis comment em streams de áudio OGG Vorbis."""
        title, artist, album = "", "", ""
        try:
            with open(path, "rb") as f:
                sample_data = f.read(16384)
                idx = sample_data.find(b"\x03vorbis")
                if idx != -1:
                    comment_block = sample_data[idx + 7 :]
                    comments = cls._parse_vorbis_comments(comment_block)
                    title = comments.get("title", "")
                    artist = comments.get("artist", "")
                    album = comments.get("album", "")
        except Exception:
            pass
        return title, artist, album, 0

    @classmethod
    def _parse_vorbis_comments(cls, data: bytes) -> Dict[str, str]:
        """Lê pares 'CHAVE=VALOR' na especificação de Vorbis Comments."""
        comments: Dict[str, str] = {}
        try:
            pos = 0
            if len(data) < 4:
                return comments
            # Pula string do fornecedor (vendor string)
            vendor_len = struct.unpack("<I", data[pos : pos + 4])[0]
            pos += 4 + vendor_len
            if pos + 4 > len(data):
                return comments

            user_comment_count = struct.unpack("<I", data[pos : pos + 4])[0]
            pos += 4

            for _ in range(user_comment_count):
                if pos + 4 > len(data):
                    break
                length = struct.unpack("<I", data[pos : pos + 4])[0]
                pos += 4
                if pos + length > len(data):
                    break
                comment = data[pos : pos + length].decode("utf-8", errors="ignore")
                pos += length
                if "=" in comment:
                    key, val = comment.split("=", 1)
                    comments[key.strip().lower()] = val.strip()
        except Exception:
            pass
        return comments
