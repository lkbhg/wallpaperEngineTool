import os
import json
import shutil
import re
import subprocess
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


# 清理文件夹名称（移除非法字符和控制字符）
def sanitize_file_name(name):
    max_length = 63

    # 删除 Windows 禁止的字符
    name = re.sub(r'[\/:*?"<>|&]', "_", name)

    # 删除控制字符（ASCII 0-31）
    name = re.sub(r"[\x00-\x1F]", "", name)

    # 删除代理对（高位 Unicode，通常用于 emoji）
    name = re.sub(r"[\uD800-\uDBFF][\uDC00-\uDFFF]", "", name)

    # 删除多余空格
    name = re.sub(r"\s+", "", name)

    # 限制文件名的最大长度
    name = name[:max_length]

    return name.strip()


def copy_images_to_root(output_path):

    special_list = {"waterripplenormal.png"}
    keywords = {"_mask_"}
    for root, dirs, files in os.walk(output_path, topdown=False):
        for file_name in files:
            file_path = Path(root) / file_name

            Name = file_path.stem.lower()
            # 检查文件是否是图片文件（PNG, JPG, JPEG）
            ext = file_path.suffix.lower()
            if (
                (
                    ext in {".png", ".jpg", ".jpeg", ".mp4", ".gif"}
                    and Name not in {"preview"}
                )
                and file_path.name not in special_list
                and not any(keyword in file_name.lower() for keyword in keywords)
            ):
                # 获取图片文件大小，单位KB
                file_size = file_path.stat().st_size / 1024

                # 如果大于20KB，则剪切到根目录
                if file_size > 20:
                    shutil.move(file_path, output_path / file_name)
                else:
                    # 删除小的图片
                    file_path.unlink()
            elif Name in {"preview"}:
                continue
            else:
                # 删除非图片文件
                file_path.unlink()

        # 如果当前目录为空，删除它
        if not os.listdir(root) and not root == str(output_path):
            os.rmdir(root)

    # 最后检查根目录是否为空，如果为空则删除根目录
    if not os.listdir(output_path):
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


# 分割文件夹
def split_folders(output_base, contains):
    Group = "group"
    Selected = "selected"
    Mp4 = "mp4"

    # 获取所有项目文件夹
    all_folders = [folder for folder in output_base.iterdir() if folder.is_dir()]

    # 分割文件夹
    folder_index = 0
    current_folder = output_base / f"output{folder_index}"
    current_folder.mkdir(parents=True, exist_ok=True)

    file_count = 0
    bar_length = 200

    # 使用 tqdm 显示进度条
    for folder in tqdm(all_folders, desc="Processing", ncols=bar_length, unit="folder"):
        folder_index = file_count // contains
        current_folder = output_base / f"output{folder_index}"
        current_folder.mkdir(parents=True, exist_ok=True)

        # 检查文件夹中所有文件的后缀名
        include_video = False
        for file in os.listdir(folder):
            file_path = Path(folder) / file
            if file_path.suffix.lower() in [".mp4", ".gif"]:  # 忽略大小写
                include_video = True
                break  # 一旦发现 .mp4 或 .gif 文件就可以停止遍历

        if include_video:
            # 如果包含 .mp4 或 .gif 文件，移动文件夹到 Mp4 文件夹
            Mp4_path = current_folder / Mp4
            Mp4_path.mkdir(parents=True, exist_ok=True)
            shutil.move(Path(folder), Mp4_path)
            # print(f"✅ {folder.name} 已移入 Mp4 文件夹")
            file_count += 1
            continue

        # 检查是否包含preview
        for file in os.listdir(folder):
            file_path = Path(folder) / file
            if (
                file_path.stem.lower() in ["preview"] and len(os.listdir(folder)) == 2
            ):  # 忽略大小写
                file_path.unlink()
                break  # 一旦发现 preview 文件就可以停止遍历

        if len(os.listdir(folder)) == 1:
            # 将当前文件移动到select文件夹
            file_names = os.listdir(folder)
            file_name = folder.name + Path(file_names[0]).suffix
            Selected_path = current_folder / Selected
            Selected_path.mkdir(parents=True, exist_ok=True)
            file_path = Selected_path / file_name
            shutil.move(Path(folder) / file_names[0], file_path)
            os.rmdir(folder)
            file_count += 1
            continue

        else:
            Group_path = current_folder / Group
            Group_path.mkdir(parents=True, exist_ok=True)
            # 将当前文件夹移动到group分割文件夹
            shutil.move(Path(folder), Group_path)
            file_count += 1

    print(f"✅ {file_count}个文件夹已按每 {contains} 项目分割完成！")


# 处理文件夹和文件
def process_folder(folder, base_path, repkg_exe, output_base):
    file_count = 0
    source_path = base_path / "Source" / folder.name
    title = get_folder_title(source_path, folder.name)

    # output_list = output_base / f"output{output_folder_index}"
    output_list = output_base
    output_list.mkdir(parents=True, exist_ok=True)

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
            return

    else:
        # 普通文件夹复制
        shutil.copytree(source_path, output_path, dirs_exist_ok=True)

    # 将图片文件复制到根目录
    file_count += copy_images_to_root(output_path)

    return file_count


def process_folders():
    root_path = Path(r"D:\wallpaper_buff")
    base_path = root_path / "wallpaper2"
    repkg_exe = root_path / "RePKG" / "RePKG.exe"
    output_base = base_path / "output"
    contains = 100
    output_base.mkdir(parents=True, exist_ok=True)

    source_base = base_path / "Source"
    folder_names = [folder for folder in source_base.iterdir() if folder.is_dir()]

    # 使用 ThreadPoolExecutor 来并行处理每个文件夹
    futures = []
    with ThreadPoolExecutor() as executor:
        for folder in tqdm(folder_names, desc="Processing", ncols=200, unit="folder"):
            futures.append(
                executor.submit(
                    process_folder, folder, base_path, repkg_exe, output_base
                )
            )

        # # 等待所有任务完成
        # total_file_count = 0
        # for future in as_completed(futures):
        #     total_file_count += future.result()  # 获取每个任务的返回值

        # 等待所有任务完成
        for future in futures:
            future.result()  # 等待任务完成

        # 获取并打印线程池中分配的线程数量
        print(
            f"Total number of threads in the ThreadPoolExecutor: {len(executor._threads)}"
        )

    print(f"✅ 所有文件夹处理完成！")

    split_folders(output_base, contains)


if __name__ == "__main__":
    process_folders()
