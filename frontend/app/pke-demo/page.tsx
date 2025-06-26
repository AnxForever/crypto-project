"use client"

import { useState, useCallback, type ChangeEvent } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import {
  Key,
  Lock,
  Unlock,
  UploadCloud,
  DownloadCloud,
  FileText,
  Send,
  RefreshCw,
  Shield,
  CheckCircle,
  PlayCircle,
  User,
  Users,
  FileUp,
  FileDown,
} from "lucide-react"

type PKEAlgorithm = "ecies" | "elgamal" | "sm2"

interface KeyPair {
  publicKey: string
  privateKey: string
}

interface EncryptedFile {
  name: string
  type: string
  size: number
  encryptedData: string // Base64 encoded encrypted content
  algorithm: PKEAlgorithm
}

export default function PKEDemoPage() {
  const [algorithm, setAlgorithm] = useState<PKEAlgorithm>("ecies")
  const [senderKeys, setSenderKeys] = useState<KeyPair | null>(null)
  const [recipientKeys, setRecipientKeys] = useState<KeyPair | null>(null)
  const [fileToEncrypt, setFileToEncrypt] = useState<File | null>(null)
  const [encryptedFile, setEncryptedFile] = useState<EncryptedFile | null>(null)
  const [decryptedFileContent, setDecryptedFileContent] = useState<string | null>(null)
  const [isGeneratingSenderKeys, setIsGeneratingSenderKeys] = useState(false)
  const [isGeneratingRecipientKeys, setIsGeneratingRecipientKeys] = useState(false)
  const [isEncrypting, setIsEncrypting] = useState(false)
  const [isDecrypting, setIsDecrypting] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const { toast } = useToast()

  const algorithmInfo = {
    ecies: { name: "ECIES", description: "高效椭圆曲线加密" },
    elgamal: { name: "ElGamal", description: "经典离散对数加密" },
    sm2: { name: "SM2", description: "国密标准椭圆曲线加密" },
  }

  const generateKeys = async (userType: "sender" | "recipient") => {
    if (userType === "sender") setIsGeneratingSenderKeys(true)
    else setIsGeneratingRecipientKeys(true)

    try {
      await new Promise((resolve) => setTimeout(resolve, 1000)) // Simulate key generation
      const mockKeyPair: KeyPair = {
        publicKey: `-----BEGIN ${algorithm.toUpperCase()} PUBLIC KEY-----\n${btoa(
          `${userType}-PublicKey-${algorithm}-${Date.now()}`,
        )}\n-----END ${algorithm.toUpperCase()} PUBLIC KEY-----`,
        privateKey: `-----BEGIN ${algorithm.toUpperCase()} PRIVATE KEY-----\n${btoa(
          `${userType}-PrivateKey-${algorithm}-${Date.now()}`,
        )}\n-----END ${algorithm.toUpperCase()} PRIVATE KEY-----`,
      }
      if (userType === "sender") setSenderKeys(mockKeyPair)
      else setRecipientKeys(mockKeyPair)
      toast({
        title: "密钥生成成功",
        description: `${userType === "sender" ? "发送方" : "接收方"} ${algorithmInfo[algorithm].name} 密钥对已生成。`,
      })
    } catch (error) {
      toast({ title: "密钥生成失败", variant: "destructive" })
    } finally {
      if (userType === "sender") setIsGeneratingSenderKeys(false)
      else setIsGeneratingRecipientKeys(false)
    }
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFileToEncrypt(event.target.files[0])
      setEncryptedFile(null)
      setDecryptedFileContent(null)
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles && acceptedFiles[0]) {
      setFileToEncrypt(acceptedFiles[0])
      setEncryptedFile(null)
      setDecryptedFileContent(null)
    }
  }, [])

  const encryptFile = async () => {
    if (!fileToEncrypt || !recipientKeys) {
      toast({
        title: "加密失败",
        description: "请选择文件并确保接收方已生成密钥。",
        variant: "destructive",
      })
      return
    }
    setIsEncrypting(true)
    setUploadProgress(0)

    try {
      // Simulate file reading and encryption
      const reader = new FileReader()
      reader.onload = async (e) => {
        const fileContent = e.target?.result as string
        // Simulate encryption process
        for (let i = 0; i <= 100; i += 10) {
          await new Promise((resolve) => setTimeout(resolve, 100))
          setUploadProgress(i)
        }
        const encryptedData = btoa(`ENCRYPTED_WITH_${algorithm}::${fileContent}`) // Mock encryption
        setEncryptedFile({
          name: fileToEncrypt.name,
          type: fileToEncrypt.type,
          size: fileToEncrypt.size,
          encryptedData,
          algorithm,
        })
        toast({
          title: "文件加密成功",
          description: `${fileToEncrypt.name} 已使用 ${recipientKeys.publicKey.substring(0, 20)}... 公钥加密。`,
        })
      }
      reader.readAsText(fileToEncrypt) // Reading as text for demo, binary for real use
    } catch (error) {
      toast({ title: "文件加密失败", variant: "destructive" })
    } finally {
      setIsEncrypting(false)
      setUploadProgress(100)
    }
  }

  const decryptFile = async () => {
    if (!encryptedFile || !recipientKeys) {
      toast({
        title: "解密失败",
        description: "没有加密文件或接收方私钥不可用。",
        variant: "destructive",
      })
      return
    }
    setIsDecrypting(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000)) // Simulate decryption
      const decryptedData = atob(encryptedFile.encryptedData).replace(`ENCRYPTED_WITH_${encryptedFile.algorithm}::`, "")
      setDecryptedFileContent(decryptedData)
      toast({ title: "文件解密成功", description: `${encryptedFile.name} 已成功解密。` })
    } catch (error) {
      toast({ title: "文件解密失败", variant: "destructive" })
    } finally {
      setIsDecrypting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-3xl p-8 border-white/10">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-r from-orange-500 to-red-500 bg-opacity-20">
            <PlayCircle className="h-6 w-6 text-orange-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">PKE应用演示：安全文件共享</h1>
            <p className="text-gray-400">PKE Application Demo: Secure File Sharing</p>
          </div>
        </div>
        <p className="text-gray-300 max-w-3xl leading-relaxed">
          体验公钥加密在安全文件共享场景中的应用。模拟文件从发送方加密到接收方解密的完整流程。
          选择PKE算法，生成密钥对，加密文件并安全传输。
        </p>
      </div>

      {/* Algorithm Selection */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Shield className="h-5 w-5 text-purple-400" />
            <span>选择PKE加密算法</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Select value={algorithm} onValueChange={(value: PKEAlgorithm) => setAlgorithm(value)}>
            <SelectTrigger className="bg-white/5 border-white/10 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="glass border-white/10">
              <SelectItem value="ecies">ECIES - {algorithmInfo.ecies.description}</SelectItem>
              <SelectItem value="elgamal">ElGamal - {algorithmInfo.elgamal.description}</SelectItem>
              <SelectItem value="sm2">SM2 - {algorithmInfo.sm2.description}</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Key Generation Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sender Keys */}
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <User className="h-5 w-5 text-blue-400" />
              <span>发送方密钥管理</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={() => generateKeys("sender")}
              disabled={isGeneratingSenderKeys}
              className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:opacity-90 text-white border-0"
            >
              {isGeneratingSenderKeys ? (
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Key className="mr-2 h-4 w-4" />
              )}
              生成发送方密钥对
            </Button>
            {senderKeys && (
              <div className="space-y-2">
                <Label className="text-gray-300">发送方公钥:</Label>
                <Textarea value={senderKeys.publicKey} readOnly className="h-20 bg-white/5 text-xs font-mono" />
                <Label className="text-gray-300">发送方私钥:</Label>
                <Textarea value={senderKeys.privateKey} readOnly className="h-20 bg-white/5 text-xs font-mono" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recipient Keys */}
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Users className="h-5 w-5 text-green-400" />
              <span>接收方密钥管理</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={() => generateKeys("recipient")}
              disabled={isGeneratingRecipientKeys}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:opacity-90 text-white border-0"
            >
              {isGeneratingRecipientKeys ? (
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Key className="mr-2 h-4 w-4" />
              )}
              生成接收方密钥对
            </Button>
            {recipientKeys && (
              <div className="space-y-2">
                <Label className="text-gray-300">接收方公钥:</Label>
                <Textarea value={recipientKeys.publicKey} readOnly className="h-20 bg-white/5 text-xs font-mono" />
                <Label className="text-gray-300">接收方私钥:</Label>
                <Textarea value={recipientKeys.privateKey} readOnly className="h-20 bg-white/5 text-xs font-mono" />
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* File Encryption Section */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Lock className="h-5 w-5 text-red-400" />
            <span>文件加密与发送 (模拟)</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="file-upload" className="text-gray-300">
              选择要加密的文件
            </Label>
            <div
              className="mt-2 flex justify-center items-center w-full h-32 px-6 pt-5 pb-6 border-2 border-dashed rounded-md cursor-pointer
                         border-white/20 hover:border-white/40 bg-white/5 hover:bg-white/10 transition-colors"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault()
                onDrop(Array.from(e.dataTransfer.files))
              }}
            >
              <div className="space-y-1 text-center">
                <UploadCloud className="mx-auto h-10 w-10 text-gray-400" />
                <div className="flex text-sm text-gray-400">
                  <Label
                    htmlFor="file-upload-input"
                    className="relative cursor-pointer rounded-md font-medium text-purple-400 hover:text-purple-300 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-purple-500"
                  >
                    <span>上传文件</span>
                    <Input
                      id="file-upload-input"
                      name="file-upload-input"
                      type="file"
                      className="sr-only"
                      onChange={handleFileChange}
                    />
                  </Label>
                  <p className="pl-1">或拖拽文件到此处</p>
                </div>
                <p className="text-xs text-gray-500">任何文本文件，最大 5MB</p>
              </div>
            </div>
          </div>

          {fileToEncrypt && (
            <div className="p-3 rounded-md bg-white/10 border border-white/20">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-purple-300" />
                <span className="text-sm text-white">{fileToEncrypt.name}</span>
                <span className="text-xs text-gray-400">({(fileToEncrypt.size / 1024).toFixed(2)} KB)</span>
              </div>
            </div>
          )}

          <Button
            onClick={encryptFile}
            disabled={!fileToEncrypt || !recipientKeys || isEncrypting}
            className="w-full bg-gradient-to-r from-red-500 to-pink-500 hover:opacity-90 text-white border-0"
          >
            {isEncrypting ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <FileUp className="mr-2 h-4 w-4" />}
            使用接收方公钥加密文件
          </Button>

          {isEncrypting && (
            <div className="space-y-1">
              <Progress value={uploadProgress} className="bg-white/10 h-2" />
              <p className="text-xs text-gray-400 text-center">加密进度: {uploadProgress}%</p>
            </div>
          )}

          {encryptedFile && (
            <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30 space-y-2">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <h4 className="font-semibold text-white">文件加密成功!</h4>
              </div>
              <p className="text-sm text-gray-300">
                文件 <span className="font-medium text-green-300">{encryptedFile.name}</span> 已使用{" "}
                <span className="font-medium text-green-300">{algorithmInfo[encryptedFile.algorithm].name}</span> 加密。
              </p>
              <Textarea
                value={encryptedFile.encryptedData.substring(0, 200) + "..."} // Show a snippet
                readOnly
                className="h-24 bg-white/5 text-xs font-mono"
                placeholder="加密后的文件内容 (部分)"
              />
              <Button variant="outline" size="sm" className="border-white/20 text-white hover:bg-white/10">
                <Send className="mr-2 h-4 w-4" />
                模拟发送给接收方
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* File Decryption Section */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Unlock className="h-5 w-5 text-cyan-400" />
            <span>文件接收与解密 (模拟)</span>
          </CardTitle>
          <CardDescription className="text-gray-400">接收方使用自己的私钥解密收到的文件。</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {!encryptedFile && (
            <div className="text-center py-8">
              <DownloadCloud className="mx-auto h-12 w-12 text-gray-500" />
              <p className="mt-2 text-sm text-gray-400">等待加密文件被"发送"...</p>
            </div>
          )}

          {encryptedFile && (
            <div className="p-3 rounded-md bg-white/10 border border-white/20">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-cyan-300" />
                <span className="text-sm text-white">已接收加密文件: {encryptedFile.name}</span>
                <span className="text-xs text-gray-400">({(encryptedFile.size / 1024).toFixed(2)} KB)</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">使用 {algorithmInfo[encryptedFile.algorithm].name} 加密</p>
            </div>
          )}

          <Button
            onClick={decryptFile}
            disabled={!encryptedFile || !recipientKeys || isDecrypting}
            className="w-full bg-gradient-to-r from-cyan-500 to-sky-500 hover:opacity-90 text-white border-0"
          >
            {isDecrypting ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <FileDown className="mr-2 h-4 w-4" />}
            使用接收方私钥解密文件
          </Button>

          {decryptedFileContent && (
            <div className="p-4 rounded-lg bg-sky-500/10 border border-sky-500/30 space-y-2">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-sky-400" />
                <h4 className="font-semibold text-white">文件解密成功!</h4>
              </div>
              <Label className="text-gray-300">解密后的文件内容:</Label>
              <Textarea value={decryptedFileContent} readOnly className="h-32 bg-white/5 text-sm" />
              <Button variant="outline" size="sm" className="border-white/20 text-white hover:bg-white/10">
                <DownloadCloud className="mr-2 h-4 w-4" />
                下载解密文件 (模拟)
              </Button>
            </div>
          )}
          {isDecrypting && !decryptedFileContent && (
            <div className="text-center py-4">
              <p className="text-sm text-gray-400">正在解密文件...</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
