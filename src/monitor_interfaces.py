from netmiko import ConnectHandler
import pandas as pd
import time

# 获取设备接口状态
def get_interface_status(device):
    try:
        print(f"监控设备：{device['host']}...")
        # 连接设备
        conn = ConnectHandler(
            device_type=device['device_type'],
            host=device['host'],
            username=device['username'],
            password=device['password'],
            secret=device['secret'],
            #开启日志
            session_log=device['session_log']

        )
        print(f"成功连接设备：{device['host']}")
        
        # 进入特权模式（华为设备需要）
        conn.enable()
        
        # 获取接口状态（华为设备命令）
        output = conn.send_command('display interface brief')
        
        # 解析输出
        status = {}
        for line in output.splitlines():
            if 'Interface' in line or 'current state' in line:
                continue
            parts = line.split()
            if len(parts) >= 6:
                intf = parts[0]
                link_status = parts[1]
                speed = parts[5]
                status[intf] = {
                    'status': 'UP' if 'up' in link_status.lower() else 'DOWN',
                    'speed': speed
                }
        return status
    
    except Exception as e:
        print(f"监控失败：{str(e)}")
        return {}

# 检查接口状态变化
def check_changes(device_ip, new_status, old_status):
    changes = []
    for intf, data in new_status.items():
        if intf not in old_status or data['status'] != old_status[intf]['status']:
            changes.append(f"{intf} 状态变化：{old_status.get(intf, {}).get('status', 'N/A')} → {data['status']}")
    return changes

if __name__ == "__main__":
    # 读取设备信息
    devices = pd.read_csv(r'F:\project\network-auto\devices\devices.csv').to_dict('records')
    last_status = {}
    # 循环监控
    while True:
        for device in devices:
            # 每次获取接口状态时重新设置日志文件路径
            device['session_log'] = r"F:/project/network-auto/logs/"+device['host']+".log"
            current = get_interface_status(device)
            if not current:
                continue
                
            # 对比状态变化
            changes = check_changes(device['host'], current, last_status.get(device['host'], {}))
            if changes:
                print(f"[告警] {device['host']} 检测到接口变化：")
                print('\n'.join(changes))
             
                
            # 更新状态记录
            last_status[device['host']] = current.copy()
            
        # 每60秒检测一次
        time.sleep(30)