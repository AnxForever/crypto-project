import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles } from "lucide-react"
import Link from "next/link"

export function HeroSection() {
  return (
    <div className="relative overflow-hidden rounded-3xl glass-card p-8 md:p-12">
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-10 w-20 h-20 bg-purple-500 rounded-full blur-xl animate-pulse" />
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-pink-500 rounded-full blur-xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-40 h-40 bg-blue-500 rounded-full blur-xl animate-pulse delay-500" />
      </div>

      <div className="relative z-10">
        <div className="flex items-center space-x-2 mb-6">
          <Sparkles className="h-6 w-6 text-purple-400" />
          <span className="text-purple-400 font-medium">现代化密码学平台</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          <span className="bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
            密码学工具平台
          </span>
        </h1>

        <p className="text-xl text-gray-300 mb-8 max-w-2xl leading-relaxed">
          一个完整的密码学工具集合，提供PKE和IBE加密算法的实现、性能分析和应用演示。
          基于现代Web技术构建，界面友好，功能强大。
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link href="/pke-tool">
            <Button
              size="lg"
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white border-0 group"
            >
              开始体验
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
          <Link href="/pke-analysis">
            <Button size="lg" variant="outline" className="border-white/20 text-white hover:bg-white/10">
              查看性能分析
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
