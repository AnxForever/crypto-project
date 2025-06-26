import { Card, CardContent } from "@/components/ui/card"
import { Key, ShieldIcon as UserShield, BarChart3, Zap } from "lucide-react"

const stats = [
  {
    icon: Key,
    value: "3",
    label: "PKE算法方案",
    description: "ECIES, ElGamal, SM2",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: UserShield,
    value: "3",
    label: "IBE算法方案",
    description: "Boneh-Franklin, Boneh-Boyen, Sakai-Kasahara",
    color: "from-purple-500 to-pink-500",
  },
  {
    icon: BarChart3,
    value: "8",
    label: "功能模块",
    description: "工具、演示、分析",
    color: "from-green-500 to-emerald-500",
  },
  {
    icon: Zap,
    value: "100%",
    label: "Web化集成",
    description: "现代化界面设计",
    color: "from-orange-500 to-red-500",
  },
]

export function StatsGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <Card
          key={index}
          className="glass-card border-white/10 hover:border-white/20 transition-all duration-300 group"
        >
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-xl bg-gradient-to-r ${stat.color} bg-opacity-20`}>
                <stat.icon className={`h-6 w-6 bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`} />
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-white group-hover:scale-110 transition-transform">
                  {stat.value}
                </div>
              </div>
            </div>
            <h3 className="font-semibold text-white mb-1">{stat.label}</h3>
            <p className="text-sm text-gray-400">{stat.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
