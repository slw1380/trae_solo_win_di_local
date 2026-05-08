import subprocess
import sys

# 配置
PROJECT_DIR = r"e:\slw\trae_solo_cn_workspace\ollama-tui-agent"
PYTHON_PATH = r"C:\Users\di\AppData\Local\Python\pythoncore-3.14-64\python.exe"

def run_git_command(args):
    """执行Git命令"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            shell=True
        )
        print(f"命令: git {' '.join(args)}")
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False

def main():
    print("=" * 50)
    print("Git 自动提交脚本")
    print("=" * 50)
    
    # 1. 添加文件
    print("\n[1/4] 添加文件...")
    if not run_git_command(["add", "README.md"]):
        print("添加文件失败")
        return
    
    # 2. 提交
    print("\n[2/4] 提交代码...")
    if not run_git_command(["commit", "-m", "fix: update README format"]):
        print("提交失败")
        return
    
    # 3. 设置远程仓库
    print("\n[3/4] 设置远程仓库...")
    run_git_command(["remote", "remove", "origin"])
    if not run_git_command(["remote", "add", "origin", "https://github.com/slw1380/trae_solo_win_di_local.git"]):
        print("设置远程仓库失败")
        return
    
    # 4. 推送
    print("\n[4/4] 推送到GitHub...")
    if not run_git_command(["push", "-u", "origin", "main", "--force"]):
        print("推送失败")
        return
    
    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
