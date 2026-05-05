from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from app.config import AppConfig


class DingTalkError(RuntimeError):
    pass


def normalize_process_code(process_code: str | None) -> str:
    # Hard requirement: keep .strip() cleanup logic
    return (process_code or "").strip()


@dataclass
class DingTalkService:
    cfg: AppConfig
    session: requests.Session = requests.Session()

    @staticmethod
    def normalize_code(process_code: str | None) -> str:
        # Hard requirement: keep .strip() cleanup logic
        return normalize_process_code(process_code)

    def _url(self, path: str) -> str:
        base = (self.cfg.oapi_base or "https://oapi.dingtalk.com").rstrip("/")
        path = path if path.startswith("/") else f"/{path}"
        return f"{base}{path}"

    def get_access_token(self) -> str:
        """
        Calls: GET /gettoken?appkey=...&appsecret=...
        Returns access_token string.
        """
        try:
            resp = self.session.get(
                self._url("/gettoken"),
                params={"appkey": self.cfg.app_key, "appsecret": self.cfg.app_secret},
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"gettoken request failed: {e}") from e

        token = data.get("access_token")
        if not token:
            raise DingTalkError(f"gettoken failed: {data}")
        return token

    def get_userid_by_auth_code(self, auth_code: str) -> str:
        """
        Calls: POST /topapi/v2/user/getuserinfo?access_token=...
        Returns userid.
        """
        token = self.get_access_token()
        try:
            resp = self.session.post(
                self._url("/topapi/v2/user/getuserinfo"),
                params={"access_token": token},
                json={"code": auth_code},
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"getuserinfo request failed: {e}") from e

        userid = (data.get("result") or {}).get("userid")
        if not userid:
            raise DingTalkError(f"getuserinfo failed: {data}")
        return userid

    def get_user_detail(self, userid: str) -> Dict[str, Any]:
        """
        Calls: POST /topapi/v2/user/get?access_token=...
        Returns result dict for a user.
        """
        uid = str(userid or "").strip()
        if not uid:
            raise DingTalkError("get_user_detail missing userid")
        token = self.get_access_token()
        try:
            resp = self.session.post(
                self._url("/topapi/v2/user/get"),
                params={"access_token": token},
                json={"userid": uid, "language": "zh_CN"},
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"user/get request failed: {e}") from e
        if data.get("errcode") != 0:
            raise DingTalkError(f"user/get failed: {data}")
        return dict(data.get("result") or {})

    def get_department_name(self, dept_id: int | str) -> str:
        """
        Calls: POST /topapi/v2/department/get?access_token=...
        Returns department name.
        """
        did = str(dept_id or "").strip()
        if not did:
            return ""
        token = self.get_access_token()
        try:
            resp = self.session.post(
                self._url("/topapi/v2/department/get"),
                params={"access_token": token},
                json={"dept_id": int(did), "language": "zh_CN"},
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"department/get request failed: {e}") from e
        if data.get("errcode") != 0:
            raise DingTalkError(f"department/get failed: {data}")
        return str((data.get("result") or {}).get("name") or "").strip()

    def list_process_instance_ids(
        self,
        process_code: str,
        userid: str,
        *,
        start_time_ms: Optional[int] = None,
        cursor: int = 0,
        size: int = 15,
    ) -> List[str]:
        """
        Calls: POST /topapi/processinstance/listids?access_token=...
        Returns list of instance IDs (strings).
        """
        token = self.get_access_token()
        p_code = DingTalkService.normalize_code(process_code)

        if start_time_ms is None:
            # Keep prior default behavior: last 120 days
            start_time_ms = int((time.time() - 120 * 24 * 3600) * 1000)

        payload = {
            "process_code": p_code,
            "start_time": start_time_ms,
            "userid": userid,
            "cursor": cursor,
            "size": size,
        }
        try:
            resp = self.session.post(
                self._url("/topapi/processinstance/listids"),
                params={"access_token": token},
                json=payload,
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"listids request failed: {e}") from e

        if data.get("errcode") != 0:
            raise DingTalkError(f"listids failed: {data}")
        return list(((data.get("result") or {}).get("list")) or [])

    def get_process_instance(self, process_instance_id: str) -> Dict[str, Any]:
        """
        Calls: POST /topapi/processinstance/get?access_token=...
        Returns process_instance dict (as-is from DingTalk).
        """
        token = self.get_access_token()
        try:
            resp = self.session.post(
                self._url("/topapi/processinstance/get"),
                params={"access_token": token},
                json={"process_instance_id": process_instance_id},
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"processinstance/get request failed: {e}") from e

        instance = data.get("process_instance")
        if not instance:
            raise DingTalkError(f"processinstance/get failed: {data}")
        return instance

    def get_process_attachment_url(self, *, process_instance_id: str, file_id: str) -> str:
        """
        Calls: POST /v1.0/workflow/processInstances/spaces/files/urls/download
        Returns downloadable attachment URL.
        """
        token = self.get_access_token()
        payload = {"processInstanceId": process_instance_id, "fileId": file_id}
        try:
            resp = self.session.post(
                "https://api.dingtalk.com/v1.0/workflow/processInstances/spaces/files/urls/download",
                headers={"x-acs-dingtalk-access-token": token},
                json=payload,
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"workflow attachment download-url request failed: {e}") from e

        if data.get("success") is False:
            raise DingTalkError(f"workflow attachment download-url failed: {data}")

        result = data.get("result") or {}
        url = str((result or {}).get("downloadUri") or "").strip()
        if not url:
            raise DingTalkError(f"workflow attachment download-url missing url: {data}")
        return url

    def download_process_attachment_pdf(self, *, process_instance_id: str, instance: Dict[str, Any]) -> Optional[bytes]:
        """
        Best effort: pick the first PDF in DDAttachment fields and download bytes.
        Returns None if no PDF attachment found or download fails.
        """
        for f in (instance or {}).get("form_component_values", []) or []:
            if str(f.get("component_type") or "") != "DDAttachment":
                continue
            raw = f.get("value")
            if not isinstance(raw, str) or not raw.strip().startswith("["):
                continue
            try:
                arr = json.loads(raw)
            except Exception:
                continue
            if not isinstance(arr, list):
                continue
            for item in arr:
                if not isinstance(item, dict):
                    continue
                file_type = str(item.get("fileType") or "").strip().lower()
                file_name = str(item.get("fileName") or "").strip().lower()
                file_id = str(item.get("fileId") or "").strip()
                if not file_id:
                    continue
                if file_type != "pdf" and not file_name.endswith(".pdf"):
                    continue
                try:
                    down_url = self.get_process_attachment_url(process_instance_id=process_instance_id, file_id=file_id)
                    res = self.session.get(down_url, timeout=self.cfg.request_timeout_seconds)
                    if res.status_code == 200 and res.content.startswith(b"%PDF"):
                        return res.content
                except Exception:
                    continue
        return None

    def download_specific_attachment_pdf(self, *, instance: Dict[str, Any], field_id: str, attachment_index: int = 0) -> Optional[bytes]:
        """
        Download a specific PDF attachment by field_id and attachment_index.
        
        Args:
            instance: Process instance data
            field_id: The field ID (e.g., "DDAttachment_1PKSP5YV9WRGG")
            attachment_index: Index of the attachment in the field (0-based)
        
        Returns:
            PDF bytes or None if not found
        """
        print(f"[DEBUG] download_specific_attachment_pdf 开始")
        print(f"[DEBUG] field_id: {field_id}")
        print(f"[DEBUG] attachment_index: {attachment_index}")
        
        # Find the specific field
        for f in (instance or {}).get("form_component_values", []) or []:
            if str(f.get("id") or "").strip() != field_id:
                continue
            
            print(f"[DEBUG] 找到字段: {field_id}")
            
            # Parse attachment value
            raw = f.get("value")
            print(f"[DEBUG] 字段原始值: {raw[:200] if raw else None}...")
            
            if not isinstance(raw, str) or not raw.strip().startswith("["):
                print(f"[DEBUG] 字段值格式不对，不是 JSON 数组")
                continue
            
            try:
                arr = json.loads(raw)
                print(f"[DEBUG] 解析成功，附件数量: {len(arr)}")
            except Exception as e:
                print(f"[DEBUG] JSON 解析失败: {e}")
                continue
            
            if not isinstance(arr, list):
                print(f"[DEBUG] 解析结果不是数组")
                continue
            
            # Check if attachment_index is valid
            if attachment_index >= len(arr):
                print(f"[DEBUG] attachment_index {attachment_index} 超出范围 (总数: {len(arr)})")
                continue
            
            # Get the specific attachment
            item = arr[attachment_index]
            print(f"[DEBUG] 附件项: {item}")
            
            if not isinstance(item, dict):
                print(f"[DEBUG] 附件项不是字典")
                continue
            
            file_type = str(item.get("fileType") or "").strip().lower()
            file_name = str(item.get("fileName") or "").strip().lower()
            file_id = str(item.get("fileId") or "").strip()
            
            print(f"[DEBUG] fileType: {file_type}")
            print(f"[DEBUG] fileName: {file_name}")
            print(f"[DEBUG] fileId: {file_id}")
            
            if not file_id:
                print(f"[DEBUG] fileId 为空")
                continue
            
            # Check if it's a PDF
            if file_type != "pdf" and not file_name.endswith(".pdf"):
                print(f"[DEBUG] 不是 PDF 文件")
                continue
            
            # Download the PDF
            try:
                # Get process_instance_id from instance
                process_instance_id = str(instance.get("process_instance_id") or instance.get("processInstanceId") or "").strip()
                print(f"[DEBUG] process_instance_id: {process_instance_id}")
                
                if not process_instance_id:
                    print(f"[DEBUG] process_instance_id 为空")
                    continue
                
                print(f"[DEBUG] 调用 get_process_attachment_url")
                down_url = self.get_process_attachment_url(process_instance_id=process_instance_id, file_id=file_id)
                print(f"[DEBUG] 下载 URL: {down_url}")
                
                res = self.session.get(down_url, timeout=self.cfg.request_timeout_seconds)
                print(f"[DEBUG] 下载响应状态: {res.status_code}, 大小: {len(res.content)} bytes")
                
                if res.status_code == 200 and res.content.startswith(b"%PDF"):
                    print(f"[DEBUG] ✅ PDF 下载成功")
                    return res.content
                else:
                    print(f"[DEBUG] ❌ 不是有效的 PDF")
            except Exception as e:
                print(f"[DEBUG] ❌ 下载失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"[DEBUG] ❌ 未找到匹配的附件")
        return None

    def list_processes_by_userid_page(
        self, *, userid: Optional[str] = None, cursor: int = 0, size: int = 100
    ) -> tuple[List[Dict[str, Any]], Optional[int]]:
        """
        Single page of POST /topapi/process/listbyuserid.
        钉钉文档：下一页必须把 offset 设为上一页 result.next_cursor（不是 offset+size）。
        userid 不传：企业下全部审批表单（可见范围内）；传入：该员工可见表单。
        """
        token = self.get_access_token()
        body: Dict[str, Any] = {"offset": int(cursor), "size": int(size)}
        u = (userid or "").strip()
        if u:
            body["userid"] = u
        try:
            resp = self.session.post(
                self._url("/topapi/process/listbyuserid"),
                params={"access_token": token},
                json=body,
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"process/listbyuserid request failed: {e}") from e

        if data.get("errcode") != 0:
            raise DingTalkError(f"process/listbyuserid failed: {data}")
        result = data.get("result") or {}
        batch = list(result.get("process_list") or [])
        raw_next = result.get("next_cursor")
        if raw_next is None:
            raw_next = result.get("nextCursor")
        next_cursor: Optional[int]
        if raw_next is None or raw_next == "":
            next_cursor = None
        else:
            try:
                next_cursor = int(raw_next)
            except (TypeError, ValueError):
                next_cursor = None
        return batch, next_cursor

    def list_processes_by_userid(
        self, *, userid: Optional[str] = None, offset: int = 0, size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calls: POST /topapi/process/listbyuserid?access_token=...
        仅取一页；全量请用 list_all_processes_by_userid。
        """
        items, _ = self.list_processes_by_userid_page(userid=userid, cursor=offset, size=size)
        return items

    def list_all_processes_by_userid(
        self,
        *,
        userid: Optional[str] = None,
        page_size: int = 100,
        max_pages: int = 500,
    ) -> tuple[List[Dict[str, Any]], bool]:
        """
        按钉钉 next_cursor 分页拉全量，直到无 next_cursor 或达到 max_pages。
        userid 为 None/空：不传 userid，拉「企业下」表单列表（通常多于单人可见）。
        """
        page_size = max(1, min(int(page_size), 100))
        max_pages = max(1, min(int(max_pages), 500))
        seen: set[str] = set()
        out: List[Dict[str, Any]] = []
        cursor = 0
        capped = False
        uid = (userid or "").strip() or None
        for _ in range(max_pages):
            batch, next_cur = self.list_processes_by_userid_page(userid=uid, cursor=cursor, size=page_size)
            if not batch:
                break
            for p in batch:
                if not isinstance(p, dict):
                    continue
                code = self.normalize_code(p.get("process_code") or p.get("processCode") or "")
                if not code or code in seen:
                    continue
                seen.add(code)
                out.append(p)
            if next_cur is None:
                break
            try:
                nxt = int(next_cur)
            except (TypeError, ValueError):
                break
            if nxt == cursor:
                break
            cursor = nxt
        else:
            capped = True
        return out, capped

    def _normalize_openapi_template_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAPI camelCase → 与本项目其它流程列表字段对齐，便于分组与兼容旧逻辑。"""
        if not isinstance(row, dict):
            return {}
        code = self.normalize_code(row.get("processCode") or row.get("process_code"))
        if not code:
            return {}
        d = dict(row)
        d["process_code"] = code
        if row.get("name"):
            d["name"] = str(row.get("name"))
        dn = row.get("dirName") or row.get("dir_name")
        if dn is not None and str(dn).strip():
            d["dir_name"] = str(dn).strip()
        iu = row.get("iconUrl") or row.get("icon_url")
        if iu:
            d["icon_url"] = str(iu)
        return d

    def list_user_visible_templates_openapi_page(
        self,
        *,
        userid: Optional[str] = None,
        next_token: int = 0,
        max_results: int = 100,
    ) -> tuple[List[Dict[str, Any]], Optional[int]]:
        """
        GET /v1.0/workflow/processes/userVisibilities/templates
        Header: x-acs-dingtalk-access-token（企业内部应用与普通 gettoken 一致）
        userId 不传：企业下全部审批表单。返回含 dirName / dirId，用于前端两级分组。
        """
        token = self.get_access_token()
        mr = max(1, min(int(max_results), 100))
        params: Dict[str, Any] = {"maxResults": mr, "nextToken": int(next_token)}
        u = (userid or "").strip()
        if u:
            params["userId"] = u
        try:
            resp = self.session.get(
                "https://api.dingtalk.com/v1.0/workflow/processes/userVisibilities/templates",
                params=params,
                headers={
                    "x-acs-dingtalk-access-token": token,
                    "Content-Type": "application/json",
                },
                timeout=self.cfg.request_timeout_seconds,
            )
            raw = resp.json()
        except Exception as e:
            raise DingTalkError(f"openapi userVisibilities/templates request failed: {e}") from e
        if resp.status_code >= 400:
            raise DingTalkError(f"openapi userVisibilities/templates HTTP {resp.status_code}: {raw}")

        result = raw.get("result")
        if not isinstance(result, dict):
            raise DingTalkError(f"openapi userVisibilities/templates bad response: {raw}")

        plist = result.get("processList")
        if plist is None:
            plist = result.get("process_list")
        batch = list(plist or [])
        nt_raw = result.get("nextToken")
        if nt_raw is None:
            nt_raw = result.get("next_token")

        norm_batch: List[Dict[str, Any]] = []
        for row in batch:
            merged = self._normalize_openapi_template_row(row if isinstance(row, dict) else {})
            if merged:
                norm_batch.append(merged)

        next_nt: Optional[int]
        if nt_raw is None or nt_raw == "":
            next_nt = None
        else:
            try:
                next_nt = int(nt_raw)
            except (TypeError, ValueError):
                next_nt = None
        return norm_batch, next_nt

    def list_all_user_visible_templates_openapi(
        self,
        *,
        userid: Optional[str] = None,
        page_size: int = 100,
        max_pages: int = 500,
    ) -> tuple[List[Dict[str, Any]], bool]:
        """游标字段为 nextToken；与旧版 offset/next_cursor 不同。"""
        page_size = max(1, min(int(page_size), 100))
        max_pages = max(1, min(int(max_pages), 500))
        uid = (userid or "").strip() or None
        seen: set[str] = set()
        out: List[Dict[str, Any]] = []
        next_token = 0
        capped = False
        for _ in range(max_pages):
            batch, nxt = self.list_user_visible_templates_openapi_page(
                userid=uid, next_token=next_token, max_results=page_size
            )
            if not batch:
                break
            for p in batch:
                c = self.normalize_code(p.get("process_code"))
                if not c or c in seen:
                    continue
                seen.add(c)
                out.append(p)
            if nxt is None:
                break
            if int(nxt) == int(next_token):
                break
            next_token = int(nxt)
        else:
            capped = True
        return out, capped

    def list_all_approval_templates(
        self,
        *,
        userid: Optional[str] = None,
        page_size: int = 100,
        max_pages: int = 500,
    ) -> tuple[List[Dict[str, Any]], bool, str]:
        """
        优先使用新版 Workflow OpenAPI（含 dirName）；失败时降级 topapi/process/listbyuserid。
        返回 (templates, capped, backend) backend 为 'openapi' | 'topapi_fallback'。
        """
        try:
            items, cap = self.list_all_user_visible_templates_openapi(
                userid=userid, page_size=page_size, max_pages=max_pages
            )
            return items, cap, "openapi"
        except DingTalkError:
            items, cap = self.list_all_processes_by_userid(
                userid=userid, page_size=page_size, max_pages=max_pages
            )
            return items, cap, "topapi_fallback"


    def get_department_list(self, dept_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get department list from DingTalk
        Calls: POST /topapi/v2/department/listsub
        """
        token = self.get_access_token()
        payload = {}
        if dept_id:
            payload["dept_id"] = int(dept_id)
        
        try:
            resp = self.session.post(
                self._url("/topapi/v2/department/listsub"),
                params={"access_token": token},
                json=payload,
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"department/listsub request failed: {e}") from e
        
        if data.get("errcode") != 0:
            raise DingTalkError(f"department/listsub failed: {data}")
        
        return list(data.get("result") or [])

    def get_dept_user_list(self, dept_id: str) -> List[Dict[str, Any]]:
        """
        Get user list in a department
        Calls: POST /topapi/user/listsimple
        """
        token = self.get_access_token()
        
        try:
            resp = self.session.post(
                self._url("/topapi/user/listsimple"),
                params={"access_token": token},
                json={"dept_id": int(dept_id), "cursor": 0, "size": 100},
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"user/listsimple request failed: {e}") from e
        
        if data.get("errcode") != 0:
            raise DingTalkError(f"user/listsimple failed: {data}")
        
        return list((data.get("result") or {}).get("list") or [])

    def get_jsapi_config(self, url: str) -> Dict[str, Any]:
        """
        生成钉钉 JSAPI 配置，用于前端 dd.config() 调用
        
        文档: https://open.dingtalk.com/document/orgapp/jsapi-overview
        
        Args:
            url: 当前页面的完整 URL（用于签名）
        
        Returns:
            包含 corpId, timeStamp, nonceStr, signature 的字典
        """
        import hashlib
        import random
        import string
        
        # 1. 获取 jsapi_ticket
        token = self.get_access_token()
        try:
            resp = self.session.get(
                self._url("/get_jsapi_ticket"),
                params={"access_token": token},
                timeout=self.cfg.request_timeout_seconds,
            )
            data = resp.json()
        except Exception as e:
            raise DingTalkError(f"get_jsapi_ticket request failed: {e}") from e
        
        ticket = data.get("ticket")
        if not ticket:
            raise DingTalkError(f"get_jsapi_ticket failed: {data}")
        
        # 2. 生成签名参数
        noncestr = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        timestamp = str(int(time.time() * 1000))
        
        # 3. 签名算法（按字典序拼接）
        sign_str = f"jsapi_ticket={ticket}&noncestr={noncestr}&timestamp={timestamp}&url={url}"
        signature = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
        
        # 4. 返回配置（企业内部应用不需要 agentId）
        return {
            "corpId": self.cfg.corp_id,
            "timeStamp": timestamp,
            "nonceStr": noncestr,
            "signature": signature,
            "jsApiList": ["biz.util.print"]
        }

