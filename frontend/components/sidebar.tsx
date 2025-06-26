"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Shield,
  Home,
  Key,
  ShieldIcon as UserShield,
  PlayCircle,
  Database,
  Rocket,
  BarChart3,
  TrendingUp,
  Menu,
  X,
} from "lucide-react"

const navigation = [
  { name: "项目概述", href: "/", icon: Home },
  { name: "PKE加密工具", href: "/pke-tool", icon: Key },
  { name: "IBE加密工具", href: "/ibe-tool", icon: UserShield },
  { name: "PKE应用演示", href: "/pke-demo", icon: PlayCircle },
  { name: "PKE真实数据应用", href: "/pke-application", icon: Database },
  { name: "IBE应用演示", href: "/ibe-demo", icon: Rocket },
  { name: "PKE性能分析", href: "/pke-analysis", icon: BarChart3 },
  { name: "IBE性能分析", href: "/ibe-analysis", icon: TrendingUp },
]

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed top-4 left-4 z-50 md:hidden glass"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-72 transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-full flex-col glass border-r border-white/10">
          {/* Logo */}
          <div className="flex h-16 items-center justify-center border-b border-white/10">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Shield className="h-8 w-8 text-purple-400" />
                <div className="absolute inset-0 h-8 w-8 text-purple-400 animate-pulse opacity-50" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  密码学工具
                </h1>
                <p className="text-xs text-gray-400">Cryptography Platform</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <ScrollArea className="flex-1 px-4 py-6">
            <nav className="space-y-2">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      "flex items-center space-x-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200",
                      isActive
                        ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-white border border-purple-500/30 glow"
                        : "text-gray-300 hover:bg-white/5 hover:text-white",
                    )}
                    onClick={() => setIsOpen(false)}
                  >
                    <item.icon className={cn("h-5 w-5", isActive ? "text-purple-400" : "text-gray-400")} />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </nav>
          </ScrollArea>

          {/* Footer */}
          <div className="border-t border-white/10 p-4">
            <div className="text-center">
              <p className="text-xs text-gray-400">© 2024 密码学工具平台</p>
              <p className="text-xs text-gray-500 mt-1">现代化加密算法演示</p>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm md:hidden" onClick={() => setIsOpen(false)} />
      )}
    </>
  )
}
