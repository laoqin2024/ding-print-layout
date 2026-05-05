#!/usr/bin/env python3
"""
升级 users.json 文件，添加权限控制所需的字段
"""

import json
import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import load_config
from app.services.dingtalk_service import DingTalkService


def upgrade_users_json():
    """升级 users.json 文件"""
    
    print("=" * 80)
    print("🔄 升级 users.json 文件")
    print("=" * 80)
    
    # 1. 备份原文件
    users_file = project_root / "data" / "users.json"
    backup_file = project_root / "data" / "users.json.backup"
    
    print(f"\n📦 备份原文件...")
    with open(users_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 备份完成: {backup_file}")
    
    # 2. 初始化钉钉服务
    print(f"\n🔧 初始化钉钉服务...")
    cfg = load_config()
    ding = DingTalkService(cfg=cfg)
    
    # 3. 获取部门主管信息
    print(f"\n👥 获取部门主管信息...")
    departments_data = data.get("departments", [])
    
    # 处理 departments 可能是列表或字典的情况
    if isinstance(departments_data, list):
        # 如果是列表，转换为字典 {dept_id: dept_info}
        departments = {str(dept.get("dept_id")): dept for dept in departments_data}
    else:
        departments = departments_data
    
    print(f"   共 {len(departments)} 个部门，预计需要 {len(departments) * 0.5:.0f} 秒")
    
    dept_managers = {}  # dept_id -> [userid1, userid2, ...]
    success_count = 0
    fail_count = 0
    
    for idx, (dept_id, dept_info) in enumerate(departments.items(), 1):
        try:
            # 显示进度
            if idx % 10 == 0 or idx == len(departments):
                print(f"   进度: {idx}/{len(departments)} ({idx*100//len(departments)}%)")
            
            # 调用钉钉 API 获取部门详情
            token = ding.get_access_token()
            resp = ding.session.post(
                ding._url("/topapi/v2/department/get"),
                params={"access_token": token},
                json={"dept_id": int(dept_id)},
                timeout=ding.cfg.request_timeout_seconds,
            )
            result = resp.json()
            
            if result.get("errcode") == 0:
                dept_result = result.get("result", {})
                manager_userids = dept_result.get("dept_manager_userid_list", [])
                dept_managers[dept_id] = manager_userids
                
                # 添加到部门信息
                dept_info["manager_userids"] = manager_userids
                dept_info["member_count"] = dept_info.get("member_count", 0)
                
                success_count += 1
                if manager_userids:
                    print(f"  ✅ {dept_info['name']}: {len(manager_userids)} 个主管")
            else:
                print(f"  ⚠️  {dept_info['name']}: {result.get('errmsg')}")
                dept_info["manager_userids"] = []
                dept_info["member_count"] = 0
                fail_count += 1
            
            # 避免请求过快
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  ❌ {dept_info.get('name', dept_id)}: {e}")
            dept_info["manager_userids"] = []
            dept_info["member_count"] = 0
            fail_count += 1
    
    print(f"\n✅ 成功: {success_count} 个部门")
    if fail_count > 0:
        print(f"⚠️  失败: {fail_count} 个部门")
    
    # 4. 更新用户信息
    print(f"\n👤 更新用户信息...")
    users = data.get("users", [])
    
    # 统计部门成员数量
    dept_member_count = {}
    for user in users:
        dept_id = user.get("dept_id")
        if dept_id:
            dept_member_count[dept_id] = dept_member_count.get(dept_id, 0) + 1
    
    # 更新部门成员数量
    for dept_id, count in dept_member_count.items():
        if dept_id in departments:
            departments[dept_id]["member_count"] = count
    
    # 更新用户字段
    manager_count = 0
    for user in users:
        userid = user.get("userid")
        dept_id = user.get("dept_id")
        
        # 检查是否是部门主管
        is_manager = False
        managed_depts = []
        
        for did, manager_ids in dept_managers.items():
            if userid in manager_ids:
                is_manager = True
                managed_depts.append(did)
        
        user["is_dept_manager"] = is_manager
        user["managed_depts"] = managed_depts
        
        if is_manager:
            manager_count += 1
    
    print(f"✅ 更新了 {len(users)} 个用户")
    print(f"✅ 识别了 {manager_count} 个部门主管")
    
    # 5. 保存更新后的文件
    print(f"\n💾 保存更新后的文件...")
    
    # 将 departments 转换回列表格式（如果原来是列表）
    if isinstance(departments_data, list):
        data["departments"] = list(departments.values())
    else:
        data["departments"] = departments
    
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 保存完成: {users_file}")
    
    # 6. 可选：重命名为 dingtalk_cache.json
    print(f"\n📝 是否重命名为 dingtalk_cache.json？")
    print(f"   (保持 users.json 名称也可以正常使用)")
    
    # 7. 显示统计信息
    print(f"\n" + "=" * 80)
    print(f"📊 升级完成统计")
    print(f"=" * 80)
    print(f"✅ 用户总数: {len(users)}")
    print(f"✅ 部门总数: {len(departments)}")
    print(f"✅ 部门主管: {manager_count}")
    print(f"✅ 备份文件: {backup_file}")
    print(f"=" * 80)
    
    # 8. 显示部门主管列表
    print(f"\n👥 部门主管列表:")
    print(f"-" * 80)
    for user in users:
        if user.get("is_dept_manager"):
            managed_dept_names = []
            for dept_id in user.get("managed_depts", []):
                if dept_id in departments:
                    managed_dept_names.append(departments[dept_id]["name"])
            print(f"  - {user['name']} ({user['dept_name']}): {', '.join(managed_dept_names)}")
    print(f"-" * 80)


if __name__ == "__main__":
    try:
        upgrade_users_json()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
