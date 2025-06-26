import type React from "react"
import type { Metadata } from "next"
import { Inter, JetBrains_Mono } from "next/font/google"
import "./globals.css"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Toaster } from "@/components/ui/toaster"

const inter = Inter({ subsets: ["latin"] })
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

export const metadata: Metadata = {
  title: "密码学工具平台 | Cryptography Tools Platform",
  description: "现代化的密码学工具集合，提供PKE和IBE加密算法的实现、性能分析和应用演示",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" className="dark">
      <body className={`${inter.className} ${jetbrainsMono.variable} antialiased`}>
        <div className="flex h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto">
              <div className="container mx-auto px-6 py-8">{children}</div>
            </main>
          </div>
        </div>
        <Toaster />
      </body>
    </html>
  )
}
