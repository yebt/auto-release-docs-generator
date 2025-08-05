# Changelog & Tutorial Video List Generator with OpenAI Responses API

This script automates the creation of two types of changelogs (commercial and technical) and a list of tutorial videos based on the Git commit history between two tags. It uses the OpenAI Responses API and displays progress spinners via the Halo library.

---

## 🛠️ Prerequisites

- Python 3.8 or higher
- Git
- An OpenAI account with access to the Responses API
- Python packages:
  - `python-dotenv`
  - `openai`
  - `halo`

---

## 📦 Installation

1. **Clone this repository**

   ```bash
   git clone https://your-repo.git
   cd your-repo

   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   > **requirements.txt**
   >
   > ```text
   > python-dotenv
   > openai
   > halo
   > ```

---

## ⚙️ Configuration

Create a `.env` file in the project root with these variables:

```dotenv
OPENAI_API_KEY=your_openai_api_key
OUTPUT_DIR=/path/to/output/directory
```

- `OPENAI_API_KEY`: Your OpenAI API key.
- `OUTPUT_DIR`: Where release folders and files will be saved.

---

## 🚀 Usage

```bash
./generate_release.py \
  --repo-dir /path/to/your/repo \
  --branch main \
  --from-tag 3.4.2 \
  --to-tag   3.5.1
```

- `--repo-dir` : Path to the Git repository.
- `--branch` : Branch name (e.g., `main`).
- `--from-tag` : Starting tag (e.g., `3.4.2`).
- `--to-tag` : Ending tag (e.g., `3.5.1`).

When run, the script:

1. Loads and verifies `OPENAI_API_KEY` and `OUTPUT_DIR`.
2. Changes to the specified repository directory.
3. Retrieves the Git log between the two tags on the given branch.
4. Creates a release folder in `OUTPUT_DIR` named `release_<to-tag>_<timestamp>`.
5. Generates:
   - `CHANGELOG_commercial.md` (customer-facing summary).
   - `CHANGELOG_technical.md` (detailed developer log).
   - `video_list.md` (suggested tutorial videos).

6. Displays success or error messages with Halo spinners.

---

## 📁 Output Structure

Inside your `OUTPUT_DIR` you will find:

```
/path/to/output/
└── release_3.5.1_20250805_143210/
    ├── CHANGELOG_commercial.md
    ├── CHANGELOG_technical.md
    └── video_list.md
```

- **CHANGELOG_commercial.md**: Key points for sales and customer communication.
- **CHANGELOG_technical.md**: Commit details and technical impact.
- **video_list.md**: List of recommended tutorial videos.

---

## 📝 Sample `CHANGELOG_commercial.md`

```markdown
# Commercial Changelog (v3.4.2 → v3.5.1)

- **New international payment gateway**: Customers can now pay with global credit cards without extra setup.
- **Dashboard enhancements**: Widgets reorganized to display key metrics at a glance.
- **Load time optimization**: Main pages load 30% faster, improving user experience.
```

---

## 🔒 License

This project is licensed under the [MIT License](LICENSE).
Contributions and feedback are welcome!

```

```
