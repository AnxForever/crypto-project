"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Key, Lock, Unlock, Copy, RefreshCw, Shield, AlertCircle, CheckCircle, Sparkles } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

type PKEAlgorithm = "ecies" | "elgamal" | "sm2"

interface KeyPair {
  publicKey: string
  privateKey: string
}

export default function PKEToolPage() {
  const [algorithm, setAlgorithm] = useState<PKEAlgorithm>("ecies")
  const [keyPair, setKeyPair] = useState<KeyPair | null>(null)
  const [plaintext, setPlaintext] = useState("")
  const [ciphertext, setCiphertext] = useState("")
  const [decryptedText, setDecryptedText] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [isEncrypting, setIsEncrypting] = useState(false)
  const [isDecrypting, setIsDecrypting] = useState(false)
  const { toast } = useToast()

  const algorithmInfo = {
    ecies: {
      name: "椭圆曲线集成加密方案",
      description: "基于椭圆曲线的公钥加密方案，提供高安全性和效率",
      features: ["高安全性", "快速加密", "紧凑密文"],
      color: "from-blue-500 to-cyan-500",
    },
    elgamal: {
      name: "ElGamal算法",
      description: "基于离散对数问题的经典公钥加密算法",
      features: ["数学可证安全", "概率加密", "同态性质"],
      color: "from-purple-500 to-pink-500",
    },
    sm2: {
      name: "国密SM2算法",
      description: "中国国家密码管理局发布的椭圆曲线公钥密码算法",
      features: ["国产自主", "符合标准", "高性能"],
      color: "from-green-500 to-emerald-500",
    },
  }

  const generateKeyPair = async () => {
    setIsGenerating(true)
    try {
      // Simulate key generation
      await new Promise((resolve) => setTimeout(resolve, 1500))

      const mockKeyPair: KeyPair = {
        publicKey: `-----BEGIN ${algorithm.toUpperCase()} PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4qiw8PWe9SkHqmNJTAN5
lc5rTNnZL5rDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3
LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bH
J7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf
-----END ${algorithm.toUpperCase()} PUBLIC KEY-----`,
        privateKey: `-----BEGIN ${algorithm.toUpperCase()} PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDiqLDw9Z71KQeq
Y0lMA3mVzmtM2dkvmsN/7xtnPpschen2sYHMEw9Skgz8sWP9+8B23Y6bHJ7m2VQ3
LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bH
J7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf
-----END ${algorithm.toUpperCase()} PRIVATE KEY-----`,
      }

      setKeyPair(mockKeyPair)
      toast({
        title: "密钥生成成功",
        description: `已生成 ${algorithmInfo[algorithm].name} 密钥对`,
      })
    } catch (error) {
      toast({
        title: "密钥生成失败",
        description: "请重试或联系技术支持",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const encryptMessage = async () => {
    if (!keyPair || !plaintext.trim()) return

    setIsEncrypting(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock encryption
      const encrypted = btoa(plaintext + "_encrypted_with_" + algorithm)
      setCiphertext(encrypted)

      toast({
        title: "加密成功",
        description: "明文已成功加密",
      })
    } catch (error) {
      toast({
        title: "加密失败",
        description: "请检查输入或重试",
        variant: "destructive",
      })
    } finally {
      setIsEncrypting(false)
    }
  }

  const decryptMessage = async () => {
    if (!keyPair || !ciphertext.trim()) return

    setIsDecrypting(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock decryption
      const decrypted = atob(ciphertext).replace("_encrypted_with_" + algorithm, "")
      setDecryptedText(decrypted)

      toast({
        title: "解密成功",
        description: "密文已成功解密",
      })
    } catch (error) {
      toast({
        title: "解密失败",
        description: "请检查密文格式或密钥",
        variant: "destructive",
      })
    } finally {
      setIsDecrypting(false)
    }
  }

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "复制成功",
      description: `${type}已复制到剪贴板`,
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-3xl p-8 border-white/10">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 bg-opacity-20">
            <Key className="h-6 w-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">PKE加密工具</h1>
            <p className="text-gray-400">Public Key Encryption Tools</p>
          </div>
        </div>
        <p className="text-gray-300 max-w-3xl leading-relaxed">
          体验三种主流的公钥加密算法：ECIES、ElGamal和国密SM2。
          提供完整的密钥生成、加密解密功能，适用于各种安全通信场景。
        </p>
      </div>

      {/* Algorithm Selection */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Shield className="h-5 w-5 text-purple-400" />
            <span>算法选择</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <Select value={algorithm} onValueChange={(value: PKEAlgorithm) => setAlgorithm(value)}>
            <SelectTrigger className="bg-white/5 border-white/10 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="glass border-white/10">
              <SelectItem value="ecies">ECIES - 椭圆曲线集成加密方案</SelectItem>
              <SelectItem value="elgamal">ElGamal - ElGamal算法</SelectItem>
              <SelectItem value="sm2">SM2 - 国密SM2算法</SelectItem>
            </SelectContent>
          </Select>

          {/* Algorithm Info */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">{algorithmInfo[algorithm].name}</h3>
                <p className="text-gray-400">{algorithmInfo[algorithm].description}</p>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-3">算法特点</h4>
              <div className="flex flex-wrap gap-2">
                {algorithmInfo[algorithm].features.map((feature, index) => (
                  <Badge key={index} variant="secondary" className="bg-white/10 text-white border-white/20">
                    {feature}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Tool Interface */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Key Management */}
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Key className="h-5 w-5 text-green-400" />
              <span>密钥管理</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={generateKeyPair}
              disabled={isGenerating}
              className={`w-full bg-gradient-to-r ${algorithmInfo[algorithm].color} hover:opacity-90 text-white border-0`}
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  生成中...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  生成密钥对
                </>
              )}
            </Button>

            {keyPair && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">公钥</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => copyToClipboard(keyPair.publicKey, "公钥")}
                    className="text-gray-400 hover:text-white"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
                <Textarea
                  value={keyPair.publicKey}
                  readOnly
                  className="bg-white/5 border-white/10 text-gray-300 text-xs font-mono h-20 resize-none"
                />

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">私钥</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => copyToClipboard(keyPair.privateKey, "私钥")}
                    className="text-gray-400 hover:text-white"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
                <Textarea
                  value={keyPair.privateKey}
                  readOnly
                  className="bg-white/5 border-white/10 text-gray-300 text-xs font-mono h-20 resize-none"
                />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Encryption/Decryption */}
        <div className="xl:col-span-2">
          <Tabs defaultValue="encrypt" className="space-y-4">
            <TabsList className="glass border-white/10">
              <TabsTrigger value="encrypt" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
                <Lock className="mr-2 h-4 w-4" />
                加密
              </TabsTrigger>
              <TabsTrigger value="decrypt" className="data-[state=active]:bg-white/20 data-[state=active]:text-white">
                <Unlock className="mr-2 h-4 w-4" />
                解密
              </TabsTrigger>
            </TabsList>

            <TabsContent value="encrypt">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Lock className="h-5 w-5 text-orange-400" />
                    <span>消息加密</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-gray-300">明文消息</Label>
                    <Textarea
                      value={plaintext}
                      onChange={(e) => setPlaintext(e.target.value)}
                      placeholder="请输入要加密的消息..."
                      className="bg-white/5 border-white/10 text-white placeholder:text-gray-500 mt-2"
                      rows={4}
                    />
                  </div>

                  <Button
                    onClick={encryptMessage}
                    disabled={!keyPair || !plaintext.trim() || isEncrypting}
                    className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:opacity-90 text-white border-0"
                  >
                    {isEncrypting ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        加密中...
                      </>
                    ) : (
                      <>
                        <Lock className="mr-2 h-4 w-4" />
                        开始加密
                      </>
                    )}
                  </Button>

                  {ciphertext && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <Label className="text-gray-300">密文结果</Label>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(ciphertext, "密文")}
                          className="text-gray-400 hover:text-white"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                      <Textarea
                        value={ciphertext}
                        readOnly
                        className="bg-white/5 border-white/10 text-gray-300 font-mono"
                        rows={4}
                      />
                      <div className="flex items-center space-x-2 mt-2">
                        <CheckCircle className="h-4 w-4 text-green-400" />
                        <span className="text-sm text-green-400">加密成功</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="decrypt">
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Unlock className="h-5 w-5 text-blue-400" />
                    <span>消息解密</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-gray-300">密文消息</Label>
                    <Textarea
                      value={ciphertext}
                      onChange={(e) => setCiphertext(e.target.value)}
                      placeholder="请输入要解密的密文..."
                      className="bg-white/5 border-white/10 text-white placeholder:text-gray-500 mt-2 font-mono"
                      rows={4}
                    />
                  </div>

                  <Button
                    onClick={decryptMessage}
                    disabled={!keyPair || !ciphertext.trim() || isDecrypting}
                    className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:opacity-90 text-white border-0"
                  >
                    {isDecrypting ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        解密中...
                      </>
                    ) : (
                      <>
                        <Unlock className="mr-2 h-4 w-4" />
                        开始解密
                      </>
                    )}
                  </Button>

                  {decryptedText && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <Label className="text-gray-300">明文结果</Label>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(decryptedText, "解密结果")}
                          className="text-gray-400 hover:text-white"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                      <Textarea
                        value={decryptedText}
                        readOnly
                        className="bg-white/5 border-white/10 text-gray-300"
                        rows={4}
                      />
                      <div className="flex items-center space-x-2 mt-2">
                        <CheckCircle className="h-4 w-4 text-green-400" />
                        <span className="text-sm text-green-400">解密成功</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Usage Notes */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-yellow-400" />
            <span>使用说明</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-white mb-3">操作步骤</h4>
              <ol className="text-gray-400 space-y-2 text-sm">
                <li>1. 选择合适的PKE算法</li>
                <li>2. 点击"生成密钥对"按钮</li>
                <li>3. 在加密标签页输入明文消息</li>
                <li>4. 点击"开始加密"获得密文</li>
                <li>5. 在解密标签页粘贴密文进行解密</li>
              </ol>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-3">注意事项</h4>
              <ul className="text-gray-400 space-y-2 text-sm">
                <li>• 私钥请妥善保管，不要泄露</li>
                <li>• 公钥可以安全地分享给他人</li>
                <li>• 不同算法的密钥格式不同</li>
                <li>• 建议定期更换密钥对</li>
                <li>• 本工具仅供学习和演示使用</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
