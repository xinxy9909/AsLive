"""
Monitor Agent - Tools 定义模块
定义所有可用的工具函数
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional
from .monitor_state import MonitorState, CameraStatus

logger = logging.getLogger(__name__)


class MonitorTools:
    """监控Agent工具集"""
    
    def __init__(self, state: MonitorState):
        """初始化工具集"""
        self.state = state
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """定义所有可用工具"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_cameras",
                    "description": "列出指定平台的所有摄像头",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "platform": {
                                "type": "string",
                                "description": "平台名称: JinLiLite 或 ChiWen",
                                "enum": ["JinLiLite", "ChiWen", "all"]
                            }
                        },
                        "required": ["platform"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "zoom_camera",
                    "description": "放大指定的摄像头，使其全屏显示或指定大小",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "camera_name": {
                                "type": "string",
                                "description": "摄像头名称，如 JinLiLite1, ChiWen2 等"
                            },
                            "zoom_level": {
                                "type": "string",
                                "description": "放大级别: fullscreen(全屏), large(大), medium(中), small(小)",
                                "enum": ["fullscreen", "large", "medium", "small"],
                                "default": "fullscreen"
                            }
                        },
                        "required": ["camera_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "hide_camera",
                    "description": "隐藏指定的摄像头",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "camera_name": {
                                "type": "string",
                                "description": "摄像头名称"
                            }
                        },
                        "required": ["camera_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "hide_all_cameras",
                    "description": "隐藏指定平台或所有平台的全部摄像头",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "platform": {
                                "type": "string",
                                "description": "平台名称，不指定则隐藏所有平台",
                                "enum": ["JinLiLite", "ChiWen", "all"]
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "show_camera",
                    "description": "显示之前隐藏的摄像头",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "camera_name": {
                                "type": "string",
                                "description": "摄像头名称"
                            }
                        },
                        "required": ["camera_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_camera_status",
                    "description": "获取摄像头或所有摄像头的状态信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "camera_name": {
                                "type": "string",
                                "description": "摄像头名称，不指定则返回所有摄像头状态"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "show_all_cameras",
                    "description": "显示指定平台或所有平台的全部摄像头",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "platform": {
                                "type": "string",
                                "description": "平台名称，不指定则显示所有平台",
                                "enum": ["JinLiLite", "ChiWen", "all"]
                            }
                        }
                    }
                }
            }
        ]
    
    def list_cameras(self, platform: str = "all") -> dict:
        """列出摄像头"""
        try:
            if platform == "all":
                cameras = self.state.get_all_cameras()
                result = {
                    "status": "success",
                    "action": "list_cameras",
                    "data": {
                        "platform": "all",
                        "cameras": [cam.to_dict() for cam in cameras],
                        "message": f"已列出全部 {len(cameras)} 个摄像头"
                    }
                }
            else:
                if platform not in ["JinLiLite", "ChiWen"]:
                    raise ValueError(f"无效的平台名称: {platform}")
                
                cameras = self.state.get_cameras_by_platform(platform)
                result = {
                    "status": "success",
                    "action": "list_cameras",
                    "data": {
                        "platform": platform,
                        "cameras": [cam.to_dict() for cam in cameras],
                        "message": f"已列出 {platform} 平台的 {len(cameras)} 个摄像头"
                    }
                }
            
            logger.info(f"list_cameras called for platform: {platform}")
            return result
        
        except Exception as e:
            logger.error(f"list_cameras error: {e}")
            return {
                "status": "error",
                "action": "list_cameras",
                "error": {
                    "code": "LIST_FAILED",
                    "message": str(e)
                }
            }
    
    def zoom_camera(self, camera_name: str, zoom_level: str = "fullscreen") -> dict:
        """放大摄像头"""
        try:
            if zoom_level not in ["fullscreen", "large", "medium", "small"]:
                zoom_level = "fullscreen"
            
            success = self.state.zoom_camera(camera_name, zoom_level)
            
            if not success:
                raise ValueError(f"摄像头不存在: {camera_name}")
            
            camera = self.state.get_camera(camera_name)
            result = {
                "status": "success",
                "action": "zoom_camera",
                "data": {
                    "camera_name": camera_name,
                    "zoom_level": zoom_level,
                    "url": camera.url,
                    "platform": camera.platform,
                    "message": f"已将 {camera_name} 放大到 {zoom_level}"
                }
            }
            
            logger.info(f"Camera {camera_name} zoomed to {zoom_level}")
            return result
        
        except Exception as e:
            logger.error(f"zoom_camera error: {e}")
            return {
                "status": "error",
                "action": "zoom_camera",
                "error": {
                    "code": "ZOOM_FAILED",
                    "message": str(e)
                }
            }
    
    def hide_camera(self, camera_name: str) -> dict:
        """隐藏摄像头"""
        try:
            success = self.state.hide_camera(camera_name)
            
            if not success:
                raise ValueError(f"摄像头不存在: {camera_name}")
            
            result = {
                "status": "success",
                "action": "hide_camera",
                "data": {
                    "camera_name": camera_name,
                    "visible": False,
                    "message": f"已隐藏 {camera_name}"
                }
            }
            
            logger.info(f"Camera {camera_name} hidden")
            return result
        
        except Exception as e:
            logger.error(f"hide_camera error: {e}")
            return {
                "status": "error",
                "action": "hide_camera",
                "error": {
                    "code": "HIDE_FAILED",
                    "message": str(e)
                }
            }
    
    def hide_all_cameras(self, platform: str = "all") -> dict:
        """隐藏所有摄像头"""
        try:
            if platform not in ["JinLiLite", "ChiWen", "all"]:
                platform = "all"
            
            hidden_list = self.state.hide_all_cameras(
                platform if platform != "all" else None
            )
            
            hidden_cameras = []
            for camera_name in hidden_list:
                camera = self.state.get_camera(camera_name)
                if camera:
                    hidden_cameras.append({
                        "camera_name": camera.name,
                        "url": camera.url,
                        "platform": camera.platform,
                        "visible": camera.visible,
                        "status": camera.status.value
                    })
            
            result = {
                "status": "success",
                "action": "hide_all_cameras",
                "data": hidden_cameras,
                "message": f"已隐藏 {len(hidden_cameras)} 个摄像头"
            }
            
            logger.info(f"Hid {len(hidden_cameras)} cameras on platform: {platform}")
            return result
        
        except Exception as e:
            logger.error(f"hide_all_cameras error: {e}")
            return {
                "status": "error",
                "action": "hide_all_cameras",
                "error": {
                    "code": "HIDE_ALL_FAILED",
                    "message": str(e)
                }
            }
    
    def show_camera(self, camera_name: str) -> dict:
        """显示摄像头"""
        try:
            success = self.state.show_camera(camera_name)
            
            if not success:
                raise ValueError(f"摄像头不存在: {camera_name}")
            
            camera = self.state.get_camera(camera_name)
            result = {
                "status": "success",
                "action": "show_camera",
                "data": {
                    "camera_name": camera_name,
                    "visible": True,
                    "url": camera.url,
                    "message": f"已显示 {camera_name}"
                }
            }
            
            logger.info(f"Camera {camera_name} shown")
            return result
        
        except Exception as e:
            logger.error(f"show_camera error: {e}")
            return {
                "status": "error",
                "action": "show_camera",
                "error": {
                    "code": "SHOW_FAILED",
                    "message": str(e)
                }
            }
    
    def get_camera_status(self, camera_name: Optional[str] = None) -> dict:
        """获取摄像头状态"""
        try:
            if camera_name:
                camera = self.state.get_camera(camera_name)
                if not camera:
                    raise ValueError(f"摄像头不存在: {camera_name}")
                
                result = {
                    "status": "success",
                    "action": "get_camera_status",
                    "data": {
                        "camera": camera.to_dict(),
                        "message": f"{camera_name} 的当前状态"
                    }
                }
            else:
                cameras = self.state.get_all_cameras()
                result = {
                    "status": "success",
                    "action": "get_camera_status",
                    "data": {
                        "cameras": [cam.to_dict() for cam in cameras],
                        "message": f"全部 {len(cameras)} 个摄像头的状态"
                    }
                }
            
            logger.info(f"get_camera_status called for camera: {camera_name}")
            return result
        
        except Exception as e:
            logger.error(f"get_camera_status error: {e}")
            return {
                "status": "error",
                "action": "get_camera_status",
                "error": {
                    "code": "STATUS_FAILED",
                    "message": str(e)
                }
            }
    
    def show_all_cameras(self, platform: str = "all") -> dict:
          """显示所有摄像头"""
          try:
              if platform not in ["JinLiLite", "ChiWen", "all"]:
                  platform = "all"
              
              shown_list = self.state.show_all_cameras(
                  platform if platform != "all" else None
              )
              
              shown_cameras = []
              for camera_name in shown_list:
                  camera = self.state.get_camera(camera_name)
                  if camera:
                      shown_cameras.append({
                          "camera_name": camera.name,
                          "url": camera.url,
                          "platform": camera.platform,
                          "visible": camera.visible,
                          "status": camera.status.value
                      })
              
              result = {
                  "status": "success",
                  "action": "show_all_cameras",
                  "data": shown_cameras,
                  "message": f"已显示 {len(shown_cameras)} 个摄像头"
              }
              
              logger.info(f"Showed {len(shown_cameras)} cameras on platform: {platform}")
              return result
          
          except Exception as e:
              logger.error(f"show_all_cameras error: {e}")
              return {
                  "status": "error",
                  "action": "show_all_cameras",
                  "error": {
                      "code": "SHOW_ALL_FAILED",
                      "message": str(e)
                  }
              }
    
    def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """执行指定的工具"""
        try:
            method = getattr(self, tool_name, None)
            if not method:
                raise ValueError(f"未知的工具: {tool_name}")
            
            return method(**tool_input)
        
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "status": "error",
                "action": tool_name,
                "error": {
                    "code": "EXECUTION_FAILED",
                    "message": str(e)
                }
            }
    
    def get_tools_definition(self) -> List[Dict[str, Any]]:
        """获取工具定义列表，用于发送给LLM"""
        return self.tools
