"""
Infrastructure Layer - Configuration Management
Quản lý việc load và parse các config files (YAML)
"""

import yaml
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class MQTTConfig:
    """MQTT Broker Configuration"""
    broker: str
    port: int
    topic: str
    qos: int = 1
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: str = "iot_security_client"
    keep_alive: int = 60


@dataclass
class DatabaseConfig:
    """Database Configuration"""
    path: str
    backup_enabled: bool = True
    backup_path: str = "data/backups/"
    auto_backup_interval: int = 3600


@dataclass
class LoggingConfig:
    """Logging Configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_to_file: bool = True
    log_file_path: str = "logs/app.log"
    csv_log_path: str = "logs/events.csv"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5


@dataclass
class AIConfig:
    """AI Model Configuration"""
    enabled: bool = True
    model_path: str = "ai_model/models/classifier.pkl"


@dataclass
class AlertConfig:
    """Alert Service Configuration"""
    # General settings
    alert_on_warning: bool = True
    alert_on_critical: bool = True
    confidence_threshold: float = 0.75
    
    # Email settings
    email_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "iot.security.system@gmail.com"
    alert_recipients: list = None
    
    # Telegram settings
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_ids: list = None
    
    def __post_init__(self):
        if self.alert_recipients is None:
            self.alert_recipients = ["admin@example.com"]
        if self.telegram_chat_ids is None:
            self.telegram_chat_ids = []
    training_data_path: str = "ai_model/datasets/training_data.csv"
    test_data_path: str = "ai_model/datasets/test_data.csv"
    retrain_interval: int = 86400
    confidence_threshold: float = 0.7


@dataclass
class AppConfig:
    """Application Configuration"""
    name: str
    version: str
    environment: str
    logging: LoggingConfig
    ai: AIConfig
    alert: AlertConfig = None
    
    def __post_init__(self):
        if self.alert is None:
            self.alert = AlertConfig()


class ConfigManager:
    """
    Central configuration manager
    Singleton pattern để đảm bảo chỉ có 1 instance
    """
    _instance = None
    _config_dir = "config"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.mqtt_config = None
            self.database_config = None
            self.app_config = None
            self.initialized = True
    
    @staticmethod
    def _load_yaml(file_path: str) -> Dict[str, Any]:
        """Load YAML file và return dictionary"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_mqtt_config(self, path: str = None) -> MQTTConfig:
        """Load MQTT configuration"""
        if path is None:
            path = os.path.join(self._config_dir, "mqtt_config.yaml")
        
        data = self._load_yaml(path)
        mqtt_data = data.get('mqtt', {})
        
        self.mqtt_config = MQTTConfig(**mqtt_data)
        return self.mqtt_config
    
    def load_database_config(self, path: str = None) -> DatabaseConfig:
        """Load Database configuration"""
        if path is None:
            path = os.path.join(self._config_dir, "database_config.yaml")
        
        data = self._load_yaml(path)
        db_data = data.get('database', {})
        
        self.database_config = DatabaseConfig(**db_data)
        return self.database_config
    
    def load_app_config(self, path: str = None) -> AppConfig:
        """Load Application configuration"""
        if path is None:
            path = os.path.join(self._config_dir, "app_config.yaml")
        
        data = self._load_yaml(path)
        
        # Parse logging config
        logging_data = data.get('logging', {})
        logging_config = LoggingConfig(**logging_data)
        
        # Parse AI config
        ai_data = data.get('ai', {})
        ai_config = AIConfig(**ai_data)
        
        # Parse app config
        app_data = data.get('app', {})
        self.app_config = AppConfig(
            name=app_data.get('name', 'IoT Security System'),
            version=app_data.get('version', '1.0.0'),
            environment=app_data.get('environment', 'development'),
            logging=logging_config,
            ai=ai_config
        )
        
        return self.app_config
    
    def load_all(self):
        """Load tất cả configurations"""
        self.load_mqtt_config()
        self.load_database_config()
        self.load_app_config()
        return self
    
    def get_config(self, config_type: str) -> Any:
        """
        Get specific configuration by type
        
        Args:
            config_type: 'mqtt', 'database', or 'app'
        """
        if config_type == 'mqtt':
            return self.mqtt_config or self.load_mqtt_config()
        elif config_type == 'database':
            return self.database_config or self.load_database_config()
        elif config_type == 'app':
            return self.app_config or self.load_app_config()
        else:
            raise ValueError(f"Unknown config type: {config_type}")


# Singleton instance
config_manager = ConfigManager()


if __name__ == "__main__":
    # Test configuration loading
    config = ConfigManager()
    config.load_all()
    
    print("=== MQTT Config ===")
    print(f"Broker: {config.mqtt_config.broker}")
    print(f"Port: {config.mqtt_config.port}")
    print(f"Topic: {config.mqtt_config.topic}")
    
    print("\n=== Database Config ===")
    print(f"Path: {config.database_config.path}")
    print(f"Backup enabled: {config.database_config.backup_enabled}")
    
    print("\n=== App Config ===")
    print(f"Name: {config.app_config.name}")
    print(f"Version: {config.app_config.version}")
    print(f"AI enabled: {config.app_config.ai.enabled}")
