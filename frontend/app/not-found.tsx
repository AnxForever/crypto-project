"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Home, ArrowLeft } from "lucide-react"

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-6">
        <div className="relative">
          <h1 className="text-9xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent animate-pulse">
            404
          </h1>
          <div className="absolute inset-0 text-9xl font-bold text-white/5">404</div>
        </div>

        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white">页面未找到</h2>
          <p className="text-gray-400 max-w-md mx-auto">
            抱歉，您访问的页面不存在或已被移动。请检查URL是否正确，或返回首页继续浏览。
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/">
            <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
              <Home className="mr-2 h-4 w-4" />
              返回首页
            </Button>
          </Link>
          <Button
            variant="outline"
            onClick={() => window.history.back()}
            className="border-white/20 text-white hover:bg-white/10"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回上页
          </Button>
        </div>
      </div>
    </div>
  )
}
