"""
Monitor Agent - 摄像头状态管理模块
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class CameraStatus(str, Enum):
    """摄像头状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class Camera:
    """摄像头数据模型"""
    name: str
    platform: str
    url: str
    visible: bool = True
    status: CameraStatus = CameraStatus.ONLINE
    zoom_level: str = "normal"  # fullscreen, large, medium, small, normal
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "platform": self.platform,
            "url": self.url,
            "visible": self.visible,
            "status": self.status.value,
            "zoom_level": self.zoom_level,
        }


class MonitorState:
    """监控状态管理器"""
    
    # 摄像头配置数据
    CAMERA_CONFIG = {
        "JinLiLite": [
            {
                "name": "JinLiLite1",
                "url": "https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb26_1080p.m3u8"
            },
            {
                "name": "JinLiLite2",
                "url": "https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb27_1080p.m3u8"
            },
            {
                "name": "JinLiLite3",
                "url": "https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45feda5_1080p.m3u8"
            },
        ],
        "ChiWen": [
            {
                "name": "ChiWen1",
                "url": "https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb2_1080p.m3u8"
            },
            {
                "name": "ChiWen2",
                "url": "https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb3_1080p.m3u8"
            },
            {
                "name": "ChiWen3",
                "url": "https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb4_1080p.m3u8"
            },
        ]
    }
    
    def __init__(self):
        """初始化监控状态管理器"""
        self.cameras: Dict[str, Camera] = {}
        self._init_cameras()
        logger.info("Monitor state initialized")
    
    def _init_cameras(self):
        """初始化摄像头"""
        for platform, camera_list in self.CAMERA_CONFIG.items():
            for camera_config in camera_list:
                camera = Camera(
                    name=camera_config["name"],
                    platform=platform,
                    url=camera_config["url"],
                    visible=False,  # 默认关闭（隐藏）摄像头
                    status=CameraStatus.ONLINE
                )
                self.cameras[camera_config["name"]] = camera
    
    def get_camera(self, camera_name: str) -> Optional[Camera]:
        """获取指定摄像头"""
        return self.cameras.get(camera_name)
    
    def get_cameras_by_platform(self, platform: str) -> List[Camera]:
        """按平台获取摄像头"""
        return [cam for cam in self.cameras.values() if cam.platform == platform]
    
    def get_all_cameras(self) -> List[Camera]:
        """获取所有摄像头"""
        return list(self.cameras.values())
    
    def zoom_camera(self, camera_name: str, zoom_level: str = "fullscreen") -> bool:
        """放大摄像头"""
        camera = self.get_camera(camera_name)
        if not camera:
            logger.warning(f"Camera {camera_name} not found")
            return False
        
        camera.zoom_level = zoom_level
        camera.visible = True
        logger.info(f"Camera {camera_name} zoomed to {zoom_level}")
        return True
    
    def hide_camera(self, camera_name: str) -> bool:
        """隐藏摄像头"""
        camera = self.get_camera(camera_name)
        if not camera:
            logger.warning(f"Camera {camera_name} not found")
            return False
        
        camera.visible = False
        logger.info(f"Camera {camera_name} hidden")
        return True
    
    def show_camera(self, camera_name: str) -> bool:
        """显示摄像头"""
        camera = self.get_camera(camera_name)
        if not camera:
            logger.warning(f"Camera {camera_name} not found")
            return False
        
        camera.visible = True
        logger.info(f"Camera {camera_name} shown")
        return True
    
    def hide_all_cameras(self, platform: Optional[str] = None) -> List[str]:
        """隐藏所有摄像头"""
        hidden_cameras = []
        
        if platform:
            cameras = self.get_cameras_by_platform(platform)
        else:
            cameras = self.get_all_cameras()
        
        for camera in cameras:
            camera.visible = False
            hidden_cameras.append(camera.name)
        
        logger.info(f"Hidden {len(hidden_cameras)} cameras")
        return hidden_cameras
    
    def show_all_cameras(self, platform: Optional[str] = None) -> List[str]:
        """显示所有摄像头"""
        shown_cameras = []
        
        if platform:
            cameras = self.get_cameras_by_platform(platform)
        else:
            cameras = self.get_all_cameras()
        
        for camera in cameras:
            camera.visible = True
            shown_cameras.append(camera.name)
        
        logger.info(f"Shown {len(shown_cameras)} cameras")
        return shown_cameras
    
    def reset_zoom(self, camera_name: Optional[str] = None):
        """重置放大状态"""
        if camera_name:
            camera = self.get_camera(camera_name)
            if camera:
                camera.zoom_level = "normal"
                logger.info(f"Camera {camera_name} zoom reset to normal")
        else:
            for camera in self.get_all_cameras():
                camera.zoom_level = "normal"
            logger.info("All cameras zoom reset to normal")
    
    def get_status_dict(self) -> dict:
        """获取状态字典"""
        return {
            "cameras": {
                name: camera.to_dict()
                for name, camera in self.cameras.items()
            }
        }
