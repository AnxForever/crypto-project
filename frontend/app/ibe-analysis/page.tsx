"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import {
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  LineChart,
  Line,
  ComposedChart,
  Area,
  AreaChart,
} from "recharts"
import {
  BarChart3,
  Zap,
  Clock,
  HardDrive,
  Play,
  Pause,
  TrendingUp,
  Award,
  Activity,
  Users,
  Settings2,
  Scaling,
  Target,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"

type IBEScheme = "boneh-franklin" | "boneh-boyen" | "sakai-kasahara"
type IBEMetricType = "pkgSetup" | "keyExtract" | "encryption" | "decryption" | "mpkSize" | "uskSize" | "cipherSize"

interface IBEPerformanceData {
  scheme: string
  pkgSetupTime: number // ms
  keyExtractTime: number // ms, per user
  encryptionTime: number // ms
  decryptionTime: number // ms
  masterPublicKeySize: number // bytes
  userPrivateKeySize: number // bytes
  cipherTextSize: number // bytes, for a standard message
  securityLevel: number // bits
  color: string
}

interface IBEBenchmarkResult {
  scheme: IBEScheme
  metric: IBEMetricType
  value: number
  timestamp: number
}

interface ScalabilityData {
  messageSize: number
  "Boneh-Franklin": number
  "Boneh-Boyen": number
  "Sakai-Kasahara": number
}

export default function IBEAnalysisPage() {
  const [selectedMetric, setSelectedMetric] = useState<IBEMetricType>("encryption")
  const [messageSize, setMessageSize] = useState([1024]) // bytes
  const [numUsersForKeyExtract, setNumUsersForKeyExtract] = useState([10]) // for key extraction benchmark
  const [isRunningBenchmark, setIsRunningBenchmark] = useState(false)
  const [benchmarkProgress, setBenchmarkProgress] = useState(0)
  const [realTimeData, setRealTimeData] = useState<IBEBenchmarkResult[]>([])
  const [selectedSchemes, setSelectedSchemes] = useState<IBEScheme[]>([
    "boneh-franklin",
    "boneh-boyen",
    "sakai-kasahara",
  ])

  const { toast } = useToast()

  const schemeInfo: Record<IBEScheme, { name: string; color: string }> = {
    "boneh-franklin": { name: "Boneh-Franklin", color: "#f59e0b" },
    "boneh-boyen": { name: "Boneh-Boyen", color: "#ef4444" },
    "sakai-kasahara": { name: "Sakai-Kasahara", color: "#06b6d4" },
  }

  // Mock IBE performance data
  const ibePerformanceData: IBEPerformanceData[] = [
    {
      scheme: "Boneh-Franklin",
      pkgSetupTime: 45.3,
      keyExtractTime: 8.2,
      encryptionTime: 12.5,
      decryptionTime: 15.1,
      masterPublicKeySize: 128,
      userPrivateKeySize: 64,
      cipherTextSize: 160,
      securityLevel: 128,
      color: "#f59e0b",
    },
    {
      scheme: "Boneh-Boyen",
      pkgSetupTime: 38.2,
      keyExtractTime: 6.8,
      encryptionTime: 9.7,
      decryptionTime: 11.5,
      masterPublicKeySize: 96,
      userPrivateKeySize: 48,
      cipherTextSize: 144,
      securityLevel: 128,
      color: "#ef4444",
    },
    {
      scheme: "Sakai-Kasahara",
      pkgSetupTime: 32.7,
      keyExtractTime: 5.9,
      encryptionTime: 8.1,
      decryptionTime: 9.3,
      masterPublicKeySize: 80,
      userPrivateKeySize: 40,
      cipherTextSize: 128,
      securityLevel: 128,
      color: "#06b6d4",
    },
  ]

  // Mock scalability data for message size analysis
  const encryptionScalabilityData: ScalabilityData[] = [
    { messageSize: 64, "Boneh-Franklin": 43.2, "Boneh-Boyen": 42.8, "Sakai-Kasahara": 31.5 },
    { messageSize: 128, "Boneh-Franklin": 40.1, "Boneh-Boyen": 39.9, "Sakai-Kasahara": 31.2 },
    { messageSize: 256, "Boneh-Franklin": 40.8, "Boneh-Boyen": 40.5, "Sakai-Kasahara": 30.8 },
    { messageSize: 512, "Boneh-Franklin": 41.3, "Boneh-Boyen": 41.1, "Sakai-Kasahara": 29.3 },
  ]

  const decryptionScalabilityData: ScalabilityData[] = [
    { messageSize: 64, "Boneh-Franklin": 0.162, "Boneh-Boyen": 0.143, "Sakai-Kasahara": 0.059 },
    { messageSize: 128, "Boneh-Franklin": 0.149, "Boneh-Boyen": 0.138, "Sakai-Kasahara": 0.058 },
    { messageSize: 256, "Boneh-Franklin": 0.151, "Boneh-Boyen": 0.142, "Sakai-Kasahara": 0.057 },
    { messageSize: 512, "Boneh-Franklin": 0.177, "Boneh-Boyen": 0.176, "Sakai-Kasahara": 0.056 },
  ]

  const chartConfig = {
    pkgSetup: { label: "PKG Setup (ms)", color: "hsl(var(--chart-1))" },
    keyExtract: { label: "Key Extract (ms/user)", color: "hsl(var(--chart-2))" },
    encryption: { label: "Encryption (ms)", color: "hsl(var(--chart-3))" },
    decryption: { label: "Decryption (ms)", color: "hsl(var(--chart-4))" },
    storage: { label: "Size (bytes)", color: "hsl(var(--chart-5))" },
  }

  const runBenchmark = async () => {
    setIsRunningBenchmark(true)
    setBenchmarkProgress(0)
    setRealTimeData([])

    const totalTests = selectedSchemes.length * 7 // 7 metrics per scheme
    let completedTests = 0

    for (const scheme of selectedSchemes) {
      const metrics: IBEMetricType[] = [
        "pkgSetup",
        "keyExtract",
        "encryption",
        "decryption",
        "mpkSize",
        "uskSize",
        "cipherSize",
      ]
      const baseData = ibePerformanceData.find((d) => d.scheme === schemeInfo[scheme].name)

      for (const metric of metrics) {
        await new Promise((resolve) => setTimeout(resolve, 200))
        let value = 0
        const factor = 0.8 + Math.random() * 0.4

        switch (metric) {
          case "pkgSetup":
            value = (baseData?.pkgSetupTime || 40) * factor
            break
          case "keyExtract":
            value = (baseData?.keyExtractTime || 7) * factor * numUsersForKeyExtract[0]
            break
          case "encryption":
            value = (baseData?.encryptionTime || 10) * factor * (messageSize[0] / 1024)
            break
          case "decryption":
            value = (baseData?.decryptionTime || 12) * factor * (messageSize[0] / 1024)
            break
          case "mpkSize":
            value = (baseData?.masterPublicKeySize || 100) * (0.9 + Math.random() * 0.2)
            break
          case "uskSize":
            value = (baseData?.userPrivateKeySize || 50) * (0.9 + Math.random() * 0.2)
            break
          case "cipherSize":
            value = (baseData?.cipherTextSize || 150) * (0.9 + Math.random() * 0.2) + messageSize[0]
            break
        }

        setRealTimeData((prev) => [
          ...prev,
          { scheme, metric, value: Math.max(0.1, Math.round(value * 10) / 10), timestamp: Date.now() },
        ])
        completedTests++
        setBenchmarkProgress((completedTests / totalTests) * 100)
      }
    }
    setIsRunningBenchmark(false)
    toast({ title: "IBE基准测试完成", description: `已测试 ${selectedSchemes.length} 个方案` })
  }

  const getMetricData = (metric: IBEMetricType) => {
    return ibePerformanceData.map((d) => {
      let value
      switch (metric) {
        case "pkgSetup":
          value = d.pkgSetupTime
          break
        case "keyExtract":
          value = d.keyExtractTime
          break
        case "encryption":
          value = d.encryptionTime
          break
        case "decryption":
          value = d.decryptionTime
          break
        case "mpkSize":
          value = d.masterPublicKeySize
          break
        case "uskSize":
          value = d.userPrivateKeySize
          break
        case "cipherSize":
          value = d.cipherTextSize
          break
        default:
          value = 0
      }
      return { name: d.scheme, value, color: d.color }
    })
  }

  const getRadarData = () => {
    return ibePerformanceData.map((d) => ({
      scheme: d.scheme,
      pkgSetup: Math.max(0, 100 - d.pkgSetupTime * 1.5),
      keyExtract: Math.max(0, 100 - d.keyExtractTime * 5),
      encryption: Math.max(0, 100 - d.encryptionTime * 4),
      decryption: Math.max(0, 100 - d.decryptionTime * 3),
      storageEfficiency: Math.max(0, 100 - (d.masterPublicKeySize + d.userPrivateKeySize + d.cipherTextSize) * 0.1),
    }))
  }

  const getBestScheme = () => {
    return [...ibePerformanceData].sort(
      (a, b) =>
        a.encryptionTime +
        a.decryptionTime +
        a.keyExtractTime -
        (b.encryptionTime + b.decryptionTime + b.keyExtractTime),
    )[0]
  }
  const bestScheme = getBestScheme()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-3xl p-8 border-white/10">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-r from-red-500 to-orange-500 bg-opacity-20">
            <BarChart3 className="h-6 w-6 text-red-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">IBE性能全景分析</h1>
            <p className="text-gray-400">系统设置、密钥提取、加密解密全流程性能对比</p>
          </div>
        </div>
        <p className="text-gray-300 max-w-3xl leading-relaxed">
          深入分析主流IBE方案的完整性能表现，包括PKG初始化、用户密钥提取、加解密操作及存储开销的全方位对比分析。
        </p>
      </div>

      {/* Benchmark Controls */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Activity className="h-5 w-5 text-blue-400" />
            <span>IBE实时基准测试</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 items-end">
            <div>
              <Label className="text-gray-300">测试方案</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {Object.entries(schemeInfo).map(([key, info]) => (
                  <Badge
                    key={key}
                    variant={selectedSchemes.includes(key as IBEScheme) ? "default" : "outline"}
                    className={`cursor-pointer transition-all ${
                      selectedSchemes.includes(key as IBEScheme)
                        ? "bg-white/20 text-white border-white/30"
                        : "border-white/20 text-gray-400 hover:bg-white/10"
                    }`}
                    onClick={() => {
                      if (selectedSchemes.includes(key as IBEScheme)) {
                        setSelectedSchemes(selectedSchemes.filter((s) => s !== key))
                      } else {
                        setSelectedSchemes([...selectedSchemes, key as IBEScheme])
                      }
                    }}
                  >
                    {info.name}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <Label className="text-gray-300">消息大小: {messageSize[0]} bytes</Label>
              <Slider
                value={messageSize}
                onValueChange={setMessageSize}
                max={8192}
                min={64}
                step={64}
                className="mt-2"
              />
            </div>
            <div>
              <Label className="text-gray-300">用户数 (密钥提取): {numUsersForKeyExtract[0]}</Label>
              <Slider
                value={numUsersForKeyExtract}
                onValueChange={setNumUsersForKeyExtract}
                max={100}
                min={1}
                step={1}
                className="mt-2"
              />
            </div>
            <Button
              onClick={runBenchmark}
              disabled={isRunningBenchmark || selectedSchemes.length === 0}
              className="bg-gradient-to-r from-red-500 to-orange-500 hover:opacity-90 text-white border-0"
            >
              {isRunningBenchmark ? <Pause className="mr-2 h-4 w-4" /> : <Play className="mr-2 h-4 w-4" />}
              开始测试
            </Button>
          </div>
          {isRunningBenchmark && (
            <div className="space-y-2 pt-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">测试进度</span>
                <span className="text-white">{Math.round(benchmarkProgress)}%</span>
              </div>
              <Progress value={benchmarkProgress} className="bg-white/10" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Performance Charts Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="glass border-white/10">
          <TabsTrigger value="overview" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
            <BarChart3 className="mr-2 h-4 w-4" />
            性能总览
          </TabsTrigger>
          <TabsTrigger value="detailed" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
            <TrendingUp className="mr-2 h-4 w-4" />
            详细分析
          </TabsTrigger>
          <TabsTrigger value="scalability" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
            <Scaling className="mr-2 h-4 w-4" />
            规模适应性
          </TabsTrigger>
          <TabsTrigger value="realtime" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
            <Activity className="mr-2 h-4 w-4" />
            实时数据
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Performance Overview Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* System Setup Performance */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Settings2 className="h-5 w-5 text-purple-400" />
                  <span>系统设置性能</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getMetricData("pkgSetup")}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {getMetricData("pkgSetup").map((entry, index) => (
                          <Bar key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* IBE Algorithm Performance Analysis */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Target className="h-5 w-5 text-blue-400" />
                  <span>IBE算法性能分析</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={getRadarData()}>
                      <PolarGrid stroke="rgba(255,255,255,0.2)" />
                      <PolarAngleAxis dataKey="scheme" tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 12 }} />
                      <PolarRadiusAxis
                        angle={90}
                        domain={[0, 100]}
                        tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                      />
                      <Radar
                        name="PKG设置"
                        dataKey="pkgSetup"
                        stroke="#8884d8"
                        fill="#8884d8"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <Radar
                        name="密钥提取"
                        dataKey="keyExtract"
                        stroke="#82ca9d"
                        fill="#82ca9d"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <Radar
                        name="加密性能"
                        dataKey="encryption"
                        stroke="#ffc658"
                        fill="#ffc658"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <Radar
                        name="解密性能"
                        dataKey="decryption"
                        stroke="#ff8042"
                        fill="#ff8042"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <ChartTooltip content={<ChartTooltipContent />} />
                    </RadarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Encryption Performance Comparison */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-yellow-400" />
                  <span>加密性能对比</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={getMetricData("encryption")}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {getMetricData("encryption").map((entry, index) => (
                          <Bar key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                      <Line type="monotone" dataKey="value" stroke="#ff7300" strokeWidth={3} dot={{ r: 6 }} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Decryption Performance Comparison */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-green-400" />
                  <span>解密性能对比</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={getMetricData("decryption")}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="#82ca9d"
                        fill="url(#decryptionGradient)"
                        strokeWidth={2}
                      />
                      <defs>
                        <linearGradient id="decryptionGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#82ca9d" stopOpacity={0.1} />
                        </linearGradient>
                      </defs>
                    </AreaChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="detailed" className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[
            {
              title: "PKG初始化速度",
              metric: "pkgSetup",
              icon: Settings2,
              gradient: "from-purple-500 to-pink-500",
              colors: ["#a855f7", "#ec4899"],
            },
            {
              title: "用户密钥提取速度",
              metric: "keyExtract",
              icon: Users,
              gradient: "from-blue-500 to-cyan-500",
              colors: ["#3b82f6", "#06b6d4"],
            },
            {
              title: "加密速度",
              metric: "encryption",
              icon: Zap,
              gradient: "from-yellow-500 to-orange-500",
              colors: ["#eab308", "#f97316"],
            },
            {
              title: "解密速度",
              metric: "decryption",
              icon: Clock,
              gradient: "from-green-500 to-emerald-500",
              colors: ["#22c55e", "#10b981"],
            },
            {
              title: "主公钥大小",
              metric: "mpkSize",
              icon: HardDrive,
              gradient: "from-indigo-500 to-purple-500",
              colors: ["#6366f1", "#a855f7"],
            },
            {
              title: "用户私钥大小",
              metric: "uskSize",
              icon: HardDrive,
              gradient: "from-pink-500 to-rose-500",
              colors: ["#ec4899", "#f43f5e"],
            },
          ].map((item) => (
            <Card key={item.metric} className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <item.icon className={`h-5 w-5 bg-gradient-to-r ${item.gradient} bg-clip-text text-transparent`} />
                  <span>{item.title}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getMetricData(item.metric as IBEMetricType)}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill={`url(#${item.metric}Gradient)`} radius={[4, 4, 0, 0]} />
                      <defs>
                        <linearGradient id={`${item.metric}Gradient`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={item.colors[0]} stopOpacity={0.8} />
                          <stop offset="100%" stopColor={item.colors[1]} stopOpacity={0.3} />
                        </linearGradient>
                      </defs>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="scalability" className="space-y-6">
          {/* Message Scalability Analysis Header */}
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-2">消息规模适应性</h2>
            <p className="text-gray-400">不同消息类型下的性能变化趋势分析</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Encryption Performance vs Message Size */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-blue-400" />
                  <span>加密性能vs消息大小</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={encryptionScalabilityData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis
                        dataKey="messageSize"
                        stroke="rgba(255,255,255,0.7)"
                        fontSize={12}
                        label={{ value: "消息大小 (字节)", position: "insideBottom", offset: -5 }}
                      />
                      <YAxis
                        stroke="rgba(255,255,255,0.7)"
                        fontSize={12}
                        label={{ value: "加密时间 (ms)", angle: -90, position: "insideLeft" }}
                      />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line
                        type="monotone"
                        dataKey="Boneh-Franklin"
                        stroke="#f59e0b"
                        strokeWidth={3}
                        dot={{ r: 6, fill: "#f59e0b" }}
                        name="Boneh-Franklin"
                      />
                      <Line
                        type="monotone"
                        dataKey="Boneh-Boyen"
                        stroke="#ef4444"
                        strokeWidth={3}
                        dot={{ r: 6, fill: "#ef4444" }}
                        name="Boneh-Boyen"
                      />
                      <Line
                        type="monotone"
                        dataKey="Sakai-Kasahara"
                        stroke="#06b6d4"
                        strokeWidth={3}
                        dot={{ r: 6, fill: "#06b6d4" }}
                        name="Sakai-Kasahara"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Decryption Performance vs Message Size */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-green-400" />
                  <span>解密性能vs消息大小</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={decryptionScalabilityData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis
                        dataKey="messageSize"
                        stroke="rgba(255,255,255,0.7)"
                        fontSize={12}
                        label={{ value: "消息大小 (字节)", position: "insideBottom", offset: -5 }}
                      />
                      <YAxis
                        stroke="rgba(255,255,255,0.7)"
                        fontSize={12}
                        label={{ value: "解密时间 (ms)", angle: -90, position: "insideLeft" }}
                      />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line
                        type="monotone"
                        dataKey="Boneh-Franklin"
                        stroke="#f59e0b"
                        strokeWidth={3}
                        dot={{ r: 6, fill: "#f59e0b" }}
                        name="Boneh-Franklin"
                      />
                      <Line
                        type="monotone"
                        dataKey="Boneh-Boyen"
                        stroke="#ef4444"
                        strokeWidth={3}
                        dot={{ r: 6, fill: "#ef4444" }}
                        name="Boneh-Boyen"
                      />
                      <Line
                        type="monotone"
                        dataKey="Sakai-Kasahara"
                        stroke="#06b6d4"
                        strokeWidth={3}
                        dot={{ r: 6, fill: "#06b6d4" }}
                        name="Sakai-Kasahara"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>

          {/* Scalability Analysis Summary */}
          <Card className="glass-card border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-purple-400" />
                <span>规模适应性分析总结</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30">
                  <h4 className="font-semibold text-blue-300 mb-2">Boneh-Franklin</h4>
                  <p className="text-gray-300">随消息大小增长，性能相对稳定，适合大文件加密场景</p>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30">
                  <h4 className="font-semibold text-red-300 mb-2">Boneh-Boyen</h4>
                  <p className="text-gray-300">在标准模型下提供安全保证，性能表现均衡</p>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-r from-cyan-500/20 to-teal-500/20 border border-cyan-500/30">
                  <h4 className="font-semibold text-cyan-300 mb-2">Sakai-Kasahara</h4>
                  <p className="text-gray-300">整体性能最优，特别适合高频率加解密操作</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="realtime">
          <Card className="glass-card border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Activity className="h-5 w-5 text-green-400" />
                <span>实时性能数据流</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {realTimeData.length > 0 ? (
                <ChartContainer config={chartConfig} className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={realTimeData.map((d, i) => ({
                        ...d,
                        name: `${schemeInfo[d.scheme].name} - ${d.metric}`,
                        index: i,
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="index" name="Test Step" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis name="Value" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent indicator="line" />} />
                      {selectedSchemes.map((sKey) => (
                        <Line
                          key={sKey}
                          type="monotone"
                          dataKey="value"
                          name={schemeInfo[sKey].name}
                          stroke={schemeInfo[sKey].color}
                          strokeWidth={2}
                          dot={false}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              ) : (
                <div className="text-center py-12 text-gray-400">运行基准测试以查看实时数据。</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Recommendations */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Award className="h-5 w-5 text-yellow-400" />
            <span>IBE方案选择建议</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <p className="text-gray-300">
            综合来看, <strong className="text-yellow-300">{bestScheme.scheme}</strong> 在当前模拟数据中表现较均衡。
          </p>
          <ul className="list-disc list-inside text-gray-400 space-y-1">
            <li>
              <strong className="text-white">Boneh-Franklin:</strong>{" "}
              作为开创性方案，安全性高，但可能效率略逊于较新方案。
            </li>
            <li>
              <strong className="text-white">Boneh-Boyen:</strong>{" "}
              优势在于标准模型下的安全性证明，适合对理论安全要求极高的场景。
            </li>
            <li>
              <strong className="text-white">Sakai-Kasahara:</strong>{" "}
              通常基于更高效的配对，可能在速度和密钥大小方面有优势。
            </li>
          </ul>
          <p className="text-gray-400">实际选择需根据具体安全需求、性能瓶颈和可接受的复杂度综合考量。</p>
        </CardContent>
      </Card>
    </div>
  )
}
