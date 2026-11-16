"""
Suíte de Testes Automatizados de Unidade do PlayMusica.
Testa o gerenciamento do config.json, a leitura de tags/duração em cabeçalhos de áudio,
a correspondência de termos de busca e a montagem da árvore de pastas.
"""

import json
import os
import struct
import tempfile
import unittest

from core.audio_engine import AudioEngine
from core.config import ConfigManager
from core.models import FolderNode, Track
from core.scanner import build_folder_tree
from core.tag_reader import AudioTagReader, clean_filename_title, format_duration


# =============================================================================
# BLOCO 1: Testes Unitários do Gerenciador de Configuração (config.json)
# =============================================================================

class TestConfigManager(unittest.TestCase):
    """Testa criação automática, fallback e persistência do config.json."""

    def setUp(self):
        """Cria um diretório temporário isolado para não afetar arquivos reais."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "test_config.json")

    def tearDown(self):
        """Remove os arquivos temporários após a execução do teste."""
        self.temp_dir.cleanup()

    def test_auto_creation_of_config_json(self):
        """Verifica se o config.json é criado automaticamente na primeira execução."""
        mgr = ConfigManager(filename=self.config_file)
        # O arquivo deve ter sido gravado fisicamente no disco
        self.assertTrue(os.path.exists(self.config_file))

        with open(self.config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Valida a presença e valores padrão dos campos essenciais
        self.assertIn("music_directory", data)
        self.assertIn("volume", data)
        self.assertEqual(data["volume"], 0.8)
        self.assertIn("shuffle", data)
        self.assertIn("repeat_mode", data)

    def test_update_and_persist_config(self):
        """Verifica se alterações de volume, shuffle e pasta são salvas e recarregadas."""
        mgr = ConfigManager(filename=self.config_file)
        new_path = os.path.join(self.temp_dir.name, "MinhasMusicas")
        mgr.music_directory = new_path
        mgr.volume = 0.5
        mgr.shuffle = True
        mgr.repeat_mode = "one"

        # Instancia um novo ConfigManager lendo o mesmo arquivo para verificar a persistência real
        mgr2 = ConfigManager(filename=self.config_file)
        self.assertEqual(mgr2.music_directory, new_path)
        self.assertAlmostEqual(mgr2.volume, 0.5)
        self.assertTrue(mgr2.shuffle)
        self.assertEqual(mgr2.repeat_mode, "one")


# =============================================================================
# BLOCO 2: Testes Unitários do Leitor de Tags e Duração (AudioTagReader)
# =============================================================================

class TestAudioTagReader(unittest.TestCase):
    """Testa a limpeza de nomes de arquivo e decodificação de cabeçalhos de áudio."""

    def test_clean_filename_title(self):
        """Valida se numerações como '01 - ' e extensões são removidas corretamente."""
        self.assertEqual(clean_filename_title("01 - Bohemian Rhapsody.mp3"), "Bohemian Rhapsody")
        self.assertEqual(clean_filename_title("02. Hotel California.flac"), "Hotel California")
        self.assertEqual(clean_filename_title("3_Stairway_To_Heaven.wav"), "Stairway To Heaven")
        self.assertEqual(clean_filename_title("Imagine.mp3"), "Imagine")

    def test_format_duration(self):
        """Valida a conversão de milissegundos para strings no formato MM:SS e HH:MM:SS."""
        self.assertEqual(format_duration(0), "00:00")
        self.assertEqual(format_duration(45000), "00:45")
        self.assertEqual(format_duration(125000), "02:05")
        self.assertEqual(format_duration(3665000), "1:01:05")

    def test_parse_wav_header(self):
        """Cria um arquivo WAV sintético binário de 1 segundo para validar a leitura da duração."""
        temp_wav = os.path.join(tempfile.gettempdir(), "test_sample.wav")
        sample_rate = 44100
        byte_rate = sample_rate * 2
        data_size = byte_rate  # 1 segundo exato de áudio mono 16-bit
        riff_size = 36 + data_size

        # Escreve o cabeçalho binário RIFF WAVE
        with open(temp_wav, "wb") as f:
            f.write(b"RIFF")
            f.write(struct.pack("<I", riff_size))
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write(struct.pack("<I", 16))
            f.write(struct.pack("<HHII", 1, 1, sample_rate, byte_rate))
            f.write(struct.pack("<HH", 2, 16))
            f.write(b"data")
            f.write(struct.pack("<I", data_size))
            f.write(b"\x00" * data_size)

        # Executa a leitura
        metadata = AudioTagReader.read_metadata(temp_wav)
        self.assertEqual(metadata["duration_ms"], 1000)
        self.assertEqual(metadata["duration_str"], "00:01")

        if os.path.exists(temp_wav):
            os.remove(temp_wav)


# =============================================================================
# BLOCO 3: Testes Unitários de Modelos e Árvore de Diretórios
# =============================================================================

class TestModelsAndFolderTree(unittest.TestCase):
    """Testa a correspondência de termos de busca e a hierarquia de pastas."""

    def test_track_matches_query(self):
        """Valida se a busca encontra faixas por título, artista, álbum ou pasta."""
        track = Track(
            id=1,
            file_path="C:/Music/Rock/Queen - Bohemian Rhapsody.mp3",
            filename="Queen - Bohemian Rhapsody.mp3",
            title="Bohemian Rhapsody",
            artist="Queen",
            album="A Night at the Opera",
            duration_ms=354000,
            duration_str="05:54",
            file_size=8500000,
            folder_relative="Rock",
            extension=".mp3",
        )

        # Deve encontrar independente de maiúsculas/minúsculas
        self.assertTrue(track.matches_query(""))
        self.assertTrue(track.matches_query("bohemian"))
        self.assertTrue(track.matches_query("QUEEN"))
        self.assertTrue(track.matches_query("opera"))
        self.assertTrue(track.matches_query("rock"))
        # Não deve encontrar termos não relacionados
        self.assertFalse(track.matches_query("jazz"))

    def test_build_folder_tree(self):
        """Valida se a árvore de pastas agrupa faixas e calcula a contagem correta."""
        tracks = [
            Track(1, "C:/Music/Rock/Queen/song1.mp3", "song1.mp3", "Song 1", "Queen", "Album", 180000, "03:00", 1000, os.path.normpath("Rock/Queen"), ".mp3"),
            Track(2, "C:/Music/Rock/Queen/song2.mp3", "song2.mp3", "Song 2", "Queen", "Album", 190000, "03:10", 1000, os.path.normpath("Rock/Queen"), ".mp3"),
            Track(3, "C:/Music/Jazz/Miles/song3.mp3", "song3.mp3", "Song 3", "Miles", "Kind", 210000, "03:30", 1000, os.path.normpath("Jazz/Miles"), ".mp3"),
        ]

        tree = build_folder_tree("C:/Music", tracks)
        self.assertEqual(tree.track_count, 3)
        self.assertEqual(len(tree.children), 2)  # Ramos 'Rock' e 'Jazz'


if __name__ == "__main__":
    unittest.main()
