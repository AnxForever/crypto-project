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
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts"
import {
  BarChart3,
  Zap,
  Clock,
  HardDrive,
  Shield,
  Play,
  Pause,
  TrendingUp,
  Award,
  AlertTriangle,
  CheckCircle,
  Activity,
  Unlock,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"

type Algorithm = "ecies" | "elgamal" | "sm2" | "boneh-franklin" | "boneh-boyen" | "sakai-kasahara"
type MetricType = "encryption" | "decryption" | "keyGen" | "keySize" | "cipherSize"

interface PerformanceData {
  algorithm: string
  type: "PKE" | "IBE"
  encryptionTime: number
  decryptionTime: number
  keyGenTime: number
  publicKeySize: number
  privateKeySize: number
  cipherTextSize: number
  securityLevel: number
  color: string
}

interface BenchmarkResult {
  algorithm: Algorithm
  metric: MetricType
  value: number
  timestamp: number
}

export default function PKEAnalysisPage() {
  const [selectedMetric, setSelectedMetric] = useState<MetricType>("encryption")
  const [messageSize, setMessageSize] = useState([1024])
  const [isRunningBenchmark, setIsRunningBenchmark] = useState(false)
  const [benchmarkProgress, setBenchmarkProgress] = useState(0)
  const [realTimeData, setRealTimeData] = useState<BenchmarkResult[]>([])
  const [selectedAlgorithms, setSelectedAlgorithms] = useState<Algorithm[]>(["ecies", "boneh-franklin"])

  const { toast } = useToast()

  const algorithmInfo: Record<Algorithm, { name: string; type: "PKE" | "IBE"; color: string }> = {
    ecies: { name: "ECIES", type: "PKE", color: "#3b82f6" },
    elgamal: { name: "ElGamal", type: "PKE", color: "#8b5cf6" },
    sm2: { name: "SM2", type: "PKE", color: "#10b981" },
    "boneh-franklin": { name: "Boneh-Franklin", type: "IBE", color: "#f59e0b" },
    "boneh-boyen": { name: "Boneh-Boyen", type: "IBE", color: "#ef4444" },
    "sakai-kasahara": { name: "Sakai-Kasahara", type: "IBE", color: "#06b6d4" },
  }

  // Mock performance data
  const performanceData: PerformanceData[] = [
    {
      algorithm: "ECIES",
      type: "PKE",
      encryptionTime: 2.3,
      decryptionTime: 3.1,
      keyGenTime: 15.2,
      publicKeySize: 65,
      privateKeySize: 32,
      cipherTextSize: 113,
      securityLevel: 128,
      color: "#3b82f6",
    },
    {
      algorithm: "ElGamal",
      type: "PKE",
      encryptionTime: 4.7,
      decryptionTime: 5.2,
      keyGenTime: 25.8,
      publicKeySize: 256,
      privateKeySize: 256,
      cipherTextSize: 512,
      securityLevel: 128,
      color: "#8b5cf6",
    },
    {
      algorithm: "SM2",
      type: "PKE",
      encryptionTime: 3.1,
      decryptionTime: 3.8,
      keyGenTime: 18.5,
      publicKeySize: 64,
      privateKeySize: 32,
      cipherTextSize: 96,
      securityLevel: 128,
      color: "#10b981",
    },
    {
      algorithm: "Boneh-Franklin",
      type: "IBE",
      encryptionTime: 8.2,
      decryptionTime: 12.5,
      keyGenTime: 45.3,
      publicKeySize: 128,
      privateKeySize: 64,
      cipherTextSize: 160,
      securityLevel: 128,
      color: "#f59e0b",
    },
    {
      algorithm: "Boneh-Boyen",
      type: "IBE",
      encryptionTime: 6.8,
      decryptionTime: 9.7,
      keyGenTime: 38.2,
      publicKeySize: 96,
      privateKeySize: 48,
      cipherTextSize: 144,
      securityLevel: 128,
      color: "#ef4444",
    },
    {
      algorithm: "Sakai-Kasahara",
      type: "IBE",
      encryptionTime: 5.9,
      decryptionTime: 8.1,
      keyGenTime: 32.7,
      publicKeySize: 80,
      privateKeySize: 40,
      cipherTextSize: 128,
      securityLevel: 128,
      color: "#06b6d4",
    },
  ]

  const chartConfig = {
    encryption: {
      label: "加密时间 (ms)",
      color: "hsl(var(--chart-1))",
    },
    decryption: {
      label: "解密时间 (ms)",
      color: "hsl(var(--chart-2))",
    },
    keyGen: {
      label: "密钥生成时间 (ms)",
      color: "hsl(var(--chart-3))",
    },
    keySize: {
      label: "密钥大小 (bytes)",
      color: "hsl(var(--chart-4))",
    },
    cipherSize: {
      label: "密文大小 (bytes)",
      color: "hsl(var(--chart-5))",
    },
  }

  const runBenchmark = async () => {
    setIsRunningBenchmark(true)
    setBenchmarkProgress(0)
    setRealTimeData([])

    const totalTests = selectedAlgorithms.length * 5 // 5 metrics per algorithm
    let completedTests = 0

    for (const algorithm of selectedAlgorithms) {
      const metrics: MetricType[] = ["encryption", "decryption", "keyGen", "keySize", "cipherSize"]

      for (const metric of metrics) {
        // Simulate benchmark execution
        await new Promise((resolve) => setTimeout(resolve, 500))

        // Generate realistic performance data with some randomness
        const baseData = performanceData.find((d) => d.algorithm === algorithmInfo[algorithm].name)
        let value = 0

        switch (metric) {
          case "encryption":
            value = (baseData?.encryptionTime || 5) * (0.8 + Math.random() * 0.4)
            break
          case "decryption":
            value = (baseData?.decryptionTime || 7) * (0.8 + Math.random() * 0.4)
            break
          case "keyGen":
            value = (baseData?.keyGenTime || 30) * (0.8 + Math.random() * 0.4)
            break
          case "keySize":
            value = (baseData?.publicKeySize || 100) * (0.9 + Math.random() * 0.2)
            break
          case "cipherSize":
            value = (baseData?.cipherTextSize || 150) * (0.9 + Math.random() * 0.2)
            break
        }

        const result: BenchmarkResult = {
          algorithm,
          metric,
          value: Math.round(value * 100) / 100,
          timestamp: Date.now(),
        }

        setRealTimeData((prev) => [...prev, result])

        completedTests++
        setBenchmarkProgress((completedTests / totalTests) * 100)
      }
    }

    setIsRunningBenchmark(false)
    toast({
      title: "基准测试完成",
      description: `已完成 ${selectedAlgorithms.length} 个算法的性能测试`,
    })
  }

  const getMetricData = (metric: MetricType) => {
    switch (metric) {
      case "encryption":
        return performanceData.map((d) => ({ name: d.algorithm, value: d.encryptionTime, type: d.type }))
      case "decryption":
        return performanceData.map((d) => ({ name: d.algorithm, value: d.decryptionTime, type: d.type }))
      case "keyGen":
        return performanceData.map((d) => ({ name: d.algorithm, value: d.keyGenTime, type: d.type }))
      case "keySize":
        return performanceData.map((d) => ({ name: d.algorithm, value: d.publicKeySize, type: d.type }))
      case "cipherSize":
        return performanceData.map((d) => ({ name: d.algorithm, value: d.cipherTextSize, type: d.type }))
    }
  }

  const getRadarData = () => {
    return performanceData.map((d) => ({
      algorithm: d.algorithm,
      type: d.type,
      encryption: Math.max(0, 100 - d.encryptionTime * 5), // Invert for radar (higher is better)
      decryption: Math.max(0, 100 - d.decryptionTime * 5),
      keyGen: Math.max(0, 100 - d.keyGenTime * 2),
      keySize: Math.max(0, 100 - d.publicKeySize * 0.5),
      cipherSize: Math.max(0, 100 - d.cipherTextSize * 0.3),
    }))
  }

  const getRecommendation = () => {
    const pkeWinner = performanceData
      .filter((d) => d.type === "PKE")
      .sort((a, b) => a.encryptionTime + a.decryptionTime - (b.encryptionTime + b.decryptionTime))[0]

    const ibeWinner = performanceData
      .filter((d) => d.type === "IBE")
      .sort((a, b) => a.encryptionTime + a.decryptionTime - (b.encryptionTime + b.decryptionTime))[0]

    return { pkeWinner, ibeWinner }
  }

  const { pkeWinner, ibeWinner } = getRecommendation()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-3xl p-8 border-white/10">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-r from-green-500 to-emerald-500 bg-opacity-20">
            <BarChart3 className="h-6 w-6 text-green-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">性能分析对比</h1>
            <p className="text-gray-400">PKE vs IBE Performance Analysis</p>
          </div>
        </div>
        <p className="text-gray-300 max-w-3xl leading-relaxed">
          深入分析PKE和IBE算法的性能表现，包括加密解密速度、密钥生成时间、存储开销等关键指标。
          通过实时基准测试和可视化图表，帮助您选择最适合的加密方案。
        </p>
      </div>

      {/* Benchmark Controls */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Activity className="h-5 w-5 text-blue-400" />
            <span>实时基准测试</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <Label className="text-gray-300">测试算法</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {Object.entries(algorithmInfo).map(([key, info]) => (
                  <Badge
                    key={key}
                    variant={selectedAlgorithms.includes(key as Algorithm) ? "default" : "outline"}
                    className={`cursor-pointer transition-all ${
                      selectedAlgorithms.includes(key as Algorithm)
                        ? "bg-white/20 text-white border-white/30"
                        : "border-white/20 text-gray-400 hover:bg-white/10"
                    }`}
                    onClick={() => {
                      if (selectedAlgorithms.includes(key as Algorithm)) {
                        setSelectedAlgorithms(selectedAlgorithms.filter((a) => a !== key))
                      } else {
                        setSelectedAlgorithms([...selectedAlgorithms, key as Algorithm])
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
                max={10240}
                min={64}
                step={64}
                className="mt-2"
              />
            </div>

            <div className="flex items-end">
              <Button
                onClick={runBenchmark}
                disabled={isRunningBenchmark || selectedAlgorithms.length === 0}
                className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:opacity-90 text-white border-0"
              >
                {isRunningBenchmark ? (
                  <>
                    <Pause className="mr-2 h-4 w-4" />
                    测试中...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    开始测试
                  </>
                )}
              </Button>
            </div>
          </div>

          {isRunningBenchmark && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">测试进度</span>
                <span className="text-white">{Math.round(benchmarkProgress)}%</span>
              </div>
              <Progress value={benchmarkProgress} className="bg-white/10" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Performance Charts */}
      <Tabs defaultValue="comparison" className="space-y-6">
        <TabsList className="glass border-white/10">
          <TabsTrigger value="comparison" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
            <BarChart3 className="mr-2 h-4 w-4" />
            性能对比
          </TabsTrigger>
          <TabsTrigger value="radar" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
            <TrendingUp className="mr-2 h-4 w-4" />
            综合评估
          </TabsTrigger>
          <TabsTrigger value="realtime" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
            <Activity className="mr-2 h-4 w-4" />
            实时数据
          </TabsTrigger>
        </TabsList>

        <TabsContent value="comparison" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Encryption Performance */}
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
                    <BarChart data={getMetricData("encryption")}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="url(#encryptionGradient)" radius={[4, 4, 0, 0]} />
                      <defs>
                        <linearGradient id="encryptionGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.8} />
                          <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.3} />
                        </linearGradient>
                      </defs>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Decryption Performance */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Unlock className="h-5 w-5 text-blue-400" />
                  <span>解密性能对比</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getMetricData("decryption")}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="url(#decryptionGradient)" radius={[4, 4, 0, 0]} />
                      <defs>
                        <linearGradient id="decryptionGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8} />
                          <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.3} />
                        </linearGradient>
                      </defs>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Key Generation Performance */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-green-400" />
                  <span>密钥生成性能</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getMetricData("keyGen")}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="url(#keyGenGradient)" radius={[4, 4, 0, 0]} />
                      <defs>
                        <linearGradient id="keyGenGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#10b981" stopOpacity={0.8} />
                          <stop offset="100%" stopColor="#10b981" stopOpacity={0.3} />
                        </linearGradient>
                      </defs>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Storage Overhead */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <HardDrive className="h-5 w-5 text-purple-400" />
                  <span>存储开销对比</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getMetricData("cipherSize")}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="url(#storageGradient)" radius={[4, 4, 0, 0]} />
                      <defs>
                        <linearGradient id="storageGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.8} />
                          <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.3} />
                        </linearGradient>
                      </defs>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="radar" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Shield className="h-5 w-5 text-blue-400" />
                  <span>PKE算法综合评估</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={getRadarData().filter((d) => d.type === "PKE")}>
                      <PolarGrid stroke="rgba(255,255,255,0.2)" />
                      <PolarAngleAxis dataKey="algorithm" tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 12 }} />
                      <PolarRadiusAxis
                        angle={90}
                        domain={[0, 100]}
                        tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                      />
                      <Radar
                        name="加密性能"
                        dataKey="encryption"
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <Radar
                        name="解密性能"
                        dataKey="decryption"
                        stroke="#10b981"
                        fill="#10b981"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <Radar
                        name="密钥生成"
                        dataKey="keyGen"
                        stroke="#f59e0b"
                        fill="#f59e0b"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <ChartTooltip content={<ChartTooltipContent />} />
                    </RadarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Shield className="h-5 w-5 text-purple-400" />
                  <span>IBE算法综合评估</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={getRadarData().filter((d) => d.type === "IBE")}>
                      <PolarGrid stroke="rgba(255,255,255,0.2)" />
                      <PolarAngleAxis dataKey="algorithm" tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 12 }} />
                      <PolarRadiusAxis
                        angle={90}
                        domain={[0, 100]}
                        tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                      />
                      <Radar
                        name="加密性能"
                        dataKey="encryption"
                        stroke="#ef4444"
                        fill="#ef4444"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <Radar
                        name="解密性能"
                        dataKey="decryption"
                        stroke="#8b5cf6"
                        fill="#8b5cf6"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <Radar
                        name="密钥生成"
                        dataKey="keyGen"
                        stroke="#06b6d4"
                        fill="#06b6d4"
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                      <ChartTooltip content={<ChartTooltipContent />} />
                    </RadarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="realtime" className="space-y-6">
          <Card className="glass-card border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Activity className="h-5 w-5 text-green-400" />
                <span>实时性能数据</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {realTimeData.length > 0 ? (
                <ChartContainer config={chartConfig} className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={realTimeData.map((d, index) => ({
                        index,
                        algorithm: algorithmInfo[d.algorithm].name,
                        value: d.value,
                        metric: d.metric,
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="index" stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.7)" fontSize={12} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              ) : (
                <div className="text-center py-12">
                  <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-400">运行基准测试以查看实时性能数据</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Award className="h-5 w-5 text-yellow-400" />
              <span>性能推荐</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30">
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="h-5 w-5 text-blue-400" />
                <span className="font-semibold text-white">PKE最佳选择</span>
              </div>
              <p className="text-blue-200 mb-2">{pkeWinner.algorithm}</p>
              <p className="text-sm text-gray-300">
                加密时间: {pkeWinner.encryptionTime}ms | 解密时间: {pkeWinner.decryptionTime}ms
              </p>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30">
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="h-5 w-5 text-purple-400" />
                <span className="font-semibold text-white">IBE最佳选择</span>
              </div>
              <p className="text-purple-200 mb-2">{ibeWinner.algorithm}</p>
              <p className="text-sm text-gray-300">
                加密时间: {ibeWinner.encryptionTime}ms | 解密时间: {ibeWinner.decryptionTime}ms
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-400" />
              <span>选择建议</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold text-white mb-2">高性能场景</h4>
              <p className="text-sm text-gray-400">推荐使用ECIES或SM2，具有较快的加密解密速度</p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-2">简化密钥管理</h4>
              <p className="text-sm text-gray-400">推荐使用IBE方案，无需复杂的证书基础设施</p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-2">存储敏感环境</h4>
              <p className="text-sm text-gray-400">选择密文开销较小的算法，如ECIES或SM2</p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-2">企业级应用</h4>
              <p className="text-sm text-gray-400">考虑Boneh-Boyen IBE，提供标准模型下的安全性</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
