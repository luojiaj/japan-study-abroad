# -*- coding: utf-8 -*-
"""
生成占位图片的辅助脚本
运行一次即可，生成的 SVG 文件会以 .jpg 后缀存放在 static/images/ 目录
（浏览器可正常渲染 SVG 内容，即使后缀为 .jpg）
后续替换为真实图片时，直接用同名文件覆盖即可
"""
import os

IMG_DIR = os.path.join(os.path.dirname(__file__), "static", "images")
os.makedirs(IMG_DIR, exist_ok=True)

def make_svg(filename, w, h, color1, color2, label, emoji=""):
    """创建一个渐变背景 + 文字标签的 SVG 占位图"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color1}"/>
      <stop offset="100%" stop-color="{color2}"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#g)"/>
  <text x="{w//2}" y="{h//2-10}" text-anchor="middle" fill="white" font-size="42">{emoji}</text>
  <text x="{w//2}" y="{h//2+30}" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="16" font-family="sans-serif">{label}</text>
</svg>'''
    path = os.path.join(IMG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✔ {filename}")

print("正在生成占位图片...")

# ---- 轮播图 Hero (1200x520) ----
make_svg("hero1.jpg", 1200, 520, "#1a2a4a", "#3a6a9c", "东京 · 樱花 · 留学之旅", "🌸")
make_svg("hero2.jpg", 1200, 520, "#2c4a7c", "#4a7ab0", "100+ 合作日本院校", "🏫")
make_svg("hero3.jpg", 1200, 520, "#1a3a5c", "#5a8aac", "95% 升学成功率", "🎓")

# ---- 热门项目图 (800x400) ----
make_svg("hot1.jpg", 800, 400, "#e8857a", "#f7a8b8", "语言学校精选班", "📚")
make_svg("hot2.jpg", 800, 400, "#5a8a4a", "#7ab06a", "本科直通车项目", "🏛")
make_svg("hot3.jpg", 800, 400, "#7a6ab0", "#9a8ad0", "名校硕士研究计划", "🔬")

# ---- 团队头像 (200x200) ----
make_svg("Teacher_luo.jpg", 200, 200, "#1a2a4a", "#2c4a7c", "老师", "👩‍🏫")
make_svg("Teacher_wang.jpg", 200, 200, "#c9a84c", "#d4b85c", "王老师",   "👨‍🏫")


print("全部占位图片已生成！")
