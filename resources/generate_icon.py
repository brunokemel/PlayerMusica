"""
Script Auxiliar: Gerador de Ícones do PlayMusica.
Cria as versões .ico (Windows) e .png (alta definição) do ícone do aplicativo
desenhando a marca minimalista (círculo laranja com triângulo Play branco).
"""

import os
from PIL import Image, ImageDraw


# =============================================================================
# BLOCO 1: Função de Geração de Ícones Multi-Resolução
# =============================================================================

def generate_icon(output_ico: str, output_png: str):
    """
    Gera um arquivo de ícone (.ico) contendo todas as resoluções padrão do Windows:
    256x256, 128x128, 64x64, 48x48, 32x32 e 16x16.
    """
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for w, h in sizes:
        # Cria imagem RGBA com fundo 100% transparente
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 1. Círculo de fundo no tom laranja clássico (#FF5722)
        pad = max(1, int(w * 0.04))
        draw.ellipse([pad, pad, w - pad - 1, h - pad - 1], fill=(255, 87, 34, 255))

        # 2. Triângulo de Play centralizado em branco puro
        pts = [
            (int(w * 0.38), int(h * 0.28)),
            (int(w * 0.72), int(h * 0.50)),
            (int(w * 0.38), int(h * 0.72)),
        ]
        draw.polygon(pts, fill=(255, 255, 255, 255))
        images.append(img)

    # Cria diretório de destino caso não exista
    os.makedirs(os.path.dirname(os.path.abspath(output_ico)), exist_ok=True)

    # Salva o arquivo ICO com todas as camadas de tamanho embutidas
    images[0].save(output_ico, format="ICO", sizes=[(im.width, im.height) for im in images])
    # Salva versão PNG em alta definição (256x256)
    images[0].save(output_png, format="PNG")
    print(f"Ícones gerados com sucesso em:\n- {output_ico}\n- {output_png}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    generate_icon(
        os.path.join(base_dir, "app_icon.ico"),
        os.path.join(base_dir, "app_icon.png"),
    )
