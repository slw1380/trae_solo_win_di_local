"""
Git操作Skill - 用于自动化Git操作

使用方法:
1. 在SOLO中调用此Skill
2. 提供操作类型和参数
3. 自动执行Git命令

支持的操作:
- status: 查看状态
- add: 添加文件
- commit: 提交代码
- push: 推送到远程
- pull: 拉取代码
- log: 查看日志
"""

import subprocess
import sys
from typing import Optional

# 配置
PROJECT_DIR = r"e:\slw\trae_solo_cn_workspace\ollama-tui-agent"
GIT_PATH = r"D:\Program Files\Git\bin\git.exe"


def run_git_command(args: list[str], cwd: str = PROJECT_DIR) -> tuple[bool, str, str]:
    """
    执行Git命令
    
    Args:
        args: Git命令参数列表
        cwd: 工作目录
        
    Returns:
        (是否成功, 标准输出, 标准错误)
    """
    try:
        result = subprocess.run(
            [GIT_PATH] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=False
        )
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def git_status() -> str:
    """查看Git状态"""
    success, stdout, stderr = run_git_command(["status"])
    if success:
        return stdout
    return f"错误: {stderr}"


def git_add(files: str = ".") -> str:
    """
    添加文件到暂存区
    
    Args:
        files: 文件路径，默认为所有文件
    """
    success, stdout, stderr = run_git_command(["add", files])
    if success:
        return f"成功添加文件: {files}\n{stdout}"
    return f"添加失败: {stderr}"


def git_commit(message: str) -> str:
    """
    提交代码
    
    Args:
        message: 提交信息
    """
    success, stdout, stderr = run_git_command(["commit", "-m", message])
    if success:
        return f"提交成功:\n{stdout}"
    return f"提交失败: {stderr}"


def git_push(branch: str = "main", force: bool = False) -> str:
    """
    推送到远程仓库
    
    Args:
        branch: 分支名，默认为main
        force: 是否强制推送
    """
    args = ["push", "-u", "origin", branch]
    if force:
        args.append("--force")
    
    success, stdout, stderr = run_git_command(args)
    if success:
        return f"推送成功:\n{stdout}"
    return f"推送失败: {stderr}"


def git_pull(branch: str = "main") -> str:
    """
    从远程仓库拉取代码
    
    Args:
        branch: 分支名，默认为main
    """
    success, stdout, stderr = run_git_command(["pull", "origin", branch])
    if success:
        return f"拉取成功:\n{stdout}"
    return f"拉取失败: {stderr}"


def git_log(n: int = 5) -> str:
    """
    查看提交日志
    
    Args:
        n: 显示最近的n条记录，默认为5
    """
    success, stdout, stderr = run_git_command(["log", "--oneline", "-n", str(n)])
    if success:
        return f"最近{n}次提交:\n{stdout}"
    return f"查看日志失败: {stderr}"


def git_full_push(message: str, files: str = ".", branch: str = "main") -> str:
    """
    完整推送流程：添加 -> 提交 -> 推送
    
    Args:
        message: 提交信息
        files: 要添加的文件，默认为所有
        branch: 分支名，默认为main
    """
    results = []
    
    # 1. 添加文件
    success, stdout, stderr = run_git_command(["add", files])
    if not success:
        return f"添加文件失败: {stderr}"
    results.append("✅ 文件已添加到暂存区")
    
    # 2. 提交
    success, stdout, stderr = run_git_command(["commit", "-m", message])
    if not success:
        return f"提交失败: {stderr}"
    results.append(f"✅ 提交成功: {message}")
    
    # 3. 推送
    success, stdout, stderr = run_git_command(["push", "-u", "origin", branch])
    if not success:
        return f"推送失败: {stderr}"
    results.append("✅ 推送到GitHub成功")
    
    return "\n".join(results)


# 主函数，用于命令行调用
def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python git_skill.py <命令> [参数]")
        print("")
        print("可用命令:")
        print("  status              查看Git状态")
        print("  add [文件]          添加文件（默认所有）")
        print("  commit <信息>       提交代码")
        print("  push [分支]         推送到远程")
        print("  pull [分支]         拉取代码")
        print("  log [数量]          查看日志")
        print("  full-push <信息>    完整推送流程")
        print("")
        print("示例:")
        print('  python git_skill.py commit "更新代码"')
        print('  python git_skill.py full-push "修复bug"')
        return
    
    command = sys.argv[1]
    
    if command == "status":
        print(git_status())
    elif command == "add":
        files = sys.argv[2] if len(sys.argv) > 2 else "."
        print(git_add(files))
    elif command == "commit":
        if len(sys.argv) < 3:
            print("错误: 请提供提交信息")
            return
        print(git_commit(sys.argv[2]))
    elif command == "push":
        branch = sys.argv[2] if len(sys.argv) > 2 else "main"
        print(git_push(branch))
    elif command == "pull":
        branch = sys.argv[2] if len(sys.argv) > 2 else "main"
        print(git_pull(branch))
    elif command == "log":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        print(git_log(n))
    elif command == "full-push":
        if len(sys.argv) < 3:
            print("错误: 请提供提交信息")
            return
        print(git_full_push(sys.argv[2]))
    else:
        print(f"未知命令: {command}")
        print("使用 'python git_skill.py' 查看帮助")


if __name__ == "__main__":
    main()
