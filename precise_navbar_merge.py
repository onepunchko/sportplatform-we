from PIL import Image, ImageDraw
import os

def merge_navbar_to_five_pages():
    """
    精确地为5个页面（首页、运动追踪、场地预约、运动社区、个人资料）添加导航栏
    """
    try:
        # 打开导航栏图片
        navbar_img = Image.open('导航栏.png')
        print(f"导航栏图片尺寸: {navbar_img.size}")
        
        # 打开小程序界面图片
        app_interface_img = Image.open('小程序界面.png')
        print(f"小程序界面图片尺寸: {app_interface_img.size}")
        
        # 转换为RGBA模式以支持透明度
        if navbar_img.mode != 'RGBA':
            navbar_img = navbar_img.convert('RGBA')
        if app_interface_img.mode != 'RGBA':
            app_interface_img = app_interface_img.convert('RGBA')
        
        # 创建结果图片，基于原始界面图片
        result_img = app_interface_img.copy()
        
        # 手动定义5个页面的精确位置
        # 根据小程序界面图片的实际布局来定义
        phone_regions = get_precise_phone_regions(app_interface_img.size)
        
        page_names = ["首页", "运动追踪", "场地预约", "运动社区", "个人资料"]
        
        # 为每个手机界面添加导航栏
        for i, region in enumerate(phone_regions):
            if i >= len(page_names):
                break
                
            x, y, width, height = region
            page_name = page_names[i]
            print(f"处理 {page_name}: 位置({x}, {y}), 尺寸({width} x {height})")
            
            # 计算导航栏在该页面中的适当尺寸
            # 导航栏宽度应该适配手机屏幕宽度
            navbar_width = int(width * 0.9)  # 使用90%的宽度，留出边距
            navbar_aspect_ratio = navbar_img.height / navbar_img.width
            navbar_height = int(navbar_width * navbar_aspect_ratio)
            
            # 缩放导航栏到适当大小
            scaled_navbar = navbar_img.resize((navbar_width, navbar_height), Image.Resampling.LANCZOS)
            
            # 计算导航栏在页面中的位置（底部居中）
            navbar_x = x + (width - navbar_width) // 2
            navbar_y = y + height - navbar_height - int(height * 0.05)  # 距离底部5%的高度
            
            # 确保位置在图片范围内
            if (navbar_x >= 0 and navbar_y >= 0 and 
                navbar_x + navbar_width <= result_img.width and 
                navbar_y + navbar_height <= result_img.height):
                
                # 粘贴导航栏到结果图片
                result_img.paste(scaled_navbar, (navbar_x, navbar_y), scaled_navbar)
                print(f"✓ 导航栏已添加到 {page_name}")
            else:
                print(f"✗ {page_name} 的导航栏位置超出图片范围，跳过")
        
        # 保存结果
        output_filename = '5页面带导航栏的小程序界面.png'
        result_img.save(output_filename, 'PNG')
        print(f"\n所有页面导航栏添加完成！保存为: {output_filename}")
        
        return output_filename
        
    except Exception as e:
        print(f"导航栏合并失败: {str(e)}")
        return None

def get_precise_phone_regions(img_size):
    """
    根据小程序界面图片的实际布局，精确定义5个页面的位置
    """
    width, height = img_size
    
    # 基于图片分析，定义手机界面的精确位置
    # 假设图片是一个3x3的网格布局，包含多个手机界面
    
    # 计算每个网格的大小
    grid_cols = 3
    grid_rows = 3
    
    col_width = width // grid_cols
    row_height = height // grid_rows
    
    # 定义5个页面的网格位置
    # 第一行：首页(0,0)、运动追踪(1,0)、场地预约(2,0)
    # 第二行：运动社区(0,1)、个人资料(1,1)
    page_positions = [
        (0, 0),  # 首页
        (1, 0),  # 运动追踪  
        (2, 0),  # 场地预约
        (0, 1),  # 运动社区
        (1, 1),  # 个人资料
    ]
    
    phone_regions = []
    
    for col, row in page_positions:
        # 计算网格位置
        grid_x = col * col_width
        grid_y = row * row_height
        
        # 在网格内寻找手机界面的实际边界
        # 假设手机界面在网格中央，占据80%的空间
        margin_x = int(col_width * 0.1)
        margin_y = int(row_height * 0.1)
        
        phone_x = grid_x + margin_x
        phone_y = grid_y + margin_y
        phone_w = col_width - 2 * margin_x
        phone_h = row_height - 2 * margin_y
        
        phone_regions.append((phone_x, phone_y, phone_w, phone_h))
    
    return phone_regions

def analyze_image_layout():
    """
    分析小程序界面图片的布局，帮助确定手机位置
    """
    try:
        app_interface_img = Image.open('小程序界面.png')
        width, height = app_interface_img.size
        
        print(f"图片尺寸: {width} x {height}")
        print(f"假设3x3网格布局:")
        print(f"每列宽度: {width // 3}")
        print(f"每行高度: {height // 3}")
        
        # 创建一个带网格线的调试图片
        debug_img = app_interface_img.copy()
        draw = ImageDraw.Draw(debug_img)
        
        # 绘制网格线
        for i in range(1, 3):
            # 垂直线
            x = i * (width // 3)
            draw.line([(x, 0), (x, height)], fill='red', width=5)
            
            # 水平线
            y = i * (height // 3)
            draw.line([(0, y), (width, y)], fill='red', width=5)
        
        # 标记5个页面的位置
        phone_regions = get_precise_phone_regions((width, height))
        page_names = ["首页", "运动追踪", "场地预约", "运动社区", "个人资料"]
        
        for i, (x, y, w, h) in enumerate(phone_regions):
            if i < len(page_names):
                # 绘制页面边界
                draw.rectangle([x, y, x + w, y + h], outline='blue', width=3)
                # 添加页面标签
                draw.text((x + 10, y + 10), page_names[i], fill='blue')
        
        debug_img.save('布局分析图.png')
        print("布局分析图已保存为: 布局分析图.png")
        
    except Exception as e:
        print(f"布局分析失败: {str(e)}")

if __name__ == "__main__":
    # 先分析布局
    print("=== 分析图片布局 ===")
    analyze_image_layout()
    
    print("\n=== 添加导航栏 ===")
    merge_navbar_to_five_pages() 