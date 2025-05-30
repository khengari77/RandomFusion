# 🎨 RandomFusion ✨

**Transforming Cryptographic Keys into Unique Visual Art!**

RandomFusion takes the often cryptic world of cryptographic key fingerprints (like those for SSH keys) and morphs them into distinctive, deterministic pieces of visual art. The core idea? Make it **easier and more intuitive for humans to visually distinguish between different keys**.

If even a single bit changes in an input key, RandomFusion's internal "avalanche" remapping ensures the resulting artwork is **dramatically different**. No more squinting at long hex strings – spot the difference with a glance!

Currently, RandomFusion crafts a vibrant "Color Blocks Grid" image, with more art styles planned for the future!

**🚀 Wanna try it yourself? Quick Start! 🚀**

Assuming you've followed the installation steps below, jump right in with this command in your terminal (from the project directory):

```bash
poetry run randomfusion generate "MD5:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00"
```
This will generate `randomfusion_output.png` using default settings.

You can add arguments to customize the image (see "Usage" section below). Try changing just one character in the fingerprint string (e.g., `...ee:ff:00` to `...ee:ff:01`) and re-run to see how vastly different the output image becomes!

---

## 🚀 Features (Current MVP)

*   🔑 Accepts SSH public key file paths or raw fingerprint strings.
*   🔍 Extracts fingerprints from key files using the standard `ssh-keygen` tool.
*   🌪️ Applies a powerful "avalanche" remapping (SHA256 hashing) to the fingerprint, maximizing visual difference for tiny key changes.
*   🖼️ Generates a deterministic procedural image ("Color Blocks Grid") based on the remapped data. Each key gets its own unique visual signature!
*   💻 User-friendly Command-Line Interface (CLI) for easy generation.
*   Generates deterministic procedural images based on the remapped data. Styles include:
    *   **Color Blocks Grid**
    *   **Concentric Circles**
    *   **NoiseScape** (Abstract Perlin noise patterns)
    *   **Mandelbrot Fractal** (Classic fractal art)
    *   **More to come!**
---

## ✅ Prerequisites

*   🐍 Python 3.9+
*   📜 Poetry (for a smooth installation and dependency management experience)
*   🔑 `ssh-keygen` command-line tool (standard with OpenSSH) accessible in your system's PATH.

---

## 🛠️ Installation & Setup

1.  **Clone the Magic:**
    ```bash
    git clone <your-repository-url> # Replace with the actual URL
    cd randomfusion
    ```

2.  **Weave the Dependencies with Poetry:**
    ```bash
    poetry install
    ```
    This conjures a virtual environment and installs all the necessary spells (packages).

---

## 💡 Usage

First, step into the RandomFusion virtual environment (if you're not already there):
```bash
poetry shell
```

Now, unleash the `randomfusion` command!

**✨ Generate Your Visual Fingerprint:**

```bash
randomfusion generate <KEY_INPUT> [OPTIONS]
```

**Arguments:**

*   `KEY_INPUT`: (Required) Your key source. This can be:
    *   A path to an SSH public key file (e.g., `~/.ssh/id_ed25519.pub`).
    *   A raw fingerprint string (e.g., `"SHA256:qL7x5Y+7Q8zRbk/yYk6xN8zW3kH9jF0oD7rX5mN6zC0"`).
        *Remember to wrap fingerprints with special characters in quotes!*

**Options to Customize Your Art:**

*   `-o, --output TEXT`: Name of the output image file. (Default: `randomfusion_output.png`)
*   `--width INTEGER`: Desired width of your art in pixels. (Default: `256`)
*   `--height INTEGER`: Desired height of your art in pixels. (Default: `256`)
*   `--grid-size INTEGER`: For the "Color Blocks" visual, this sets the number of blocks per row/column. (Default: `8`)
*   `--help`: Reveals more command secrets and options.
*   `--style TEXT`: Visual style to generate. (Choices: `color_blocks`, `circles`, `noisescape`, `mandelbrot`; Default: `color_blocks`)
*   `--grid-size INTEGER`: [Style: color_blocks] Number of blocks per row/column. (Default: `8`)
*   `--num-circles INTEGER`: [Style: circles] Override the seed-derived number of circles.
*   `--base-stroke INTEGER`: [Style: circles] Override the seed-derived base stroke width for circles.

**Example Incantations:**

1.  **From your trusted SSH public key file:**
    ```bash
    randomfusion generate ~/.ssh/id_ed25519.pub
    ```
    (Look for `randomfusion_output.png` in your current directory!)

2.  **From a fingerprint string, crafting a larger, more detailed piece:**
    ```bash
    randomfusion generate "SHA256:MyAwesomeKeyPrintThatIsSuperUnique12345" -o my_masterpiece.png --width 512 --height 512 --grid-size 16
    ```

3.  **Seek Guidance:**
    ```bash
    randomfusion --help
    randomfusion generate --help
    ```
4.  **Generate "Concentric Circles" style:**
    ```bash
    randomfusion generate your_key_input --style circles -o my_circles.png
    ```
5.  **Generate "NoiseScape" style:**
    ```bash
    randomfusion generate your_key_input --style noisescape -o my_noisescape.png
    ```
6.  **Generate "Mandelbrot" style:**
    ```bash
    randomfusion generate your_key_input --style mandelbrot -o my_mandelbrot.png
    ```
---

## 🧑‍💻 For Developers

Want to peek behind the curtain or contribute?

**Run the Test Suite:**
```bash
poetry run pytest
```

---

## 🔮 Future Visions & Enhancements

The journey has just begun! Here's a glimpse of what could be:

*   🎨 More diverse procedural art algorithms (fractals, patterns, abstract flows).
*   🧠 Integration with advanced generative AI models (like Stable Diffusion) for even richer, more complex visuals.
*   👁️ Option to instantly display the generated image.
*   🖱️ A Graphical User Interface (GUI) or Web UI for a more visual interaction.

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for full details. (You'll need to add a `LICENSE` file if you decide on one, e.g., MIT).

