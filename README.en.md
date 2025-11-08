# Wallpaper Processing Automation Tool 🎨🖼️

This project provides a set of Python scripts to automate the extraction, processing, and organization of wallpaper project files. The tool extracts resources from wallpaper project packages (`scene.pkg`), cleans up files, and organizes image files into appropriate directories.  
**Note: This is a personal tool, and the output is tailored to personal preferences for extracting wallpaper images. Not intended for R18 content.** ⚠️

## Features ✨

- **Filename Cleaning**: Removes illegal characters, control characters, and emoji from filenames.🧹
- **Image Processing**: Moves large image files to the root directory and deletes image files smaller than the specified size.📸
- **RePKG Extraction**: Automatically uses the RePKG tool to extract content from `scene.pkg` files.📦
- **Folder Management**: Automatically extracts the project name and organizes the content into subdirectories based on specific rules.📂

## Requirements 🖥️

- Python 3.6+ 🐍
- RePKG tool (RePKG.exe) 🛠️
- tqdm library (for displaying progress bars) 📊

You can install the required Python libraries using pip:

```bash
pip install tqdm
````

I am using uv, and you can build the environment with `uv sync`. ⚡

Make sure the `RePKG.exe` executable file is located in your project directory. 📍

## File Descriptions 📄

```python
parrel.py
```

This script handles parallel processing of multiple wallpaper project folders. It extracts resources from `scene.pkg` files and processes image files. The output is organized into subfolders based on the configured project count per subfolder.

```python
main.py
```

This script processes each wallpaper project folder sequentially, extracts resources from `scene.pkg` files, moves image files to the root directory, and organizes files into specified folders. **Please prefer using `parrel.py`, as it has more complete and accurate functionality. `main.py` is more for testing purposes.**

## Usage 🛠️

1. Set up your directory structure: `Source`, `output`, `RePkg`. Store the workshop download folders with IDs in the `Source` folder. 🗂️
2. Run the `*.py` scripts: These scripts will process the wallpaper project folders in the `Source` directory and output the results to the `output` directory. 🔄
3. Parallel Processing: If you want to speed up the process, you can use the `parrel.py` script, which will process multiple folders in parallel. 🚀

**Output Result**: After processing, the `output` directory will contain organized subdirectories with extracted content, `only` including image and video files. You can configure custom filtering rules in the `spliter_folder` function using the `special list` and file extensions. It will also automatically `remove` empty folders and subfolders. 🗑️

## Configuration ⚙️

Configure paths for `Source`, `Output`, and `Repkg` as needed.

* **contains**: This variable controls how many projects each folder should contain. When the folder reaches the specified number of projects, a new subfolder will automatically be created. 📁
* **Image Size Limit**: The script will move image files larger than `20KB (configurable)` to the root directory and delete files smaller than this size. You can adjust this behavior as needed. ⚖️

## Example Output Directory Structure 📂

After processing, the `output` directory structure might look like this:

```
output/
├── output0/
│   ├── group/
│   ├── mp4/
│   ├── selected/
├── output1/
│   ├── group/
│   ├── mp4/
│   ├── selected/
```

* **group**: Contains groups of image files. 📸
* **mp4**: Contains video files (if any). 🎥
* **selected**: Contains individual wallpaper selections. 💎

## Troubleshooting ⚠️

* **RePKG Extraction Failed**: Ensure the `RePKG.exe` file is in the correct location and that you have execution permissions. 🔑
* **File Output Mess**: If the output files are messy, please check the folder paths. 🛑

## License 📝

This project is licensed under the MIT License - see the LICENSE file for details. 📜

### Acknowledgements

* **Contributors**: Kan Liu 🤝
* **Contact**: [lkbhg@outlook.com](mailto:lkbhg@outlook.com) 📧