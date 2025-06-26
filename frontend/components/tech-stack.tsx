import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const technologies = [
  {
    name: "Python + Flask",
    description: "后端框架与API",
    icon: "🐍",
    category: "后端",
  },
  {
    name: "HTML5 + CSS3",
    description: "现代前端技术",
    icon: "🌐",
    category: "前端",
  },
  {
    name: "JavaScript",
    description: "交互逻辑实现",
    icon: "⚡",
    category: "前端",
  },
  {
    name: "Chart.js",
    description: "数据可视化",
    icon: "📊",
    category: "可视化",
  },
  {
    name: "PyCryptodome",
    description: "密码学基础库",
    icon: "🔐",
    category: "密码学",
  },
  {
    name: "ECIES",
    description: "椭圆曲线加密",
    icon: "🔑",
    category: "密码学",
  },
]

export function TechStack() {
  return (
    <Card className="glass-card border-white/10">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <span className="text-2xl">⚙️</span>
          <span>技术架构</span>
        </CardTitle>
        <p className="text-gray-400">本平台采用现代化的Web技术栈，前后端分离架构，确保高性能和良好的用户体验。</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {technologies.map((tech, index) => (
            <div
              key={index}
              className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
            >
              <div className="flex items-center space-x-3 mb-2">
                <span className="text-2xl">{tech.icon}</span>
                <div>
                  <h4 className="font-semibold text-white">{tech.name}</h4>
                  <Badge variant="outline" className="text-xs border-white/20 text-gray-400">
                    {tech.category}
                  </Badge>
                </div>
              </div>
              <p className="text-sm text-gray-400">{tech.description}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
