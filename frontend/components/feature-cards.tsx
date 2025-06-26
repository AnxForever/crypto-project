import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Key, ShieldIcon as UserShield, BarChart3, PlayCircle, ArrowRight, CheckCircle } from "lucide-react"
import Link from "next/link"

const features = [
  {
    icon: Key,
    title: "PKE加密工具",
    description: "提供三种经典的公钥加密算法实现，支持密钥生成、加密解密等完整功能。",
    features: ["椭圆曲线集成加密方案 (ECIES)", "ElGamal算法实现", "国密SM2算法", "Web界面操作"],
    href: "/pke-tool",
    gradient: "from-blue-500 to-cyan-500",
    badge: "PKE",
  },
  {
    icon: UserShield,
    title: "IBE加密工具",
    description: "基于身份的加密算法集合，实现了三种主流IBE方案，支持完整的加密生命周期。",
    features: ["Boneh-Franklin IBE方案", "Boneh-Boyen IBE方案", "Sakai-Kasahara IBE方案", "身份管理系统"],
    href: "/ibe-tool",
    gradient: "from-purple-500 to-pink-500",
    badge: "IBE",
  },
  {
    icon: BarChart3,
    title: "性能分析",
    description: "全面的性能测试和分析工具，提供详细的性能指标和可视化图表。",
    features: ["加密解密性能测试", "密钥生成性能分析", "算法对比分析", "可视化图表展示"],
    href: "/pke-analysis",
    gradient: "from-green-500 to-emerald-500",
    badge: "分析",
  },
  {
    icon: PlayCircle,
    title: "应用演示",
    description: "实际应用场景演示，展示各种加密算法在不同环境下的应用效果。",
    features: ["文件加密演示", "消息传输演示", "批量操作演示", "交互式体验"],
    href: "/pke-demo",
    gradient: "from-orange-500 to-red-500",
    badge: "演示",
  },
]

export function FeatureCards() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-4">核心功能</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          探索我们的密码学工具集合，从基础加密到高级性能分析，一站式解决您的密码学需求
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {features.map((feature, index) => (
          <Card
            key={index}
            className="glass-card border-white/10 hover:border-white/20 transition-all duration-300 group overflow-hidden"
          >
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl bg-gradient-to-r ${feature.gradient} bg-opacity-20`}>
                  <feature.icon
                    className={`h-6 w-6 bg-gradient-to-r ${feature.gradient} bg-clip-text text-transparent`}
                  />
                </div>
                <Badge variant="secondary" className="bg-white/10 text-white border-white/20">
                  {feature.badge}
                </Badge>
              </div>
              <CardTitle className="text-white group-hover:text-purple-300 transition-colors">
                {feature.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-300 leading-relaxed">{feature.description}</p>

              <ul className="space-y-2">
                {feature.features.map((item, idx) => (
                  <li key={idx} className="flex items-center space-x-2 text-sm text-gray-400">
                    <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>

              <Link href={feature.href}>
                <Button className="w-full bg-white/10 hover:bg-white/20 text-white border-white/20 group">
                  立即体验
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
