"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  ShieldIcon as UserShield,
  Settings,
  Key,
  Lock,
  Unlock,
  Copy,
  RefreshCw,
  Shield,
  AlertCircle,
  CheckCircle,
  Sparkles,
  Users,
  Mail,
  CreditCard,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"

type IBEScheme = "boneh-franklin" | "boneh-boyen" | "sakai-kasahara"

interface MasterKeys {
  publicKey: string
  privateKey: string
}

interface UserKey {
  identity: string
  privateKey: string
}

export default function IBEToolPage() {
  const [scheme, setScheme] = useState<IBEScheme>("boneh-franklin")
  const [masterKeys, setMasterKeys] = useState<MasterKeys | null>(null)
  const [userKeys, setUserKeys] = useState<UserKey[]>([])
  const [newIdentity, setNewIdentity] = useState("")
  const [recipientIdentity, setRecipientIdentity] = useState("")
  const [plaintext, setPlaintext] = useState("")
  const [ciphertext, setCiphertext] = useState("")
  const [decryptedText, setDecryptedText] = useState("")
  const [selectedUserKey, setSelectedUserKey] = useState("")

  const [isSettingUp, setIsSettingUp] = useState(false)
  const [isGeneratingKey, setIsGeneratingKey] = useState(false)
  const [isEncrypting, setIsEncrypting] = useState(false)
  const [isDecrypting, setIsDecrypting] = useState(false)

  const { toast } = useToast()

  const schemeInfo = {
    "boneh-franklin": {
      name: "Boneh-Franklin IBE",
      description: "第一个实用的基于身份加密方案，基于双线性对和Weil配对",
      features: ["首个实用IBE", "双线性对", "随机预言模型", "高安全性"],
      color: "from-purple-500 to-pink-500",
      year: "2001",
      security: "DBDH假设",
    },
    "boneh-boyen": {
      name: "Boneh-Boyen IBE",
      description: "改进的IBE方案，在标准模型下可证安全，无需随机预言模型",
      features: ["标准模型安全", "选择性安全", "高效验证", "紧致证明"],
      color: "from-blue-500 to-cyan-500",
      year: "2004",
      security: "DBDH假设",
    },
    "sakai-kasahara": {
      name: "Sakai-Kasahara IBE",
      description: "基于椭圆曲线的高效IBE方案，具有更好的性能表现",
      features: ["椭圆曲线", "高效计算", "短密文", "快速配对"],
      color: "from-green-500 to-emerald-500",
      year: "2003",
      security: "GDBH假设",
    },
  }

  const setupMasterKeys = async () => {
    setIsSettingUp(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000))

      const mockMasterKeys: MasterKeys = {
        publicKey: `-----BEGIN ${scheme.toUpperCase()} MASTER PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4qiw8PWe9SkHqmNJTAN5
lc5rTNnZL5rDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3
LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bH
J7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf
-----END ${scheme.toUpperCase()} MASTER PUBLIC KEY-----`,
        privateKey: `-----BEGIN ${scheme.toUpperCase()} MASTER PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDiqLDw9Z71KQeq
Y0lMA3mVzmtM2dkvmsN/7xtnPpschen2sYHMEw9Skgz8sWP9+8B23Y6bHJ7m2VQ3
LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bH
J7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf
-----END ${scheme.toUpperCase()} MASTER PRIVATE KEY-----`,
      }

      setMasterKeys(mockMasterKeys)
      setUserKeys([]) // Reset user keys when changing scheme
      toast({
        title: "系统初始化成功",
        description: `${schemeInfo[scheme].name} 主密钥已生成`,
      })
    } catch (error) {
      toast({
        title: "系统初始化失败",
        description: "请重试或联系技术支持",
        variant: "destructive",
      })
    } finally {
      setIsSettingUp(false)
    }
  }

  const generateUserKey = async () => {
    if (!masterKeys || !newIdentity.trim()) return

    setIsGeneratingKey(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))

      const userKey: UserKey = {
        identity: newIdentity.trim(),
        privateKey: `-----BEGIN ${scheme.toUpperCase()} USER PRIVATE KEY-----
Identity: ${newIdentity.trim()}
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDiqLDw9Z71KQeq
${btoa(newIdentity.trim() + "_" + scheme)}_UserKey_Generated_From_Master
LrhUVVV8H5KfJ9J5ZrDf+8bZz6bHJ7m2VQ3LrhUVVV8H5KfJ9J5ZrDf+8bZz6bH
-----END ${scheme.toUpperCase()} USER PRIVATE KEY-----`,
      }

      setUserKeys([...userKeys, userKey])
      setNewIdentity("")
      toast({
        title: "用户密钥生成成功",
        description: `已为身份 "${userKey.identity}" 生成私钥`,
      })
    } catch (error) {
      toast({
        title: "密钥生成失败",
        description: "请检查身份格式或重试",
        variant: "destructive",
      })
    } finally {
      setIsGeneratingKey(false)
    }
  }

  const encryptMessage = async () => {
    if (!masterKeys || !recipientIdentity.trim() || !plaintext.trim()) return

    setIsEncrypting(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1200))

      const encrypted = btoa(
        JSON.stringify({
          recipient: recipientIdentity.trim(),
          message: plaintext,
          scheme: scheme,
          timestamp: Date.now(),
        }),
      )
      setCiphertext(encrypted)

      toast({
        title: "加密成功",
        description: `消息已使用身份 "${recipientIdentity}" 加密`,
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
    if (!selectedUserKey || !ciphertext.trim()) return

    setIsDecrypting(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1200))

      const encryptedData = JSON.parse(atob(ciphertext))
      const selectedUser = userKeys.find((key) => key.identity === selectedUserKey)

      if (encryptedData.recipient !== selectedUserKey) {
        throw new Error("身份不匹配")
      }

      setDecryptedText(encryptedData.message)
      toast({
        title: "解密成功",
        description: `使用身份 "${selectedUserKey}" 成功解密消息`,
      })
    } catch (error) {
      toast({
        title: "解密失败",
        description: "请检查密文格式、身份匹配或密钥",
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

  const getIdentityIcon = (identity: string) => {
    if (identity.includes("@")) return <Mail className="h-4 w-4" />
    if (/^\d+$/.test(identity)) return <CreditCard className="h-4 w-4" />
    return <Users className="h-4 w-4" />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-3xl p-8 border-white/10">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 bg-opacity-20">
            <UserShield className="h-6 w-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">IBE加密工具</h1>
            <p className="text-gray-400">Identity-Based Encryption Tools</p>
          </div>
        </div>
        <p className="text-gray-300 max-w-3xl leading-relaxed">
          体验三种主流的基于身份加密算法：Boneh-Franklin、Boneh-Boyen和Sakai-Kasahara。
          无需证书管理，直接使用身份信息进行加密，简化密钥管理流程。
        </p>
      </div>

      {/* Scheme Selection */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Shield className="h-5 w-5 text-purple-400" />
            <span>IBE方案选择</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <Select value={scheme} onValueChange={(value: IBEScheme) => setScheme(value)}>
            <SelectTrigger className="bg-white/5 border-white/10 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="glass border-white/10">
              <SelectItem value="boneh-franklin">Boneh-Franklin IBE (2001)</SelectItem>
              <SelectItem value="boneh-boyen">Boneh-Boyen IBE (2004)</SelectItem>
              <SelectItem value="sakai-kasahara">Sakai-Kasahara IBE (2003)</SelectItem>
            </SelectContent>
          </Select>

          {/* Scheme Info */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">{schemeInfo[scheme].name}</h3>
                <p className="text-gray-400">{schemeInfo[scheme].description}</p>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-3">方案特点</h4>
              <div className="flex flex-wrap gap-2">
                {schemeInfo[scheme].features.map((feature, index) => (
                  <Badge key={index} variant="secondary" className="bg-white/10 text-white border-white/20">
                    {feature}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">提出年份:</span>
                <span className="text-white">{schemeInfo[scheme].year}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">安全假设:</span>
                <span className="text-white">{schemeInfo[scheme].security}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Setup */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Settings className="h-5 w-5 text-blue-400" />
            <span>系统初始化 (PKG Setup)</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300">初始化私钥生成器(PKG)并生成系统主密钥</p>
              <p className="text-sm text-gray-400 mt-1">每次更换IBE方案都需要重新初始化系统</p>
            </div>
            <Button
              onClick={setupMasterKeys}
              disabled={isSettingUp}
              className={`bg-gradient-to-r ${schemeInfo[scheme].color} hover:opacity-90 text-white border-0`}
            >
              {isSettingUp ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  初始化中...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  初始化系统
                </>
              )}
            </Button>
          </div>

          {masterKeys && (
            <div className="space-y-4 pt-4 border-t border-white/10">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-gray-300">系统公钥 (Master Public Key)</Label>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(masterKeys.publicKey, "系统公钥")}
                      className="text-gray-400 hover:text-white"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                  <Textarea
                    value={masterKeys.publicKey}
                    readOnly
                    className="bg-white/5 border-white/10 text-gray-300 text-xs font-mono h-24 resize-none"
                  />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-gray-300">系统私钥 (Master Private Key)</Label>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(masterKeys.privateKey, "系统私钥")}
                      className="text-gray-400 hover:text-white"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                  <Textarea
                    value={masterKeys.privateKey}
                    readOnly
                    className="bg-white/5 border-white/10 text-gray-300 text-xs font-mono h-24 resize-none"
                  />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Key Generation */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Key className="h-5 w-5 text-green-400" />
            <span>用户密钥生成</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <Label className="text-gray-300">用户身份 (Identity)</Label>
              <Input
                value={newIdentity}
                onChange={(e) => setNewIdentity(e.target.value)}
                placeholder="例如: alice@example.com, user123, 身份证号..."
                className="bg-white/5 border-white/10 text-white placeholder:text-gray-500 mt-2"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={generateUserKey}
                disabled={!masterKeys || !newIdentity.trim() || isGeneratingKey}
                className="bg-gradient-to-r from-green-500 to-emerald-500 hover:opacity-90 text-white border-0"
              >
                {isGeneratingKey ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Key className="mr-2 h-4 w-4" />
                    生成密钥
                  </>
                )}
              </Button>
            </div>
          </div>

          {userKeys.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-white/10">
              <Label className="text-gray-300">已生成的用户密钥</Label>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {userKeys.map((userKey, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/10"
                  >
                    <div className="flex items-center space-x-3">
                      {getIdentityIcon(userKey.identity)}
                      <span className="text-white font-medium">{userKey.identity}</span>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(userKey.privateKey, `${userKey.identity}的私钥`)}
                      className="text-gray-400 hover:text-white"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Encryption/Decryption */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Lock className="h-5 w-5 text-orange-400" />
              <span>身份加密</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-300">接收者身份</Label>
              <Input
                value={recipientIdentity}
                onChange={(e) => setRecipientIdentity(e.target.value)}
                placeholder="输入接收者的身份信息..."
                className="bg-white/5 border-white/10 text-white placeholder:text-gray-500 mt-2"
              />
            </div>

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
              disabled={!masterKeys || !recipientIdentity.trim() || !plaintext.trim() || isEncrypting}
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
                  使用身份加密
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
                  <span className="text-sm text-green-400">已使用身份 "{recipientIdentity}" 加密</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Unlock className="h-5 w-5 text-blue-400" />
              <span>身份解密</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-300">选择解密身份</Label>
              <Select value={selectedUserKey} onValueChange={setSelectedUserKey}>
                <SelectTrigger className="bg-white/5 border-white/10 text-white mt-2">
                  <SelectValue placeholder="选择一个已生成密钥的身份..." />
                </SelectTrigger>
                <SelectContent className="glass border-white/10">
                  {userKeys.map((userKey) => (
                    <SelectItem key={userKey.identity} value={userKey.identity}>
                      <div className="flex items-center space-x-2">
                        {getIdentityIcon(userKey.identity)}
                        <span>{userKey.identity}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

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
              disabled={!selectedUserKey || !ciphertext.trim() || isDecrypting}
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
                  使用身份解密
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
                  <span className="text-sm text-green-400">使用身份 "{selectedUserKey}" 解密成功</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* IBE Workflow & Usage Notes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-yellow-400" />
              <span>IBE工作流程</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center text-xs font-bold text-white">
                  1
                </div>
                <div>
                  <h4 className="font-semibold text-white">系统初始化</h4>
                  <p className="text-sm text-gray-400">PKG生成系统主密钥对</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold text-white">
                  2
                </div>
                <div>
                  <h4 className="font-semibold text-white">用户注册</h4>
                  <p className="text-sm text-gray-400">PKG为用户身份生成私钥</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center text-xs font-bold text-white">
                  3
                </div>
                <div>
                  <h4 className="font-semibold text-white">身份加密</h4>
                  <p className="text-sm text-gray-400">使用接收者身份和系统公钥加密</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-gradient-to-r from-orange-500 to-red-500 flex items-center justify-center text-xs font-bold text-white">
                  4
                </div>
                <div>
                  <h4 className="font-semibold text-white">身份解密</h4>
                  <p className="text-sm text-gray-400">使用对应身份的私钥解密</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Shield className="h-5 w-5 text-green-400" />
              <span>IBE优势特点</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-white mb-2">核心优势</h4>
                <ul className="text-gray-400 space-y-1 text-sm">
                  <li>• 无需证书基础设施(PKI)</li>
                  <li>• 身份即公钥，简化密钥管理</li>
                  <li>• 支持离线加密</li>
                  <li>• 减少密钥分发复杂度</li>
                </ul>
              </div>
              <Separator className="bg-white/10" />
              <div>
                <h4 className="font-semibold text-white mb-2">应用场景</h4>
                <ul className="text-gray-400 space-y-1 text-sm">
                  <li>• 企业内部安全通信</li>
                  <li>• 电子邮件加密</li>
                  <li>• 物联网设备认证</li>
                  <li>• 云存储数据保护</li>
                </ul>
              </div>
              <Separator className="bg-white/10" />
              <div>
                <h4 className="font-semibold text-white mb-2">注意事项</h4>
                <ul className="text-gray-400 space-y-1 text-sm">
                  <li>• PKG是可信第三方</li>
                  <li>• 需要安全的密钥分发渠道</li>
                  <li>• 身份撤销机制重要</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
