from netmiko import ConnectHandler
import pandas as pd
from datetime import datetime
from paramiko import AutoAddPolicy, SSHClient

def backup_device(device):
    try:
        print(f"尝试连接设备: {device['IP地址']}...")
        # 连接设备
        conn = ConnectHandler(
            host=device['IP地址'],
            device_type=device['设备类型'],
            username=device['用户名'],
            password=device['密码'],
            secret=device['特权密码'],
            encoding='gbk',  # 华为设备使用GBK编码
            global_delay_factor=2  # 增加延迟避免超时
        )
        print(f"成功连接设备: {device['IP地址']}")
        
        # 进入特权模式（华为设备需要）
        conn.enable()
        
        # 获取配置（华为设备命令）
        output = conn.send_command(
            'display current-configuration', 
            read_timeout=120
        )
        
        # 处理中文编码（华为设备使用GBK）
        output = output.encode('iso-8859-1').decode('gbk')
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"F:\\project\\network-auto\\backups\\{device['IP地址']}_{timestamp}.cfg"
        
        # 保存配置
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(output)
        
        # 记录备份时间
        with open("F:\\project\\network-auto\\backups\\backup_log.txt", 'a', encoding='utf-8') as log_file:
            log_file.write(f"{device['IP地址']} 备份于 {timestamp}\n")
            
        print(f"[成功] {device['IP地址']} 配置备份完成！")
        
    except Exception as e:
        print(f"[失败] {device['IP地址']} 连接错误：{str(e)}")



if __name__ == "__main__": 
    # 读取设备清单
    devices = pd.read_excel(r'F:\project\network-auto\devices\devices.xlsx').to_dict('records')
    
    # 执行备份
    for device in devices:
        backup_device(device)