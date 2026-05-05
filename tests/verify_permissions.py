#!/usr/bin/env python3
"""
打印门户权限配置验证工具

用法：
    python3 verify_permissions.py

功能：
    1. 检查 print_layouts.json 中的权限配置
    2. 验证部门名称和用户ID是否存在于 users.json
    3. 生成权限配置报告
"""

import json
from pathlib import Path
from typing import Dict, List, Set


def load_json(file_path: Path) -> dict:
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法加载 {file_path}: {e}")
        return {}


def get_all_depts(users: List[dict]) -> Set[str]:
    """获取所有部门名称"""
    return {u.get('dept_name', '') for u in users if u.get('dept_name')}


def get_all_userids(users: List[dict]) -> Set[str]:
    """获取所有用户ID"""
    return {u.get('userid', '') for u in users if u.get('userid')}


def verify_permissions(base_dir: Path):
    """验证权限配置"""
    
    # 加载配置文件
    layouts_path = base_dir / "data" / "print_layouts.json"
    users_path = base_dir / "data" / "users.json"
    
    layouts = load_json(layouts_path)
    users_data = load_json(users_path)
    users = users_data.get('users', [])
    
    if not layouts:
        print("⚠️  print_layouts.json 为空或无法加载")
        return
    
    if not users:
        print("⚠️  users.json 为空或无法加载")
        return
    
    # 获取所有有效的部门和用户
    valid_depts = get_all_depts(users)
    valid_userids = get_all_userids(users)
    
    print("=" * 80)
    print("打印门户权限配置验证报告")
    print("=" * 80)
    print(f"\n📊 统计信息：")
    print(f"   - 流程总数: {len(layouts)}")
    print(f"   - 用户总数: {len(users)}")
    print(f"   - 部门总数: {len(valid_depts)}")
    print(f"\n📋 有效部门列表：")
    for dept in sorted(valid_depts):
        print(f"   - {dept}")
    
    # 验证每个流程的权限配置
    print(f"\n🔍 权限配置检查：\n")
    
    has_errors = False
    processes_with_permissions = 0
    processes_without_permissions = 0
    
    for p_code, p_info in layouts.items():
        p_name = p_info.get('name', p_code)
        permissions = p_info.get('permissions')
        
        if not permissions:
            processes_without_permissions += 1
            print(f"✓ {p_name} ({p_code})")
            print(f"  └─ 无权限配置（所有用户可见）\n")
            continue
        
        processes_with_permissions += 1
        print(f"🔒 {p_name} ({p_code})")
        
        # 检查部门权限
        allowed_depts = permissions.get('allowed_depts', [])
        if allowed_depts:
            print(f"  ├─ 允许部门: {len(allowed_depts)} 个")
            for dept in allowed_depts:
                if dept in valid_depts:
                    print(f"  │  ✓ {dept}")
                else:
                    print(f"  │  ❌ {dept} (不存在于 users.json)")
                    has_errors = True
        
        # 检查用户权限
        allowed_users = permissions.get('allowed_users', [])
        if allowed_users:
            print(f"  └─ 允许用户: {len(allowed_users)} 个")
            for userid in allowed_users:
                user = next((u for u in users if u.get('userid') == userid), None)
                if user:
                    print(f"     ✓ {user.get('name', '未知')} ({userid})")
                else:
                    print(f"     ❌ {userid} (不存在于 users.json)")
                    has_errors = True
        
        print()
    
    # 总结
    print("=" * 80)
    print("📈 总结：")
    print(f"   - 配置了权限的流程: {processes_with_permissions} 个")
    print(f"   - 未配置权限的流程: {processes_without_permissions} 个")
    
    if has_errors:
        print(f"\n❌ 发现配置错误！请检查上述标记为 ❌ 的项目")
        print(f"   建议：")
        print(f"   1. 访问 /admin/users 同步最新用户信息")
        print(f"   2. 检查部门名称和用户ID是否正确")
        print(f"   3. 修正 print_layouts.json 中的配置")
    else:
        print(f"\n✅ 所有权限配置验证通过！")
    
    print("=" * 80)


def main():
    """主函数"""
    # 获取项目根目录
    base_dir = Path(__file__).resolve().parent
    verify_permissions(base_dir)


if __name__ == "__main__":
    main()
