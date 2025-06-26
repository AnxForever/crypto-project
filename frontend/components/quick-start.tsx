import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import Link from "next/link"

const steps = [
  {
    number: "01",
    title: "选择加密方案",
    description: "从PKE或IBE工具中选择适合你需求的加密算法，每种算法都有详细的说明和特点介绍。",
    links: [
      { label: "PKE工具", href: "/pke-tool" },
      { label: "IBE工具", href: "/ibe-tool" },
    ],
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    number: "02",
    title: "体验功能演示",
    description: "通过实际应用演示了解各算法的使用场景，包括文件加密、消息传输等实用功能。",
    links: [
      { label: "PKE演示", href: "/pke-demo" },
      { label: "IBE演示", href: "/ibe-demo" },
    ],
    gradient: "from-purple-500 to-pink-500",
  },
  {
    number: "03",
    title: "查看性能分析",
    description: "深入了解各算法的性能表现，通过详细的图表和数据对比选择最适合的方案。",
    links: [{ label: "性能分析", href: "/pke-analysis" }],
    gradient: "from-green-500 to-emerald-500",
  },
]

export function QuickStart() {
  return (
    <Card className="glass-card border-white/10">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <span className="text-2xl">🚀</span>
          <span>快速开始</span>
        </CardTitle>
        <p className="text-gray-400">三个简单步骤，快速上手我们的密码学工具平台</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="p-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all duration-300 h-full">
                <div
                  className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-r ${step.gradient} bg-opacity-20 mb-4`}
                >
                  <span className={`text-lg font-bold bg-gradient-to-r ${step.gradient} bg-clip-text text-transparent`}>
                    {step.number}
                  </span>
                </div>

                <h3 className="text-lg font-semibold text-white mb-3">{step.title}</h3>
                <p className="text-gray-400 mb-4 leading-relaxed">{step.description}</p>

                <div className="flex flex-wrap gap-2">
                  {step.links.map((link, linkIndex) => (
                    <Link key={linkIndex} href={link.href}>
                      <Button variant="outline" size="sm" className="border-white/20 text-white hover:bg-white/10">
                        {link.label}
                        <ArrowRight className="ml-1 h-3 w-3" />
                      </Button>
                    </Link>
                  ))}
                </div>
              </div>

              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 w-6 h-0.5 bg-gradient-to-r from-white/20 to-transparent" />
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
