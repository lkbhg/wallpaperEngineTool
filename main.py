import os
import json
import shutil
import re
import subprocess
from pathlib import Path
from tqdm import tqdm


# 清理文件夹名称（移除非法字符和控制字符）
def sanitize_file_name(name):
    # 删除 Windows 禁止的字符
    name = re.sub(r'[\/:*?"<>|&]', "_", name)

    # 删除控制字符（ASCII 0-31）
    name = re.sub(r"[\x00-\x1F]", "", name)

    # 删除代理对（高位 Unicode，通常用于 emoji）
    name = re.sub(r"[\uD800-\uDBFF][\uDC00-\uDFFF]", "", name)

    # 删除多余空格
    name = re.sub(r"\s+", "", name)
    return name.strip()


def copy_images_to_root(output_path):

    for root, dirs, files in os.walk(output_path, topdown=False):
        for file_name in files:
            file_path = Path(root) / file_name

            # 检查文件是否是图片文件（PNG, JPG, JPEG）
            _, ext = file_path.suffix.lower(), file_path.suffix.lower()
            if ext in {".png", ".jpg", ".jpeg"}:
                # 获取图片文件大小，单位KB
                file_size = file_path.stat().st_size / 1024

                # 如果大于500KB，则剪切到根目录
                if file_size > 500:
                    shutil.move(file_path, output_path / file_name)
                else:
                    # 删除小于500KB的图片
                    file_path.unlink()
            else:
                # 删除非图片文件
                file_path.unlink()

        # 如果当前目录为空，删除它
        if not os.listdir(root) and not root == str(output_path):
            os.rmdir(root)

    # 最后检查根目录是否为空，如果为空则删除根目录
    if not os.listdir(root):
        os.rmdir(output_path)  # 删除空目录
        return 0  # 返回0，表示目录为空并已删除
    else:
        return 1  # 返回1，表示目录不为空


# 提取项目的标题和文件夹名称
def get_folder_title(source_path, folder_name):
    proj_json_path = source_path / "project.json"
    if proj_json_path.exists():
        with open(proj_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        title = f"{data['title']}_{folder_name}"
    else:
        title = folder_name

    # 清理文件夹名称
    return sanitize_file_name(title)


# 处理文件夹和文件
def process_folders():
    base_path = Path(r"D:\wallpaper_buff\wallpaper2")
    repkg_exe = base_path / "RePKG" / "RePKG.exe"
    output_base = base_path / "output"
    contains = 100
    output_folder_index = 0
    output_base.mkdir(parents=True, exist_ok=True)

    source_base = base_path / "Source"
    folder_names = [folder for folder in source_base.iterdir() if folder.is_dir()]

    # total = len(folder_names)
    file_count = 0
    bar_length = 200

    # 使用 tqdm 显示进度条
    for folder in tqdm(
        folder_names, desc="Processing", ncols=bar_length, unit="folder"
    ):

        # 每处理contains个文件，创建一个新的子文件夹
        output_folder_index = file_count // contains
        output_list = output_base / f"output{output_folder_index}"
        output_list.mkdir(parents=True, exist_ok=True)

        source_path = source_base / folder.name
        title = get_folder_title(source_path, folder.name)

        # 构造输出路径
        output_path = output_list / title
        output_path.mkdir(parents=True, exist_ok=True)


        # 如果存在 scene.pkg 文件，进行提取
        pkg_path = source_path / "scene.pkg"
        if pkg_path.exists():
            cmd = f'"{repkg_exe}" extract "{pkg_path}" -o "{output_path}" -c --overwrite >nul 2>&1'

            # 执行提取命令
            status = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if status.returncode != 0:
                print(f"❌ RePKG 提取失败：{folder.name}")
                continue
        else:
            # 普通文件夹复制
            shutil.copytree(source_path, output_path, dirs_exist_ok=True)

        # 将图片文件复制到根目录
        file_count += copy_images_to_root(output_path)

    print("✅ 所有文件夹处理完成！")


if __name__ == "__main__":
    process_folders()
